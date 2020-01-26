package main

import (
	"crypto/aes"
)

var key []byte
var data []byte
var result []byte

//go:export keyAddr
func keyAddr() *byte {
	return &key[0]
}

//go:export dataAddr
func dataAddr() *byte {
	return &data[0]
}

//go:export resultAddr
func resultAddr() *byte {
	return &result[0]
}

//go:export allocateKey
func allocateKey(cnt int) {
	key = make([]byte, cnt)
}

//go:export allocateData
func allocateData(cnt int) {
	data = make([]byte, cnt)
}

//go:export encrypt
func encrypt() {
	block, err := aes.NewCipher(key)
	if err != nil {
		panic(err)
	}

	iv := []byte("1337133713371377")

	ctr := NewCTR(block, iv)

	result = make([]byte, len(data))
	ctr.XORKeyStream(result, data)
}

//go:export decrypt
func decrypt() {
	encrypt()
}

func main() {
}
