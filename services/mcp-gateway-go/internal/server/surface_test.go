package server

import (
	"context"
	"strings"
	"testing"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// connect starts the gateway on an in-memory transport and returns a client session.
func connect(t *testing.T) *mcp.ClientSession {
	t.Helper()
	serverTransport, clientTransport := mcp.NewInMemoryTransports()
	server := New(fakeAnalytics{}, "test")
	ctx := context.Background()
	if _, err := server.Connect(ctx, serverTransport, nil); err != nil {
		t.Fatalf("server connect: %v", err)
	}
	client := mcp.NewClient(&mcp.Implementation{Name: "surface-test", Version: "0"}, nil)
	session, err := client.Connect(ctx, clientTransport, nil)
	if err != nil {
		t.Fatalf("client connect: %v", err)
	}
	t.Cleanup(func() { _ = session.Close() })
	return session
}

func names[T any](items []T, name func(T) string) []string {
	out := make([]string, 0, len(items))
	for _, item := range items {
		out = append(out, name(item))
	}
	return out
}

func assertSameSet(t *testing.T, label string, got []string, want []string) {
	t.Helper()
	if len(got) != len(want) {
		t.Fatalf("%s: got %d (%v), want %d (%v)", label, len(got), got, len(want), want)
	}
	seen := map[string]bool{}
	for _, item := range got {
		seen[item] = true
	}
	for _, item := range want {
		if !seen[item] {
			t.Fatalf("%s: missing %q in %v", label, item, got)
		}
	}
}

func TestAdvertisedSurfaceMatchesDescribe(t *testing.T) {
	session := connect(t)
	ctx := context.Background()
	surface := Describe()

	tools, err := session.ListTools(ctx, nil)
	if err != nil {
		t.Fatalf("list tools: %v", err)
	}
	assertSameSet(t, "tools", names(tools.Tools, func(tool *mcp.Tool) string { return tool.Name }), surface.Tools)

	prompts, err := session.ListPrompts(ctx, nil)
	if err != nil {
		t.Fatalf("list prompts: %v", err)
	}
	assertSameSet(t, "prompts", names(prompts.Prompts, func(p *mcp.Prompt) string { return p.Name }), surface.Prompts)

	templates, err := session.ListResourceTemplates(ctx, nil)
	if err != nil {
		t.Fatalf("list resource templates: %v", err)
	}
	assertSameSet(t, "resource templates", names(templates.ResourceTemplates, func(r *mcp.ResourceTemplate) string { return r.Name }), surface.ResourceTemplates)
}

func TestPromptsRenderAndRequireArguments(t *testing.T) {
	session := connect(t)
	ctx := context.Background()

	result, err := session.GetPrompt(ctx, &mcp.GetPromptParams{
		Name:      "equity_research",
		Arguments: map[string]string{"ticker": "MSFT", "horizon": "1q"},
	})
	if err != nil {
		t.Fatalf("get prompt: %v", err)
	}
	if len(result.Messages) != 1 {
		t.Fatalf("expected one message, got %d", len(result.Messages))
	}
	text, ok := result.Messages[0].Content.(*mcp.TextContent)
	if !ok {
		t.Fatalf("expected text content, got %T", result.Messages[0].Content)
	}
	for _, want := range []string{"MSFT", "1q", "research_brief", "Do not estimate"} {
		if !strings.Contains(text.Text, want) {
			t.Fatalf("prompt text missing %q: %s", want, text.Text)
		}
	}

	if _, err := session.GetPrompt(ctx, &mcp.GetPromptParams{Name: "equity_research"}); err == nil {
		t.Fatalf("expected an error when the required ticker argument is missing")
	}
}
