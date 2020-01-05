package main

import (
	"context"
	"github.com/sirupsen/logrus"
	"net/http"
	"os"
	"os/signal"
	"time"
)

func main() {
	ks := NewServer()

	httpServer := http.Server{
		Addr:         "0.0.0.0:9998",
		Handler:      ks,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  30 * time.Second,
	}

	go func() {
		logrus.Infof("Serving on http://%s", httpServer.Addr)
		if err := httpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logrus.Fatal("Error serving api server: ", err)
		}
	}()

	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt)
	signal.Notify(c, os.Kill)

	<-c

	logrus.Infof("Shutting down http server...")

	httpCtx, httpCancel := context.WithTimeout(context.Background(), time.Second*10)
	defer httpCancel()
	err := httpServer.Shutdown(httpCtx)
	if err != nil {
		logrus.Fatal(err)
	}

	logrus.Infof("Shutdown successful")
}
