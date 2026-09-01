# Low-Level Design

## Repository Layout

```text
MarketSage/
  STATE.md
  Makefile
  README.md
  docker-compose.yml
  .github/workflows/check.yml
  apps/
    web/                         # Next.js analyst workbench
  clients/
    mcp-cli/                     # TypeScript MCP client demo
  services/
    mcp-gateway-go/              # Go MCP gateway
    analytics-python/            # FastAPI OpenBB/HF analytics core
  packages/
    contracts/                   # Shared JSON schemas/OpenAPI artifacts
  data/
    seed/                        # Small committed fixture data only
    local/                       # Ignored DuckDB/cache/model artifacts
  docs/
    design/
    research/
    tasks/
```

Application code should not be created until the execution plan is approved.

## Module Design

| Module | Responsibilities | Inputs | Outputs | Dependencies |
| --- | --- | --- | --- | --- |
| `services/mcp-gateway-go/cmd/marketsage-mcp` | Start MCP server over stdio or streamable HTTP | Env config, MCP requests | MCP responses, stderr logs | Go MCP SDK, internal gateway packages |
| `services/mcp-gateway-go/internal/tools` | Tool/resource/prompt registration and schema mapping | Contract schemas, Python client | MCP primitive definitions | Go SDK, contracts |
| `services/mcp-gateway-go/internal/coreclient` | Typed HTTP client to analytics core | Normalized requests | Normalized responses | net/http |
| `services/mcp-gateway-go/internal/audit` | Request IDs, argument hashes, audit event forwarding | Tool metadata | Audit events | coreclient |
| `services/analytics-python/marketsage_api` | FastAPI app and route handlers | HTTP requests | JSON responses | FastAPI, pydantic |
| `services/analytics-python/marketsage_core/openbb_adapter` | OpenBB live/offline market access | Tickers, dates, provider mode | Normalized market data | OpenBB, fixtures |
| `services/analytics-python/marketsage_core/datasets` | HF dataset manifest, bounded downloads, license metadata | Dataset ids | Manifest rows, seed files | HF Dataset Viewer API, DuckDB |
| `services/analytics-python/marketsage_core/sentiment` | FinBERT/fallback sentiment | Text, ticker, source metadata | Sentiment observations | transformers, optional model cache |
| `services/analytics-python/marketsage_core/retrieval` | Evidence chunking/search | Query, filters | Ranked evidence snippets | DuckDB, embeddings or lexical fallback |
| `services/analytics-python/marketsage_core/briefs` | Research brief orchestration | Brief request | Structured brief JSON | OpenBB, sentiment, retrieval |
| `clients/mcp-cli` | MCP discovery and demo workflow | Server command/URL | Terminal demo output | TypeScript MCP SDK |
| `apps/web` | Analyst workbench UI | User inputs, API responses | Dashboard views | Next.js, React, TypeScript |
| `packages/contracts` | JSON schema/OpenAPI contract artifacts | Schema source | Generated types and validation inputs | JSON Schema tooling |

## Contracts

### MCP Tools

All tools are read-only from the user's perspective. Local writes are limited to cache and audit state.

| Tool | Purpose | Key Inputs | Key Outputs |
| --- | --- | --- | --- |
| `health_check` | Report MarketSage readiness | none | service status, mode, dependency status, dataset status |
| `dataset_status` | Report configured HF datasets and local cache state | optional dataset id | rows, splits, license, local availability |
| `market_snapshot` | Get normalized current market snapshot | ticker, provider mode | price fields, source, timestamp, warnings |
| `price_history` | Get historical price data | ticker, start, end, interval, provider mode | observations array, source, warnings |
| `market_compare` | Compare multiple tickers | tickers, metrics, lookback | comparison table, caveats |
| `sentiment_score_text` | Score supplied financial text | text, model preference | label, confidence, model id, fallback flag |
| `news_sentiment` | Score available news/headline fixture or live data | ticker, lookback, provider mode | headline sentiment summary |
| `evidence_search` | Search financial passages | query, ticker, dataset, top_k | ranked snippets, source docs, scores |
| `research_brief` | Assemble a structured market brief | tickers, horizon, sections, mode | brief sections, evidence, caveats, run id |
| `audit_recent` | Read recent local audit events | limit, tool filter | event summaries |

### MCP Resources

| Resource URI | Purpose |
| --- | --- |
| `marketsage://schema` | Human-readable summary of tool/resource schemas |
| `marketsage://datasets` | Current dataset manifest and license notes |
| `marketsage://demo/portfolio` | Seed demo portfolio and tickers |
| `marketsage://runs/{run_id}` | Saved research run result and tool-call evidence |

### MCP Prompts

| Prompt | Purpose |
| --- | --- |
| `equity_research_brief` | Guide an LLM through a sourced ticker brief |
| `portfolio_risk_scan` | Guide an LLM through multi-ticker risk/sentiment scan |
| `earnings_call_questions` | Generate questions grounded in transcript evidence |
| `source_quality_review` | Ask the LLM to assess source freshness and limitations |
| `demo_walkthrough` | Reviewer-friendly scripted MarketSage demo |

### Python Core HTTP API

