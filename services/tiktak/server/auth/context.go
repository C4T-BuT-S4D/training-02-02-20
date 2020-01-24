package auth

import (
	"github.com/labstack/echo"
	"net/http"
	"strconv"
)

const HashCookieName = "hash"
const IdCookieName = "user_id"

func Cookies(id int64) (*http.Cookie, *http.Cookie) {
	ids := strconv.FormatInt(id, 10)
	return &http.Cookie{Value: ids, Name: IdCookieName}, &http.Cookie{Value: Generate(ids), Name: HashCookieName}
}

type Context struct {
	echo.Context
}

func (uc *Context) GetId() (uid int64) {
	idc, err := uc.Cookie(IdCookieName)
	if err != nil {
		return
	}
	hashc, err := uc.Cookie(HashCookieName)
	if err != nil {
		return
	}

	v, err := strconv.ParseInt(idc.Value, 10, 64)
	if Validate(idc.Value, hashc.Value) && err == nil {
		uid = v
	}
	return
}
