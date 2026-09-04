# MarketSage — Overview

**What it is:** an existing kind of application, the market-intelligence workbench an analyst already uses, rebuilt so that a language model can use it too, through typed tools, with every run saved and every source caveated.

**Read this if** you want the design reasoning. [SHOWCASE.md](SHOWCASE.md) tours the features with commands.

---

## The setting

A research desk has a workflow: pull a snapshot for a ticker, look at the price trend, read what the filings and the news are saying, score the tone, write a brief. The tooling for this is mature. What is new is the demand from LLM clients (assistants, agents, copilots) to drive that workflow rather than replace it.

The naive integration is a chat window over the data. It fails in the ways that matter to a desk: the model has no structure to call, so it improvises; there is no record of what it looked at, so a brief cannot be reproduced; and there is no honesty about the data's provenance, so seeded or stale numbers look the same as live ones.

The Model Context Protocol is the right abstraction for this. A tool has a name, a schema and a result. A resource has a URI. A client discovers what it can do and calls it. MarketSage is the analyst workflow expressed that way.

## The design

**A Go gateway that respects the transport.** MCP over stdio is unforgiving: anything written to stdout that is not JSON-RPC corrupts the stream. The Go gateway logs to stderr only, forwards bearer tokens server-side, and does nothing but translate between the protocol and the analytics core's HTTP API. It is small on purpose.

**A Python core where the integrations live.** Market data through an OpenBB-ready adapter; Hugging Face datasets with a reviewed manifest; sentiment scoring with a deterministic fallback and an opt-in FinBERT; lexical evidence retrieval; brief orchestration; DuckDB persistence. Every optional dependency is optional in the strict sense: absent, the system runs in seeded mode and says so.

**Three data modes, and warnings that cannot be suppressed.** `seeded` is deterministic and credential-free. `hybrid` tries live data and falls back with a warning in the payload. `live` fails clearly when its dependencies are missing. A consumer of the tool output can always tell what it is looking at.

**Saved runs as a resource.** A research brief is written to DuckDB with its inputs, evidence and caveats, and exposed as `marketsage://runs/{run_id}`. A client can read back exactly what was produced. Audit events record every tool call.

**A conventional surface alongside the tool surface.** The Next.js workbench proxies to the same core server-side. Analysts and stakeholders who will never use an MCP client get the same capabilities, with a mode selector, source-aware snapshot, evidence list, brief, dataset table, warnings and caveats.

**Provenance and licensing reviewed before release.** `docs/research/source-notes.md` records which datasets and models were considered; two were excluded (one pending licence review, one under CC-BY-SA-4.0 requiring explicit acceptance). `docs/third-party-notices.md` lists every licence. The repository is AGPL-3.0 because OpenBB is, and the README says how to change that if needed.

## What is measured

One gate, `npm run check`, covering four languages and the protocol boundary:

| Check | Result at ship |
|---|---|
| Docs, `ruff`, `pytest` (15 tests) | Pass |
| `go fmt`, `go test`, `go vet` (8 tests) | Pass |
| MCP CLI smoke: discover 7 tools, call the chain, read `marketsage://runs/{run_id}` | Pass |
| Next.js production build, workspace check | Pass |
| Desktop and mobile browser: `Run Brief` completes | Pass; a duplicate-key overlay and a mobile overflow were found and fixed |
| `npm audit --audit-level=high` | 0 vulnerabilities |
| `uv pip check`, `govulncheck` | Compatible; 0 called vulnerabilities |
| Secret scan | Placeholders and test tokens only |

## Honest limits

Seeded data is illustrative, not current. Live mode depends on optional OpenBB installation and provider configuration. FinBERT is opt-in; the default sentiment is a deterministic fallback. Evidence retrieval is lexical; embedding retrieval is a planned step. Bearer auth is a local control, not identity management.

## Where it sits among the other projects

MarketSage is the integration-surface project. Where [REGLENS](https://github.com/roshanrana/RegLens) is about whether an answer can be trusted and [PROVENANCE](https://github.com/roshanrana/PROVENANCE) about whether the platform can, MarketSage is about exposing an existing workflow to models cleanly, with provenance, and without pretending the data is better than it is.
