package main

import (
    "crypto/sha1"
    "fmt"
    "strconv"
)

func captcha(nonce []byte) int {
    for i := 0; ; i++ {
        s := strconv.Itoa(i)
        cur := make([]byte, len(nonce) + len(s))
        copy(cur, nonce)
        copy(cur[len(nonce):], s)

        hs := sha1.New()
        _, err := hs.Write(cur)
        if err != nil {
            panic(err)
        }

        res := fmt.Sprintf("%x", hs.Sum(nil))[:6]
        if res == "133337" {
            return i
        }
    }
}

func main() {
    fmt.Println(captcha([]byte("test_captcha")))
}