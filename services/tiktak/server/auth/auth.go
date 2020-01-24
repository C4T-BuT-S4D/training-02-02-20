package auth

import (
	"crypto/sha256"
	"fmt"
)

var Salt = ""

func SetSalt(s string) {
	Salt = s
}

func RandomSalt() {

}

func Validate(id string, hash string) bool {
	return Generate(id) == hash
}

func Generate(id string) string {
	return hashSha(Salt, id)
}

func hashSha(strings ...string) string {
	h := sha256.New()
	for _, s := range strings {
		h.Write([]byte(s))
	}
	return fmt.Sprintf("%x", h.Sum(nil))
}
