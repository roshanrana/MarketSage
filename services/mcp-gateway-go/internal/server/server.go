package server

import (
	"context"
	"encoding/json"
	"strings"

	"github.com/modelcontextprotocol/go-sdk/mcp"
	"github.com/roshanrana/marketsage/services/mcp-gateway-go/internal/coreclient"
)

type AnalyticsClient interface {
	Health(context.Context) (*coreclient.HealthEnvelope, error)
	Datasets(context.Context) (*coreclient.ResponseEnvelope[coreclient.DatasetStatusData], error)
	MarketSnapshot(context.Context, coreclient.TickerRequest) (*coreclient.ResponseEnvelope[coreclient.MarketSnapshotData], error)
	PriceHistory(context.Context, coreclient.PriceHistoryRequest) (*coreclient.ResponseEnvelope[coreclient.PriceHistoryData], error)
	SentimentText(context.Context, coreclient.SentimentRequest) (*coreclient.ResponseEnvelope[coreclient.SentimentData], error)
	EvidenceSearch(context.Context, coreclient.EvidenceSearchRequest) (*coreclient.ResponseEnvelope[coreclient.EvidenceSearchData], error)
	ResearchBrief(context.Context, coreclient.ResearchBriefRequest) (*coreclient.ResponseEnvelope[coreclient.ResearchBriefData], error)
	ResearchRun(context.Context, string) (*coreclient.ResponseEnvelope[coreclient.SavedResearchRunData], error)
}

type Handlers struct {
	analytics AnalyticsClient
}

type HealthInput struct{}

type HealthOutput struct {
	RequestID    string                        `json:"request_id"`
	Mode         string                        `json:"mode"`
	Status       string                        `json:"status"`
	Service      string                        `json:"service"`
	Version      string                        `json:"version"`
	Source       string                        `json:"source"`
	Dependencies []coreclient.DependencyStatus `json:"dependencies"`
	Warnings     []string                      `json:"warnings"`
	Caveats      []string                      `json:"caveats"`
}

type DatasetStatusInput struct{}

type DatasetStatusOutput struct {
	RequestID string                    `json:"request_id"`
	Mode      string                    `json:"mode"`
	Source    string                    `json:"source"`
	Count     int                       `json:"count"`
	Datasets  []coreclient.DatasetEntry `json:"datasets"`
	Warnings  []string                  `json:"warnings"`
	Caveats   []string                  `json:"caveats"`
}

type TickerInput struct {
	Ticker       string `json:"ticker" jsonschema:"Ticker symbol, for example AAPL or SPY"`
	ProviderMode string `json:"provider_mode,omitempty" jsonschema:"Optional mode override: seeded, live, or hybrid"`
}

type PriceHistoryInput struct {
	Ticker       string `json:"ticker" jsonschema:"Ticker symbol, for example AAPL or SPY"`
	ProviderMode string `json:"provider_mode,omitempty" jsonschema:"Optional mode override: seeded, live, or hybrid"`
	Start        string `json:"start,omitempty" jsonschema:"Optional inclusive start date in YYYY-MM-DD format"`
	End          string `json:"end,omitempty" jsonschema:"Optional inclusive end date in YYYY-MM-DD format"`
	Interval     string `json:"interval,omitempty" jsonschema:"Price interval, one of 1d, 1wk, or 1mo"`
}

type MarketSnapshotOutput struct {
	RequestID string                        `json:"request_id"`
	Mode      string                        `json:"mode"`
	Source    string                        `json:"source"`
	Data      coreclient.MarketSnapshotData `json:"data"`
	Warnings  []string                      `json:"warnings"`
	Caveats   []string                      `json:"caveats"`
}

type PriceHistoryOutput struct {
	RequestID string                      `json:"request_id"`
	Mode      string                      `json:"mode"`
	Source    string                      `json:"source"`
	Data      coreclient.PriceHistoryData `json:"data"`
	Warnings  []string                    `json:"warnings"`
	Caveats   []string                    `json:"caveats"`
}

type SentimentInput struct {
	Text            string `json:"text" jsonschema:"Financial text to score, up to 4000 characters"`
	Ticker          string `json:"ticker,omitempty" jsonschema:"Optional ticker symbol for context"`
	ModelPreference string `json:"model_preference,omitempty" jsonschema:"Optional model preference, auto or finbert"`
}

type SentimentOutput struct {
	RequestID string                   `json:"request_id"`
	Mode      string                   `json:"mode"`
	Source    string                   `json:"source"`
	Data      coreclient.SentimentData `json:"data"`
	Warnings  []string                 `json:"warnings"`
	Caveats   []string                 `json:"caveats"`
}

type EvidenceSearchInput struct {
	Query   string `json:"query" jsonschema:"Financial evidence query"`
	Ticker  string `json:"ticker,omitempty" jsonschema:"Optional ticker filter"`
	Dataset string `json:"dataset,omitempty" jsonschema:"Optional Hugging Face dataset id filter"`
	TopK    int    `json:"top_k,omitempty" jsonschema:"Maximum number of snippets, from 1 to 10"`
}

