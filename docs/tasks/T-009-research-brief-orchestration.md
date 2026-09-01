# T-009: Research Brief Orchestration

Status: done
Milestone: M2
Depends On: T-005, T-007, T-008
Risk: high
Suggested Agent Tier: design then standard-dev
Scope: `services/analytics-python/marketsage_core/briefs`, Go MCP tool mapping for `research_brief`, research run persistence, integration tests
Design References: docs/design/02-hld.md#flow-4-research-brief, docs/design/03-lld.md#mcp-tools

## Objective

Assemble sourced market research briefs from market data, sentiment, and evidence search.

## Definition Of Ready

- T-005, T-007, and T-008 are complete.
- Brief schema and caveat requirements are stable.
- Persistence schema for `research_run` is implemented or ready.

## Acceptance Criteria

- `research_brief` accepts one or more tickers, horizon, sections, and mode.
- Output includes summary, market signals, sentiment, evidence table, caveats, and run id.
- Research runs are persisted and retrievable through resource/API path.
- Integration tests prove seeded brief generation.

## Implementation Notes

- Keep synthesis structured. Do not call an LLM inside the server for MVP unless explicitly approved.
- Let the MCP host LLM perform final prose if needed, using structured data and prompts.
- Include no-advice caveats in every brief.

## Validation

- `make check`
- Python integration tests
- MCP smoke test for `research_brief`

## Definition Of Done

- Brief generation works end to end through MCP.
- Saved run resource works.
- Design docs are updated if orchestration changes frozen interfaces.
- `STATE.md` and this task pack record evidence.

## Handoff Notes

- Added structured research brief orchestration, local DuckDB run persistence, `/runs/{run_id}`, MCP `research_brief`, and `marketsage://runs/{run_id}` resource template.
- Validation: `npm run check` passed on 2026-08-31; MCP smoke created a brief and read the saved run resource.
- Files touched: `services/analytics-python`, `services/mcp-gateway-go`, `clients/mcp-cli`, `data/seed`.
