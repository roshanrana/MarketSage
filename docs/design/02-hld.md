# High-Level Design

## Context

MarketSage sits between AI clients and financial data systems. An LLM host connects to the MarketSage MCP server, discovers tools/resources/prompts, and calls them to answer market research questions. The server orchestrates OpenBB market access, Hugging Face finance/NLP assets, local cache state, and audit logs.

External systems:

- OpenBB ODP Python package and provider extensions for live market data.
- Hugging Face datasets and models for seeded research workflows.
- MCP hosts and clients such as ChatGPT-compatible clients, VS Code, Cursor, Claude Desktop, and custom demo clients.
- Local browser for the Next.js analyst workbench.

## Goals And Non-Goals

- Goal: Build a complete MCP server and client demo that exposes a traditional finance research app to LLMs. Covers FR-001 through FR-015.
- Goal: Demonstrate implementation-relevant production judgment: integration boundaries, observability, validation, data provenance, and user-facing demo quality. Covers NFR-001 through NFR-010.
- Goal: Make the default demo reproducible without paid credentials by using seeded/offline data. Covers FR-004 and NFR-001.
- Goal: Use Go where it improves the product story without forcing the data/AI layer out of Python. Covers the user's stack preference.
- Non-goal: Trade execution or regulated investment advice.
- Non-goal: Full enterprise auth/multitenancy.
- Non-goal: Training or fine-tuning financial models.

## Architecture Options

| Option | Fit | Tradeoffs |
| --- | --- | --- |
| Use OpenBB's existing MCP server directly and add clients | Fastest path to a working MCP demo | Too thin for an implementation portfolio; limited original backend, data, and workflow design |
| Python-only MCP server using OpenBB and HF directly | Strong ecosystem fit and lower complexity | Less Go signal; one process carries MCP, OpenBB, ML, cache, and API concerns |
| Go MCP gateway plus Python analytics core | Strong delivery signal: boundary service, typed contracts, operational discipline, Python where it belongs | More moving parts; needs M0 spike to prove Go MCP SDK and Python service integration |
| TypeScript MCP server plus Next.js app | Smooth UI/client sharing and strong web story | OpenBB/HF integration still needs Python or subprocess boundary; weaker Go signal |

## Recommended Architecture

Use a Go MCP gateway in front of a Python analytics core, with TypeScript clients.

The Go gateway owns MCP protocol exposure, input validation, request IDs, audit-event envelopes, transport selection, and safe logging behavior. The Python analytics core owns OpenBB integration, Hugging Face dataset/model loading, market normalization, sentiment scoring, evidence retrieval, and DuckDB persistence. TypeScript provides a CLI MCP client and a Next.js analyst workbench.

This is the best portfolio shape because it shows an implementation engineer can compose existing platforms instead of rebuilding them, choose language boundaries intentionally, and ship an agent-facing interface with traditional product UX.

## Component Model

| Component | Responsibility | Interfaces | Owner |
| --- | --- | --- | --- |
| Go MCP Gateway | MCP tools/resources/prompts, stdio/HTTP transports, input validation, request IDs, audit envelopes | MCP JSON-RPC over stdio and streamable HTTP; HTTP calls to Python core | Backend |
| Python Analytics Core | OpenBB adapter, HF dataset/model adapters, sentiment, retrieval, brief assembly, DuckDB reads/writes | FastAPI local API; DuckDB; provider APIs | Data/AI |
| DuckDB Store | Local cache, dataset manifest, sampled evidence chunks, research runs, audit log | SQL through Python core | Data |
| TypeScript MCP CLI Client | Reviewer-friendly scripted MCP discovery/call demo | MCP stdio or HTTP client | Client |
| Next.js Analyst Workbench | Traditional app UI for ticker brief, compare, evidence search, run history | HTTP API/MCP gateway endpoint | Frontend |
| Test/Validation Harness | Single command verification, contract tests, smoke tests, CI | `make check`, GitHub Actions | Platform |
| Documentation And Demo Assets | README, architecture docs, setup, demo script, screenshots after implementation | Markdown, terminal transcripts | Product |

## Data Architecture

MarketSage uses a local-first data architecture:

- DuckDB is the default store for cached observations, dataset manifests, audit events, research runs, and sampled evidence chunks.
- OpenBB live calls are normalized before persistence so MCP outputs do not depend on provider-specific shapes.
- Hugging Face datasets are referenced by manifest and sampled into local fixtures for reproducible demos.
- Larger datasets, especially transcripts, are not fully downloaded in M0/M1. Use metadata plus bounded samples until license and disk impact are approved.
- Embeddings are generated lazily for sampled evidence chunks and can be regenerated from source text.

Core entities:

- `instrument`: ticker, name, exchange, sector, source.
- `market_observation`: ticker, observation type, timestamp, source, payload JSON.
- `sentiment_observation`: text hash, model, label, score, source, created timestamp.
- `source_document`: dataset, document id, title, ticker, period, license, source URL.
- `evidence_chunk`: document id, chunk id, text, metadata, embedding metadata.
- `research_run`: prompt/input, tool calls, output summary, caveats, created timestamp.
- `audit_event`: request id, tool name, arguments hash, mode, status, duration, warnings.

## Critical Flows

### Flow 1: Ticker Snapshot

1. MCP client calls `market_snapshot` with a ticker.
2. Go validates input and adds request metadata.
3. Python core checks cache, then calls OpenBB in live mode or seed data in offline mode.
4. Python returns normalized market snapshot with source, staleness, and warnings.
5. Go returns MCP content and records an audit event.

