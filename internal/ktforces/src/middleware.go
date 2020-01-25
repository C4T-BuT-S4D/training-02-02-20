package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

func withCORSAllowAll(c *gin.Context) {
	c.Writer.Header().Set("Access-Control-Allow-Origin", "http://127.0.0.1:8080")
	c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
	c.Writer.Header().Set("Access-Control-Allow-Headers", "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Referer")
}

func (ks *KTFServer) withCurrentUser() gin.HandlerFunc {
	return func(c *gin.Context) {
		username, err := ks.DataController.ValidateSession(c)
		if err != nil {
			c.JSON(http.StatusForbidden, gin.H{"error": err.Error()})
			c.Abort()
			return
		}
		user, err := ks.DataController.GetUser(username)
		if err != nil {
			c.JSON(http.StatusForbidden, gin.H{"error": err.Error()})
			c.Abort()
			return
		}
		c.Set("user", user)
	}
}
