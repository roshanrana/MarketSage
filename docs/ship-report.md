# Ship Report

Date: 2026-09-01
Status: GitHub-ready MVP.

## Built Scope

- Python analytics core with health, dataset status, market snapshot/history, sentiment, evidence search, research brief, and saved-run APIs.
- Go MCP gateway exposing seven tools and one saved-run resource template over stdio.
- TypeScript MCP CLI demo that starts analytics, launches the gateway, calls the tool chain, and reads a saved resource.
- Next.js analyst workbench with ticker input, mode selection, market snapshot, price trend, evidence list, research brief, dataset table, warnings, and caveats.
- DuckDB local store for dataset manifest, research runs, and audit events.
- Optional HTTP bearer auth using `MARKETSAGE_HTTP_TOKEN`.
- Documentation for architecture, lifecycle decisions, security posture, source notes, demo flow, and third-party notices.

## Validation Evidence

Latest `npm run check` result: passed.

- `docs`: passed.
- `ruff`: passed.
- `pytest`: 15 passed, 1 third-party `TestClient` deprecation warning.
- `go fmt`: passed.
- `go test ./...`: passed.
- `go vet ./...`: passed.
- MCP CLI smoke: passed; discovered 7 tools and read `marketsage://runs/{run_id}`.
- Next.js build: passed.
- Workspace check: passed.

Browser verification:

- Desktop workbench loaded and completed `Run Brief`.
- Mobile viewport completed `Run Brief`.
- React duplicate-key overlay fixed.
- Mobile horizontal overflow fixed.

Security/dependency sweep:

- `npm audit --workspaces --audit-level=high`: 0 vulnerabilities.
- `uv pip check --project services/analytics-python`: compatible dependencies.
- `go run golang.org/x/vuln/cmd/govulncheck@latest ./...`: code affected by 0 vulnerabilities; one required-module vulnerability was not called.
- Secret text scan found only placeholders, docs, source identifiers, and test tokens.

## Source And License Notes

- OpenBB remains optional for live mode; seeded mode works without OpenBB installation.
- Hugging Face MVP fixtures use reviewed MIT datasets.
- `glopardo/sp500-earnings-transcripts` is excluded from default flow until license review.
- `nlpaueb/sec-bert-base` is excluded from MVP because CC-BY-SA-4.0 requires explicit acceptance.
- Repository license: `AGPL-3.0-only`.

## Known Limitations

- Seeded market data is illustrative and not current market data.
- Live mode depends on optional OpenBB installation and provider configuration.
- FinBERT model use is opt-in; deterministic sentiment fallback is the default.
- Evidence retrieval is lexical in the MVP; embedding retrieval is planned.
- Bearer auth is a local demo/prototype control, not production identity management.

## Reviewer Story

MarketSage shows the full path an FDE is expected to own: problem framing, architecture, integration, data provenance, LLM-facing MCP tools, a usable stakeholder UI, validation, security posture, and pragmatic tradeoffs.
