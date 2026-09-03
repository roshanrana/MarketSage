# T-011: Hardening, Observability, And Security

Status: done
Milestone: M4
Depends On: T-003, T-005, T-009, T-010
Risk: high
Suggested Agent Tier: security-review then standard-dev
Scope: gateway/core/client logging, auth config, validation harness, dependency/license scanning, docs updates
Design References: docs/design/02-hld.md#cross-cutting-concerns, docs/design/03-lld.md#error-taxonomy

## Objective

Harden MarketSage for a credible enterprise/implementation portfolio release.

## Definition Of Ready

- M0 through M3 core workflows are implemented.
- Validation command is stable.
- Known runtime and license dependencies are listed.

## Acceptance Criteria

- HTTP mode requires token when configured.
- Stdio mode does not write ordinary logs to stdout.
- Audit events include request id, tool, status, duration, mode, and warning count.
- Dependency audit and license report are documented.
- Error paths are tested for invalid input and provider/model/dataset unavailable states.

## Implementation Notes

- Keep auth simple and local: bearer token for HTTP mode only.
- No secret values in logs, screenshots, committed config, or test fixtures.
- Add OpenTelemetry-ready structure without overbuilding exporters in MVP.

## Validation

- `make check`
- Dependency audit commands chosen by stack
- Secret scan command if available
- Manual MCP stdio log check if automated check is impractical

## Definition Of Done

- Hardening evidence is captured.
- Known residual risks are documented.
- `STATE.md` and this task pack record evidence.

## Handoff Notes

- Completed 2026-09-01.
- Added optional bearer auth on the FastAPI analytics surface using `MARKETSAGE_HTTP_TOKEN`.
- Updated the Next.js proxy and Go MCP gateway to forward the token server-side when configured.
- Expanded DuckDB `audit_event` rows with request id, tool/source, status, duration, mode, warning count, detail, and timestamp.
- Added error audit rows for known market data and saved-run failures.
- Added tests for token enforcement, audit persistence, invalid ticker input, live provider failure, FinBERT fallback, and unknown dataset filters.
- Added `docs/security-and-ops.md` and `docs/third-party-notices.md`.
- Added `npm run audit:deps` and `make audit-deps`.
- Validation evidence: `npm run check:python` passed with 15 tests; `npm run check:go` passed; `npm audit` found 0 vulnerabilities; `uv pip check` passed; `govulncheck` found 0 called vulnerabilities; secret text scan found no committed secrets.
