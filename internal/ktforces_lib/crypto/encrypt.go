package main

import (
	"crypto/cipher"
)

type ctr struct {
	b       cipher.Block
	ctr     []byte
	out     []byte
	outUsed int
}

const streamBufferSize = 512

type ctrAble interface {
	NewCTR(iv []byte) cipher.Stream
}

func NewCTR(block cipher.Block, iv []byte) cipher.Stream {
	if ctr, ok := block.(ctrAble); ok {
		return ctr.NewCTR(iv)
	}
	if len(iv) != block.BlockSize() {
		panic("cipher.NewCTR: IV length must equal block size")
	}
	bufSize := streamBufferSize
	if bufSize < block.BlockSize() {
		bufSize = block.BlockSize()
	}
	ivc := make([]byte, len(iv))
	copy(ivc, iv)
	return &ctr{
		b:       block,
		ctr:     ivc,
		out:     make([]byte, 0, bufSize),
		outUsed: 0,
	}
}

func (x *ctr) refill() {
	remain := len(x.out) - x.outUsed
	copy(x.out, x.out[x.outUsed:])
	x.out = x.out[:cap(x.out)]
	bs := x.b.BlockSize()
	for remain <= len(x.out)-bs {
		x.b.Encrypt(x.out[remain:], x.ctr)
		remain += bs
	}
	x.out = x.out[:remain]
	x.outUsed = 0
}

func xorBytes(dst, a, b []byte) (n int) {
	for i := range a {
		dst[i] = a[i] ^ b[i % len(b)]
	}
	return len(a)
}

func (x *ctr) XORKeyStream(dst, src []byte) {
	if len(dst) < len(src) {
		panic("crypto/cipher: output smaller than input")
	}
	for len(src) > 0 {
		if x.outUsed >= len(x.out)-x.b.BlockSize() {
			x.refill()
		}
		n := xorBytes(dst, src, x.out[x.outUsed:])
		dst = dst[n:]
		src = src[n:]
		x.outUsed += n
	}
}
