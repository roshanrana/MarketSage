# Codebase graph

MarketSage carries a queryable code knowledge graph built with [graphify](https://pypi.org/project/graphifyy/)
(tree-sitter over 37 languages, offline, no LLM or API key required). It answers "what depends on
this?", "how do A and B connect?" and "what is X?" with file:line citations in a few hundred
tokens, where grepping the same answer costs thousands. Agents working in this repo should query
the graph before reading source files — see the `graphify` section at the top of `CLAUDE.md` and
`.claude/skills/graphify/SKILL.md`.

## Build and query

```bash
graphify update .                              # rebuild the graph (AST only, no API key), ~seconds
graphify explain "<class or module>"           # what a node is and what it connects to
graphify path "<A>" "<B>"                      # shortest relationship between two symbols
graphify affected "<symbol>" --depth 2         # blast radius of a change
```

Run `graphify update .` after code changes so `affected` and `path` stay truthful. `make graph`
wraps the update-and-cluster step (see `Makefile`).

## Three real queries

**1. `graphify explain "server.go"`** — the Go MCP gateway's tool registry:

```
Node: server.go
  ID:        server_server
  Source:    services/mcp-gateway-go/internal/server/server.go L1
  Type:      code
  Community: 1
  Degree:    21

Connections (21):
  --> Handlers [contains] [EXTRACTED]
  --> Describe() [contains] [EXTRACTED]
  --> New() [contains] [EXTRACTED]
  --> AnalyticsClient [contains] [EXTRACTED]
  --> DatasetStatusOutput / EvidenceSearchOutput / HealthOutput / MarketSnapshotOutput /
      PriceHistoryOutput / ResearchBriefOutput / SentimentOutput [contains] [EXTRACTED]
  --> DatasetStatusInput / EvidenceSearchInput / HealthInput / PriceHistoryInput /
      ResearchBriefInput / SentimentInput [contains] [EXTRACTED]
  --> ResourceTemplateNames() / ToolNames() [contains] [EXTRACTED]
  --> Surface [contains] [EXTRACTED]
  ... and 1 more
```

One node, `server.go`, contains all seven tool input/output pairs plus `Describe()`,
`ToolNames()` and `ResourceTemplateNames()` — confirms the tool registry lives in a single file,
as `docs/SHOWCASE.md` describes.

**2. `graphify path "main.go" "client.go"`** — the Go entry point to the analytics-core HTTP
client:

```
warning: target match was ambiguous (top score 4274.3, runner-up 4270.11)
Shortest path (3 hops):
  main.go --contains [EXTRACTED]--> main() --calls [INFERRED]--> NewWithToken() --references [EXTRACTED]--> Client
```

Traces the gateway's startup path from `cmd/marketsage-mcp/main.go` into
`internal/coreclient/client.go`'s constructor. Note the AMBIGUOUS-adjacent warning: `client.go`
matched two candidate nodes at nearly identical scores, so multi-word or path-qualified queries
are safer than a bare filename when several files share a name.

**3. `graphify affected "models.py" --depth 2`** — blast radius of the shared Pydantic contract
models:

```
Affected nodes for models.py
- routes.py [imports_from] services/analytics-python/src/marketsage_api/routes.py:L1
- briefs.py [imports_from] services/analytics-python/src/marketsage_core/briefs.py:L1
- contracts.py [imports_from] services/analytics-python/src/marketsage_core/contracts.py:L1
- datasets.py, openbb_adapter.py, retrieval.py, sentiment.py, storage.py [imports_from] (marketsage_core)
- api_eval.py, sentiment_eval.py, retrieval_eval.py [imports_from] (marketsage_eval)
- test_retrieval.py, test_contracts.py [imports_from] (tests)
- app.py [imports_from] services/analytics-python/src/marketsage_api/app.py:L1
```

14 dependents two hops out — every route, core module, eval script and test that imports the
shared response models. This is the list to hand a Verifier when `models.py` changes.

**What the graph got wrong:** `graphify path` found no route between a Next.js file
(`page.tsx`/`analyst-workbench.tsx`) and the Python `routes.py` it calls over HTTP
(`No path found`). The graph is built from static AST edges (imports, calls, references) within
and across files graphify can parse structurally; it does not trace `fetch()` calls or HTTP
routing across the TypeScript-to-Python process boundary. For that boundary, read
`apps/web/app/api/marketsage/[...path]/route.ts` (the proxy) and
`services/analytics-python/src/marketsage_api/routes.py` directly — the graph tells you *what
exists*, not *what calls it over the network*.

## Numbers

- 1199 nodes, 2180 edges, 90 communities (81 shown, 9 thin omitted)
- 89 files, ~36,000 words in the corpus
- Extraction: 77% EXTRACTED, 23% INFERRED, 0% AMBIGUOUS (INFERRED edges average confidence 0.5)
- Build time: a few seconds, offline, no API key

## What `.graphifyignore` excludes

`node_modules/`, `.venv/`, `.next/`, `dist/`, `bin/`, the generated `graphify-out/` directory
itself, the committed FinanceBench/FiQA data corpus under `data/fixtures/` (data, not code),
generated contract fixtures under `packages/contracts/fixtures/`, lockfiles
(`package-lock.json`, `services/analytics-python/uv.lock`), and the pytest/ruff caches.

Only `graphify-out/GRAPH_REPORT.md` is committed; `graph.json`, `graph.html`, `cache/` and
`manifest.json` are gitignored (1-2 MB, rebuilt in seconds, would churn every commit).

## Hooks (local opt-in, not committed)

`graphify install --project` can add `.claude/settings.json` PreToolUse hooks that intercept
Read/Grep and nudge toward `graphify query` first. Those hooks are a local, per-developer opt-in
and are **not** committed to this repo — the graph itself and the agent-facing skill
(`.claude/skills/graphify/`) are.

## Shipyard integration

Implementers query the graph before opening files for a task pack; Verifiers run `graphify
affected` on every symbol a diff touches and flag anything outside the pack's declared scope.
