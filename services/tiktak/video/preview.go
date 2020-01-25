package video

import (
	"context"
	"fmt"
	"github.com/disintegration/imaging"
	"image"
	"image/png"
	"os"
	"os/exec"
	"strings"
	"time"
)

var (
	ProcessingDeadline = 2 * time.Second
	semaphore          = make(chan struct{}, 75)
)

func generatePreview(ctx context.Context, inp string, out string) error {
	cmd := exec.CommandContext(ctx, "ffmpeg", "-y", "-i", inp, "-vframes", "1", out)
	s := strings.Builder{}
	cmd.Stdout = &s
	cmd.Stderr = &s
	err := cmd.Run()
	if err != nil {
		fmt.Println(s.String())
	}
	return err
}

func GeneratePreview(ctx context.Context, inp string, out string) error {
	select {
	case semaphore <- struct{}{}:
		ctx, cancel := context.WithTimeout(ctx, ProcessingDeadline)
		defer func() {
			cancel()
			<-semaphore
		}()
		return generatePreview(ctx, inp, out)
	case <-ctx.Done():
		return ctx.Err()
	}
}

func Blur(inp string, out string) error {
	f, err := os.Open(inp)
	if err != nil {
		return err
	}
	img, _, err := image.Decode(f)
	if err != nil {
		return err
	}
	outimg := imaging.Blur(img, 5)
	outfile, err := os.Create(out)
	if err != nil {
		return err
	}
	defer outfile.Close()
	return png.Encode(outfile, outimg)
}