type EvidenceSearchOutput struct {
	RequestID string                        `json:"request_id"`
	Mode      string                        `json:"mode"`
	Source    string                        `json:"source"`
	Data      coreclient.EvidenceSearchData `json:"data"`
	Warnings  []string                      `json:"warnings"`
	Caveats   []string                      `json:"caveats"`
}

type ResearchBriefInput struct {
	Tickers      []string `json:"tickers" jsonschema:"One to five ticker symbols"`
	Horizon      string   `json:"horizon,omitempty" jsonschema:"Research horizon, for example 1w or 1q"`
	Sections     []string `json:"sections,omitempty" jsonschema:"Requested brief sections"`
	ProviderMode string   `json:"provider_mode,omitempty" jsonschema:"Optional mode override: seeded, live, or hybrid"`
}

type ResearchBriefOutput struct {
	RequestID string                       `json:"request_id"`
	Mode      string                       `json:"mode"`
	Source    string                       `json:"source"`
	Data      coreclient.ResearchBriefData `json:"data"`
	Warnings  []string                     `json:"warnings"`
	Caveats   []string                     `json:"caveats"`
}

func New(analytics AnalyticsClient, version string) *mcp.Server {
	handlers := &Handlers{analytics: analytics}
	mcpServer := mcp.NewServer(&mcp.Implementation{Name: "marketsage", Version: version}, nil)
	mcp.AddTool(
		mcpServer,
		&mcp.Tool{
			Name:        "health_check",
			Description: "Report MarketSage readiness, dependency status, and seeded/live mode.",
		},
		handlers.HealthCheck,
	)
	mcp.AddTool(
		mcpServer,
		&mcp.Tool{
			Name:        "dataset_status",
			Description: "Report configured Hugging Face finance datasets, row counts, license notes, and local availability.",
		},
		handlers.DatasetStatus,
	)
	mcp.AddTool(
		mcpServer,
		&mcp.Tool{
			Name:        "market_snapshot",
			Description: "Return a normalized seeded or OpenBB-backed market snapshot for a ticker.",
		},
		handlers.MarketSnapshot,
	)
	mcp.AddTool(
		mcpServer,
		&mcp.Tool{
			Name:        "price_history",
			Description: "Return normalized seeded or OpenBB-backed price history for a ticker.",
		},
		handlers.PriceHistory,
	)
	mcp.AddTool(
		mcpServer,
		&mcp.Tool{
			Name:        "sentiment_score_text",
			Description: "Score financial text sentiment using FinBERT when enabled or a deterministic local fallback.",
		},
		handlers.SentimentText,
	)
	mcp.AddTool(
		mcpServer,
		&mcp.Tool{
			Name:        "evidence_search",
			Description: "Search seeded financial evidence and return citation-ready snippets.",
		},
		handlers.EvidenceSearch,
	)
	mcp.AddTool(
		mcpServer,
		&mcp.Tool{
			Name:        "research_brief",
			Description: "Assemble a structured market research brief from market data, sentiment, and evidence.",
		},
		handlers.ResearchBrief,
	)
	mcpServer.AddResourceTemplate(
		&mcp.ResourceTemplate{
			Name:        "research_run",
			Title:       "Saved research run",
			URITemplate: "marketsage://runs/{run_id}",
			MIMEType:    "application/json",
			Description: "Read a saved MarketSage research run by run id.",
		},
		handlers.ResearchRunResource,
	)
	return mcpServer
}

func (h *Handlers) HealthCheck(
	ctx context.Context,
	req *mcp.CallToolRequest,
	input HealthInput,
) (*mcp.CallToolResult, HealthOutput, error) {
	health, err := h.analytics.Health(ctx)
	if err != nil {
		return nil, HealthOutput{}, err
	}

	return nil, HealthOutput{
		RequestID:    health.RequestID,
		Mode:         health.Mode,
		Status:       health.Data.Status,
		Service:      health.Data.Service,
		Version:      health.Data.Version,
		Source:       health.Source,
		Dependencies: health.Data.Dependencies,
		Warnings:     health.Warnings,
		Caveats:      health.Caveats,
	}, nil
}

func (h *Handlers) DatasetStatus(
	ctx context.Context,
	req *mcp.CallToolRequest,
	input DatasetStatusInput,
) (*mcp.CallToolResult, DatasetStatusOutput, error) {
	datasets, err := h.analytics.Datasets(ctx)
	if err != nil {
		return nil, DatasetStatusOutput{}, err
	}
	return nil, DatasetStatusOutput{
		RequestID: datasets.RequestID,
		Mode:      datasets.Mode,
		Source:    datasets.Source,
		Count:     datasets.Data.Count,
		Datasets:  datasets.Data.Datasets,
		Warnings:  datasets.Warnings,
		Caveats:   datasets.Caveats,
	}, nil
}

