package video

import (
	"bytes"
	"context"
	"fmt"
	"math"
	"os/exec"
	"strings"
)

func GetDuration(ctx context.Context, inp string) (res float64, err error) {

	args := []string{"-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", inp}

	cmd := exec.CommandContext(ctx, "ffprobe", args...)

	out, err := cmd.Output()

	if err != nil {
		return -1, err
	}

	_, err = fmt.Fscan(bytes.NewReader(out), &res)
	return
}

func GenerateVtt(ctx context.Context, inp string, s string) ([]string, error) {
	duration, err := GetDuration(ctx, inp)
	if err != nil {
		return nil, err
	}
	lines := strings.Split(s, "\n")
	vttLines := make([]string, len(lines))
	delta := duration / float64(len(lines))
	for i := range vttLines {
		s1 := generateStamp(float64(i) * delta)
		s2 := generateStamp(float64(i+1) * delta)
		vttLines[i] = fmt.Sprintf("%s --> %s\n", s1, s2)
		vttLines[i] += lines[i] + "\n"
	}
	return vttLines, err

}

func generateStamp(p float64) string {
	m := math.Floor(p / 60)
	s := math.Mod(p, 60.0)
	return fmt.Sprintf("%02.0f:%06.3f", m, s)

}
