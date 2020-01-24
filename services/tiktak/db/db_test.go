package db

import (
	"context"
	"github.com/gocraft/dbr/v2"
	_ "github.com/mattn/go-sqlite3"
	"testing"
)

func setup() (*Storage, func()) {
	conn, err := dbr.Open("sqlite3", ":memory:", nil)
	if err != nil {
		panic(err)
	}
	return New(conn), func() {
		conn.Close()
	}
}

func TestStorage_InsertUser(t *testing.T) {
	db, teardown := setup()
	defer teardown()
	ctx := context.Background()
	u := User{Login: "user", Password: "test"}
	err := db.InsertUser(ctx, &u)
	if err != nil {
		t.Error("failed to insert user", err.Error())
	}
	if u.ID <= 0 {
		t.Error("id should be positive")
	}
	err = db.InsertUser(ctx, &u)
	if err == nil {
		t.Error("should fail when inserting same user")
	}
}

func TestStorage_FindUser(t *testing.T) {
	db, teardown := setup()
	defer teardown()
	ctx := context.Background()
	u := User{Login: "user", Password: "test"}
	err := db.InsertUser(ctx, &u)
	if err != nil {
		t.Fatal("failed to insert user", err.Error())
	}

	u1, err := db.FindUser(ctx, "user", "test")
	if err != nil {
		t.Error("failed to retrieve user", err.Error())
	}
	if u1.Password != u.Password || u1.Login != u.Login {
		t.Error("users should be equal")
	}
	u2, err := db.FindUser(ctx, "test", "test")
	if err == nil {
		t.Error("should fail because no user not found")
	}
	if u2 != nil {
		t.Error("should be nil if user not found")
	}
}

func TestStorage_AddVideo(t *testing.T) {
	db, teardown := setup()
	defer teardown()
	ctx := context.Background()
	v := Video{
		UserID:      1,
		Description: "Test",
		Private:     false,
		Link:        "test",
	}
	err := db.AddVideo(ctx, &v)
	if err != nil {
		t.Error("failed to insert video")
	}

	if v.ID <= 0 {
		t.Error("id should be positive")
	}
}

func TestStorage_ListVideo(t *testing.T) {
	db, teardown := setup()
	defer teardown()
	ctx := context.Background()
	v := Video{
		UserID:      1,
		Description: "Test",
		Private:     false,
		Link:        "test",
	}
	err := db.AddVideo(ctx, &v)
	if err != nil {
		t.Fatal("failed to insert video")
	}

	vds, err := db.ListVideo(ctx, 1)
	if err != nil || len(vds) < 1 {
		t.Error("failed to retrieve videos from db")
	}

	v.ID = vds[0].ID
	if vds[0] != v {
		t.Error("v != res[0]")
	}
}

func TestStorage_ListUserVideo(t *testing.T) {
	db, teardown := setup()
	defer teardown()
	ctx := context.Background()
	for _, v := range []Video{
		{UserID: 1, Description: "Test", Private: false, Link: "test"},
		{UserID: 2, Description: "Test2", Private: false, Link: "test2"}} {
		if err := db.AddVideo(ctx, &v); err != nil {
			t.Fatal("failed to insert video:", err)
		}

	}

	for _, u := range []int64{1, 2} {
		vds, err := db.ListUserVideo(ctx, int64(u))
		if err != nil || len(vds) != 1 {
			t.Error("failed to retrieve videos from db for user: ", u)
		}
		if vds[0].UserID != u {
			t.Errorf("video with wrong uid found. Expected %d, found %d", u, vds[0].UserID)
		}
	}
}

func TestStorage_GetVideo(t *testing.T) {
	db, teardown := setup()
	defer teardown()
	ctx := context.Background()
	v := Video{
		UserID:      1,
		Description: "Test",
		Private:     false,
		Link:        "test",
	}
	err := db.AddVideo(ctx, &v)
	if err != nil {
		t.Fatal("failed to insert video")
	}

	v2, err := db.GetVideo(ctx, v.ID)
	if err != nil {
		t.Errorf("failed to get video %v", err.Error())
	}
	if *v2 != v {
		t.Errorf("videos dont match: expected %v, found %v", v, v2)
	}
}

func TestStorage_AddAccess_HavAccess(t *testing.T) {
	db, teardown := setup()
	defer teardown()
	ctx := context.Background()
	if db.HaveAccess(ctx, 1, 2) {
		t.Error("should not have access: empty table")
	}
	if err := db.AddAccess(ctx, 1, 2); err != nil {
		t.Error("failed to add access", err)
	}
	if !db.HaveAccess(ctx, 1, 2) {
		t.Error("should have access")
	}

}
