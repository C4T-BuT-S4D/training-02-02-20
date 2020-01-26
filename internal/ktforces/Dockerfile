FROM golang:1.13.5-alpine

ADD src /app
WORKDIR /app
RUN go get
RUN go build -o ktforces

CMD ["./ktforces"]
