import { readFile, readdir } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = new URL("..", import.meta.url);
const rootPath = fileURLToPath(root);
const required = [
  "STATE.md",
  "docs/design/01-requirements.md",
  "docs/design/02-hld.md",
  "docs/design/03-lld.md",
  "docs/design/04-execution-plan.md",
  "docs/design/decisions.md"
];

const forbidden = /\b(TODO|TBD|FIXME|INSERT_|YOUR_|lorem ipsum)\b/i;

async function walk(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (["node_modules", ".venv", ".git", "data"].includes(entry.name)) continue;
      files.push(...await walk(path));
    } else {
      files.push(path);
    }
  }
  return files;
}

for (const file of required) {
  await readFile(new URL(file, root), "utf8");
}

for (const file of await walk(rootPath)) {
  if (!file.endsWith(".md")) continue;
  const text = await readFile(file, "utf8");
  const match = text.match(forbidden);
  if (match) {
    throw new Error(`Forbidden placeholder marker "${match[0]}" found in ${file}`);
  }
}

console.log("docs: ok");
