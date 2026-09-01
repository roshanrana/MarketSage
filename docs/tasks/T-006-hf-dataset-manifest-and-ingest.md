# T-006: Hugging Face Dataset Manifest And Seeded Ingest

Status: done
Milestone: M1
Depends On: T-002
Risk: medium
Suggested Agent Tier: standard-dev
Scope: `services/analytics-python/marketsage_core/datasets`, `data/seed`, `docs/research`, Python tests
Design References: docs/design/01-requirements.md#integrations-and-data, docs/design/03-lld.md#data-schemas

## Objective

Implement a reproducible dataset manifest and bounded seeded ingest for approved Hugging Face datasets.

## Definition Of Ready

- T-002 is complete.
- Dataset ids and initial usage are approved.
- License handling rules are accepted.

## Acceptance Criteria

- Dataset manifest records ids, splits, row counts, license, source URL, and local status.
- Seed ingest creates small deterministic local samples for sentiment and evidence demos.
- Datasets with unclear or restrictive licenses are marked optional or blocked.
- Tests validate manifest shape and local sample bounds.

## Implementation Notes

- Use Hugging Face Dataset Viewer API for metadata.
- MVP approved datasets: `zeroshot/twitter-financial-news-sentiment`, `TheFinAI/fiqa-sentiment-classification`, `mteb/FinanceBenchRetrieval`.
- Keep `glopardo/sp500-earnings-transcripts` optional until license clarity.

## Validation

- `make check`
- Python dataset tests
- Manifest freshness test with mocked HTTP

## Definition Of Done

- Seeded dataset samples are reproducible.
- License metadata is visible through `dataset_status`.
- `STATE.md` and this task pack record evidence.

## Handoff Notes

- Added curated Hugging Face dataset manifest with row counts, license notes, local status, and DuckDB manifest writes.
- Validation: `npm run check` passed on 2026-08-31; MCP smoke exercised `dataset_status`.
- Files touched: `services/analytics-python`, `services/mcp-gateway-go`, `clients/mcp-cli`, `docs/research`.
