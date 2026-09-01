# T-002: Python Analytics Core Skeleton

Status: done
Milestone: M0
Depends On: T-001
Risk: medium
Suggested Agent Tier: standard-dev
Scope: `services/analytics-python`, `packages/contracts`, tests for Python core
Design References: docs/design/03-lld.md#module-design, docs/design/03-lld.md#python-core-http-api

## Objective

Create a FastAPI analytics core with health/status behavior, config loading, response envelopes, and DuckDB connection setup.

## Definition Of Ready

- T-001 is complete.
- Common response envelope fields are confirmed.
- Python version and package manager are confirmed.

## Acceptance Criteria

- `GET /health` returns service status, mode, config summary, and dependency readiness fields.
- Pydantic models define common response envelope and health response.
- DuckDB opens in the configured data directory without committing local artifacts.
- Tests cover health response and config defaults.

## Implementation Notes

- Do not import OpenBB on every test unless needed; keep startup fast.
- Use `MARKETSAGE_MODE=seeded` as the default.
- Keep logs structured and free of secrets.

## Validation

- `make check`
- Python unit tests through `uv run pytest`

## Definition Of Done

- Health endpoint works locally.
- Tests pass.
- Contracts are documented or generated as planned.
- `STATE.md` and this task pack record evidence.

## Handoff Notes

- Created FastAPI analytics core, settings loader, pydantic response envelope, DuckDB readiness setup, and health tests.
- Validation: `npm run check` passed on 2026-08-31.
- Files touched: `services/analytics-python`, `packages/contracts`.
