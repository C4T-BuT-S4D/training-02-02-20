package main

import (
	"context"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	"github.com/gocraft/dbr/v2"
	"github.com/thanhpk/randstr"
	"net/http"
	"os"
	"os/signal"
	"tiktak/db"
	"tiktak/server"
	"tiktak/server/auth"
	"tiktak/video"
	"time"
)

func main() {
	conn, err := dbr.Open(
		"mysql",
		"root:root@tcp(db:3306)/tiktak", nil)

	if err != nil {
		panic(err)
	}
	defer conn.Close()

	auth.SetSalt(randstr.Hex(20))
	config := server.Config{
		StaticFolder:    "public/static",
		VttFolder:       "public/vtt",
		TemplatesFolder: "templates",
	}
	srv := server.NewServer(db.New(conn), &video.Storage{Directory: "public/video"}, config)

	// Start server
	go func() {
		if err := http.ListenAndServe(":4000", srv); err != nil {
			fmt.Println("shutting down the server")
		}
	}()

	// Graceful shutdown
	quit := make(chan os.Signal)
	signal.Notify(quit, os.Interrupt)
	<-quit
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		panic(err)
	}
}
