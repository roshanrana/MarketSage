# MarketSage

**An MCP-native market intelligence workbench: a traditional analyst workflow, exposed to LLM clients as tools, with every run saved and every source caveated.**

A Go MCP gateway exposes seven finance tools and a saved-run resource over stdio. Behind it, a Python FastAPI analytics core provides market snapshots, price history, sentiment scoring, evidence search and research briefs, with an OpenBB-ready market adapter and a Hugging Face dataset boundary. DuckDB persists dataset manifests, research runs and audit events. A Next.js workbench gives analysts the same capabilities as a conventional application surface.

MarketSage does not execute trades, move money or provide investment advice.

---

## At a glance

| | |
|---|---|
| **The problem** | Analyst teams have a workflow that works. LLM clients want to use it. Bolting a chat box onto a finance app gives the model no structure, no provenance and no record; exposing the workflow as typed tools with saved, auditable runs does. |
| **What it does** | Seven MCP tools (`health_check`, `dataset_status`, `market_snapshot`, `price_history`, `sentiment_score_text`, `evidence_search`, `research_brief`) and a `marketsage://runs/{run_id}` resource; seeded, hybrid and live data modes with explicit warnings when live data is unavailable; deterministic sentiment with opt-in FinBERT; lexical evidence retrieval; research briefs with source caveats; DuckDB audit and run persistence; optional bearer auth; a Next.js analyst workbench. |
| **Stack** | Go 1.24 (MCP gateway), Python 3.12 with FastAPI and `uv` (analytics core), TypeScript MCP SDK (client), Next.js and React (workbench), DuckDB, optional OpenBB, Hugging Face datasets and models, GitHub Actions. |
| **Validation** | One gate, `npm run check`: docs, `ruff`, `pytest`, `go fmt`/`test`/`vet`, an MCP CLI smoke across all seven tools and the saved-run resource, the Next.js production build, and a workspace check. Plus `npm run audit:deps`: `npm audit`, `uv pip check`, `govulncheck`, and a secret scan. Desktop and mobile browser verification of the workbench. |

## Architecture

```
LLM host / MCP client ──stdio JSON-RPC──► Go MCP gateway ──HTTP──► Python analytics core
                                                                      ├── OpenBB-ready market adapter
Next.js analyst workbench ──server-side proxy───────────────────────────────────►  ├── Hugging Face dataset/model boundary
                                                                      └── DuckDB: manifests, runs, audit events
```

Three languages, each where it is strongest: Go for a transport-disciplined MCP server that never writes to stdout in stdio mode, Python for the data and model integrations, TypeScript for the client and the product surface. One schema in `packages/contracts/marketsage.schema.json` describes the shared payloads.

## Quick start

Requires Node.js 22+, Go 1.24+ and `uv`.

```bash
npm install
npm run check        # the gate
npm run demo:mcp     # a TypeScript MCP client starts the stack, lists tools, runs the chain, reads a saved run
```

For the workbench, in two terminals:

```bash
npm run dev:analytics
npm run dev --workspace apps/web     # http://localhost:3000, then Run Brief
```

## Data and model modes

| Mode | Behaviour |
|---|---|
| `seeded` | Deterministic local data from `data/seed/`; no credentials, no network. The default. |
| `hybrid` | Tries live OpenBB data and falls back to seeded data, with a warning in the response so the fallback is never silent. |
| `live` | Requires the optional OpenBB dependencies and fails clearly when they are missing. |

Model downloads are off by default. `MARKETSAGE_ENABLE_MODEL_DOWNLOADS=true` enables FinBERT; otherwise the deterministic sentiment fallback is used and reported as such.

## Protected local mode

The analytics API is open for local demos. Set `MARKETSAGE_HTTP_TOKEN` to require bearer auth; the Go gateway and the Next.js proxy forward the same token server-side.

## Documentation

| | |
|---|---|
| [`docs/OVERVIEW.md`](docs/OVERVIEW.md) | The problem, the design and its reasons, what is measured |
| [`docs/SHOWCASE.md`](docs/SHOWCASE.md) | A guided tour of every feature, with commands and files |
| [`docs/demo-script.md`](docs/demo-script.md) | A five-minute walkthrough |
| [`docs/security-and-ops.md`](docs/security-and-ops.md) | Security posture, dependency sweeps, operational notes |
| [`docs/research/source-notes.md`](docs/research/source-notes.md) | Which datasets and models were reviewed, and why some were excluded |
| [`docs/third-party-notices.md`](docs/third-party-notices.md) | Licences of everything used |
| [`docs/ship-report.md`](docs/ship-report.md) | Validation evidence and known limitations |
| [`docs/design/`](docs/design/) | Requirements, high-level design, low-level design, execution plan, decisions |

## License

`AGPL-3.0-only`, because OpenBB is. To relicense permissively, isolate OpenBB behind an external service boundary first and confirm compatibility.