Failure handling:

- Invalid ticker returns validation error.
- Provider timeout returns a structured unavailable status and optional offline fallback.
- No data returns empty result with source caveat, never fabricated data.

### Flow 2: Sentiment Scan

1. MCP client calls `sentiment_score_text` or `news_sentiment`.
2. Python core uses FinBERT if local model dependencies are available.
3. If model assets are not available, core returns a fallback demo classifier with lower confidence and an explicit warning.
4. Results include label, confidence, model id, and source text hash.

Failure handling:

- Text length limits prevent runaway inference.
- Model download errors do not break seeded demo mode.

### Flow 3: Evidence Search

1. MCP client calls `evidence_search` with a finance question, ticker, or document filter.
2. Python core searches indexed seeded passages from FinanceBenchRetrieval and sampled transcripts.
3. Results include source document ids, ranked snippets, and retrieval scores.
4. Go returns MCP content and a resource URI for the evidence bundle.

Failure handling:

- If embeddings are unavailable, fallback to lexical retrieval with visible caveat.
- Large transcript records are chunked and truncated safely.

### Flow 4: Research Brief

1. MCP client calls `research_brief` with ticker(s), horizon, and requested sections.
2. Go validates the request and forwards to Python.
3. Python orchestrates market snapshot, price history, sentiment, and evidence search.
4. Output includes executive summary, signals, evidence table, caveats, and next questions.
5. Research run is persisted for audit and later retrieval.

Failure handling:

- Missing sections degrade independently.
- Output labels distinguish generated synthesis from sourced observations.

### Flow 5: Reviewer Demo

1. Reviewer runs setup command and seeded demo command.
2. CLI client lists MCP tools and calls health, market snapshot, evidence search, and research brief.
3. Web workbench shows the same flow in a traditional app surface.
4. README includes a short transcript and screenshots only after implementation exists.

## Cross-Cutting Concerns

- Auth: local stdio mode needs no auth; HTTP mode requires optional bearer token for production-like demos.
- Authorization: all initial tools are read-only except local cache/audit writes.
- Observability: structured logs to stderr for stdio, request IDs, durations, dependency status, and tool-call audit rows.
- Error handling: typed errors for validation, provider unavailable, dataset unavailable, model unavailable, license blocked, and internal errors.
- Accessibility: web dashboard must support keyboard navigation, clear focus states, semantic regions, and readable contrast.
- Performance: cache OpenBB/HF metadata, avoid loading large models until needed, bound result sizes.
- Cost: seeded demo defaults to local assets and no external paid API calls.
- Compliance: no investment advice, no trading, visible data caveats.
- License: OpenBB AGPL and dataset/model licenses must be documented before publication.

## Tech Stack Recommendation

| Layer | Viable Options | Recommendation | Why | Delivery Signal |
| --- | --- | --- | --- | --- |
| MCP server | Go, Python, TypeScript | Go gateway, with M0 spike | Go is Tier 1 in official MCP SDK docs and is strong for boundary services and CLIs | Shows production backend judgment and Go capability |
| Analytics/data integration | Python, Go subprocesses, TypeScript | Python 3.12 with uv, FastAPI, OpenBB, pandas/polars, DuckDB | OpenBB and Hugging Face fit Python best | Shows data/AI implementation depth |
| OpenBB access | OpenBB Python API, OpenBB REST, OpenBB MCP | Python API first; reference OpenBB MCP/server behavior | Python gives direct control over normalization and fallback behavior | Shows integration, not just wrapping an existing MCP |
| Persistence | DuckDB, SQLite, PostgreSQL | DuckDB for local MVP; PostgreSQL optional later | Great local analytics and parquet workflow | Shows SQL/data modeling without setup friction |
| Sentiment | FinBERT, FIQA labels, fallback rules | ProsusAI/finbert with deterministic fallback | Finance-domain classifier and robust demo mode | Shows model integration and operational fallback |
| Retrieval | BGE, MiniLM, lexical search | BGE small if available; MiniLM or lexical fallback | Balances quality, local cost, and setup reliability | Shows RAG/evidence workflow |
| Web client | Next.js, Vite, Streamlit | Next.js with TypeScript | Strong portfolio UI and enterprise web signal | Shows full-stack product delivery |
| CLI client | TypeScript, Go, Python | TypeScript MCP client | Exercises official MCP client flow and mirrors common app integrations | Shows complete server/client interfacing |
| Packaging | Docker Compose, Make, GitHub Actions | Make plus Docker Compose plus CI | Repeatable local and reviewer setup | Shows production hygiene |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Go MCP SDK integration costs more than expected | Medium | Medium | M0 spike validates discovery and one tool call before deeper work; ask before switching to Python MCP |
| OpenBB direct dependency license affects repo license | High | Medium | Default to AGPL-compatible repo license or isolate OpenBB adapter with clear license notes |
| OpenBB provider data varies or needs keys | Medium | Medium | Seeded/offline mode is first-class; live mode is optional |
| HF model download is slow or unavailable | Medium | Low | Lazy-load model and provide explicit fallback classifier |
| Large transcript data is too heavy for reviewers | High | Low | Use metadata plus bounded samples, never full corpus by default |
| LLM users over-trust outputs | Medium | High | Add disclaimers, source metadata, no-advice wording, and caveats in every synthesized result |
