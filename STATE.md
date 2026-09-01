# State

Project: MarketSage
Lifecycle Track: full
Phase: 5
Status: ship-ready
Validation Command: npm run check
Model Routing: design=gpt-5.6-sol/high; standard-dev=gpt-5.6-terra/medium; small-dev=gpt-5.6-luna/medium; security-review=gpt-5.6-sol/high
Approved Stack: Go MCP gateway; Python 3.12+ analytics core with OpenBB and Hugging Face; TypeScript/React/Next.js clients; DuckDB local analytics store; Docker; GitHub Actions
Current Task: T-012
Updated: 2026-09-01

## Now
- M0 through M4 passed validation.
- M3 analyst workbench is browser-verified on desktop and mobile.
- M4 hardening is implemented: optional HTTP bearer auth, server-side token forwarding, structured audit events, dependency/security evidence, and license notes.
- M5 portfolio docs are drafted: README, demo script, and ship report.
- Repository license is `AGPL-3.0-only`.

## Next
- Commit the initialized repository and push to GitHub.

## Decisions
- 2026-08-31: Use the full lifecycle track because MarketSage has multiple components, data/model licensing concerns, MCP contracts, and a portfolio-grade delivery surface. See docs/design/decisions.md#adr-001-use-full-lifecycle-track.
- 2026-08-31: Propose Go for the MCP gateway, Python for OpenBB/HF analytics, and TypeScript/Next.js for demo clients. See docs/design/decisions.md#adr-002-use-go-mcp-gateway-python-analytics-core-and-typescript-clients.
- 2026-08-31: Propose DuckDB for local demo analytics and cache persistence. See docs/design/decisions.md#adr-003-use-duckdb-for-local-analytics-and-cache-state.
- 2026-08-31: Treat OpenBB license compatibility as a first-class design constraint. See docs/design/decisions.md#adr-004-default-to-openbb-compatible-licensing.
- 2026-08-31: Use `npm run check` as the local validation command because GNU Make is not installed on this Windows machine; keep `Makefile` as a wrapper for Unix-like reviewer environments.

## Task Log
- T-001: done - Repository guardrails and validation skeleton.
- T-002: done - Python analytics core skeleton.
- T-003: done - Go MCP gateway walking skeleton and spike.
- T-004: done - TypeScript MCP client smoke demo.
- T-005: done - OpenBB adapter and live/offline market data boundary.
- T-006: done - Hugging Face dataset manifest and seeded ingest.
- T-007: done - Sentiment analysis pipeline.
- T-008: done - Evidence retrieval pipeline.
- T-009: done - Research brief orchestration.
- T-010: done - Next.js analyst workbench.
- T-011: done - Observability, security, and operational hardening.
- T-012: done - Portfolio docs and public repository license are ready.

## Blockers
- None.

## Deviations
- Phase 0 through Phase 3 planning artifacts were drafted in one pass because the user requested autonomous progress. The hard gate before application code remains in force.
