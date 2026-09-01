import { spawnSync } from "node:child_process";

const result = spawnSync("gofmt", ["-l", "."], {
  cwd: "services/mcp-gateway-go",
  encoding: "utf8"
});

if (result.status !== 0) {
  process.stderr.write(result.stderr);
  process.exit(result.status ?? 1);
}

const changed = result.stdout.trim();
if (changed) {
  console.error(`go files need formatting:\n${changed}`);
  process.exit(1);
}

console.log("go fmt: ok");
