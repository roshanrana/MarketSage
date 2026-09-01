import { spawnSync } from "node:child_process";

const checks = [
  ["docs", "node", ["scripts/check-docs.mjs"]],
  ["python lint", "uv", ["run", "--project", "services/analytics-python", "ruff", "check", "."]],
  ["python test", "uv", ["run", "--project", "services/analytics-python", "pytest"]],
  ["go fmt", "node", ["scripts/check-go-format.mjs"]],
  ["go test", "go", ["test", "./..."], { cwd: "services/mcp-gateway-go" }],
  ["go vet", "go", ["vet", "./..."], { cwd: "services/mcp-gateway-go" }],
  ["typescript", "npm", ["run", "check", "--workspace", "clients/mcp-cli", "--if-present"]],
  ["web", "npm", ["run", "check", "--workspace", "apps/web", "--if-present"]]
];

let failed = false;

function quoteWindows(value) {
  if (/^[A-Za-z0-9_./:-]+$/.test(value)) {
    return value;
  }
  return `"${value.replaceAll('"', '\\"')}"`;
}

function run(command, args, options = {}) {
  if (process.platform !== "win32") {
    return spawnSync(command, args, { stdio: "inherit", ...options });
  }

  const shellLine = [command, ...args].map(quoteWindows).join(" ");
  return spawnSync(process.env.ComSpec ?? "cmd.exe", ["/d", "/s", "/c", shellLine], {
    stdio: "inherit",
    ...options
  });
}

for (const [label, cmd, args, options] of checks) {
  console.log(`\n== ${label} ==`);
  const result = run(cmd, args, options);
  if (result.status !== 0) {
    failed = true;
    if (result.error) {
      console.error(result.error.message);
    }
    console.error(`check failed: ${label}`);
    break;
  }
}

if (failed) {
  process.exit(1);
}

console.log("\nworkspace: ok");
