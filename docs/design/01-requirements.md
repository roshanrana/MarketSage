# Requirements

## Problem

Investment analysts, treasury teams, and finance operators often have market data, filings, sentiment, and research notes spread across APIs, notebooks, terminals, and dashboards. LLMs can help synthesize this information, but they need trustworthy, structured, auditable access to tools and evidence instead of ad hoc copy/paste.

MarketSage will be a portfolio-grade fintech product that exposes a traditional market intelligence application through MCP. It should demonstrate how an implementation engineer can discover a real workflow, integrate existing systems, wrap them in safe agent interfaces, and ship a polished demo with operational discipline.

## Product Shape

MarketSage is an MCP-native market intelligence workbench.

- The MCP server exposes OpenBB-backed market tools, finance/NLP dataset resources, reusable prompts, and audit-friendly research runs.
- Demo clients show the same capabilities through terminal, MCP host, and web dashboard workflows.
- The default reviewer path should run locally with seeded data and no private credentials.
- Optional live mode can use OpenBB provider configuration and API keys when available.

## Users And Workflows

- Technical reviewer: wants to see a complete product, clean architecture, sensible tradeoffs, reliable setup, and a demo that proves real integration.
- Buy-side or corporate treasury analyst: wants a ticker or portfolio brief with price movement, sentiment, document evidence, and clear source boundaries.
- Platform engineer: wants a well-scoped MCP server with typed tools, input validation, logs, tests, and safe defaults.
- AI application user: wants to ask natural-language market questions while the LLM calls tools and receives structured evidence.

## Functional Requirements

- FR-001: Provide an MCP server named `marketsage` with tool discovery, tool execution, resources, and prompts.
- FR-002: Expose a health/status tool that reports service readiness, data mode, dependency status, and dataset availability.
- FR-003: Fetch equity market snapshots and historical prices through OpenBB in live mode.
- FR-004: Provide deterministic seeded/offline market data so the demo works without paid credentials or external API reliability.
- FR-005: Normalize market outputs into stable JSON schemas with ticker, observation time, source, values, and warnings.
- FR-006: Score financial text sentiment using a finance-domain model when local model dependencies are available.
- FR-007: Provide a lightweight fallback sentiment path for demo mode if model download is unavailable.
- FR-008: Ingest selected Hugging Face finance datasets into a local manifest and cache.
- FR-009: Search financial evidence from seeded filings/transcripts/benchmark passages and return cited snippets with source metadata.
- FR-010: Generate a structured research brief that combines market data, sentiment, evidence, assumptions, and limitations.
- FR-011: Provide reusable MCP prompts for equity research, portfolio risk scan, earnings-call questions, and source-quality review.
- FR-012: Persist research runs and tool-call audit events locally.
- FR-013: Provide a TypeScript MCP client that demonstrates server discovery and at least three real tool calls.
- FR-014: Provide a Next.js workbench that lets a reviewer run the main demo workflow without reading code first.
- FR-015: Document setup for MCP hosts that support stdio or streamable HTTP.

## Non-Functional Requirements

- NFR-001: Local seeded demo setup should complete with one command after dependencies are installed.
- NFR-002: A single `make check` command must run formatting, linting, type checks, unit tests, and MCP smoke tests.
- NFR-003: MCP stdio mode must never write ordinary logs to stdout.
- NFR-004: Tool responses must include source, timestamp, data mode, and caveats where relevant.
- NFR-005: No tool may execute trades, place orders, transfer funds, or present output as financial advice.
- NFR-006: Secrets must come from environment variables or local ignored files; committed seed data must contain no credentials or personal user data.
- NFR-007: Live provider failures must degrade into clear errors or offline fallback, not silent hallucinated data.
- NFR-008: Typical seeded demo tool calls should complete in under 2 seconds after first startup, excluding optional model download.
- NFR-009: The web UI must be responsive and usable on laptop and mobile widths.
- NFR-010: License metadata for OpenBB, Hugging Face datasets, and Hugging Face models must be documented before release.

## Integrations And Data

