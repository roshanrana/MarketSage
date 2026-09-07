# T-013: Offline Evaluation Harness

Status: done (2026-09-07)

## Goal

Give the README a results card whose every number is observed by a command a
reviewer can run offline, and make the weak parts visible instead of implied.

## Scope

- Commit the FinanceBench retrieval fixture (145 filing excerpts, 150 queries,
  150 relevance links) and the FiQA sentiment test split (234 rows), both MIT,
  sha256-pinned in `data/fixtures/manifest.json`. The six hand-written evidence
  rows that carried a FinanceBench label without coming from it are gone.
- Tag every corpus document with a ticker through a hand-checked company map
  (`data/fixtures/manifest.json` lists the 32 companies); three queries that
  never name their company were resolved from adjacent queries and document
  content.
- BM25 retrieval (`marketsage_core.retrieval`) with the original term-overlap
  scorer kept behind `MARKETSAGE_RETRIEVAL_SCORER=overlap` for comparison.
- Brief sections carry a `references` list paired with `bullets`, so grounding
  can be scored: every claim resolves to a snapshot, evidence id or sentiment
  hash in the same payload, and tickers without evidence say so.
- `packages/contracts/marketsage.schema.json` is generated from the Pydantic
  models (`npm run contracts`); the harness validates every live response
  against it and exports pinned fixtures that the Go client decodes with
  unknown fields forbidden.
- Nine named fault injections (`marketsage_eval.scenarios`) classify each
  outcome as an honest fallback or a clean error; pytest asserts all of them.
- Four MCP prompts (FR-011) and `marketsage-mcp --describe`.
- `npm run eval` writes `metrics/headline.json`; `npm run card` renders
  `docs/assets/metrics.svg` and the README block; `npm run check` fails when
  either drifts.

## Acceptance

- `npm run check` green, including the two drift checks.
- No figure on the card that the harness did not compute in that run.
- Pending rows for FinBERT, embedding retrieval and live OpenBB data.

## Not done, on purpose

- No FinBERT or embedding numbers: both need downloads the offline gate forbids.
  They belong in a recorded run under `bench/` with the exact command, the way
  the GPU figures are handled elsewhere in the portfolio.
- Seeded prices remain illustrative and are not scored.
