package main

import (
	"github.com/gin-contrib/gzip"
	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
	"net/http"
)

type KTFServer struct {
	DataController *DataController
	Engine         *gin.Engine
}

func NewServer() *KTFServer {
	ms := &KTFServer{
		Engine:         gin.Default(),
		DataController: NewDataController(),
	}
	ms.registerMiddleware()
	ms.registerRoutes()
	return ms
}

func (ks *KTFServer) registerRoutes() {
	ks.Engine.RedirectTrailingSlash = true

	api := ks.Engine.Group("/api")
	api.GET("/", ks.statusHandler())
	api.GET("/ping/", ks.statusHandler())
	api.GET("/status/", ks.statusHandler())

	api.POST("/register/", ks.registerHandler())
	api.POST("/login/", ks.loginHandler())

	authorized := api.Group("/")
	authorized.Use(ks.withCurrentUser())

	users := authorized.Group("/users")
	users.GET("/me/", ks.meHandler())

	tasks := authorized.Group("/tasks")
	tasks.POST("/", ks.createTaskHandler())
	tasks.GET("/", ks.listTasksHandler())
	tasks.GET("/:id/", ks.getTaskHandler())
	tasks.POST("/:id/", ks.submitTaskHandler())

	logrus.Info("Routes registered successfully")
}

func (ks *KTFServer) registerMiddleware() {
	ks.Engine.Use(gzip.Gzip(gzip.DefaultCompression))
	ks.Engine.Use(withCORSAllowAll)
	logrus.Info("Middleware registered successfully")
}

func (ks *KTFServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	ks.Engine.ServeHTTP(w, r)
}
