package db

type User struct {
	ID       int64
	Login    string
	Password string
}

type Video struct {
	ID          int64
	UserID      int64
	Description string
	Private     bool
	Link        string
}
