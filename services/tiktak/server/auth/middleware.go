package auth

import (
	"github.com/labstack/echo"
	"net/http"
)

func RequiredMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		ac := c.(*Context)
		if ac == nil || ac.GetId() == 0 {
			return c.Redirect(http.StatusFound, "/login")
		}
		return next(c)
	}
}
