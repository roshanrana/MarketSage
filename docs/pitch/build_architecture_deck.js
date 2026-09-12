const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625
pres.author = "Roshan Rana";
pres.title = "MarketSage — AI Systems Architecture Review";

// Palette
const NAVY = "14213D", INK = "1B2A41", WHITE = "FFFFFF", ICE = "DCE7F5", MINT = "2EC4B6",
  GOLD = "F2B134", MUTED = "6B7A90", CARD = "F3F6FA", LINE = "C9D3E0", CARD_D = "1C2B4F", RED = "D64550";
const HF = "Cambria", BF = "Calibri";
const ASSETS = "C:/Code-Central/MarketSage/docs/assets/";

let n = 0;
function base(title, kicker) {
  const s = pres.addSlide();
  n += 1;
  s.background = { color: WHITE };
  if (kicker) s.addText(kicker.toUpperCase(), { x: 0.5, y: 0.28, w: 6, h: 0.25, fontFace: BF, fontSize: 10, bold: true, color: MINT, charSpacing: 2, isTextBox: true, margin: 0 });
  s.addText(title, { x: 0.5, y: 0.5, w: 9, h: 0.6, fontFace: HF, fontSize: 26, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  s.addText(`MarketSage · AI Systems Architecture Review · ${n}`, { x: 0.5, y: 5.25, w: 9, h: 0.25, fontFace: BF, fontSize: 8, color: MUTED, isTextBox: true, margin: 0 });
  return s;
}
function dark(title, sub) {
  const s = pres.addSlide();
  n += 1;
  s.background = { color: NAVY };
  s.addText(title, { x: 0.6, y: 1.9, w: 8.8, h: 0.9, fontFace: HF, fontSize: 34, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  if (sub) s.addText(sub, { x: 0.6, y: 2.85, w: 8.8, h: 0.6, fontFace: BF, fontSize: 15, italic: true, color: ICE, isTextBox: true, margin: 0 });
  return s;
}
function card(s, x, y, w, h, fill = CARD, line = LINE) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: line, width: 0.75 }, rectRadius: 0.06 });
}
function box(s, x, y, w, h, title, body, opt = {}) {
  const fill = opt.fill || CARD, tcol = opt.tcol || NAVY, bcol = opt.bcol || INK, line = opt.line || LINE;
  card(s, x, y, w, h, fill, line);
  s.addText(title, { x: x + 0.1, y: y + 0.06, w: w - 0.2, h: 0.28, fontFace: BF, fontSize: opt.ts || 11, bold: true, color: tcol, isTextBox: true, margin: 0 });
  if (body) s.addText(body, { x: x + 0.1, y: y + 0.34, w: w - 0.2, h: h - 0.4, fontFace: BF, fontSize: opt.bs || 8.5, color: bcol, isTextBox: true, margin: 0, valign: "top" });
}
function arrow(s, x1, y1, x2, y2, color = MUTED, w = 1.25) {
  const flipH = x2 < x1, flipV = y2 < y1;
  s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.01, h: Math.abs(y2 - y1) || 0.01, line: { color, width: w, endArrowType: "triangle" }, flipH, flipV });
}
function bullets(s, items, x, y, w, h, fs = 11, color = INK) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })), { x, y, w, h, fontFace: BF, fontSize: fs, color, isTextBox: true, margin: 0, paraSpaceAfter: 4, valign: "top" });
}
function table(s, rows, x, y, w, colW, fs = 8.5, rowH) {
  const data = rows.map((r, i) => r.map((c) => ({ text: c, options: i === 0 ? { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: fs } : { fontSize: fs, color: INK } })));
  s.addTable(data, { x, y, w, colW, fontFace: BF, border: { type: "solid", pt: 0.5, color: LINE }, autoPage: false, rowH });
}
function imgFit(s, path, x, y, maxW, maxH, pw, ph) {
  const r = Math.min(maxW / pw, maxH / ph);
  const w = pw * r, h = ph * r;
  s.addImage({ path, x: x + (maxW - w) / 2, y, w, h });
  return { w, h };
}
function caption(s, text, x, y, w) {
  s.addText(text, { x, y, w, h: 0.3, fontFace: BF, fontSize: 9, italic: true, color: MUTED, isTextBox: true, margin: 0 });
}

