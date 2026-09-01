package coreclient

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestHealthDecodesEnvelope(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/health" {
			t.Fatalf("unexpected path: %s", r.URL.Path)
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{
			"request_id": "req-1",
			"mode": "seeded",
			"generated_at": "2026-08-31T00:00:00Z",
			"source": "test",
			"data": {
				"service": "marketsage-analytics",
				"status": "ok",
				"version": "0.1.0",
				"config": {
					"mode": "seeded",
					"data_dir": "data/local",
					"model_downloads_enabled": false,
					"http_auth_required": false
				},
				"dependencies": [
					{"name": "duckdb", "status": "ok", "detail": "ready"}
				]
			},
			"warnings": [],
			"caveats": []
		}`))
	}))
	defer server.Close()

	client, err := New(server.URL, time.Second)
	if err != nil {
		t.Fatalf("New returned error: %v", err)
	}

	health, err := client.Health(context.Background())
	if err != nil {
		t.Fatalf("Health returned error: %v", err)
	}

	if health.Data.Service != "marketsage-analytics" {
		t.Fatalf("unexpected service: %s", health.Data.Service)
	}
	if len(health.Data.Dependencies) != 1 || health.Data.Dependencies[0].Name != "duckdb" {
		t.Fatalf("dependencies not decoded: %#v", health.Data.Dependencies)
	}
}

func TestBearerTokenIsForwarded(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if got := r.Header.Get("Authorization"); got != "Bearer local-token" {
			t.Fatalf("authorization header not forwarded: %q", got)
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{
			"request_id": "req-1",
			"mode": "seeded",
			"generated_at": "2026-08-31T00:00:00Z",
			"source": "test",
			"data": {
				"service": "marketsage-analytics",
				"status": "ok",
				"version": "0.1.0",
				"config": {
					"mode": "seeded",
					"data_dir": "data/local",
					"model_downloads_enabled": false,
					"http_auth_required": true
				},
				"dependencies": []
			},
			"warnings": [],
			"caveats": []
		}`))
	}))
	defer server.Close()

	client, err := NewWithToken(server.URL, time.Second, "local-token")
	if err != nil {
		t.Fatalf("NewWithToken returned error: %v", err)
	}

	health, err := client.Health(context.Background())
	if err != nil {
		t.Fatalf("Health returned error: %v", err)
	}
	if !health.Data.Config.HTTPAuthRequired {
		t.Fatal("expected auth-required config to decode")
	}
}

func TestMarketSnapshotPostsTicker(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost || r.URL.Path != "/market/snapshot" {
			t.Fatalf("unexpected request: %s %s", r.Method, r.URL.Path)
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{
			"request_id": "req-2",
			"mode": "seeded",
			"generated_at": "2026-08-31T00:00:00Z",
			"source": "test",
			"data": {
				"ticker": "AAPL",
				"name": "Apple Inc.",
				"as_of": "2026-08-28T20:00:00Z",
				"price": 226.84,
				"currency": "USD",
				"change": 1.42,
				"change_percent": 0.63,
				"volume": 51234000,
				"sector": "Technology",
				"source_name": "seed"
			},
			"warnings": [],
			"caveats": []
		}`))
	}))
	defer server.Close()

	client, err := New(server.URL, time.Second)
	if err != nil {
		t.Fatalf("New returned error: %v", err)
	}

	snapshot, err := client.MarketSnapshot(context.Background(), TickerRequest{Ticker: "AAPL"})
	if err != nil {
		t.Fatalf("MarketSnapshot returned error: %v", err)
	}
	if snapshot.Data.Ticker != "AAPL" || snapshot.Data.Price <= 0 {
		t.Fatalf("unexpected snapshot: %#v", snapshot.Data)
	}
}

func TestNewRejectsInvalidURL(t *testing.T) {
	if _, err := New("file:///tmp/nope", time.Second); err == nil {
		t.Fatal("expected invalid url error")
	}
}
