# T-008: Evidence Retrieval

Status: done
Milestone: M2
Depends On: T-006
Risk: medium
Suggested Agent Tier: standard-dev
Scope: `services/analytics-python/marketsage_core/retrieval`, `data/seed`, retrieval tests, contract schemas touched only for evidence fields
Design References: docs/design/02-hld.md#flow-3-evidence-search, docs/design/03-lld.md#data-schemas

## Objective

Implement evidence search across seeded financial passages with source metadata and retrieval fallback behavior.

## Definition Of Ready

- T-006 is complete.
- Evidence sample data exists.
- Retrieval response schema is stable.

## Acceptance Criteria

- `evidence_search` returns ranked snippets, document metadata, scores, and source URIs.
- BGE or MiniLM embedding path is optional and lazy.
- Lexical fallback works in seeded mode.
- Tests cover ranking shape, source metadata, top_k bounds, and fallback warnings.

## Implementation Notes

- Start with FinanceBenchRetrieval because it is small and MIT licensed.
- Use transcript samples only after license review.
- Avoid committing large model artifacts or large parquet files.

## Validation

- `make check`
- Python retrieval tests
- Dataset/license manifest checks

## Definition Of Done

- Evidence search is reliable in seeded mode.
- Outputs are citation-ready for research briefs.
- `STATE.md` and this task pack record evidence.

## Handoff Notes

- Added seeded evidence corpus, lexical retrieval, source metadata, and `evidence_search` MCP tool.
- Validation: `npm run check` passed on 2026-08-31; MCP smoke exercised `evidence_search`.
- Files touched: `services/analytics-python`, `services/mcp-gateway-go`, `clients/mcp-cli`, `data/seed`.
