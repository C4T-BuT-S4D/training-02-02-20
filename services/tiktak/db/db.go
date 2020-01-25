package db

import (
	"context"
	"github.com/gocraft/dbr/v2"
)

type Storage struct {
	conn *dbr.Connection
}

func New(conn *dbr.Connection) *Storage {
	s := Storage{conn}
	s.init()
	return &s
}

func (s *Storage) init() {
	for _, q := range []string{
		"CREATE TABLE IF NOT EXISTS users(id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT, login VARCHAR(200) UNIQUE , password VARCHAR(200))",
		"CREATE TABLE IF NOT EXISTS video(id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT, user_id INTEGER, description VARCHAR(500), private BOOLEAN, link VARCHAR(400))",
		"CREATE TABLE IF NOT EXISTS access(id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT, user_id INTEGER, video_id INTEGER)",
	} {
		_, err := s.conn.Exec(q)
		if err != nil {
			panic(err)
		}
	}
}

func (s *Storage) InsertUser(ctx context.Context, user *User) error {
	sess := s.conn.NewSession(nil)
	_, err := sess.InsertInto("users").Columns("login", "password").Record(user).ExecContext(ctx)
	return err
}

func (s *Storage) FindUser(ctx context.Context, login, password string) (*User, error) {
	sess := s.conn.NewSession(nil)
	user := new(User)
	err := sess.Select("*").
		From("users").
		Where("login = ?", login).
		Where("password = ?", password).
		LoadOneContext(ctx, user)
	if err != nil {
		return nil, err
	}
	return user, err
}

func (s *Storage) AddVideo(ctx context.Context, v *Video) error {
	sess := s.conn.NewSession(nil)
	_, err := sess.InsertInto("video").
		Columns("user_id", "description", "private", "link").
		Record(v).ExecContext(ctx)

	return err
}

func (s *Storage) ListVideo(ctx context.Context, limit int) (v []Video, err error) {
	sess := s.conn.NewSession(nil)
	_, err = sess.Select("*").
		From("video").
		OrderDesc("id").
		Limit(uint64(limit)).
		LoadContext(ctx, &v)
	return
}

func (s *Storage) ListUserVideo(ctx context.Context, userId int64) (v []Video, err error) {
	sess := s.conn.NewSession(nil)
	_, err = sess.Select("*").
		From("video").
		Where("user_id = ?", userId).
		OrderDesc("id").LoadContext(ctx, &v)
	return
}

func (s *Storage) GetVideo(ctx context.Context, id interface{}) (*Video, error) {
	sess := s.conn.NewSession(nil)
	v := new(Video)
	err := sess.Select("*").From("video").Where("id = ?", id).LoadOneContext(ctx, v)
	return v, err
}

func (s *Storage) HaveAccess(ctx context.Context, id interface{}, userId int64) bool {
	sess := s.conn.NewSession(nil)

	var c int
	err := sess.Select("count(*)").
		From("access").
		Where("user_id = ?", userId).
		Where("video_id = ?", id).
		LoadOneContext(ctx, &c)
	if err != nil {
		return false
	}
	return c > 0
}

func (s *Storage) AddAccess(ctx context.Context, id int, userId int64) error {
	sess := s.conn.NewSession(nil)

	_, err := sess.InsertInto("access").
		Pair("video_id", id).
		Pair("user_id", userId).
		ExecContext(ctx)
	return err
}
