# Decisions

## ADR-001: Use Full Lifecycle Track

Date: 2026-08-31
Status: proposed

### Context

MarketSage is a greenfield project with multiple runtime components, MCP contracts, OpenBB integration, Hugging Face assets, local persistence, licensing concerns, and a portfolio-grade demo requirement.

### Options

- Compact lifecycle: faster, but likely to under-document architecture and risk.
- Full lifecycle: more upfront structure, but clearer task boundaries and resume state.

### Decision

Use the full enterprise-dev-lifecycle track.

### Consequences

The project gets requirements, HLD, LLD, execution plan, task packs, validation gates, and ship report. Application code waits until the execution plan is approved.

## ADR-002: Use Go MCP Gateway, Python Analytics Core, And TypeScript Clients

Date: 2026-08-31
Status: proposed

### Context

The user wants an implementation-oriented portfolio project, prefers OpenBB, wants Go incorporated where applicable, and wants complete MCP server/client interfacing.

### Options

- Python-only MCP server: lowest risk and best OpenBB/HF ecosystem fit.
- Use OpenBB MCP directly: fastest, but not enough original product surface.
- Go MCP gateway plus Python analytics core: strongest delivery signal but higher integration complexity.
- TypeScript-only MCP server: convenient for web, but Python still fits OpenBB/HF better.

### Decision

Use Go for the MCP gateway, Python for analytics/OpenBB/HF, and TypeScript for clients. Put a Go MCP spike in M0 so the choice is validated early.

### Consequences

The architecture demonstrates language-boundary judgment, typed protocol design, and production-friendly service separation. It also adds integration overhead, which is controlled by making M0 prove discovery and one real tool call before deeper implementation.

## ADR-003: Use DuckDB For Local Analytics And Cache State

Date: 2026-08-31
Status: proposed

### Context

MarketSage needs a local store for seeded datasets, cached observations, audit events, and research runs. The default reviewer path should avoid a database server.

### Options

- SQLite: very simple, but less natural for parquet analytics.
- DuckDB: excellent local analytics and parquet workflow, lightweight enough for demos.
- PostgreSQL: enterprise signal, but more setup for reviewers.

### Decision

Use DuckDB for MVP local persistence. Keep schemas portable enough that PostgreSQL can become an optional future backend.

### Consequences

Reviewer setup stays low-friction while still showing SQL/data modeling. Large data and production multi-user patterns remain future work.

## ADR-004: Default To OpenBB-Compatible Licensing

Date: 2026-08-31
Status: proposed

### Context

The OpenBB GitHub repository currently states AGPLv3 licensing. MarketSage's direct use of OpenBB packages may affect the appropriate license for a public portfolio repository.

### Options

- License MarketSage as AGPL-3.0-only: safest compatibility posture if OpenBB remains a direct dependency.
- Keep MarketSage MIT and isolate OpenBB as an optional external service: more permissive but requires careful separation and documentation.
- Delay licensing: fastest now, risky before public release.

### Decision

Default recommendation is AGPL-3.0-only unless the user prefers an isolated adapter strategy.

### Consequences

The project avoids muddled licensing for public GitHub use. Before publishing, include third-party notices and make the no-legal-advice limitation explicit.

## ADR-005: Use Seeded Data First, Live Data Second

Date: 2026-08-31
Status: proposed

### Context

Technical reviewers need a demo that works quickly. Live finance APIs can need credentials, rate limits, network access, or provider-specific setup.

### Options

- Live-first: more realistic, but brittle for reviewers.
- Seeded-first with optional live mode: reliable demo and clear integration boundary.

### Decision

Build seeded mode first and live OpenBB mode second.

### Consequences

MarketSage can prove the full MCP/client workflow early. Live OpenBB integration remains central, but the demo is not blocked by external data access.
