package video

import (
	"errors"
	"github.com/google/uuid"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
)

const (
	MaxSize = 5 << 20
)

var (
	validationError = errors.New("unsupported video format. should be webm")
)

type Storage struct {
	Directory string
}

func (p *Storage) validateWebm(h io.Reader) bool {
	header := make([]byte, 512)
	_, err := h.Read(header)
	if err != nil {
		return false
	}
	if http.DetectContentType(header) == "video/webm" {
		return true
	}
	return false
}

func (p *Storage) Store(src multipart.File) (string, error) {
	if !p.validateWebm(src) {
		return "", validationError
	}
	_, err := src.Seek(0, io.SeekStart)
	if err != nil {
		return "", err
	}

	vid := p.generateId()
	dst, err := os.Create(p.Path(vid))
	if err != nil {
		return "", err
	}
	defer dst.Close()

	_, err = io.Copy(dst, src)
	return vid, err
}

func (p *Storage) Path(vid string) string {
	return filepath.Join(p.Directory, vid) + ".webm"
}

func (p *Storage) generateId() string {
	return uuid.New().String()
}
