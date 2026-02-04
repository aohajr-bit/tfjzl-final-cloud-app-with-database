FROM golang:1.22 AS builder

WORKDIR /app
COPY main.go .

RUN go mod init guestbook || true
RUN go get github.com/codegangsta/negroni github.com/gorilla/mux github.com/xyproto/simpleredis/v2
RUN go mod tidy

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o guestbook main.go

FROM alpine:3.19

WORKDIR /app
COPY --from=builder /app/guestbook /app/guestbook
COPY public /app/public

EXPOSE 3000
CMD ["/app/guestbook"]
