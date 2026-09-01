# T-004: TypeScript MCP Client Smoke Demo

Status: done
Milestone: M0
Depends On: T-003
Risk: low
Suggested Agent Tier: small-dev
Scope: `clients/mcp-cli`, client tests, README snippets for local smoke only
Design References: docs/design/03-lld.md#module-design, docs/design/04-execution-plan.md#m0-walking-skeleton

## Objective

Create a TypeScript MCP client that demonstrates discovery and a real `health_check` tool call against the MarketSage gateway.

## Definition Of Ready

- T-003 is complete.
- MCP server startup command is known.
- Expected health response shape is stable.

## Acceptance Criteria

- CLI lists MarketSage tools.
- CLI calls `health_check` and prints concise structured output.
- CLI exits non-zero on failed tool call.
- Smoke test runs as part of `make check`.

## Implementation Notes

- Keep output reviewer-friendly.
- Avoid requiring an LLM API key for this client.
- Prefer a scriptable command such as `npm run demo:mcp`.

## Validation

- `make check`
- TypeScript type check
- MCP smoke test

## Definition Of Done

- CLI proves server/client interfacing.
- Smoke path is documented.
- `STATE.md` and this task pack record evidence.

## Handoff Notes

- Created TypeScript MCP CLI that starts analytics, launches the Go stdio MCP gateway, lists tools, and calls `health_check`.
- Validation: `npm run check` passed on 2026-08-31.
- Files touched: `clients/mcp-cli`.
