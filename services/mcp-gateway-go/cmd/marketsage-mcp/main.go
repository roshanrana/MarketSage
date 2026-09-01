package main

import (
	"context"
	"log/slog"
	"os"
	"time"

	"github.com/modelcontextprotocol/go-sdk/mcp"
	"github.com/roshanrana/marketsage/services/mcp-gateway-go/internal/coreclient"
	gateway "github.com/roshanrana/marketsage/services/mcp-gateway-go/internal/server"
)

const version = "0.1.0"

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stderr, &slog.HandlerOptions{Level: slog.LevelInfo}))
	analyticsURL := getenv("MARKETSAGE_ANALYTICS_URL", "http://127.0.0.1:8765")
	client, err := coreclient.NewWithToken(
		analyticsURL,
		5*time.Second,
		os.Getenv("MARKETSAGE_HTTP_TOKEN"),
	)
	if err != nil {
		logger.Error("invalid analytics url", "error", err)
		os.Exit(1)
	}

	server := gateway.New(client, version)
	if err := server.Run(context.Background(), &mcp.StdioTransport{}); err != nil {
		logger.Error("mcp server stopped", "error", err)
		os.Exit(1)
	}
}

func getenv(key string, fallback string) string {
	value := os.Getenv(key)
	if value == "" {
		return fallback
	}
	return value
}
