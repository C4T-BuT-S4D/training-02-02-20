package server

import (
	"context"
	"fmt"
	"github.com/labstack/echo"
	"github.com/labstack/echo/middleware"
	"html/template"
	"net/http"
	"os"
	"path"
	"strconv"
	"tiktak/db"
	"tiktak/keygen"
	"tiktak/server/auth"
	"tiktak/video"
	"time"
)

func NewServer(db *db.Storage, vs *video.Storage, c Config) *Server {
	s := &Server{echo.New(), db, vs, c}

	t := Template{template.Must(template.ParseGlob(c.TemplatesFolder + "/*.html"))}
	s.e.Renderer = &t
	s.e.Use(middleware.Recover())
	s.e.Use(func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			cc := &auth.Context{Context: c}
			return next(cc)
		}
	})
	s.routes()
	return s
}

type Server struct {
	e  *echo.Echo
	db *db.Storage
	vs *video.Storage
	c  Config
}

func (s *Server) loginPage(c echo.Context) error {
	return c.Render(200, "login", nil)
}

func (s *Server) handleLogin(c echo.Context) error {
	login := c.FormValue("login")
	password := c.FormValue("password")

	user, err := s.db.FindUser(context.Background(), login, password)
	if err != nil {
		return c.Render(http.StatusUnprocessableEntity, "login", ErrorResponse{err.Error()})
	}

	c1, c2 := auth.Cookies(user.ID)
	c.SetCookie(c1)
	c.SetCookie(c2)

	return c.Redirect(http.StatusFound, "/home")
}

func (s *Server) registerPage(c echo.Context) error {
	return c.Render(200, "register", nil)
}

func (s *Server) handleRegister(c echo.Context) error {
	login := c.FormValue("login")
	password := c.FormValue("password")
	if login == "" || password == "" {
		return c.Render(http.StatusUnprocessableEntity, "register", ErrorResponse{"fill the form"})
	}
	u := db.User{Login: login, Password: password}
	err := s.db.InsertUser(context.Background(), &u)
	if err != nil {
		return c.Render(http.StatusUnprocessableEntity, "register", ErrorResponse{err.Error()})
	}

	c1, c2 := auth.Cookies(u.ID)
	c.SetCookie(c1)
	c.SetCookie(c2)

	return c.Redirect(http.StatusFound, "/home")
}

func (s *Server) createPage(c echo.Context) error {
	return c.Render(http.StatusOK, "create", nil)
}

func (s *Server) handleCreate(c echo.Context) error {
	ac := c.(*auth.Context)
	uid := ac.GetId()

	f, err := c.FormFile("video")

	if err != nil {
		return c.Render(http.StatusUnprocessableEntity, "create", ErrorResponse{err.Error()})
	}
	if f.Size > video.MaxSize {
		return c.Render(http.StatusUnprocessableEntity, "create", ErrorResponse{"file is too large"})
	}
	vfile, err := f.Open()
	if err != nil {
		return c.Render(http.StatusUnprocessableEntity, "create", ErrorResponse{err.Error()})
	}

	link, err := s.vs.Store(vfile)
	if err != nil {
		return c.Render(http.StatusUnprocessableEntity, "create", ErrorResponse{"failed to store video: " + err.Error()})
	}

	descr := c.FormValue("description")
	subt := c.FormValue("subtitles")
	isPrivate := c.FormValue("private")
	v := db.Video{UserID: uid, Description: descr, Private: isPrivate == "on", Link: link}

	ctx := context.Background()
	err = s.db.AddVideo(ctx, &v)
	if err != nil {
		return c.Render(http.StatusUnprocessableEntity, "create", ErrorResponse{"failed to store record: " + err.Error()})
	}

	ppath := s.previewPath(v.ID)

	ctx, cancel := context.WithTimeout(ctx, time.Second*7)
	defer cancel()

	err = video.GeneratePreview(ctx, s.vs.Path(link), ppath)
	if err != nil {
		return c.Render(http.StatusUnprocessableEntity, "create", ErrorResponse{"failed to generate preview: " + err.Error()})
	}
	if err := s.storeVtt(ctx, v, subt); err != nil {
		return c.Render(http.StatusUnprocessableEntity, "create", ErrorResponse{err.Error()})
	}
	if v.Private {
		if err = video.Blur(ppath, s.privatePreviewPath(v.ID)); err != nil {
			return c.Render(http.StatusUnprocessableEntity, "create", ErrorResponse{"failed to blur preview: " + err.Error()})
		}
	}
	return c.Redirect(http.StatusFound, fmt.Sprintf("/watch/%d", v.ID))
}

func (s *Server) handleFeed(c echo.Context) error {
	ctx := context.Background()
	vds, err := s.db.ListVideo(ctx, 50)
	if err != nil {
		return c.JSON(http.StatusServiceUnavailable, jsonError(err.Error()))
	}
	resp := make([]FeedResponse, len(vds))
	for i, v := range vds {
		resp[i].ID = vds[i].ID
		if v.Private {
			resp[i].Preview = s.privatePreviewPath(v.ID)
		} else {
			resp[i].Preview = s.previewPath(v.ID)
		}
	}
	return c.Render(http.StatusOK, "feed", resp)
}