func (h *Handlers) MarketSnapshot(
	ctx context.Context,
	req *mcp.CallToolRequest,
	input TickerInput,
) (*mcp.CallToolResult, MarketSnapshotOutput, error) {
	snapshot, err := h.analytics.MarketSnapshot(ctx, coreclient.TickerRequest{
		Ticker:       input.Ticker,
		ProviderMode: input.ProviderMode,
	})
	if err != nil {
		return nil, MarketSnapshotOutput{}, err
	}
	return nil, MarketSnapshotOutput{
		RequestID: snapshot.RequestID,
		Mode:      snapshot.Mode,
		Source:    snapshot.Source,
		Data:      snapshot.Data,
		Warnings:  snapshot.Warnings,
		Caveats:   snapshot.Caveats,
	}, nil
}

func (h *Handlers) PriceHistory(
	ctx context.Context,
	req *mcp.CallToolRequest,
	input PriceHistoryInput,
) (*mcp.CallToolResult, PriceHistoryOutput, error) {
	history, err := h.analytics.PriceHistory(ctx, coreclient.PriceHistoryRequest{
		Ticker:       input.Ticker,
		ProviderMode: input.ProviderMode,
		Start:        input.Start,
		End:          input.End,
		Interval:     input.Interval,
	})
	if err != nil {
		return nil, PriceHistoryOutput{}, err
	}
	return nil, PriceHistoryOutput{
		RequestID: history.RequestID,
		Mode:      history.Mode,
		Source:    history.Source,
		Data:      history.Data,
		Warnings:  history.Warnings,
		Caveats:   history.Caveats,
	}, nil
}

func (h *Handlers) SentimentText(
	ctx context.Context,
	req *mcp.CallToolRequest,
	input SentimentInput,
) (*mcp.CallToolResult, SentimentOutput, error) {
	sentiment, err := h.analytics.SentimentText(ctx, coreclient.SentimentRequest{
		Text:            input.Text,
		Ticker:          input.Ticker,
		ModelPreference: input.ModelPreference,
	})
	if err != nil {
		return nil, SentimentOutput{}, err
	}
	return nil, SentimentOutput{
		RequestID: sentiment.RequestID,
		Mode:      sentiment.Mode,
		Source:    sentiment.Source,
		Data:      sentiment.Data,
		Warnings:  sentiment.Warnings,
		Caveats:   sentiment.Caveats,
	}, nil
}

func (h *Handlers) EvidenceSearch(
	ctx context.Context,
	req *mcp.CallToolRequest,
	input EvidenceSearchInput,
) (*mcp.CallToolResult, EvidenceSearchOutput, error) {
	evidence, err := h.analytics.EvidenceSearch(ctx, coreclient.EvidenceSearchRequest{
		Query:   input.Query,
		Ticker:  input.Ticker,
		Dataset: input.Dataset,
		TopK:    input.TopK,
	})
	if err != nil {
		return nil, EvidenceSearchOutput{}, err
	}
	return nil, EvidenceSearchOutput{
		RequestID: evidence.RequestID,
		Mode:      evidence.Mode,
		Source:    evidence.Source,
		Data:      evidence.Data,
		Warnings:  evidence.Warnings,
		Caveats:   evidence.Caveats,
	}, nil
}

func (h *Handlers) ResearchBrief(
	ctx context.Context,
	req *mcp.CallToolRequest,
	input ResearchBriefInput,
) (*mcp.CallToolResult, ResearchBriefOutput, error) {
	brief, err := h.analytics.ResearchBrief(ctx, coreclient.ResearchBriefRequest{
		Tickers:      input.Tickers,
		Horizon:      input.Horizon,
		Sections:     input.Sections,
		ProviderMode: input.ProviderMode,
	})
	if err != nil {
		return nil, ResearchBriefOutput{}, err
	}
	return nil, ResearchBriefOutput{
		RequestID: brief.RequestID,
		Mode:      brief.Mode,
		Source:    brief.Source,
		Data:      brief.Data,
		Warnings:  brief.Warnings,
		Caveats:   brief.Caveats,
	}, nil
}

func (h *Handlers) ResearchRunResource(
	ctx context.Context,
	req *mcp.ReadResourceRequest,
) (*mcp.ReadResourceResult, error) {
	uri := req.Params.URI
	const prefix = "marketsage://runs/"
	if !strings.HasPrefix(uri, prefix) {
		return nil, mcp.ResourceNotFoundError(uri)
	}
	runID := strings.TrimPrefix(uri, prefix)
	if runID == "" {
		return nil, mcp.ResourceNotFoundError(uri)
	}

	run, err := h.analytics.ResearchRun(ctx, runID)
	if err != nil {
		return nil, err
	}
	body, err := json.MarshalIndent(run.Data, "", "  ")
	if err != nil {
		return nil, err
	}

	return &mcp.ReadResourceResult{
		Contents: []*mcp.ResourceContents{
			{
				URI:      uri,
				MIMEType: "application/json",
				Text:     string(body),
			},
		},
	}, nil
}
