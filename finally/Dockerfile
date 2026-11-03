# Dockerfile for Go web server
# Template variables: http://app:8000, 8000
# Multi-stage build: golang:1.22-alpine builder -> alpine:3.20 runtime
# The web app runs on HOST (not in Docker). Playwright container reaches it via host.docker.internal.

FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY cmd/server/main.go ./cmd/server/
RUN CGO_ENABLED=0 go build -o /server ./cmd/server

FROM alpine:3.20
WORKDIR /app
COPY --from=builder /server /usr/local/bin/server
COPY web ./web
EXPOSE 8080
CMD ["server", "-addr", ":8080"]