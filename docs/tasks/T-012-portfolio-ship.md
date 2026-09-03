# T-012: Portfolio Ship

Status: done
Milestone: M5
Depends On: T-011
Risk: low
Suggested Agent Tier: small-dev
Scope: `README.md`, `docs/ship-report.md`, demo scripts, screenshots or transcripts after behavior exists
Design References: docs/design/04-execution-plan.md#validation-gates, docs/design/01-requirements.md#portfolio-delivery-signals

## Objective

Package MarketSage as a GitHub-ready portfolio product with a clear demo story.

## Definition Of Ready

- T-011 is complete.
- Core demo workflow works from a clean checkout.
- License posture is confirmed.

## Acceptance Criteria

- README explains product value, architecture, setup, demo workflow, and delivery signals.
- Demo script has 3 to 5 commands or prompts.
- Ship report captures validation evidence, source/license notes, risks, and known limitations.
- Screenshots or terminal transcript are included only after the behavior exists.

## Implementation Notes

- Keep claims grounded: MCP server, clients, OpenBB integration, seeded data, evidence retrieval, and analyst workbench.
- Highlight the distinction between seeded demo data and live mode.
- Include financial disclaimer and data provenance notes.

## Validation

- `make check`
- Fresh setup dry run from README where feasible
- Link and markdown checks if configured

## Definition Of Done

- Repository is ready to push to GitHub.
- Demo path is reviewer-friendly.
- `STATE.md` marks Phase 7 ship-readiness evidence.

## Handoff Notes

- Packaging work completed 2026-09-01.
- Replaced the README with current architecture, setup, MCP surface, validation, data modes, security posture, and delivery signals.
- Added `docs/demo-script.md` with a 5 minute walkthrough.
- Added `docs/ship-report.md` with validation evidence, source/license notes, known limitations, and reviewer story.
- Added canonical AGPLv3 license text and set package metadata to `AGPL-3.0-only`.
