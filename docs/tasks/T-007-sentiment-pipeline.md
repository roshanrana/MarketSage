# T-007: Sentiment Pipeline

Status: done
Milestone: M1
Depends On: T-006
Risk: medium
Suggested Agent Tier: standard-dev
Scope: `services/analytics-python/marketsage_core/sentiment`, sentiment tests, contracts touched only for sentiment fields
Design References: docs/design/02-hld.md#flow-2-sentiment-scan, docs/design/03-lld.md#mcp-tools

## Objective

Implement finance-text sentiment scoring with FinBERT when available and deterministic fallback behavior when not.

## Definition Of Ready

- T-006 is complete.
- Model download policy is confirmed.
- Sentiment response schema is stable.

## Acceptance Criteria

- `sentiment_score_text` returns label, confidence, model id, fallback flag, warnings, and text hash.
- Demo mode works without downloading a model.
- Optional model-enabled path can use `ProsusAI/finbert`.
- Tests cover fallback, text length validation, and response schema.

## Implementation Notes

- Lazy-load model dependencies.
- Do not make investment advice claims from sentiment.
- Cache duplicate text hashes where practical.

## Validation

- `make check`
- Python sentiment unit tests

## Definition Of Done

- Sentiment endpoint and MCP mapping pass tests.
- Fallback behavior is explicit and documented.
- `STATE.md` and this task pack record evidence.

## Handoff Notes

- Added deterministic fallback sentiment and optional lazy FinBERT path behind `MARKETSAGE_ENABLE_MODEL_DOWNLOADS`.
- Validation: `npm run check` passed on 2026-08-31; MCP smoke exercised `sentiment_score_text`.
- Files touched: `services/analytics-python`, `services/mcp-gateway-go`, `clients/mcp-cli`.
