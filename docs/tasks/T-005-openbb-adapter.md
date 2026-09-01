# T-005: OpenBB Adapter

Status: done
Milestone: M1
Depends On: T-002
Risk: medium
Suggested Agent Tier: standard-dev
Scope: `services/analytics-python/marketsage_core/openbb_adapter`, seed fixtures, Python tests, contract schemas
Design References: docs/design/02-hld.md#flow-1-ticker-snapshot, docs/design/03-lld.md#python-core-http-api

## Objective

Implement normalized seeded and live-mode market data access behind stable Python core endpoints.

## Definition Of Ready

- T-002 is complete.
- Seed fixture format is selected.
- OpenBB dependency and license note are documented.

## Acceptance Criteria

- Seeded `market_snapshot` and `price_history` work without credentials.
- Live mode attempts OpenBB calls only when configured.
- Provider failures return typed errors or seeded fallback with visible warning.
- Outputs include source, timestamp, mode, and caveats.

## Implementation Notes

- Use a small seed set such as AAPL, MSFT, JPM, XOM, and SPY.
- Do not claim seed data is current.
- Keep OpenBB imports controlled to avoid slow test startup.

## Validation

- `make check`
- Python adapter unit tests
- Integration test for seeded snapshot/history

## Definition Of Done

- Seeded market endpoints are reliable.
- Live-mode boundary is implemented and documented.
- `STATE.md` and this task pack record evidence.

## Handoff Notes

- Added seeded market snapshot/history endpoints and optional lazy OpenBB live-mode adapter.
- Validation: `npm run check` passed on 2026-08-31; MCP smoke exercised `market_snapshot`.
- Files touched: `services/analytics-python`, `services/mcp-gateway-go`, `clients/mcp-cli`, `data/seed`.
