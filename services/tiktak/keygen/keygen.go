package keygen

/*
#cgo LDFLAGS: ${SRCDIR}/legacy/keygen.a -lm
#include <keygen.h>
*/
import "C"
import (
	"strings"
	"unsafe"
)

func GenerateKey(vid int) string {
	var key [C.TOK_SIZE]byte
	keyPtr := (*C.char)(unsafe.Pointer(&key[0]))
	C.GenerateToken(C.int(vid), keyPtr)
	res := strings.Builder{}
	for _, v := range key {
		res.WriteByte(v)
	}
	return res.String()
}

func ValidateKey(token string, vid int) bool {
	res := C.ValidateToken(C.int(vid), C.CString(token))
	return res == 1
}
