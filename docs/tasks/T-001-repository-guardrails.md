# T-001: Repository Guardrails

Status: done
Milestone: M0
Depends On: none
Risk: medium
Suggested Agent Tier: standard-dev
Scope: repository root, `.github/workflows`, `services/*` scaffold directories, `apps/*` scaffold directories, `clients/*` scaffold directories, `packages/contracts`, validation config only
Design References: docs/design/03-lld.md#repository-layout, docs/design/04-execution-plan.md#validation-gates

## Objective

Create the repository skeleton and single validation command without implementing product behavior.

## Definition Of Ready

- Execution plan is approved.
- Folder layout and validation command are accepted.
- No license decision is blocking local-only development.

## Acceptance Criteria

- Repository has Makefile or equivalent with `make check`.
- Basic Go, Python, TypeScript, and docs validation hooks are represented.
- CI runs the same validation command.
- Local cache and secret files are ignored.
- Project state remains accurate.

## Implementation Notes

- Use `uv` for Python environment management.
- Use Go module for the MCP gateway.
- Use npm workspaces or a clear Node package layout for TypeScript client and web app.
- Keep seed data tiny and reviewable.

## Validation

- `make check`
- `git status --short`

## Definition Of Done

- Validation command exists and passes for the empty skeleton.
- CI configuration references the same command.
- `STATE.md` and this task pack record evidence.

## Handoff Notes

- Created root npm workspace validation, Makefile wrapper, CI workflow, ignores, env example, docs checker, Go format checker, contracts scaffold, README, and web scaffold.
- Validation: `npm run check` passed on 2026-08-31.
- Files touched: repository root, scripts, `.github/workflows`, `packages/contracts`, `apps/web`.
