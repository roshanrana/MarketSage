# Demo Script

Use this path for a 5 minute portfolio walkthrough.

## 1. Validate The Repo

```powershell
npm install
npm run check
```

Say: "This is a multi-service MCP product with one local gate covering docs, Python, Go, TypeScript, the MCP smoke path, and the Next.js build."

## 2. Show MCP Discovery And Tool Calls

```powershell
npm run demo:mcp
```

Point out:

- The TypeScript client starts the Python analytics core.
- The Go MCP server runs over stdio.
- The client lists tools, calls market/sentiment/evidence/brief workflows, and reads `marketsage://runs/{run_id}`.

## 3. Show The Analyst Workbench

Terminal 1:

```powershell
npm run dev:analytics
```

Terminal 2:

```powershell
npm run dev --workspace apps/web
```

Open `http://localhost:3000`, click `Run Brief`, and point out:

- Source-aware market snapshot.
- Evidence snippets with dataset/license metadata.
- Generated research brief.
- Warnings and caveats visible in the workflow.

## 4. Show Enterprise Controls

```powershell
$env:MARKETSAGE_HTTP_TOKEN="local-demo-token"
npm run dev:analytics
```

Say: "Protected mode requires bearer auth. The web proxy and Go gateway forward the token server-side; secrets are not exposed in the health payload."

## 5. Show Auditability

```powershell
uv run --project services/analytics-python python -c "import duckdb; conn = duckdb.connect('data/local/marketsage.duckdb'); print(conn.execute('select request_id, tool_name, status, duration_ms, mode, warning_count from audit_event order by created_at desc limit 5').fetchall())"
```

Say: "Every successful analytics response writes request id, tool/source, status, duration, mode, and warning count. Known data failures write error rows."
