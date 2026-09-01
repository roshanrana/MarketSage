# T-010: Next.js Analyst Workbench

Status: done
Milestone: M3
Depends On: T-009
Risk: medium
Suggested Agent Tier: standard-dev
Scope: `apps/web`, web tests, API client generated from contracts
Design References: docs/design/02-hld.md#flow-5-reviewer-demo, docs/design/03-lld.md#module-design

## Objective

Build a polished traditional app surface for the core MarketSage workflow.

## Definition Of Ready

- T-009 is complete.
- API contracts are stable.
- Visual direction is selected from existing project goals.

## Acceptance Criteria

- Web app supports ticker input, mode selection, snapshot, evidence search, research brief, and recent runs.
- UI makes source, freshness, warnings, and caveats visible.
- Layout works on laptop and mobile widths.
- Type checks and basic workflow tests pass.

## Implementation Notes

- Prioritize a dense analyst workbench, not a marketing landing page.
- Use icons, tabs, segmented controls, and structured tables where appropriate.
- Avoid feature-explainer text inside the app; the UI should be self-evident.

## Validation

- `make check`
- TypeScript type check
- Web unit or component tests
- Browser screenshot verification after dev server starts

## Definition Of Done

- Reviewer can run the main workflow in the browser.
- UI has been visually verified.
- `STATE.md` and this task pack record evidence.

## Handoff Notes

- Started 2026-08-31 after M2 passed.
- Completed 2026-09-01.
- Added `apps/web` Next.js analyst workbench with ticker input, mode selection, status cards, market snapshot, price trend, evidence list, research brief, dataset table, warnings, and caveats.
- Added server-side proxy route under `/api/marketsage/[...path]` so the browser never calls the analytics core directly.
- Browser verified desktop and mobile `Run Brief` workflow.
- Fixed React duplicate-key warning from repeated caveat text.
- Fixed mobile horizontal overflow by setting shrink-safe panel minimums.
- Validation evidence: `npm run check` passed after the UI fixes.
