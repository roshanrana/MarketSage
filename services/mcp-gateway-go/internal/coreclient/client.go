package coreclient

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"path"
	"strings"
	"time"
)

type Client struct {
	baseURL     string
	bearerToken string
	httpClient  *http.Client
}

type ResponseEnvelope[T any] struct {
	RequestID   string   `json:"request_id"`
	Mode        string   `json:"mode"`
	GeneratedAt string   `json:"generated_at"`
	Source      string   `json:"source"`
	Data        T        `json:"data"`
	Warnings    []string `json:"warnings"`
	Caveats     []string `json:"caveats"`
}

type ConfigSummary struct {
	Mode                  string `json:"mode"`
	DataDir               string `json:"data_dir"`
	ModelDownloadsEnabled bool   `json:"model_downloads_enabled"`
	HTTPAuthRequired      bool   `json:"http_auth_required"`
}

type DependencyStatus struct {
	Name   string `json:"name"`
	Status string `json:"status"`
	Detail string `json:"detail"`
}

type HealthData struct {
	Service      string             `json:"service"`
	Status       string             `json:"status"`
	Version      string             `json:"version"`
	Config       ConfigSummary      `json:"config"`
	Dependencies []DependencyStatus `json:"dependencies"`
}

type HealthEnvelope = ResponseEnvelope[HealthData]

type DatasetStatusData struct {
	Count    int            `json:"count"`
	Datasets []DatasetEntry `json:"datasets"`
}

type DatasetEntry struct {
	DatasetID   string `json:"dataset_id"`
	Config      string `json:"config"`
	Split       string `json:"split"`
	RowsCount   int    `json:"rows_count"`
	License     string `json:"license"`
	SourceURL   string `json:"source_url"`
	Role        string `json:"role"`
	LocalStatus string `json:"local_status"`
}

type TickerRequest struct {
	Ticker       string `json:"ticker"`
	ProviderMode string `json:"provider_mode,omitempty"`
}

type PriceHistoryRequest struct {
	Ticker       string `json:"ticker"`
	ProviderMode string `json:"provider_mode,omitempty"`
	Start        string `json:"start,omitempty"`
	End          string `json:"end,omitempty"`
	Interval     string `json:"interval,omitempty"`
}

type MarketSnapshotData struct {
	Ticker        string  `json:"ticker"`
	Name          string  `json:"name"`
	AsOf          string  `json:"as_of"`
	Price         float64 `json:"price"`
	Currency      string  `json:"currency"`
	Change        float64 `json:"change"`
	ChangePercent float64 `json:"change_percent"`
	Volume        int64   `json:"volume"`
	Sector        string  `json:"sector"`
	SourceName    string  `json:"source_name"`
	SourceURL     string  `json:"source_url,omitempty"`
}

type PriceObservation struct {
	Date   string  `json:"date"`
	Close  float64 `json:"close"`
	Volume *int64  `json:"volume,omitempty"`
}

type PriceHistoryData struct {
	Ticker       string             `json:"ticker"`
	Interval     string             `json:"interval"`
	Observations []PriceObservation `json:"observations"`
	SourceName   string             `json:"source_name"`
	SourceURL    string             `json:"source_url,omitempty"`
}

type SentimentRequest struct {
	Text            string `json:"text"`
	Ticker          string `json:"ticker,omitempty"`
	ModelPreference string `json:"model_preference,omitempty"`
}

type SentimentData struct {
	Label        string   `json:"label"`
	Confidence   float64  `json:"confidence"`
	ModelID      string   `json:"model_id"`
	Fallback     bool     `json:"fallback"`
	TextHash     string   `json:"text_hash"`
	MatchedTerms []string `json:"matched_terms"`
}

type EvidenceSearchRequest struct {
	Query   string `json:"query"`
	Ticker  string `json:"ticker,omitempty"`
	Dataset string `json:"dataset,omitempty"`
	TopK    int    `json:"top_k,omitempty"`
}

type EvidenceSnippet struct {
	ID         string  `json:"id"`
	DocumentID string  `json:"document_id"`
	DatasetID  string  `json:"dataset_id"`
	Ticker     string  `json:"ticker"`
	Title      string  `json:"title"`
	Text       string  `json:"text"`
	Score      float64 `json:"score"`
	SourceURL  string  `json:"source_url"`
	License    string  `json:"license"`
}

type EvidenceSearchData struct {
	Query         string            `json:"query"`
	Count         int               `json:"count"`
	RetrievalMode string            `json:"retrieval_mode"`
	Results       []EvidenceSnippet `json:"results"`
}

type ResearchBriefRequest struct {
	Tickers      []string `json:"tickers"`
	Horizon      string   `json:"horizon,omitempty"`
	Sections     []string `json:"sections,omitempty"`
	ProviderMode string   `json:"provider_mode,omitempty"`
}

type BriefSection struct {
	Title   string   `json:"title"`
	Bullets []string `json:"bullets"`
}

