# T-003: Go MCP Gateway Skeleton

Status: done
Milestone: M0
Depends On: T-001, T-002
Risk: medium
Suggested Agent Tier: standard-dev
Scope: `services/mcp-gateway-go`, `packages/contracts`, tests for Go gateway
Design References: docs/design/02-hld.md#recommended-architecture, docs/design/03-lld.md#mcp-tools

## Objective

Prove the Go MCP gateway can expose MarketSage discovery and call the Python analytics core for `health_check`.

## Definition Of Ready

- T-001 and T-002 are complete.
- Go MCP SDK package choice is confirmed by a small spike.
- Python health endpoint contract is stable.

## Acceptance Criteria

- Gateway starts in stdio mode without writing ordinary logs to stdout.
- Gateway exposes at least `health_check` through MCP tool discovery.
- `health_check` calls the Python core and returns a structured MCP response.
- Tests validate input/output mapping and no stdout logging in stdio path where feasible.

## Implementation Notes

- Use the official Go MCP SDK if it remains practical.
- Keep this as a spike plus walking skeleton; do not implement all tools here.
- If SDK friction blocks the task, document evidence and ask before switching to Python MCP.

## Validation

- `make check`
- `go test ./...`
- MCP smoke test for `health_check`

## Definition Of Done

- MCP discovery and `health_check` work against the Python core.
- Spike outcome is recorded in decisions if it changes architecture confidence.
- `STATE.md` and this task pack record evidence.

## Handoff Notes

- Created Go MCP gateway with official Go SDK, analytics HTTP client, and `health_check` tool.
- Validation: `npm run check` passed on 2026-08-31; TypeScript smoke called `health_check` through MCP.
- Files touched: `services/mcp-gateway-go`, `packages/contracts`.
