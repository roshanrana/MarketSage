package server

import (
	"context"
	"fmt"
	"strings"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// promptSpec is one reusable prompt (FR-011). The body is a template the host
// LLM receives as a user message; every prompt steers the model toward the
// MarketSage tools and toward stating caveats rather than inventing figures.
type promptSpec struct {
	name        string
	title       string
	description string
	arguments   []*mcp.PromptArgument
	build       func(args map[string]string) string
}

var promptSpecs = []promptSpec{
	{
		name:        "equity_research",
		title:       "Equity research brief",
		description: "Build a cited research brief for one ticker using MarketSage tools only.",
		arguments: []*mcp.PromptArgument{
			{Name: "ticker", Description: "Ticker symbol, for example MSFT", Required: true},
			{Name: "horizon", Description: "Research horizon such as 1w or 1q"},
		},
		build: func(args map[string]string) string {
			return fmt.Sprintf(
				"Prepare a research brief for %s over a %s horizon. Call market_snapshot, "+
					"evidence_search and research_brief before writing. Cite every figure by "+
					"evidence id or snapshot, quote the data mode and as_of time, and repeat the "+
					"caveats the tools return. Do not estimate numbers the tools did not provide.",
				argOr(args, "ticker", "the requested ticker"), argOr(args, "horizon", "1w"),
			)
		},
	},
	{
		name:        "portfolio_risk_scan",
		title:       "Portfolio risk scan",
		description: "Scan up to five tickers for evidence-backed risk factors.",
		arguments: []*mcp.PromptArgument{
			{Name: "tickers", Description: "Comma-separated ticker symbols", Required: true},
		},
		build: func(args map[string]string) string {
			return fmt.Sprintf(
				"For each of %s, call evidence_search with a query about risk, liquidity and "+
					"customer concentration, then summarise the risks the evidence actually "+
					"states. List tickers with no committed evidence separately instead of "+
					"guessing. This is research support, not advice.",
				argOr(args, "tickers", "the requested tickers"),
			)
		},
	},
	{
		name:        "earnings_call_questions",
		title:       "Earnings-call questions",
		description: "Draft analyst questions grounded in filing evidence for one ticker.",
		arguments: []*mcp.PromptArgument{
			{Name: "ticker", Description: "Ticker symbol", Required: true},
		},
		build: func(args map[string]string) string {
			return fmt.Sprintf(
				"Use evidence_search for %s on revenue drivers, margins and cash flow, then "+
					"draft five questions an analyst could ask on the next earnings call. Tie "+
					"each question to the evidence id that motivates it.",
				argOr(args, "ticker", "the requested ticker"),
			)
		},
	},
	{
		name:        "source_quality_review",
		title:       "Source quality review",
		description: "Review the provenance, licence and staleness of what MarketSage returned.",
		arguments:   nil,
		build: func(map[string]string) string {
			return "Call dataset_status and health_check. Report the data mode, each dataset's " +
				"licence and local status, the seed data as_of date, and any warnings. Flag " +
				"anything that is metadata-only, blocked pending licence review, or stale."
		},
	},
}

// PromptNames lists the prompts the gateway registers, in registration order.
func PromptNames() []string {
	names := make([]string, 0, len(promptSpecs))
	for _, spec := range promptSpecs {
		names = append(names, spec.name)
	}
	return names
}

func registerPrompts(mcpServer *mcp.Server) {
	for _, spec := range promptSpecs {
		spec := spec
		mcpServer.AddPrompt(
			&mcp.Prompt{
				Name:        spec.name,
				Title:       spec.title,
				Description: spec.description,
				Arguments:   spec.arguments,
			},
			func(_ context.Context, req *mcp.GetPromptRequest) (*mcp.GetPromptResult, error) {
				for _, arg := range spec.arguments {
					if arg.Required && strings.TrimSpace(req.Params.Arguments[arg.Name]) == "" {
						return nil, fmt.Errorf("prompt %s requires argument %q", spec.name, arg.Name)
					}
				}
				return &mcp.GetPromptResult{
					Description: spec.description,
					Messages: []*mcp.PromptMessage{
						{Role: "user", Content: &mcp.TextContent{Text: spec.build(req.Params.Arguments)}},
					},
				}, nil
			},
		)
	}
}

func argOr(args map[string]string, key string, fallback string) string {
	if value, ok := args[key]; ok && strings.TrimSpace(value) != "" {
		return strings.TrimSpace(value)
	}
	return fallback
}
