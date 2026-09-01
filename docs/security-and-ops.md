# Security And Operations

Last updated: 2026-09-01

## Runtime Posture

MarketSage is a local research demo by default. It does not execute trades, move money, or provide investment advice.

The analytics core exposes HTTP endpoints for the web workbench and the Go MCP gateway. Set `MARKETSAGE_HTTP_TOKEN` to require bearer auth on every HTTP request:

```powershell
$env:MARKETSAGE_HTTP_TOKEN="local-demo-token"
npm run dev:analytics
```

Clients pass the same token with:

```http
Authorization: Bearer local-demo-token
```

The Next.js proxy and Go MCP gateway both forward `MARKETSAGE_HTTP_TOKEN` server-side when it is configured. The token is never returned by `/health`; the public health contract only exposes `http_auth_required`.

## Audit Events

Successful analytics responses write a DuckDB row in `audit_event` with:

- `request_id`
- `tool_name`
- `status`
- `duration_ms`
- `mode`
- `warning_count`
- `detail`
- `created_at`

Known market data and saved-run failures also write `status = 'error'` rows. Audit persistence is best effort so a local DuckDB issue does not mask API behavior; `/health` still reports DuckDB availability.

Example local inspection:

```powershell
uv run --project services/analytics-python python -c "import duckdb; conn = duckdb.connect('data/local/marketsage.duckdb'); print(conn.execute('select request_id, tool_name, status, duration_ms, mode, warning_count from audit_event order by created_at desc limit 5').fetchall())"
```

## Stdio Discipline

The MCP server runs over stdio. JSON-RPC uses stdout, so ordinary logs must never write there. `services/mcp-gateway-go/cmd/marketsage-mcp/main.go` uses `slog.NewJSONHandler(os.Stderr, ...)` and the MCP SDK `StdioTransport`.

## Validation Evidence

Primary local gate:

```powershell
npm run check
```

Latest result on 2026-09-01: passed.

- Docs guard: passed.
- Python lint/tests: 15 passed.
- Go fmt/test/vet: passed.
- TypeScript MCP smoke: passed.
- Next.js production build: passed.
- Browser verification: desktop and mobile workbench flows completed with no dev overlay or mobile horizontal overflow.

Security and dependency sweep:

```powershell
npm audit --workspaces --audit-level=high
uv pip check --project services/analytics-python
cd services/mcp-gateway-go; go run golang.org/x/vuln/cmd/govulncheck@latest ./...
rg -n "(api[_-]?key|secret|token|password|BEGIN PRIVATE KEY|HF_TOKEN|OPENBB_API_KEY)" -g !node_modules -g !.venv -g !uv.lock -g !package-lock.json .
```

Latest result on 2026-09-01:

- `npm audit`: 0 vulnerabilities.
- `uv pip check`: all installed packages compatible.
- `govulncheck`: code affected by 0 vulnerabilities; one required-module vulnerability was not called.
- Secret text scan: only docs, placeholders, source identifiers, and test tokens were found.

## Residual Risks

- Live OpenBB mode depends on optional dependencies and provider availability.
- FinBERT and embedding retrieval are opt-in because model downloads can be slow or gated.
- Transcript-scale datasets are blocked until license review.
- The local bearer token is suitable for demo/prototype protection, not a substitute for production identity, network policy, or managed secrets.