- OpenBB ODP Python package: primary live market data integration.
- OpenBB MCP package: reference implementation and possible adapter source, not the core product by itself.
- Hugging Face Dataset Viewer API: read-only metadata and optional seed download.
- `zeroshot/twitter-financial-news-sentiment`: sentiment demo data, 11,931 rows across train/validation, MIT license.
- `TheFinAI/fiqa-sentiment-classification`: sentiment evaluation fixture, 1,173 rows across train/test/valid, MIT license.
- `mteb/FinanceBenchRetrieval`: evidence retrieval fixture, 445 rows across corpus/qrels/queries, MIT license.
- `glopardo/sp500-earnings-transcripts`: earnings transcript corpus, 20,681 rows and about 562 MB parquet; use only sampled subsets until license is confirmed.
- `ProsusAI/finbert`: finance-domain sentiment model.
- `BAAI/bge-small-en-v1.5`: embedding model candidate, MIT license.
- `sentence-transformers/all-MiniLM-L6-v2`: lightweight embedding fallback, Apache-2.0 license.
- `nlpaueb/sec-bert-base`: SEC-domain language model candidate, CC-BY-SA-4.0; optional, not in MVP unless license implications are acceptable.

## Security, Privacy, Compliance

- MarketSage is a research/demo tool, not an investment adviser, broker, trading system, or treasury execution system.
- All agent-triggered writes are limited to local cache, local audit logs, and saved research runs.
- Any future destructive or external write action must require explicit user confirmation and separate task approval.
- HTTP mode must support a local bearer token in production-like runs.
- Inputs must validate ticker symbols, date ranges, provider names, text length, and query limits.
- Logs must avoid secrets and large raw transcripts by default.
- Financial data provenance, staleness, and model limitations must be visible in outputs.

## Constraints

- Project path: `C:\Users\rosha\OneDrive\Documents\Code-Central\MarketSage`.
- Target GitHub positioning: portfolio product, not a toy MCP wrapper.
- Preferred stack: Go where applicable, Python for OpenBB/HF, TypeScript/React for clients.
- Python should be managed through `uv` because direct `python` currently resolves to the Windows Store shim on this machine.
- Local toolchain observed on 2026-08-31: Go 1.27.0, Node 24.14.0, npm 11.9.0, uv 0.11.23.
- Do not switch to a materially different stack without user approval.

## Portfolio Delivery Signals

- Customer workflow framing: market brief, evidence search, and portfolio risk questions.
- Real integration: OpenBB, MCP, Hugging Face datasets/models, and local persistence.
- Production engineering: Go boundary service, typed contracts, tests, Docker, CI, observability-ready logs, auth-aware HTTP mode.
- Data/AI depth: sentiment classification, retrieval, dataset manifests, model fallback behavior, and license tracking.
- Demo polish: CLI transcript, MCP host config, and Next.js analyst dashboard.

## Assumptions

- A-001: The user approves MarketSage as the local folder name and GitHub product name.
- A-002: It is acceptable for the MVP to avoid trading or financial write actions.
- A-003: Seeded/offline mode is required so technical reviewers can run the project without private credentials.
- A-004: Go MCP gateway is worth a short spike because the official MCP SDK lists Go as Tier 1, but Python remains the fallback if the Go gateway adds more risk than value.
- A-005: OpenBB license compatibility should be resolved before public release; default recommendation is AGPL-3.0-only if OpenBB remains a direct dependency.

## Out Of Scope

- Trading execution, portfolio rebalancing, bank connectivity, payment rails, or broker integration.
- Investment recommendations, price prediction claims, or automated financial advice.
- Production multi-tenant auth, billing, and user management.
- Hosting a public live financial data API.
- Full ingestion of large transcript corpora in the MVP.

## Acceptance

Implementation planning can start when:

- Requirements clearly define the MarketSage demo workflow and non-goals.
- Architecture identifies MCP, OpenBB, Hugging Face, persistence, clients, and validation.
- Task packs are scoped with risk, model tier, dependencies, and acceptance criteria.
- User approves the execution plan before application code begins.