// ---------- 1 Title
{
  const s = pres.addSlide(); n += 1; s.background = { color: NAVY };
  s.addText("MarketSage", { x: 0.6, y: 1.35, w: 8.4, h: 0.9, fontFace: HF, fontSize: 44, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  s.addText("AI Systems Architecture Review", { x: 0.6, y: 2.2, w: 8, h: 0.5, fontFace: BF, fontSize: 22, color: ICE, isTextBox: true, margin: 0 });
  s.addText("An MCP-native market intelligence workbench: typed finance tools, saved and auditable runs, sources that never hide what they are", { x: 0.6, y: 2.75, w: 8.6, h: 0.6, fontFace: BF, fontSize: 13, italic: true, color: ICE, isTextBox: true, margin: 0 });
  s.addText("Release/ship date · 12 September 2026 · Roshan Rana", { x: 0.6, y: 4.6, w: 8.8, h: 0.3, fontFace: BF, fontSize: 10, color: MUTED, isTextBox: true, margin: 0 });
  s.addShape(pres.shapes.OVAL, { x: 8.2, y: 1.2, w: 1.1, h: 1.1, fill: { color: MINT }, line: { color: MINT } });
  s.addText("M", { x: 8.2, y: 1.2, w: 1.1, h: 1.1, fontFace: HF, fontSize: 40, bold: true, color: NAVY, align: "center", valign: "middle", isTextBox: true, margin: 0 });
}

// ---------- 2 Executive summary
{
  const s = base("Executive summary", "Overview");
  const cols = [
    ["What it is", ["A Go MCP gateway exposes seven finance tools and a saved-run resource over stdio, backed by a Python FastAPI analytics core: market data, sentiment, evidence search and research briefs.", "A Next.js analyst workbench gives the same capabilities to reviewers who never touch an MCP client; DuckDB persists every dataset, run and audit event."]],
    ["What it proves", ["Three data modes and warnings that cannot be suppressed: seeded is deterministic and credential-free, hybrid falls back with a payload warning, live fails clearly without OpenBB.", "Every research-brief bullet carries a reference to the snapshot, evidence id or sentiment hash behind it — 12 / 12 grounded on the committed fixtures."]],
    ["Why it is enterprise-ready", ["Built through 13 task packs (T-001…T-013) with frozen requirements, HLD, LLD and an execution plan; one gate (`npm run check`) covers four languages plus an offline evaluation with drift checks.", "A separate dependency and vulnerability sweep (`npm run audit:deps`); CI runs the same gate on every push."]],
  ];
  cols.forEach((c, i) => {
    const x = 0.5 + i * 3.05;
    card(s, x, 1.3, 2.9, 3.25);
    s.addText(c[0], { x: x + 0.15, y: 1.4, w: 2.6, h: 0.35, fontFace: HF, fontSize: 15, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    bullets(s, c[1], x + 0.15, 1.85, 2.6, 2.6, 11);
  });
  s.addText("Ask of the audience: agree the pilot scope (filing evidence for the other three seeded tickers, embedding retrieval, a recorded FinBERT run, a live OpenBB provider) and the identity model that would sit in front of bearer auth.", { x: 0.5, y: 4.7, w: 9, h: 0.45, fontFace: BF, fontSize: 10.5, italic: true, color: INK, isTextBox: true, margin: 0 });
}

// ---------- 3 Problem and users
{
  const s = base("The problem and the users", "Context");
  box(s, 0.5, 1.3, 4.3, 1.75, "The analyst's problem", "A snapshot, a price trend, what the filings and the sentiment say, then a brief — a mature workflow, spread across a quote screen, a filings reader and a spreadsheet. A chat box bolted onto the same data gives a model no structure to call, no record of what it looked at, and no way to tell live data from illustrative seed data.", { bs: 10 });
  box(s, 5.2, 1.3, 4.3, 1.75, "The constraints", "MarketSage does not execute trades, move money or provide investment advice. Every tool response must say which data mode produced it, cite the evidence behind each claim, and leave an audit row an operator can replay.", { bs: 10 });
  table(s, [
    ["Actor", "Needs", "Where it is met"],
    ["Analyst (primary)", "Ticker in, brief out: snapshot, evidence, sentiment, caveats, in one workbench or one MCP call", "Next.js workbench; `research_brief` tool"],
    ["Compliance / reviewer", "An audit row per call: request id, tool, status, duration, mode, warning count", "DuckDB `audit_event`; `docs/security-and-ops.md`"],
    ["Platform team", "One local gate, no keys for the default path, optional bearer auth", "`npm run check`; `MARKETSAGE_HTTP_TOKEN`"],
    ["AI assistant / MCP host", "Typed tools and a resource it can discover, not a chat window", "7 tools, 4 prompts, 1 resource template"],
  ], 0.5, 3.25, 9.0, [1.9, 4.3, 2.8], 9);
}

// ---------- 4 Solution at a glance
{
  const s = base("Solution at a glance", "Approach");
  const steps = [
    ["1", "Ticker in", "health_check and dataset_status confirm DuckDB, the market adapter and the Hugging Face manifest are ready, in seeded mode by default."],
    ["2", "Market + evidence", "market_snapshot / price_history (seeded, hybrid or live) and evidence_search: BM25 over the committed FinanceBench filing corpus, ticker-scoped."],
    ["3", "Sentiment", "sentiment_score_text: a deterministic lexicon fallback by default, FinBERT opt-in behind an explicit environment flag."],
    ["4", "Research brief", "research_brief assembles sections whose every bullet carries a reference; the run is saved to DuckDB and readable back as `marketsage://runs/{run_id}`."],
  ];
  steps.forEach((st, i) => {
    const x = 0.5 + i * 2.3;
    card(s, x, 1.35, 2.15, 2.15, CARD_D, CARD_D);
    s.addShape(pres.shapes.OVAL, { x: x + 0.15, y: 1.5, w: 0.4, h: 0.4, fill: { color: MINT }, line: { color: MINT } });
    s.addText(st[0], { x: x + 0.15, y: 1.5, w: 0.4, h: 0.4, fontFace: BF, fontSize: 14, bold: true, color: NAVY, align: "center", valign: "middle", isTextBox: true, margin: 0 });
    s.addText(st[1], { x: x + 0.65, y: 1.52, w: 1.4, h: 0.36, fontFace: BF, fontSize: 12.5, bold: true, color: WHITE, isTextBox: true, margin: 0, valign: "middle" });
    s.addText(st[2], { x: x + 0.15, y: 2.0, w: 1.85, h: 1.4, fontFace: BF, fontSize: 8.5, color: ICE, isTextBox: true, margin: 0, valign: "top" });
    if (i < 3) arrow(s, x + 2.15, 2.4, x + 2.3, 2.4, MINT, 2);
  });
  box(s, 0.5, 3.75, 4.4, 1.3, "Surfaces", "A Go MCP gateway over stdio, and a Next.js workbench proxying server-side, both call the same FastAPI analytics core; neither one computes anything itself.", { bs: 10 });
  box(s, 5.1, 3.75, 4.4, 1.3, "Two data modes, one schema", "`seeded` is deterministic and credential-free (the default). `hybrid` tries OpenBB and falls back with a warning in the payload. `live` fails clearly when the optional dependency is missing.", { bs: 10 });
}

// ---------- 5 System context (C4 L1)
{
  const s = base("System context", "Architecture · C4 level 1");
  const actors = [["Analyst", "browser"], ["AI assistant", "MCP host, stdio"], ["Automation", "MCP CLI client"]];
  actors.forEach((a, i) => { box(s, 0.5, 1.3 + i * 0.95, 1.7, 0.78, a[0], a[1], { bs: 8.5 }); arrow(s, 2.2, 1.69 + i * 0.95, 2.75, 2.85, MUTED, 1); });
  card(s, 2.8, 1.3, 3.4, 3.4, "EEF6F4", MINT);
  s.addText("MarketSage", { x: 2.95, y: 1.38, w: 3, h: 0.3, fontFace: HF, fontSize: 14, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  box(s, 2.95, 1.75, 3.1, 0.75, "Surfaces", "Go MCP gateway (stdio) · Next.js workbench (server-side proxy)", { bs: 8.5 });
  box(s, 2.95, 2.6, 3.1, 1.0, "Python analytics core", "market/sentiment/evidence/briefs · OpenBB adapter · HF dataset boundary", { bs: 8.5 });
  box(s, 2.95, 3.7, 3.1, 0.85, "DuckDB", "dataset manifest · research runs · audit events", { bs: 8.5 });
  box(s, 6.9, 1.3, 2.6, 0.75, "OpenBB (optional)", "seeded / hybrid / live market data; absent, seeded mode runs and says so", { bs: 8 });
  box(s, 6.9, 2.2, 2.6, 0.75, "Hugging Face", "FinanceBench + FiQA fixtures (build-time); FinBERT opt-in at runtime", { bs: 8 });
  box(s, 6.9, 3.1, 2.6, 0.75, "GitHub Actions", "`npm run check` on every push, ubuntu-latest", { bs: 8 });
  box(s, 6.9, 4.0, 2.6, 0.7, "MCP client (browser/host)", "reads `marketsage://runs/{run_id}` back", { bs: 8 });
  arrow(s, 6.2, 3.0, 6.9, 1.67, MUTED, 1); arrow(s, 6.2, 3.1, 6.9, 2.57, MUTED, 1); arrow(s, 6.2, 3.2, 6.9, 3.47, MUTED, 1); arrow(s, 6.2, 3.3, 6.9, 4.35, MUTED, 1);
  s.addText("Model downloads are off by default (MARKETSAGE_ENABLE_MODEL_DOWNLOADS enables FinBERT). Live OpenBB mode needs its optional dependency and provider configuration; the offline gate and CI never touch either.", { x: 0.5, y: 4.85, w: 9, h: 0.35, fontFace: BF, fontSize: 9, italic: true, color: MUTED, isTextBox: true, margin: 0 });
}

// ---------- 6 Component architecture (C4 L2)
{
  const s = base("Component architecture", "Architecture · C4 level 2");
  const groups = [
    { t: "Go gateway (stdio)", x: 0.5, items: [["main.go", "stdio transport, stderr logs"], ["server.go", "7 tools, 1 resource template"], ["prompts.go", "4 MCP prompts"], ["coreclient/", "HTTP client, token forward"]] },
    { t: "Python core", x: 2.85, items: [["openbb_adapter.py", "seeded/hybrid/live modes"], ["datasets.py", "HF manifest + status"], ["sentiment.py", "lexicon default, FinBERT opt-in"], ["retrieval.py", "BM25 over FinanceBench"], ["briefs.py", "sections + references"]] },
    { t: "Persistence + API", x: 5.2, items: [["storage.py / repo.py", "DuckDB: manifest, runs, audit"], ["routes.py", "HTTP surface, JSON envelope"], ["config.py", "modes, switches, from env"]] },
    { t: "Clients + contracts", x: 7.55, items: [["mcp-cli", "TS MCP client, `demo:mcp`"], ["apps/web", "Next.js workbench + proxy"], ["marketsage.schema.json", "generated from Pydantic"], ["Go strict decode", "unknown fields forbidden"]] },
  ];
  groups.forEach((g) => {
    card(s, g.x, 1.3, 2.15, 3.55);
    s.addText(g.t, { x: g.x + 0.1, y: 1.36, w: 2, h: 0.3, fontFace: BF, fontSize: 10.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    g.items.forEach((it, i) => {
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: g.x + 0.1, y: 1.72 + i * 0.62, w: 1.95, h: 0.54, fill: { color: WHITE }, line: { color: LINE, width: 0.75 }, rectRadius: 0.05 });
      s.addText(it[0], { x: g.x + 0.18, y: 1.75 + i * 0.62, w: 1.8, h: 0.24, fontFace: "Courier New", fontSize: 8.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
      s.addText(it[1], { x: g.x + 0.18, y: 1.97 + i * 0.62, w: 1.8, h: 0.26, fontFace: BF, fontSize: 7.5, color: INK, isTextBox: true, margin: 0 });
    });
  });
  arrow(s, 2.65, 3.1, 2.85, 3.1, MINT, 2); arrow(s, 5.0, 3.1, 5.2, 3.1, MINT, 2); arrow(s, 7.35, 3.1, 7.55, 3.1, MINT, 2);
  s.addText("One schema, generated from the Pydantic models, describes every payload; the harness validates live responses against it and exports fixtures the Go client decodes with unknown fields forbidden.", { x: 0.5, y: 4.9, w: 9, h: 0.3, fontFace: BF, fontSize: 9, italic: true, color: MUTED, isTextBox: true, margin: 0 });
}

// ---------- 7 The research-brief pipeline
{
  const s = base("The research-brief pipeline", "Architecture · critical flow");
  const stages = [
    ["Ticker in", "health_check + dataset_status confirm readiness; mode defaults to seeded"],
    ["Market", "market_snapshot / price_history: seeded, hybrid (fallback + warning) or live"],
    ["Evidence", "BM25 over the committed FinanceBench corpus, ticker-scoped; warns when a ticker has none"],
    ["Sentiment", "lexicon fallback (marketsage-lexicon-v0) or FinBERT when enabled; warns on fallback"],
    ["Assemble", "briefs.py builds sections; every bullet pairs with a `references` entry"],
    ["Persist", "DuckDB stores the run (input + output) and an audit_event row"],
    ["Expose", "`marketsage://runs/{run_id}` resource; a client reads the saved run back"],
    ["Render", "Next.js workbench shows the same brief, evidence and caveats server-side"],
  ];
  stages.forEach((st, i) => {
    const col = i % 4, row = Math.floor(i / 4);
    const x = 0.5 + col * 2.3, y = 1.4 + row * 1.7;
    card(s, x, y, 2.15, 1.35, row === 0 ? CARD : "EEF6F4", row === 0 ? LINE : MINT);
    s.addText(`${i + 1}. ${st[0]}`, { x: x + 0.1, y: y + 0.08, w: 1.95, h: 0.3, fontFace: BF, fontSize: 11, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(st[1], { x: x + 0.1, y: y + 0.4, w: 1.95, h: 0.9, fontFace: BF, fontSize: 8.5, color: INK, isTextBox: true, margin: 0, valign: "top" });
    if (col < 3) arrow(s, x + 2.15, y + 0.67, x + 2.3, y + 0.67, MUTED, 1.25);
  });
  arrow(s, 9.0, 2.75, 9.0, 3.1, MUTED, 1.25);
  s.addText("Failure is first-class, not an afterthought: nine named fault injections are scored 9 / 9 handled honestly — an explicit warning on degrade, a clean error and an audit row on failure, never invented data.", { x: 0.5, y: 4.85, w: 9, h: 0.35, fontFace: BF, fontSize: 9, italic: true, color: MUTED, isTextBox: true, margin: 0 });
}

// ---------- 8 Core mechanism: the grounded brief
{
  const s = base("The core mechanism: every bullet carries a reference", "Design · grounding");
  card(s, 0.5, 1.3, 4.6, 3.55, CARD_D, CARD_D);
  s.addText("One section of a real saved run (MSFT)", { x: 0.65, y: 1.38, w: 4.3, h: 0.3, fontFace: BF, fontSize: 11, bold: true, color: MINT, isTextBox: true, margin: 0 });
  s.addText([
    '{', '  "title": "Sentiment",', '  "bullets": [', '    "Neutral sentiment (55% confidence,',
    '     marketsage-lexicon-v0)."', '  ],', '  "references": [',
    '    "sentiment:29e7347946b40c0470c..."', '  ]', '}',
  ].join("\n"), { x: 0.65, y: 1.72, w: 4.3, h: 1.85, fontFace: "Courier New", fontSize: 8.5, color: WHITE, isTextBox: true, margin: 0, valign: "top" });
  s.addText("What the harness scores", { x: 0.65, y: 3.6, w: 4.3, h: 0.3, fontFace: BF, fontSize: 11, bold: true, color: MINT, isTextBox: true, margin: 0 });
  bullets(s, ["every bullet's reference must resolve to a snapshot, evidence id or sentiment hash in the same payload", "a ticker with no committed evidence says so instead of borrowing another company's"], 0.65, 3.9, 4.3, 0.9, 9, ICE);
  const badges = [["12 / 12", "brief claims grounded, across 5 tickers", MINT], ["8 / 8", "responses conforming to the generated JSON Schema contract", "3A7BD5"], ["9 / 9", "fault injections handled with a warning or a clean error, never invented data", GOLD]];
  badges.forEach((b, i) => {
    const y = 1.3 + i * 0.95;
    card(s, 5.4, y, 4.1, 0.8);
    s.addText(b[0], { x: 5.55, y: y + 0.06, w: 1.3, h: 0.68, fontFace: HF, fontSize: 20, bold: true, color: NAVY, isTextBox: true, margin: 0, valign: "middle" });
    s.addText(b[1], { x: 6.9, y: y + 0.06, w: 2.5, h: 0.68, fontFace: BF, fontSize: 9, color: INK, isTextBox: true, margin: 0, valign: "middle" });
  });
  box(s, 5.4, 4.15, 4.1, 0.7, "Why this matters to a reviewer", "The reference list is the control, and the eval suite reports grounding as a headline KPI, not a claim about prose quality.", { bs: 8.5 });
}

// ---------- 9 Data architecture
{
  const s = base("Data architecture: fixtures, runs, audit", "Architecture · data");
  box(s, 0.5, 1.3, 2.9, 1.9, "Committed fixtures (MIT)", "FinanceBenchRetrieval: corpus/test 145 rows, queries/test 150, qrels/test 150. fiqa-sentiment-classification default/test 234 rows. sha256-pinned in data/fixtures/manifest.json; 32 companies mapped by ticker.", { bs: 9 });
  box(s, 0.5, 3.35, 2.9, 1.5, "Coverage is explicit", "Only 2 of 5 seeded tickers (MSFT, JPM) have filing excerpts in the corpus; the other 3 get a stated coverage warning instead of borrowed evidence.", { bs: 9 });
  arrow(s, 3.4, 2.2, 4.1, 2.6, MINT, 2); arrow(s, 3.4, 4.0, 4.1, 3.2, MINT, 2);
  card(s, 4.1, 2.2, 2.2, 1.9, "EEF6F4", MINT);
  s.addText("DuckDB, three tables", { x: 4.2, y: 2.28, w: 2, h: 0.3, fontFace: BF, fontSize: 10.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  s.addText("dataset manifest\nresearch runs\naudit_event", { x: 4.2, y: 2.62, w: 2, h: 1.35, fontFace: "Courier New", fontSize: 10, color: INK, isTextBox: true, margin: 0 });
  arrow(s, 6.3, 3.05, 6.95, 3.05, MINT, 2);
  box(s, 6.95, 1.3, 2.55, 3.55, "Every write is addressable", "• `marketsage://runs/{run_id}` reads a saved run's exact input and output\n• `audit_event`: request id, tool, status, duration, mode, warning count\n• audit persistence is best-effort so a local DuckDB issue never masks API behaviour\n• `/health` still reports DuckDB availability on its own", { bs: 9 });
  s.addText("Seeded market data (5 illustrative tickers) is not scored by the eval harness; only the retrieval and sentiment fixtures are.", { x: 0.5, y: 4.95, w: 9, h: 0.3, fontFace: BF, fontSize: 9, italic: true, color: MUTED, isTextBox: true, margin: 0 });
}

// ---------- 10 Integration and live-mode design
{
  const s = base("Data modes and warnings that cannot be suppressed", "Architecture · live mode");
  const modes = [
    ["seeded (default)", "Deterministic local data from data/seed/. No credentials, no network. What every screenshot in this deck shows."],
    ["hybrid", "Tries OpenBB live data; on failure, falls back to seeded data with an explicit warning in the response payload — never a silent substitution."],
    ["live", "Requires the optional OpenBB dependency and provider configuration; fails clearly, with a stated reason, when either is missing."],
  ];
  modes.forEach((m, i) => {
    const x = 0.5 + i * 3.05;
    box(s, x, 1.3, 2.9, 1.7, m[0], m[1], { bs: 9, fill: i === 0 ? "EEF6F4" : CARD, line: i === 0 ? MINT : LINE });
  });
  box(s, 0.5, 3.2, 4.4, 1.65, "Model downloads: off by default", "Deterministic sentiment fallback runs with no download. `MARKETSAGE_ENABLE_MODEL_DOWNLOADS=true` enables FinBERT. The offline eval harness and CI never trigger a download; FinBERT accuracy is unmeasured here and marked pending.", { bs: 9 });
  box(s, 5.1, 3.2, 4.4, 1.65, "Protected local mode", "`MARKETSAGE_HTTP_TOKEN` requires bearer auth on every analytics HTTP request. The Go gateway and the Next.js proxy both forward the same token server-side; `/health` reports only `http_auth_required`, never the token.", { bs: 9 });
}

// ---------- 11 Design choices
{
  const s = base("Design choices and why", "Design decisions");
  table(s, [
    ["Decision", "Alternatives considered", "Why this one"],
    ["Go gateway + Python core + TS clients (ADR-002)", "Python-only MCP server; wrap OpenBB's own MCP server directly; TypeScript-only server", "Go's stdio transport discipline plus Python's OpenBB/HF ecosystem fit; a Go spike in M0 proved the boundary before deeper build"],
    ["DuckDB for local persistence (ADR-003)", "SQLite; PostgreSQL", "Strong local analytics/parquet fit, no database server for a reviewer to stand up; schemas kept portable enough for Postgres later"],
    ["AGPL-3.0-only licensing (ADR-004)", "MIT with OpenBB isolated behind an external service; delay the licensing decision", "OpenBB states AGPLv3; this is the safe compatibility default while OpenBB is a direct dependency"],
    ["Seeded data first, live second (ADR-005)", "Live-first integration", "A reviewer gets a working demo with no credentials or rate limits; live OpenBB mode layers on afterward"],
    ["Lexical BM25 retrieval, no vector database", "Embeddings with bge-small/MiniLM + a vector store", "Deterministic in CI, ticker-scoped and explainable today; embedding retrieval is one function to add, and is listed pending"],
    ["Deterministic sentiment fallback as the default", "FinBERT as the default classifier", "No model download needed for the demo or CI; the fallback's weak 8.1% commit rate is scored and shown, not hidden"],
  ], 0.5, 1.3, 9.0, [2.7, 2.9, 3.4], 8.5);
}

// ---------- 12 Major features
{
  const s = base("Major features", "Product");
  const feats = [
    ["Seven MCP tools, one resource", "health_check, dataset_status, market_snapshot, price_history, sentiment_score_text, evidence_search, research_brief; marketsage://runs/{run_id}"],
    ["Four MCP prompts", "equity_research, portfolio_risk_scan, earnings_call_questions, source_quality_review; read from marketsage-mcp --describe"],
    ["Analyst workbench (Next.js)", "ticker + evidence-query inputs, mode selector, snapshot, price chart, evidence list, brief, dataset/caveat log"],
    ["Offline evaluation harness", "BM25 recall, sentiment-fallback scoring, brief grounding, contract conformance, 9 fault injections, audit completeness, latency budget"],
    ["DuckDB audit trail", "request id, tool, status, duration, mode and warning count on every analytics call"],
    ["Dependency and vulnerability sweeps", "npm audit, uv pip check, govulncheck and a secret-text scan, in `npm run audit:deps`"],
  ];
  feats.forEach((f, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    box(s, 0.5 + col * 3.05, 1.3 + row * 1.55, 2.9, 1.4, f[0], f[1], { bs: 8.5 });
  });
}

// ---------- 13 Screenshot: workbench snapshot + evidence
{
  const s = base("The analyst workbench: snapshot, trend and evidence", "Screenshots · seeded mode, no keys");
  imgFit(s, ASSETS + "10-workbench-snapshot.png", 0.5, 1.25, 9.0, 3.65, 1440, 965);
  caption(s, "Seeded mode, no credentials. MSFT snapshot with a one-quarter close series and two FinanceBench filing excerpts scored by BM25, each captioned with its dataset and licence.", 0.5, 4.95, 9);
}

// ---------- 14 Screenshot: saved research brief
{
  const s = base("The saved run: every section keeps its references", "Screenshots · seeded mode, saved run");
  imgFit(s, ASSETS + "11-workbench-brief.png", 0.5, 1.25, 9.0, 3.65, 1440, 1020);
  caption(s, "The same run, readable back through marketsage://runs/{run_id}: a run id badge, referenced sections, and the dataset/caveat log.", 0.5, 4.95, 9);
}

// ---------- 15 Screenshot: MCP tool call
{
  const s = base("Driving the gateway: tool discovery and a live call", "Screenshots · MCP CLI (npm run demo:mcp)");
  imgFit(s, ASSETS + "12-mcp-tool-call.png", 0.5, 1.15, 9.0, 3.85, 980, 760);
  caption(s, "The TypeScript MCP client discovers all seven tools, calls market_snapshot and evidence_search, and reads the saved run back as a resource — exactly what an LLM host would see.", 0.5, 5.03, 9);
}

// ---------- 16 Screenshot: audit trail
{
  const s = base("Every call leaves a row", "Screenshots · DuckDB audit_event");
  imgFit(s, ASSETS + "13-audit-trail.png", 0.7, 1.35, 8.6, 3.0, 1180, 460);
  box(s, 0.5, 4.45, 9.0, 0.75, "What you are looking at", "The eight most recent audit_event rows from this session's own demo run and workbench call: request id, tool/source, status, duration, mode and warning count — 0 orphans.", { bs: 9 });
}

// ---------- 17 Security and compliance
{
  const s = base("Security and compliance controls", "Enterprise readiness · controls");
  table(s, [
    ["Boundary", "Threat", "Control in the code", "Evidence"],
    ["B1 client input", "malformed ticker, oversized text", "Pydantic validators: ticker matches ^[A-Z][A-Z0-9.-]{0,9}$; sentiment text bounded 1-4000 chars", "models.py TickerRequest/SentimentRequest"],
    ["B2 analytics HTTP API", "unauthenticated access", "optional bearer auth (MARKETSAGE_HTTP_TOKEN); Go gateway and Next.js proxy forward it server-side; never returned by /health", "security-and-ops.md"],
    ["B3 MCP stdio transport", "stdout corruption breaks JSON-RPC", "slog.NewJSONHandler(os.Stderr, ...) only; StdioTransport from the MCP SDK", "main.go; T-011 acceptance criteria"],
    ["B4 analytics responses", "unaudited or silent failures", "DuckDB audit_event row per call; best-effort so a local DB issue never masks API behaviour; known failures write status=error rows", "storage.py, repo.py"],
    ["B5 dependencies and secrets", "known CVEs, leaked keys", "npm audit (0 high+), uv pip check, govulncheck, and a secret-text regex scan, run in npm run audit:deps", "ship-report.md, 2026-09-07"],
    ["B6 data and model licensing", "unlicensed reuse", "source-notes.md review; sp500-earnings-transcripts blocked pending license, sec-bert-base excluded (CC-BY-SA-4.0)", "docs/research/source-notes.md"],
  ], 0.5, 1.25, 9.0, [1.35, 1.8, 3.85, 2.0], 8);
  s.addText("Residual risk, stated plainly: the local bearer token is a demo/prototype control, not production identity management, network policy or managed secrets (docs/security-and-ops.md).", { x: 0.5, y: 4.75, w: 9, h: 0.4, fontFace: BF, fontSize: 9, italic: true, color: MUTED, isTextBox: true, margin: 0 });
}

// ---------- 18 Enterprise readiness: process
{
  const s = base("How it was built: a gated lifecycle, one validation gate", "Enterprise readiness · process");
  const gates = ["Requirements", "HLD", "LLD", "Execution plan", "Decisions (5 ADRs)", "13 task packs", "Build (M0-M5)", "Ship report"];
  gates.forEach((g, i) => {
    const x = 0.5 + i * 1.11;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.35, w: 1.03, h: 0.62, fill: { color: i < 5 ? CARD_D : "1E5C57" }, line: { color: i < 5 ? CARD_D : "1E5C57" }, rectRadius: 0.05 });
    s.addText(g, { x: x + 0.04, y: 1.37, w: 0.95, h: 0.58, fontFace: BF, fontSize: 7.5, bold: true, color: WHITE, align: "center", valign: "middle", isTextBox: true, margin: 0 });
  });
  const stats = [["13", "task packs, T-001 through T-013, each with acceptance criteria, milestone and risk tier"], ["5", "architecture decision records, each with context, options considered and consequences"], ["45", "Python tests passed (pytest), including nine named fault injections and the contract checks"], ["11", "Go tests passed, including strict decoding of the exported contract fixtures"]];
  stats.forEach((st, i) => {
    const x = 0.5 + i * 2.3;
    card(s, x, 2.2, 2.15, 1.25);
    s.addText(st[0], { x: x + 0.12, y: 2.25, w: 1.9, h: 0.5, fontFace: HF, fontSize: 28, bold: true, color: GOLD, isTextBox: true, margin: 0 });
    s.addText(st[1], { x: x + 0.12, y: 2.75, w: 1.9, h: 0.65, fontFace: BF, fontSize: 8.5, color: INK, isTextBox: true, margin: 0, valign: "top" });
  });
  box(s, 0.5, 3.65, 4.4, 1.25, "Documents that stay frozen", "docs/design/01-requirements.md, 02-hld.md, 03-lld.md and 04-execution-plan.md are cited, not re-derived, once a task pack is in flight; docs/design/decisions.md records every ADR with its consequence.", { bs: 9 });
  box(s, 5.1, 3.65, 4.4, 1.25, "One command validates everything", "docs, ruff, pytest, go fmt/test/vet, an MCP CLI smoke, the Next.js build, a workspace check, and an offline eval with drift checks on the results card and the generated contract. CI (.github/workflows/check.yml) runs the same command on ubuntu-latest on every push.", { bs: 9 });
}

// ---------- 19 Quality metrics (native chart)
{
  const s = base("Quality metrics from the eval harness", "Enterprise readiness · measurement");
  s.addChart(pres.charts.BAR, [{ name: "Recall@k", labels: ["BM25, ticker @1", "BM25, ticker @5", "BM25, ticker @10", "BM25, no hint @1", "BM25, no hint @5", "BM25, no hint @10", "Term overlap @1", "Term overlap @5", "Term overlap @10"], values: [47.3, 94.7, 100.0, 20.7, 44.0, 60.7, 12.0, 26.7, 38.0] }], {
    x: 0.5, y: 1.25, w: 5.3, h: 3.65, barDir: "bar", chartColors: [MINT], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", dataLabelFontSize: 7.5, dataLabelColor: INK,
    catAxisLabelColor: INK, catAxisLabelFontSize: 7.5, valAxisLabelColor: MUTED, valAxisLabelFontSize: 8, valAxisMinVal: 0, valAxisMaxVal: 110, valGridLine: { color: LINE, size: 0.5 }, catGridLine: { style: "none" }, showLegend: false, showTitle: true, title: "FinanceBench recall %, by scorer and hint (150 queries)", titleFontSize: 9.5, titleColor: NAVY,
  });
  table(s, [
    ["KPI", "Value", "Note"],
    ["Evidence recall@5, ticker given", "94.7%", "no hint: 44.0%, nDCG@10 0.38"],
    ["Sentiment fallback commit rate", "8.1%", "19/234 FiQA; 89.5% right when it fires"],
    ["Brief claims grounded", "12 / 12", "5 tickers; 3 say so, not borrowed"],
    ["Contract conformance", "8 / 8", "vs. the generated JSON Schema"],
    ["Fault injections handled honestly", "9 / 9", "warning or clean error only"],
    ["Audit completeness", "8 / 8", "0 orphaned rows"],
    ["Latency budget, 8 endpoints", "8 / 8 < 2s p95", "5 runs; p95 63-252ms"],
  ], 5.9, 1.25, 3.6, [1.55, 0.85, 1.2], 7.5);
  s.addText("Every figure is written by `npm run eval` to metrics/headline.json; `npm run check` fails if the README card or the generated contract drifts from it.", { x: 0.5, y: 4.95, w: 9, h: 0.3, fontFace: BF, fontSize: 9, italic: true, color: MUTED, isTextBox: true, margin: 0 });
}

// ---------- 20 Quirks and limitations
{
  const s = base("Quirks and known limitations (stated, not hidden)", "Honesty");
  const q = [
    ["Evidence coverage is 2 of 5 tickers", "Only MSFT and JPM have filing excerpts in the committed corpus; the other three seeded tickers get an explicit warning, never borrowed evidence."],
    ["Recall collapses without the ticker hint", "94.7% recall@5 becomes 44.0% (MRR 0.33, nDCG@10 0.38) without it; the structured hint is doing the heavy lifting, and the card says so."],
    ["The sentiment fallback is weak by design", "marketsage-lexicon-v0 commits on 8.1% of FiQA test sentences (19/234); it exists so the demo runs with no download, not as a classifier."],
    ["FinBERT accuracy is unmeasured here", "Needs MARKETSAGE_ENABLE_MODEL_DOWNLOADS=true and a model download; the offline harness scores the lexicon fallback only."],
    ["Embedding retrieval is not implemented", "The bge-small / MiniLM path is pending; lexical BM25 is the only scorer in the eval today."],
    ["Live OpenBB data is not scored", "Seeded prices are illustrative; live mode needs the optional dependency and provider configuration, and is out of the offline gate by design."],
    ["`go fmt` flags every Go file on this Windows host", "A CRLF checkout artifact, not a real formatting diff (gofmt -d shows only line-ending changes); CI on ubuntu-latest is green."],
    ["Bearer auth is a demo control", "MARKETSAGE_HTTP_TOKEN is local prototype protection, not production identity, network policy or managed secrets."],
  ];
  q.forEach((it, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    box(s, 0.5 + col * 4.6, 1.3 + row * 0.9, 4.45, 0.82, it[0], it[1], { bs: 7.8, ts: 9.5 });
  });
}

// ---------- 21 Cost and performance
{
  const s = base("Cost, performance and operability", "Enterprise readiness · operations");
  const cards = [["0 keys", "needed for seeded mode, the demo, or the offline eval harness"], ["8 / 8", "endpoints under the 2s p95 latency budget, in-process over 5 runs"], ["56", "tests passed at ship (45 pytest + 11 Go), plus the eval harness and CI"], ["0", "high-severity findings: npm audit, uv pip check, govulncheck all clean"]];
  cards.forEach((c, i) => {
    const x = 0.5 + i * 2.3;
    card(s, x, 1.3, 2.15, 1.35);
    s.addText(c[0], { x: x + 0.12, y: 1.35, w: 1.9, h: 0.5, fontFace: HF, fontSize: 26, bold: true, color: GOLD, isTextBox: true, margin: 0 });
    s.addText(c[1], { x: x + 0.12, y: 1.87, w: 1.9, h: 0.75, fontFace: BF, fontSize: 8.5, color: INK, isTextBox: true, margin: 0, valign: "top" });
  });
  box(s, 0.5, 2.85, 4.4, 2.0, "Operability", "• demo-script.md: a five-minute walkthrough, check → demo:mcp → workbench → protected mode → eval → audit query\n• SHOWCASE.md: a ten- and twenty-minute tour with commands and files\n• Health endpoint reports duckdb/openbb/huggingface dependency status independently\n• Protected mode is one environment variable away (MARKETSAGE_HTTP_TOKEN)", { bs: 9 });
  box(s, 5.1, 2.85, 4.4, 2.0, "Observability and audit", "• DuckDB audit_event: request id, tool, status, duration, mode, warning count, per call\n• Best-effort audit writes so a local DB issue never masks API behaviour\n• Every payload carries its own warnings array; nothing is silently substituted\n• The saved-run resource makes every brief reproducible after the fact", { bs: 9 });
}

// ---------- 22 Roadmap
{
  const s = base("Roadmap to a pilot", "Next steps");
  const phases = [["Now", "Close the accuracy gap", ["Record a FinBERT run with model downloads enabled; publish it as a recorded, not re-observed, figure", "Add embedding retrieval behind the same scorer switch, scored on the same fixture"]], ["Next", "Widen evidence coverage", ["Filing excerpts for the three seeded tickers that currently get a coverage warning", "Live OpenBB provider configuration and credentials for a real pilot ticker set"]], ["Then", "Harden for a pilot", ["An identity layer in front of MARKETSAGE_HTTP_TOKEN", "A tamper-evident audit sink, and a runbook for the on-call path"]], ["Later", "Scale", ["Full ticker universe instead of five seeded illustrative names", "Batch briefs and a dashboard over audit and warning rates"]]];
  phases.forEach((p, i) => {
    const x = 0.5 + i * 2.3;
    card(s, x, 1.3, 2.15, 3.5, i === 0 ? "EEF6F4" : CARD, i === 0 ? MINT : LINE);
    s.addText(p[0], { x: x + 0.12, y: 1.36, w: 1.9, h: 0.28, fontFace: BF, fontSize: 9, bold: true, color: MINT, charSpacing: 1, isTextBox: true, margin: 0 });
    s.addText(p[1], { x: x + 0.12, y: 1.62, w: 1.9, h: 0.35, fontFace: HF, fontSize: 14, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    bullets(s, p[2], x + 0.12, 2.05, 1.9, 2.7, 9);
  });
  s.addText("The first two items are the project's own stated next steps (STATE.md); nothing below changes the contracts, the audit row, or the grounding check.", { x: 0.5, y: 4.95, w: 9, h: 0.3, fontFace: BF, fontSize: 9, italic: true, color: MUTED, isTextBox: true, margin: 0 });
}

// ---------- 23 Appendix: decision log
{
  const s = base("Appendix A — Decision log", "Appendix");
  table(s, [
    ["ID", "Decision", "Consequence"],
    ["ADR-001", "Use the full enterprise-dev-lifecycle track", "Requirements, HLD, LLD, execution plan, task packs and a ship report before code merges"],
    ["ADR-002", "Go MCP gateway, Python analytics core, TypeScript clients", "Transport discipline in Go, OpenBB/HF fit in Python; a Go spike in M0 validated the boundary first"],
    ["ADR-003", "DuckDB for local analytics and cache state", "No database server for a reviewer; schemas kept portable enough for Postgres later"],
    ["ADR-004", "Default to OpenBB-compatible (AGPL-3.0-only) licensing", "Avoids muddled licensing for a public repository while OpenBB is a direct dependency"],
    ["ADR-005", "Seeded data first, live data second", "The full MCP/client workflow proven early; live OpenBB integration layered on without blocking the demo"],
  ], 0.5, 1.3, 9.0, [1.1, 3.6, 4.3], 8.5);
}

// ---------- 24 Appendix: process stats and lessons
{
  const s = base("Appendix B — Task packs and lessons", "Appendix");
  table(s, [
    ["Task", "Milestone", "Status"],
    ["T-001 Repository guardrails and validation skeleton", "M0", "done"],
    ["T-002 … T-004  Python core, Go gateway, TS client skeletons", "M0-M1", "done"],
    ["T-005 … T-009  OpenBB adapter, HF manifest, sentiment, evidence, briefs", "M1-M2", "done"],
    ["T-010 Next.js analyst workbench", "M3", "done"],
    ["T-011 Hardening, observability and security", "M4", "done"],
    ["T-012 Portfolio docs and public license", "M5", "done"],
    ["T-013 Offline evaluation harness, real evidence corpus, contracts, MCP prompts", "M5", "done"],
  ], 0.5, 1.3, 9.0, [5.2, 1.7, 2.1], 8.5);
  box(s, 0.5, 3.85, 9.0, 1.15, "Lessons recorded in STATE.md and the T-013 task pack", "• Phases 0-3 planning artifacts were drafted in one pass at the user's request; the hard gate before application code stayed in force regardless.\n• \"Not done, on purpose\": FinBERT and embedding numbers need downloads the offline gate forbids; they belong in a recorded run under a bench/ path, not asserted here.\n• Six hand-written evidence rows that carried a FinanceBench label without coming from it were removed once the real corpus was committed.", { bs: 8.5 });
}

// ---------- 25 Appendix: repository map
{
  const s = base("Appendix C — Repository map and how to run", "Appendix");
  s.addText(["apps/web/            Next.js workbench + server-side API proxy", "clients/mcp-cli/     TypeScript MCP client (`npm run demo:mcp`)", "services/", "  mcp-gateway-go/    Go stdio MCP server: 7 tools, 4 prompts, 1 resource", "  analytics-python/  FastAPI core: market, sentiment, evidence, briefs,", "                     OpenBB adapter, HF datasets, DuckDB storage, eval", "packages/contracts/  marketsage.schema.json, generated from Pydantic", "data/fixtures/       FinanceBench + FiQA, MIT, sha256-pinned manifest", "metrics/             headline.json, eval-latest.json, render.py", "docs/design/         requirements, HLD, LLD, execution plan, decisions", "docs/tasks/          13 task packs, T-001 … T-013", "docs/graph/          codebase knowledge graph (graphify): 1199 nodes,", "                     2180 edges, 90 communities"].join("\n"), { x: 0.5, y: 1.3, w: 5.6, h: 3.3, fontFace: "Courier New", fontSize: 7.8, color: INK, isTextBox: true, margin: 0, valign: "top" });
  card(s, 6.3, 1.3, 3.2, 3.55, CARD_D, CARD_D);
  s.addText("Run it", { x: 6.45, y: 1.38, w: 3, h: 0.3, fontFace: BF, fontSize: 11, bold: true, color: MINT, isTextBox: true, margin: 0 });
  s.addText(["npm install", "npm run check        # the gate", "npm run demo:mcp     # MCP client, all 7 tools", "npm run eval         # the results-card harness", "", "# the workbench, two terminals", "npm run dev:analytics", "npm run dev --workspace apps/web", "", "# protected mode", "$env:MARKETSAGE_HTTP_TOKEN=\"<key>\"", "npm run dev:analytics"].join("\n"), { x: 6.45, y: 1.72, w: 3, h: 3.05, fontFace: "Courier New", fontSize: 8.5, color: WHITE, isTextBox: true, margin: 0, valign: "top" });
}

// ---------- 26 Close
{
  const s = dark("Questions", "MarketSage · roshanrana/MarketSage · AGPL-3.0-only · design docs, ship report and demo script in the repository");
}

pres.writeFile({ fileName: "C:/Code-Central/MarketSage/docs/pitch/marketsage-architecture-deck.pptx" }).then((f) => console.log("wrote", f, "slides", n));
