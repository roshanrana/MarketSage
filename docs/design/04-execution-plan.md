# Execution Plan

## Track And Gate

Lifecycle Track: full
Current Phase: 5
Status: ship-ready
Validation Command: `npm run check`

This plan intentionally started with a walking skeleton and a Go MCP spike. The Go gateway passed validation, so it remains the MCP boundary. Stop and ask before switching to a Python MCP server.

## Definition Of Ready

A task is ready when:

- Its requirements and design references are listed.
- Write scope is explicit.
- Inputs, outputs, contracts, and validation commands are clear.
- Risk and suggested agent tier are set.
- Any stack or license deviation has user approval.

## Definition Of Done

A task is done when:

- Acceptance criteria pass.
- The relevant local validation command passes.
- Handoff notes record changed files, decisions, and evidence.
- `STATE.md` and the task pack are updated.
- No known scope drift remains unresolved.

## Milestones

- M0 Walking Skeleton: complete.
- M1 Data Foundation: complete.
- M2 Intelligence Layer: complete.
- M3 Product Surface: complete.
- M4 Hardening: complete.
- M5 Portfolio Ship: complete.

## Dependency Graph

| Task | Title | Risk | Agent Tier | Depends On | Parallel Wave | Validation |
| --- | --- | --- | --- | --- | --- | --- |
| T-001 | Repository guardrails and validation skeleton | medium | standard-dev | none | W0 | make check |
| T-002 | Python analytics core skeleton | medium | standard-dev | T-001 | W1 | make check |
| T-003 | Go MCP gateway walking skeleton and spike | medium | standard-dev | T-001, T-002 | W2 | make check |
| T-004 | TypeScript MCP client smoke demo | low | small-dev | T-003 | W3 | make check |
| T-005 | OpenBB adapter and live/offline boundary | medium | standard-dev | T-002 | W4 | make check |
| T-006 | Hugging Face dataset manifest and seeded ingest | medium | standard-dev | T-002 | W4 | make check |
| T-007 | Sentiment analysis pipeline | medium | standard-dev | T-006 | W5 | make check |
| T-008 | Evidence retrieval pipeline | medium | standard-dev | T-006 | W5 | make check |
| T-009 | Research brief orchestration | high | design then standard-dev | T-005, T-007, T-008 | W6 | make check |
| T-010 | Next.js analyst workbench | medium | standard-dev | T-009 | W7 | make check |
| T-011 | Observability, security, and operational hardening | high | security-review then standard-dev | T-003, T-005, T-009, T-010 | W8 | make check |
| T-012 | Portfolio README, demo script, and ship report | low | small-dev | T-011 | W9 | make check |

## Parallelization Plan

- Do not parallelize T-001 through T-004 because they establish shared conventions and contracts.
- T-005 and T-006 can run in parallel after T-002 if their write scopes remain separate.
- T-007 and T-008 can run in parallel after T-006 if they do not change shared dataset schemas.
- T-011 should include a stronger review pass because it touches security, observability, and release posture.

## Validation Gates

- M0 gate: `make check` passes and the TypeScript client can list MCP tools and call `health_check`.
- M1 gate: seeded mode returns market data, dataset manifest, and sentiment with source/warnings.
- M2 gate: `research_brief` combines market, sentiment, and evidence with a saved run id.
- M3 gate: web workbench completes the reviewer workflow on desktop and mobile widths.
- M4 gate: dependency audit, license notes, token handling, no stdout logging in stdio mode, and contract tests pass.
- M5 gate: fresh clone/reviewer path works from README, with no private credentials, and repository license is present.

## Model Routing Summary

- Design and high-risk reviews: `gpt-5.6-sol` high or xhigh.
- Medium-risk implementation: `gpt-5.6-terra` medium.
- Low-risk leaf work: `gpt-5.6-luna` low or medium.
- Escalate any implementation task that changes contracts, schemas, auth, live data behavior, concurrency, or deployment.

## Implementation Stack Signals

- Go: MCP gateway, service boundary, concurrency-ready backend, single-binary CLI/server potential.
- Python: OpenBB integration, Hugging Face datasets/models, analytics workflows.
- TypeScript/Next.js: client/demo surface and typed frontend.
- SQL/DuckDB: local analytics, cache, audit, and reproducible seeded data.
- Docker/GitHub Actions/Make: repeatable setup and validation.
- Observability/security: logs, request IDs, local auth, dependency/license checks, audit events.

## Top Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Go MCP gateway proves too costly | M0 spike; ask before switching to Python MCP |
| OpenBB license implications | Default AGPL-compatible posture; third-party notices documented |
| Live data requires provider keys | Seeded mode first; live mode optional |
| HF model/dataset downloads slow | Lazy loading, bounded samples, deterministic fallback |
| LLM over-trust | Caveats and source metadata in all synthesized outputs |

## Open Questions

- If a permissive license is desired later, isolate OpenBB behind an optional external service and revisit licensing.
- Confirm whether the first public demo should optimize for a terminal/MCP-host walkthrough first or the web dashboard first. Default recommendation: terminal/MCP first, then web.

## Approval Gate

Reply "approved" to proceed with implementation, or tell me what to change.
