package main

import (
	"encoding/base64"
	goalone "github.com/bwmarrin/go-alone"
	"github.com/gin-gonic/gin"
	"os"
)

type SessionStorage struct {
	secret []byte
	signer *goalone.Sword
}

func NewSessionStorage() *SessionStorage {
	ss := &SessionStorage{}
	ss.secret = []byte(os.Getenv("SECRET"))
	if len(ss.secret) == 0 {
		ss.secret = []byte("change_me")
	}
	ss.signer = goalone.New(ss.secret)
	return ss
}

func (ss *SessionStorage) SetSession(username string, c *gin.Context) {
	token := ss.signer.Sign([]byte(username))
	tokenEnc := base64.StdEncoding.EncodeToString(token)
	c.SetCookie("session", tokenEnc, 24*3600, "/", "", false, true)
}

func (ss *SessionStorage) ValidateSession(c *gin.Context) (username string, err error) {
	tokenEnc, err := c.Cookie("session")
	if err != nil {
		return
	}
	token, err := base64.StdEncoding.DecodeString(tokenEnc)
	if err != nil {
		return
	}
	data, err := ss.signer.Unsign(token)
	if err != nil {
		return
	}
	username = string(data)
	return
}
