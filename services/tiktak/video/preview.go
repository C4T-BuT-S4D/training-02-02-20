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
)

func GeneratePreview(ctx context.Context, inp string, out string) error {
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
