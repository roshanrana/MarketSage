# MarketSage

MarketSage is an MCP-native market intelligence workbench that connects a traditional finance analytics application to LLM clients. It is built as a customer-facing implementation portfolio product: practical fintech workflow, real service boundaries, seeded offline demos, optional live OpenBB integration, Hugging Face finance assets, auditability, and a polished analyst UI.

MarketSage does not execute trades, move money, or provide investment advice.

## What It Demonstrates

- A Go MCP gateway exposing finance tools and saved-run resources over stdio.
- A Python FastAPI analytics core with OpenBB-ready market data, Hugging Face dataset manifests, sentiment scoring, evidence retrieval, and brief orchestration.
- A TypeScript MCP client that starts the stack, discovers tools, calls them, and reads a saved MCP resource.
- A Next.js analyst workbench for a traditional application surface: ticker input, mode selection, source-aware snapshot, evidence search, research brief, warnings, and caveats.
- DuckDB persistence for audit events, dataset manifests, and research runs.
- Enterprise habits: validation gates, optional bearer auth, no stdout logging in stdio mode, dependency/security sweeps, and license notes.

## Architecture

```text
LLM host / MCP client
        |
        | stdio JSON-RPC
        v
Go MCP gateway
        |
        | HTTP JSON
        v
Python analytics core
        |
        +-- OpenBB-ready market adapter
        +-- Hugging Face dataset/model boundary
        +-- DuckDB local audit and run store

Next.js analyst workbench
        |
        | server-side proxy
        v
Python analytics core
```

## MCP Surface

Tools:

- `health_check`
- `dataset_status`
- `market_snapshot`
- `price_history`
- `sentiment_score_text`
- `evidence_search`
- `research_brief`

Resource template:

- `marketsage://runs/{run_id}`

## Quick Start

Prerequisites:

- Node.js 22+
- Go 1.24+
- `uv`

Install and validate:

```powershell
npm install
npm run check
```

Run the MCP demo:

```powershell
npm run demo:mcp
```

Run the web workbench:

```powershell
npm run dev:analytics
npm run dev --workspace apps/web
```

Open `http://localhost:3000`.

## Protected Local Mode

By default, the analytics API is open for frictionless local demos. Set `MARKETSAGE_HTTP_TOKEN` to require bearer auth on HTTP requests:

```powershell
$env:MARKETSAGE_HTTP_TOKEN="local-demo-token"
npm run dev:analytics
```

The Go MCP gateway and Next.js proxy forward the same token server-side when configured.

## Data And Model Modes

- `seeded`: deterministic local demo data, no private credentials.
- `hybrid`: tries live OpenBB data and falls back to seeded data with warnings.
- `live`: uses optional OpenBB dependencies and fails clearly if unavailable.

Optional model downloads are off by default. Set `MARKETSAGE_ENABLE_MODEL_DOWNLOADS=true` to try FinBERT; otherwise the deterministic local sentiment fallback is used.

## Validation

Primary gate:

```powershell
npm run check
```

Deep dependency sweep:

```powershell
npm run audit:deps
```

Latest local evidence is recorded in:

- `docs/security-and-ops.md`
- `docs/third-party-notices.md`
- `docs/ship-report.md`

## Delivery Signals

- Discovery-to-delivery lifecycle artifacts in `docs/design` and `docs/tasks`.
- Go service boundary for MCP and transport discipline.
- Python data/AI integration layer for OpenBB and Hugging Face workflows.
- TypeScript/Next.js product surface for analysts and stakeholders.
- SQL/DuckDB persistence for auditability and reproducibility.
- Security, observability, license, and dependency posture documented before public release.

## License

MarketSage is licensed under `AGPL-3.0-only`. If you want a permissive license later, isolate OpenBB behind an optional external service boundary and confirm compatibility before switching.