The Python core exposes local HTTP endpoints consumed by the Go gateway and web app.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Dependency and mode readiness |
| `GET` | `/datasets` | Dataset manifest |
| `POST` | `/market/snapshot` | Normalized market snapshot |
| `POST` | `/market/history` | Normalized price history |
| `POST` | `/market/compare` | Multi-ticker comparison |
| `POST` | `/sentiment/text` | Sentiment score |
| `POST` | `/sentiment/news` | News/headline sentiment |
| `POST` | `/evidence/search` | Evidence retrieval |
| `POST` | `/briefs/research` | Research brief orchestration |
| `GET` | `/runs/{run_id}` | Saved run retrieval |
| `POST` | `/audit/events` | Audit event write |
| `GET` | `/audit/recent` | Audit event read |

## Data Schemas

Use pydantic models in Python and generated JSON Schema in `packages/contracts`.

### Common Response Envelope

- `request_id`: string.
- `mode`: `seeded`, `live`, or `hybrid`.
- `generated_at`: ISO timestamp.
- `source`: source id and provider.
- `data`: typed payload.
- `warnings`: array of strings.
- `caveats`: array of strings for finance/model limitations.

### DuckDB Tables

| Table | Key Fields | Notes |
| --- | --- | --- |
| `dataset_manifest` | dataset_id, config, split, rows, license, source_url, local_status, checked_at | Populated from HF metadata and local samples |
| `market_observation` | id, ticker, observation_type, observed_at, provider, mode, payload_json | Cache normalized OpenBB/seed data |
| `sentiment_observation` | id, text_hash, ticker, model_id, label, confidence, payload_json, created_at | Avoid storing duplicate long text |
| `source_document` | id, dataset_id, ticker, title, period, license, source_url, metadata_json | Evidence provenance |
| `evidence_chunk` | id, document_id, chunk_index, text, embedding_model, embedding_json, metadata_json | Store bounded sampled chunks |
| `research_run` | id, input_json, output_json, created_at, warnings_json | Saved brief output |
| `audit_event` | id, request_id, tool_name, args_hash, mode, status, duration_ms, created_at, warnings_json | Agent-facing audit trail |

## Error Taxonomy

| Error | Cause | User Impact | Handling | Observability |
| --- | --- | --- | --- | --- |
| `validation_error` | Bad ticker, date range, top_k, text length | Tool call rejected | Return field-level message | Audit status failed |
| `provider_unavailable` | OpenBB/provider timeout or missing key | Live data unavailable | Offer seeded fallback when allowed | Log provider, duration, retryable flag |
| `dataset_unavailable` | HF API/download/cache failure | Evidence fixture unavailable | Degrade to available datasets | Log dataset id and phase |
| `model_unavailable` | Model missing/download/inference failure | Sentiment/retrieval quality lower | Use fallback with warning | Log model id and fallback |
| `license_blocked` | Dataset/model license not approved | Feature disabled | Return explicit blocked message | Log asset id |
| `internal_error` | Unexpected exception | Tool fails | Return generic safe error with request id | Log stack to stderr/file, not stdout in stdio |

## Config Matrix

| Setting | Local | Test | Production-Like | Secret? |
| --- | --- | --- | --- | --- |
| `MARKETSAGE_MODE` | `seeded` or `hybrid` | `seeded` | `live` or `hybrid` | no |
| `MARKETSAGE_DATA_DIR` | `data/local` | temp dir | mounted volume | no |
| `MARKETSAGE_ANALYTICS_URL` | `http://127.0.0.1:8765` | test server | internal URL | no |
| `MARKETSAGE_HTTP_TOKEN` | optional | test token | required for HTTP mode | yes |
| `OPENBB_*` provider keys | optional | unset | set as needed | yes |
| `HF_TOKEN` | optional | unset | optional for gated assets | yes |
| `MARKETSAGE_ENABLE_MODEL_DOWNLOADS` | `false` by default | `false` | configurable | no |
| `MARKETSAGE_LOG_LEVEL` | `info` | `warning` | `info` | no |

## Test Strategy

- Unit tests: Go validation/schema mapping; Python adapters and fallback logic; TypeScript client formatting.
- Contract tests: generated JSON schemas match pydantic models and MCP tool input schemas.
- Integration tests: Go gateway calls Python core for `health_check`, `market_snapshot`, and `research_brief` in seeded mode.
- MCP smoke test: TypeScript client lists tools and executes at least one resource read and three tool calls.
- UI tests: basic Next.js render and critical workflow test with mocked/seeded API.
- Security tests: secret scan, dependency audit where available, HTTP token test, no stdout logging in stdio mode.
- Data tests: dataset manifest validates expected ids, splits, row counts, license values, and local sample limits.

## Model Routing Plan

- Design and cross-component reviews: `gpt-5.6-sol` with high or xhigh reasoning.
- Medium-risk implementation: `gpt-5.6-terra` with medium reasoning.
- Low-risk implementation of fixtures, docs, narrow validators, and UI leaf components: `gpt-5.6-luna` with low or medium reasoning.
- Security/license reviews: `gpt-5.6-sol` with high reasoning.
- Escalate any small-dev task if it changes MCP contracts, persistence schemas, auth, live data behavior, concurrency, dependency management, or fails validation once for a non-obvious reason.

## Frozen Interfaces

These interfaces become frozen after user approval of the execution plan:

- MCP tool names in this LLD.
- Python core endpoint paths in this LLD.
- Common response envelope fields.
- DuckDB table names and high-level purpose.
- Demo workflow: health, market snapshot, evidence search, research brief, web workbench.

Changing frozen interfaces requires an LLD update and affected task review.
