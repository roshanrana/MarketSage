package server

import (
	"context"
	"strings"
	"testing"

	"github.com/modelcontextprotocol/go-sdk/mcp"
	"github.com/roshanrana/marketsage/services/mcp-gateway-go/internal/coreclient"
)

type fakeAnalytics struct {
	health *coreclient.HealthEnvelope
	err    error
}

func (f fakeAnalytics) Health(context.Context) (*coreclient.HealthEnvelope, error) {
	return f.health, f.err
}

func (f fakeAnalytics) Datasets(context.Context) (*coreclient.ResponseEnvelope[coreclient.DatasetStatusData], error) {
	return &coreclient.ResponseEnvelope[coreclient.DatasetStatusData]{
		RequestID: "req-datasets",
		Mode:      "seeded",
		Source:    "test",
		Data: coreclient.DatasetStatusData{
			Count: 1,
			Datasets: []coreclient.DatasetEntry{
				{DatasetID: "mteb/FinanceBenchRetrieval", Config: "corpus", Split: "test", RowsCount: 145},
			},
		},
	}, nil
}

func (f fakeAnalytics) MarketSnapshot(context.Context, coreclient.TickerRequest) (*coreclient.ResponseEnvelope[coreclient.MarketSnapshotData], error) {
	return &coreclient.ResponseEnvelope[coreclient.MarketSnapshotData]{
		RequestID: "req-market",
		Mode:      "seeded",
		Source:    "test",
		Data: coreclient.MarketSnapshotData{
			Ticker: "AAPL",
			Price:  226.84,
		},
	}, nil
}

func (f fakeAnalytics) PriceHistory(context.Context, coreclient.PriceHistoryRequest) (*coreclient.ResponseEnvelope[coreclient.PriceHistoryData], error) {
	return &coreclient.ResponseEnvelope[coreclient.PriceHistoryData]{
		RequestID: "req-history",
		Mode:      "seeded",
		Source:    "test",
		Data: coreclient.PriceHistoryData{
			Ticker: "AAPL",
			Observations: []coreclient.PriceObservation{
				{Date: "2026-08-28", Close: 226.84},
			},
		},
	}, nil
}

func (f fakeAnalytics) SentimentText(context.Context, coreclient.SentimentRequest) (*coreclient.ResponseEnvelope[coreclient.SentimentData], error) {
	return &coreclient.ResponseEnvelope[coreclient.SentimentData]{
		RequestID: "req-sentiment",
		Mode:      "seeded",
		Source:    "test",
		Data: coreclient.SentimentData{
			Label:      "positive",
			Confidence: 0.65,
			ModelID:    "marketsage-lexicon-v0",
			Fallback:   true,
		},
	}, nil
}

func (f fakeAnalytics) EvidenceSearch(context.Context, coreclient.EvidenceSearchRequest) (*coreclient.ResponseEnvelope[coreclient.EvidenceSearchData], error) {
	return &coreclient.ResponseEnvelope[coreclient.EvidenceSearchData]{
		RequestID: "req-evidence",
		Mode:      "seeded",
		Source:    "test",
		Data: coreclient.EvidenceSearchData{
			Query:         "revenue",
			Count:         1,
			RetrievalMode: "lexical",
			Results: []coreclient.EvidenceSnippet{
				{ID: "ev-1", Ticker: "AAPL", Score: 1},
			},
		},
	}, nil
}

func (f fakeAnalytics) ResearchBrief(context.Context, coreclient.ResearchBriefRequest) (*coreclient.ResponseEnvelope[coreclient.ResearchBriefData], error) {
	return &coreclient.ResponseEnvelope[coreclient.ResearchBriefData]{
		RequestID: "req-brief",
		Mode:      "seeded",
		Source:    "test",
		Data: coreclient.ResearchBriefData{
			RunID:   "run-1",
			Title:   "MarketSage brief: AAPL",
			Tickers: []string{"AAPL"},
		},
	}, nil
}

func (f fakeAnalytics) ResearchRun(context.Context, string) (*coreclient.ResponseEnvelope[coreclient.SavedResearchRunData], error) {
	return &coreclient.ResponseEnvelope[coreclient.SavedResearchRunData]{
		RequestID: "req-run",
		Mode:      "seeded",
		Source:    "test",
		Data: coreclient.SavedResearchRunData{
			RunID: "run-1",
			Output: coreclient.ResearchBriefData{
				RunID: "run-1",
				Title: "MarketSage brief: AAPL",
			},
		},
	}, nil
}

func TestHealthCheckMapsAnalyticsEnvelope(t *testing.T) {
	handler := &Handlers{
		analytics: fakeAnalytics{
			health: &coreclient.HealthEnvelope{
				RequestID: "req-1",
				Mode:      "seeded",
				Source:    "test",
				Data: coreclient.HealthData{
					Service: "marketsage-analytics",
					Status:  "ok",
					Version: "0.1.0",
					Dependencies: []coreclient.DependencyStatus{
						{Name: "duckdb", Status: "ok", Detail: "ready"},
					},
				},
				Warnings: []string{"seeded"},
				Caveats:  []string{"research only"},
			},
		},
	}

	_, output, err := handler.HealthCheck(context.Background(), &mcp.CallToolRequest{}, HealthInput{})
	if err != nil {
		t.Fatalf("HealthCheck returned error: %v", err)
	}

	if output.Service != "marketsage-analytics" {
		t.Fatalf("unexpected service: %s", output.Service)
	}
	if output.Status != "ok" {
		t.Fatalf("unexpected status: %s", output.Status)
	}
	if len(output.Dependencies) != 1 || output.Dependencies[0].Name != "duckdb" {
		t.Fatalf("unexpected dependencies: %#v", output.Dependencies)
	}
}

func TestNewRegistersServer(t *testing.T) {
	server := New(fakeAnalytics{}, "test")
	if server == nil {
		t.Fatal("expected server")
	}
}

func TestMarketSnapshotMapsAnalyticsEnvelope(t *testing.T) {
	handler := &Handlers{analytics: fakeAnalytics{}}

	_, output, err := handler.MarketSnapshot(context.Background(), &mcp.CallToolRequest{}, TickerInput{
		Ticker: "AAPL",
	})
	if err != nil {
		t.Fatalf("MarketSnapshot returned error: %v", err)
	}
	if output.Data.Ticker != "AAPL" || output.Data.Price <= 0 {
		t.Fatalf("unexpected output: %#v", output)
	}
}

func TestResearchRunResourceReturnsJSON(t *testing.T) {
	handler := &Handlers{analytics: fakeAnalytics{}}

	result, err := handler.ResearchRunResource(
		context.Background(),
		&mcp.ReadResourceRequest{
			Params: &mcp.ReadResourceParams{URI: "marketsage://runs/run-1"},
		},
	)
	if err != nil {
		t.Fatalf("ResearchRunResource returned error: %v", err)
	}
	if len(result.Contents) != 1 || result.Contents[0].MIMEType != "application/json" {
		t.Fatalf("unexpected resource result: %#v", result)
	}
	if !strings.Contains(result.Contents[0].Text, "MarketSage brief: AAPL") {
		t.Fatalf("unexpected resource body: %s", result.Contents[0].Text)
	}
}
