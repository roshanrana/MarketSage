import { spawn, spawnSync, type ChildProcess } from "node:child_process";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "../../..");
const analyticsDir = join(repoRoot, "services", "analytics-python");
const gatewayDir = join(repoRoot, "services", "mcp-gateway-go");
const analyticsURL = process.env.MARKETSAGE_ANALYTICS_URL ?? "http://127.0.0.1:8765";

type CliOptions = {
  startAnalytics: boolean;
};

function parseArgs(argv: string[]): CliOptions {
  return {
    startAnalytics: argv.includes("--start-analytics")
  };
}

function envWith(overrides: Record<string, string>): Record<string, string> {
  const env: Record<string, string> = {};
  for (const [key, value] of Object.entries(process.env)) {
    if (value !== undefined) {
      env[key] = value;
    }
  }
  return { ...env, ...overrides };
}

function startAnalytics(): ChildProcess {
  const url = new URL(analyticsURL);
  const child = spawn(
    "uv",
    [
      "run",
      "--project",
      analyticsDir,
      "uvicorn",
      "marketsage_api.app:create_app",
      "--factory",
      "--host",
      url.hostname,
      "--port",
      url.port || "8765"
    ],
    {
      cwd: repoRoot,
      env: envWith({
        MARKETSAGE_MODE: process.env.MARKETSAGE_MODE ?? "seeded",
        MARKETSAGE_DATA_DIR: process.env.MARKETSAGE_DATA_DIR ?? join(repoRoot, "data", "local")
      }),
      stdio: ["ignore", "pipe", "pipe"]
    }
  );

  child.stdout.on("data", (chunk) => process.stderr.write(`[analytics] ${chunk}`));
  child.stderr.on("data", (chunk) => process.stderr.write(`[analytics] ${chunk}`));
  return child;
}

async function waitForAnalytics(timeoutMs = 20_000): Promise<void> {
  const started = Date.now();
  let lastError = "";

  while (Date.now() - started < timeoutMs) {
    try {
      const response = await fetch(`${analyticsURL}/health`);
      if (response.ok) {
        return;
      }
      lastError = `status ${response.status}`;
    } catch (error) {
      lastError = error instanceof Error ? error.message : String(error);
    }
    await new Promise((resolveWait) => setTimeout(resolveWait, 250));
  }

  throw new Error(`analytics core did not become ready: ${lastError}`);
}

function stopProcessTree(child: ChildProcess): void {
  if (process.platform === "win32" && child.pid) {
    spawnSync("taskkill", ["/pid", String(child.pid), "/T", "/F"], { stdio: "ignore" });
    return;
  }
  child.kill("SIGTERM");
}

function renderToolResult(result: unknown): string {
  const value = result as {
    structuredContent?: unknown;
    content?: Array<{ type?: string; text?: string }>;
  };

  if (value.structuredContent) {
    return JSON.stringify(value.structuredContent, null, 2);
  }

  const text = value.content
    ?.filter((item) => item.type === "text" && typeof item.text === "string")
    .map((item) => item.text)
    .join("\n");
  if (text) {
    return text;
  }

  return JSON.stringify(result, null, 2);
}

function structuredPayload(result: unknown): Record<string, unknown> | undefined {
  const value = result as { structuredContent?: unknown };
  if (value.structuredContent && typeof value.structuredContent === "object") {
    return value.structuredContent as Record<string, unknown>;
  }
  return undefined;
}

async function main(): Promise<void> {
  const options = parseArgs(process.argv.slice(2));
  let analyticsProcess: ChildProcess | undefined;

  try {
    if (options.startAnalytics) {
      analyticsProcess = startAnalytics();
      await waitForAnalytics();
    }

    const client = new Client({
      name: "marketsage-mcp-cli",
      version: "0.1.0"
    });
    const transport = new StdioClientTransport({
      command: "go",
      args: ["run", "./cmd/marketsage-mcp"],
      cwd: gatewayDir,
      env: envWith({ MARKETSAGE_ANALYTICS_URL: analyticsURL })
    });

    await client.connect(transport);
    const tools = await client.listTools();
    console.log(`MarketSage MCP tools (${tools.tools.length})`);
    for (const tool of tools.tools) {
      console.log(`- ${tool.name}: ${tool.description ?? ""}`);
    }

    const result = await client.callTool({ name: "health_check", arguments: {} });
    console.log("\nhealth_check");
    console.log(renderToolResult(result));

    const datasets = await client.callTool({ name: "dataset_status", arguments: {} });
    console.log("\ndataset_status");
    console.log(renderToolResult(datasets));

    const snapshot = await client.callTool({
      name: "market_snapshot",
      arguments: { ticker: "AAPL", provider_mode: "seeded" }
    });
    console.log("\nmarket_snapshot AAPL");
    console.log(renderToolResult(snapshot));

    const sentiment = await client.callTool({
      name: "sentiment_score_text",
      arguments: {
        ticker: "MSFT",
        text: "Revenue growth was strong, but margin pressure remains.",
        model_preference: "auto"
      }
    });
    console.log("\nsentiment_score_text");
    console.log(renderToolResult(sentiment));

    const evidence = await client.callTool({
      name: "evidence_search",
      arguments: { query: "Apple services revenue margin", ticker: "AAPL", top_k: 3 }
    });
    console.log("\nevidence_search");
    console.log(renderToolResult(evidence));

    const brief = await client.callTool({
      name: "research_brief",
      arguments: { tickers: ["AAPL"], horizon: "1w", provider_mode: "seeded" }
    });
    console.log("\nresearch_brief");
    console.log(renderToolResult(brief));

    const briefPayload = structuredPayload(brief);
    const briefData = briefPayload?.data as { run_id?: string } | undefined;
    if (briefData?.run_id) {
      const resource = await client.readResource({
        uri: `marketsage://runs/${briefData.run_id}`
      });
      console.log("\nresource marketsage://runs/{run_id}");
      console.log(JSON.stringify(resource.contents, null, 2));
    }

    await client.close();

    console.log("\nM2 demo complete. Next milestone is the analyst workbench.");
  } finally {
    if (analyticsProcess) {
      stopProcessTree(analyticsProcess);
    }
  }
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`marketsage mcp demo failed: ${message}`);
  process.exit(1);
});