func (s *Server) handleWatch(c echo.Context) error {
	ac := c.(*auth.Context)
	vid := c.Param("id")
	ctx := context.Background()
	v, err := s.db.GetVideo(ctx, vid)
	if err != nil {
		return c.NoContent(http.StatusNotFound)
	}
	uid := ac.GetId()
	if s.haveAccess(ctx, uid, *v) {
		resp := WatchResponse{
			Description: v.Description,
			VttPath:     "/vtt/?id=" + vid,
			VideoPath:   s.vs.Path(v.Link),
		}
		return c.Render(http.StatusOK, "watch", resp)
	}
	return c.Render(http.StatusForbidden, "access", AccessResponse{ID: int(v.ID)})
}

func (s *Server) handleVtt(c echo.Context) error {
	ac := c.(*auth.Context)
	vid := c.QueryParam("id")
	uid := ac.GetId()
	ctx := context.Background()
	v, _ := s.db.GetVideo(ctx, vid)
	if !s.haveAccess(ctx, uid, *v) {
		return c.NoContent(http.StatusForbidden)
	}
	vttPath := path.Join(s.c.VttFolder, vid+".vtt")
	return c.File(vttPath)
}

func (s *Server) handleAccess(c echo.Context) error {
	ac := c.(*auth.Context)
	vidString := c.FormValue("videoID")
	vid, err := strconv.Atoi(vidString)
	if err != nil {
		return c.Render(http.StatusUnprocessableEntity, "access", AccessResponse{
			ErrorResponse: ErrorResponse{"bad video id: " + err.Error()},
			ID:            0,
		})
	}

	key := c.FormValue("token")
	if keygen.ValidateKey(key, vid) {
		ctx := context.Background()
		if err := s.db.AddAccess(ctx, vid, ac.GetId()); err != nil {
			return c.Render(http.StatusServiceUnavailable, "access", AccessResponse{
				ErrorResponse: ErrorResponse{"try again later: " + err.Error()},
				ID:            vid,
			})
		}
		return c.Redirect(http.StatusFound, "/watch/"+strconv.Itoa(vid))
	}
	return c.Render(http.StatusUnprocessableEntity, "access", AccessResponse{
		ErrorResponse: ErrorResponse{"Bad token"},
		ID:            vid,
	})

}

func (s *Server) homePage(c echo.Context) error {
	ac := c.(*auth.Context)
	vds, err := s.db.ListUserVideo(context.Background(), ac.GetId())
	if err != nil {
		return c.Render(http.StatusServiceUnavailable, "home", ErrorResponse{Error: err.Error()})
	}
	vresp := make([]VideoResponse, len(vds))
	for i, v := range vds {
		vresp[i].ID = v.ID
		vresp[i].Private = v.Private
		vresp[i].Description = v.Description
		if v.Private {
			vresp[i].Token = keygen.GenerateKey(int(v.ID))
			vresp[i].Preview = s.privatePreviewPath(v.ID)
		} else {
			vresp[i].Preview = s.previewPath(v.ID)
		}
	}
	return c.Render(http.StatusOK, "home", vresp)
}

func (s *Server) indexPage(c echo.Context) error {
	ac := c.(*auth.Context)
	if ac.GetId() != 0 {
		return c.Redirect(http.StatusFound, "/home")
	}
	return c.Redirect(http.StatusFound, "/login")
}

func (s *Server) haveAccess(ctx context.Context, uid int64, v db.Video) bool {
	if v.UserID == uid {
		return true
	}
	if !v.Private {
		return true
	}
	return s.db.HaveAccess(ctx, v.ID, uid)
}

func (s *Server) storeVtt(ctx context.Context, v db.Video, subtitles string) error {
	vtt, err := video.GenerateVtt(ctx, s.vs.Path(v.Link), subtitles)
	if err != nil {
		return err
	}

	f, err := os.Create(path.Join(s.c.VttFolder, fmt.Sprintf("%d.vtt", v.ID)))
	if err != nil {
		return err
	}
	defer f.Close()
	fmt.Fprint(f, "WEBVTT Kind: captions; Language: ctf\n\n")
	for _, line := range vtt {
		fmt.Fprintln(f, line)
	}
	return nil
}

func (s *Server) previewPath(vid int64) string {
	return path.Join(s.c.StaticFolder, fmt.Sprintf("preview_%d.png", vid))
}

func (s *Server) privatePreviewPath(vid int64) string {
	return path.Join(s.c.StaticFolder, fmt.Sprintf("preview_%d_blured.png", vid))
}

func (s *Server) routes() {
	s.e.GET("/login", s.loginPage)
	s.e.POST("/login", s.handleLogin)
	s.e.GET("/register", s.registerPage)
	s.e.POST("/register", s.handleRegister)
	s.e.GET("/create", s.createPage, auth.RequiredMiddleware)
	s.e.POST("/create", s.handleCreate, auth.RequiredMiddleware)
	s.e.GET("/feed", s.handleFeed)
	s.e.GET("/watch/:id", s.handleWatch)
	s.e.POST("/access", s.handleAccess, auth.RequiredMiddleware)
	s.e.GET("/vtt/", s.handleVtt)
	s.e.GET("/home", s.homePage, auth.RequiredMiddleware)
	s.e.Static("/"+s.vs.Directory, s.vs.Directory)
	s.e.Static("/"+s.c.StaticFolder, s.c.StaticFolder)
	s.e.GET("/", s.indexPage)
}

func (s *Server) Shutdown(ctx context.Context) error {
	return s.e.Shutdown(ctx)
}

func (s *Server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	s.e.ServeHTTP(w, r)
}
