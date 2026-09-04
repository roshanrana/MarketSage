# MarketSage — Showcase

The feature tour, with commands and files. [OVERVIEW.md](OVERVIEW.md) has the reasoning; [demo-script.md](demo-script.md) is the five-minute version.

## Ten minutes

```bash
npm install
npm run check      # docs, Python, Go, TypeScript, MCP smoke, Next.js build, in one gate
npm run demo:mcp   # watch a client discover and drive the tools
```

`npm run demo:mcp` runs `clients/mcp-cli/src/index.ts`: it starts the Python core, launches the Go gateway over stdio, lists the seven tools, calls the market, sentiment, evidence and brief tools in sequence, and reads the saved run back through `marketsage://runs/{run_id}`. Everything it prints is what an LLM host would see.

## Twenty minutes, with the workbench

```bash
npm run dev:analytics
npm run dev --workspace apps/web     # http://localhost:3000
```

Enter a ticker, choose `hybrid` mode, and click `Run Brief`. Without OpenBB installed, the snapshot carries a warning that live data was unavailable and seeded data was used. That warning is the design working.

## Feature tour

### 1. The MCP gateway (`services/mcp-gateway-go/`)

| Look at | What it shows |
|---|---|
| `cmd/marketsage-mcp/main.go` | A stdio MCP server; logging to stderr only, because stdout is the protocol |
| `internal/server/server.go` | Seven tools and one resource template, each with a schema; `server_test.go` |
| `internal/coreclient/client.go` | The HTTP client to the analytics core, forwarding the bearer token when configured; `client_test.go` |

**Why it matters:** the gateway is deliberately thin. It owns transport discipline and nothing else, so the analytics core can be used by the web app, a CLI and an MCP client without knowing which one is calling.

### 2. The analytics core (`services/analytics-python/src/marketsage_core/`)

| Look at | What it shows |
|---|---|
| `openbb_adapter.py` | The OpenBB-ready market boundary; seeded, hybrid and live modes with explicit warnings on fallback |
| `datasets.py` | The Hugging Face dataset manifest and status reporting |
| `sentiment.py` | Deterministic sentiment by default; FinBERT behind `MARKETSAGE_ENABLE_MODEL_DOWNLOADS` |
| `retrieval.py` | Lexical evidence search over the seeded corpus |
| `briefs.py` | Research-brief orchestration: snapshot, trend, evidence, sentiment, caveats, saved run |
| `storage.py`, `repo.py` | DuckDB persistence for manifests, runs and audit events |
| `config.py` | Every mode and switch, from environment |

`services/analytics-python/src/marketsage_api/routes.py` is the HTTP surface the gateway and the web proxy both call.

### 3. The client (`clients/mcp-cli/src/index.ts`)

A TypeScript MCP client using the official SDK. Read it to see the full lifecycle a host performs: process start, capability discovery, tool calls with typed arguments, resource read.

### 4. The workbench (`apps/web/`)

| Look at | What it shows |
|---|---|
| `app/_components/analyst-workbench.tsx` | Ticker input, mode selection, snapshot, price trend, evidence list, brief, dataset table, warnings and caveats |
| `app/api/marketsage/[...path]/route.ts` | A server-side proxy so the browser never holds the API token |

Verified on desktop and mobile viewports; two rendering defects found and fixed before ship.

### 5. Contracts (`packages/contracts/marketsage.schema.json`)

The shared payload schema across Go, Python and TypeScript.

### 6. Security and provenance (`docs/security-and-ops.md`, `docs/research/source-notes.md`, `docs/third-party-notices.md`)

Optional bearer auth; no stdout logging in stdio mode; `npm audit`, `uv pip check` and `govulncheck` run before release; a secret scan; a reviewed dataset and model list with two exclusions on licence grounds; a full third-party notice.

### 7. The gate (`package.json`, `npm run check`)

Docs, `ruff`, `pytest`, `go fmt`/`test`/`vet`, the MCP CLI smoke, the Next.js build, a workspace check. Four languages, one command, and the protocol boundary is exercised rather than mocked.

## Things worth noticing

- **The fallback warns.** Hybrid mode never silently substitutes seeded data for live; the warning is in the payload, so a downstream model or analyst cannot miss it.
- **The saved run is a resource.** A brief is reproducible because its inputs, evidence and caveats are stored and addressable.
- **Licences were reviewed before release, and two assets were excluded.** That is more diligence than most demos bother with, and it is the diligence a regulated buyer asks about first.
- **stdout is sacred.** A single stray print would corrupt the MCP stream; the gateway's logging discipline is a test.

## Questions this project answers, and where

| Question | Where the answer lives |
|---|---|
| How do you expose an existing workflow to an LLM without a chat box? | `internal/server/server.go`: typed tools and a resource, discovered by the client |
| How does an analyst know whether the number is live? | `openbb_adapter.py` modes and the warning in the payload |
| How do you reproduce a brief a model produced last week? | `marketsage://runs/{run_id}` and DuckDB in `storage.py` |
| Why Go for the gateway? | Transport discipline over stdio; `docs/design/decisions.md` |
| What did you check before making this public? | `docs/security-and-ops.md`, `docs/third-party-notices.md`, `docs/research/source-notes.md` |