type ResearchBriefData struct {
	RunID           string               `json:"run_id"`
	Title           string               `json:"title"`
	Tickers         []string             `json:"tickers"`
	Horizon         string               `json:"horizon"`
	GeneratedAt     string               `json:"generated_at"`
	Sections        []BriefSection       `json:"sections"`
	MarketSnapshots []MarketSnapshotData `json:"market_snapshots"`
	Sentiment       *SentimentData       `json:"sentiment"`
	Evidence        []EvidenceSnippet    `json:"evidence"`
}

type SavedResearchRunData struct {
	RunID     string            `json:"run_id"`
	CreatedAt string            `json:"created_at"`
	Input     map[string]any    `json:"input"`
	Output    ResearchBriefData `json:"output"`
}

func New(baseURL string, timeout time.Duration) (*Client, error) {
	return NewWithToken(baseURL, timeout, "")
}

func NewWithToken(baseURL string, timeout time.Duration, bearerToken string) (*Client, error) {
	parsed, err := url.Parse(baseURL)
	if err != nil {
		return nil, err
	}
	if parsed.Scheme != "http" && parsed.Scheme != "https" {
		return nil, fmt.Errorf("analytics url must use http or https")
	}
	if parsed.Host == "" {
		return nil, fmt.Errorf("analytics url must include host")
	}
	if timeout <= 0 {
		timeout = 5 * time.Second
	}
	return &Client{
		baseURL:     strings.TrimRight(baseURL, "/"),
		bearerToken: strings.TrimSpace(bearerToken),
		httpClient:  &http.Client{Timeout: timeout},
	}, nil
}

func (c *Client) Health(ctx context.Context) (*HealthEnvelope, error) {
	var envelope HealthEnvelope
	if err := c.get(ctx, "/health", &envelope); err != nil {
		return nil, err
	}
	return &envelope, nil
}

func (c *Client) Datasets(ctx context.Context) (*ResponseEnvelope[DatasetStatusData], error) {
	var envelope ResponseEnvelope[DatasetStatusData]
	if err := c.get(ctx, "/datasets", &envelope); err != nil {
		return nil, err
	}
	return &envelope, nil
}

func (c *Client) MarketSnapshot(
	ctx context.Context,
	request TickerRequest,
) (*ResponseEnvelope[MarketSnapshotData], error) {
	var envelope ResponseEnvelope[MarketSnapshotData]
	if err := c.post(ctx, "/market/snapshot", request, &envelope); err != nil {
		return nil, err
	}
	return &envelope, nil
}

func (c *Client) PriceHistory(
	ctx context.Context,
	request PriceHistoryRequest,
) (*ResponseEnvelope[PriceHistoryData], error) {
	var envelope ResponseEnvelope[PriceHistoryData]
	if err := c.post(ctx, "/market/history", request, &envelope); err != nil {
		return nil, err
	}
	return &envelope, nil
}

func (c *Client) SentimentText(
	ctx context.Context,
	request SentimentRequest,
) (*ResponseEnvelope[SentimentData], error) {
	var envelope ResponseEnvelope[SentimentData]
	if err := c.post(ctx, "/sentiment/text", request, &envelope); err != nil {
		return nil, err
	}
	return &envelope, nil
}

func (c *Client) EvidenceSearch(
	ctx context.Context,
	request EvidenceSearchRequest,
) (*ResponseEnvelope[EvidenceSearchData], error) {
	var envelope ResponseEnvelope[EvidenceSearchData]
	if err := c.post(ctx, "/evidence/search", request, &envelope); err != nil {
		return nil, err
	}
	return &envelope, nil
}

func (c *Client) ResearchBrief(
	ctx context.Context,
	request ResearchBriefRequest,
) (*ResponseEnvelope[ResearchBriefData], error) {
	var envelope ResponseEnvelope[ResearchBriefData]
	if err := c.post(ctx, "/briefs/research", request, &envelope); err != nil {
		return nil, err
	}
	return &envelope, nil
}

func (c *Client) ResearchRun(
	ctx context.Context,
	runID string,
) (*ResponseEnvelope[SavedResearchRunData], error) {
	var envelope ResponseEnvelope[SavedResearchRunData]
	if err := c.get(ctx, "/runs/"+path.Clean(runID), &envelope); err != nil {
		return nil, err
	}
	return &envelope, nil
}

func (c *Client) get(ctx context.Context, requestPath string, output any) error {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, c.baseURL+requestPath, nil)
	if err != nil {
		return err
	}
	return c.do(req, output)
}

func (c *Client) post(ctx context.Context, requestPath string, input any, output any) error {
	body, err := json.Marshal(input)
	if err != nil {
		return err
	}
	req, err := http.NewRequestWithContext(
		ctx,
		http.MethodPost,
		c.baseURL+requestPath,
		bytes.NewReader(body),
	)
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	return c.do(req, output)
}

func (c *Client) do(req *http.Request, output any) error {
	if c.bearerToken != "" {
		req.Header.Set("Authorization", "Bearer "+c.bearerToken)
	}
	res, err := c.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer res.Body.Close()

	if res.StatusCode < 200 || res.StatusCode > 299 {
		return fmt.Errorf("analytics %s returned status %d", req.URL.Path, res.StatusCode)
	}

	return json.NewDecoder(res.Body).Decode(output)
}
