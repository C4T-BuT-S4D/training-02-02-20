package server

import "fmt"

func jsonError(s string) interface{} {
	return map[string]string{"error": s}
}

func jsonErrorf(f string, a ...interface{}) interface{} {
	return jsonError(fmt.Sprintf(f, a))
}

type BaseResponse struct {
	UserId int
	Error  string
}

type ErrorResponse struct {
	Error string
}

type FeedResponse struct {
	ID      int64
	Preview string
}

type WatchResponse struct {
	Description string
	VttPath     string
	VideoPath   string
}

type VideoResponse struct {
	FeedResponse
	Private     bool
	Token       string
	Description string
}

type AccessResponse struct {
	ErrorResponse
	ID int
}
