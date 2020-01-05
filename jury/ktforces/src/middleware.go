package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

func withCORSAllowAll(c *gin.Context) {
	c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
}

func (ks *KTFServer) withCurrentUser() gin.HandlerFunc {
	return func(c *gin.Context) {
		username, err := ks.DataController.ValidateSession(c)
		if err != nil {
			c.JSON(http.StatusForbidden, gin.H{"error": err.Error()})
			c.Abort()
			return
		}
		user, err := ks.DataController.TryGetUser(username)
		if err != nil {
			c.JSON(http.StatusForbidden, gin.H{"error": err.Error()})
			c.Abort()
			return
		}
		c.Set("user", user)
	}
}
