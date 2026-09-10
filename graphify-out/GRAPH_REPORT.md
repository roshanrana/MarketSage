# Graph Report - MarketSage  (2026-09-10)

## Corpus Check
- 89 files · ~36,069 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1199 nodes · 2180 edges · 90 communities (81 shown, 9 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 496 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `544e7f5e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 87|Community 87]]

## God Nodes (most connected - your core abstractions)
1. `Settings` - 58 edges
2. `MarketDataError` - 37 edges
3. `TickerRequest` - 35 edges
4. `ResearchBriefRequest` - 35 edges
5. `Client` - 35 edges
6. `MarketSnapshotData` - 32 edges
7. `ResearchBriefData` - 32 edges
8. `EvidenceSearchRequest` - 31 edges
9. `SentimentRequest` - 30 edges
10. `SentimentData` - 28 edges

## Surprising Connections (you probably didn't know these)
- `FastAPI` --uses--> `Settings`  [INFERRED]
  services/analytics-python/src/marketsage_api/app.py → services/analytics-python/src/marketsage_core/config.py
- `ResearchBriefRequest` --uses--> `EvidenceSnippet`  [INFERRED]
  services/analytics-python/src/marketsage_core/briefs.py → services/analytics-python/src/marketsage_core/models.py
- `Settings` --uses--> `EvidenceSnippet`  [INFERRED]
  services/analytics-python/src/marketsage_core/briefs.py → services/analytics-python/src/marketsage_core/models.py
- `ResearchBriefData` --uses--> `EvidenceSnippet`  [INFERRED]
  services/analytics-python/src/marketsage_core/briefs.py → services/analytics-python/src/marketsage_core/models.py
- `MarketSnapshotData` --uses--> `EvidenceSnippet`  [INFERRED]
  services/analytics-python/src/marketsage_core/briefs.py → services/analytics-python/src/marketsage_core/models.py

## Import Cycles
- 1-file cycle: `services/analytics-python/src/marketsage_api/app.py -> services/analytics-python/src/marketsage_api/app.py`
- 2-file cycle: `services/analytics-python/src/marketsage_api/app.py -> services/analytics-python/src/marketsage_api/routes.py -> services/analytics-python/src/marketsage_api/app.py`

## Communities (90 total, 9 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.14
Nodes (80): BaseModel, BriefSection, HealthData, _brief_query(), build_research_brief(), _caveats_section(), _evidence_section(), _market_section() (+72 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (48): CallToolRequest, CallToolResult, ClientSession, getenv(), main(), PromptArgument, ReadResourceRequest, ReadResourceResult (+40 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (48): EvidenceSnippet, repo_root(), _bm25(), corpus_size(), corpus_tickers(), Document, Index, _overlap() (+40 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (34): BriefSection, Client, New(), NewWithToken(), TestBearerTokenIsForwarded(), TestHealthDecodesEnvelope(), TestMarketSnapshotPostsTicker(), TestNewRejectsInvalidURL() (+26 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (33): FastAPI, create_app(), FastAPI surface for the MarketSage analytics core., score_text(), _score_with_finbert(), _score_with_lexicon(), _ece(), _macro_f1() (+25 more)

### Community 5 - "Community 5"
Cohesion: 0.11
Nodes (32): build_schema(), committed_schema(), envelope_schema(), export_schema(), The MarketSage response contracts as one JSON Schema document.  ``packages/con, Objects reject unknown keys, so both languages must agree on every field., A self-contained schema for one endpoint, usable with any validator., render_schema() (+24 more)

### Community 6 - "Community 6"
Cohesion: 0.05
Nodes (37): $ref, title, type, DependencyStatus, HealthData, items, title, type (+29 more)

### Community 7 - "Community 7"
Cohesion: 0.11
Nodes (21): fakeAnalytics, TestHealthCheckMapsAnalyticsEnvelope(), TestMarketSnapshotMapsAnalyticsEnvelope(), TestNewRegistersServer(), TestResearchRunResourceReturnsJSON(), Context, DatasetStatusData, EvidenceSearchData (+13 more)

### Community 8 - "Community 8"
Cohesion: 0.20
Nodes (24): datasets(), _duration_ms(), _envelope(), evidence_search_route(), health(), market_snapshot_route(), price_history_route(), _record_failure() (+16 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (26): ADR-001: Use Full Lifecycle Track, ADR-002: Use Go MCP Gateway, Python Analytics Core, And TypeScript Clients, ADR-003: Use DuckDB For Local Analytics And Cache State, ADR-004: Default To OpenBB-Compatible Licensing, ADR-005: Use Seeded Data First, Live Data Second, Consequences, Consequences, Consequences (+18 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (26): description, devDependencies, engines, node, license, name, private, scripts (+18 more)

### Community 11 - "Community 11"
Cohesion: 0.17
Nodes (22): _audit_store_unwritable(), _client(), _env(), _error_rows(), _evidence_for_uncovered_ticker(), _fail_openbb(), _invalid_ticker_rejected(), _live_unavailable_hybrid_mode() (+14 more)

### Community 12 - "Community 12"
Cohesion: 0.09
Nodes (13): AnalystWorkbench(), DatasetEntry, DatasetStatusData, DependencyStatus, Envelope, EvidenceSearchData, EvidenceSnippet, HealthData (+5 more)

### Community 13 - "Community 13"
Cohesion: 0.10
Nodes (19): dependencies, lucide-react, next, react, react-dom, devDependencies, @types/node, @types/react (+11 more)

### Community 14 - "Community 14"
Cohesion: 0.10
Nodes (19): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+11 more)

### Community 15 - "Community 15"
Cohesion: 0.11
Nodes (18): title, type, format, title, type, PriceObservation, additionalProperties, properties (+10 more)

### Community 16 - "Community 16"
Cohesion: 0.12
Nodes (16): Architecture Options, Component Model, Context, Critical Flows, Cross-Cutting Concerns, Data Architecture, Flow 1: Ticker Snapshot, Flow 2: Sentiment Scan (+8 more)

### Community 17 - "Community 17"
Cohesion: 0.12
Nodes (16): Common Response Envelope, Config Matrix, Contracts, Data Schemas, DuckDB Tables, Error Taxonomy, Frozen Interfaces, Low-Level Design (+8 more)

### Community 18 - "Community 18"
Cohesion: 0.12
Nodes (16): title, type, title, type, title, type, properties, title (+8 more)

### Community 19 - "Community 19"
Cohesion: 0.12
Nodes (16): title, type, title, type, properties, title, type, dataset_id (+8 more)

### Community 20 - "Community 20"
Cohesion: 0.12
Nodes (16): properties, title, type, title, type, license, local_status, role (+8 more)

### Community 21 - "Community 21"
Cohesion: 0.12
Nodes (15): dependencies, @modelcontextprotocol/sdk, devDependencies, tsx, @types/node, typescript, license, name (+7 more)

### Community 22 - "Community 22"
Cohesion: 0.13
Nodes (14): description, endpoints, DatasetStatusEnvelope, EvidenceSearchEnvelope, HealthEnvelope, MarketSnapshotEnvelope, PriceHistoryEnvelope, ResearchBriefEnvelope (+6 more)

### Community 23 - "Community 23"
Cohesion: 0.14
Nodes (14): title, type, items, title, type, properties, interval, observations (+6 more)

### Community 24 - "Community 24"
Cohesion: 0.14
Nodes (13): Acceptance, Assumptions, Constraints, Functional Requirements, Integrations And Data, Non-Functional Requirements, Out Of Scope, Portfolio Delivery Signals (+5 more)

### Community 25 - "Community 25"
Cohesion: 0.14
Nodes (13): Approval Gate, Definition Of Done, Definition Of Ready, Dependency Graph, Execution Plan, Implementation Stack Signals, Milestones, Model Routing Summary (+5 more)

### Community 26 - "Community 26"
Cohesion: 0.23
Nodes (13): analyticsDir, CliOptions, __dirname, envWith(), gatewayDir, main(), parseArgs(), renderToolResult() (+5 more)

### Community 27 - "Community 27"
Cohesion: 0.15
Nodes (13): additionalProperties, description, properties, required, title, type, title, type (+5 more)

### Community 28 - "Community 28"
Cohesion: 0.15
Nodes (13): title, type, items, title, type, additionalProperties, properties, required (+5 more)

### Community 29 - "Community 29"
Cohesion: 0.15
Nodes (13): items, title, type, $ref, items, title, type, evidence (+5 more)

### Community 30 - "Community 30"
Cohesion: 0.15
Nodes (13): properties, query, retrieval_mode, scorer, title, type, enum, title (+5 more)

### Community 31 - "Community 31"
Cohesion: 0.15
Nodes (13): title, type, horizon, run_id, sections, sentiment, properties, title (+5 more)

### Community 32 - "Community 32"
Cohesion: 0.17
Nodes (12): items, items, type, references, tickers, items, title, type (+4 more)

### Community 33 - "Community 33"
Cohesion: 0.18
Nodes (10): compilerOptions, esModuleInterop, forceConsistentCasingInFileNames, module, moduleResolution, noEmit, skipLibCheck, strict (+2 more)

### Community 34 - "Community 34"
Cohesion: 0.31
Nodes (10): clip(), load(), main(), md_cell(), Path, Render metrics/headline.json into a results card.  Outputs:   docs/assets/met, render_markdown(), render_svg() (+2 more)

### Community 35 - "Community 35"
Cohesion: 0.20
Nodes (10): properties, title, type, title, type, title, type, data_dir (+2 more)

### Community 36 - "Community 36"
Cohesion: 0.22
Nodes (9): additionalProperties, properties, required, type, DatasetStatusEnvelope, format, title, type (+1 more)

### Community 37 - "Community 37"
Cohesion: 0.22
Nodes (9): MarketSnapshotEnvelope, additionalProperties, properties, required, type, enum, title, type (+1 more)

### Community 38 - "Community 38"
Cohesion: 0.39
Nodes (7): build(), Assemble and validate metrics/headline.json from the evaluation results., render(), validate(), write(), Any, Path

### Community 39 - "Community 39"
Cohesion: 0.22
Nodes (9): Architecture, At a glance, Data and model modes, Documentation, License, MarketSage, Protected local mode, Quick start (+1 more)

### Community 40 - "Community 40"
Cohesion: 0.22
Nodes (8): Acceptance Criteria, Definition Of Done, Definition Of Ready, Handoff Notes, Implementation Notes, Objective, T-001: Repository Guardrails, Validation

### Community 41 - "Community 41"
Cohesion: 0.22
Nodes (8): Acceptance Criteria, Definition Of Done, Definition Of Ready, Handoff Notes, Implementation Notes, Objective, T-002: Python Analytics Core Skeleton, Validation

### Community 42 - "Community 42"
Cohesion: 0.22
Nodes (8): Acceptance Criteria, Definition Of Done, Definition Of Ready, Handoff Notes, Implementation Notes, Objective, T-003: Go MCP Gateway Skeleton, Validation

### Community 43 - "Community 43"
Cohesion: 0.22
Nodes (8): Acceptance Criteria, Definition Of Done, Definition Of Ready, Handoff Notes, Implementation Notes, Objective, T-004: TypeScript MCP Client Smoke Demo, Validation

### Community 44 - "Community 44"
Cohesion: 0.22
Nodes (8): Acceptance Criteria, Definition Of Done, Definition Of Ready, Handoff Notes, Implementation Notes, Objective, T-005: OpenBB Adapter, Validation

### Community 45 - "Community 45"
Cohesion: 0.22
Nodes (8): Acceptance Criteria, Definition Of Done, Definition Of Ready, Handoff Notes, Implementation Notes, Objective, T-006: Hugging Face Dataset Manifest And Seeded Ingest, Validation

### Community 46 - "Community 46"
Cohesion: 0.22
Nodes (8): Acceptance Criteria, Definition Of Done, Definition Of Ready, Handoff Notes, Implementation Notes, Objective, T-007: Sentiment Pipeline, Validation

### Community 47 - "Community 47"
Cohesion: 0.22
Nodes (8): Acceptance Criteria, Definition Of Done, Definition Of Ready, Handoff Notes, Implementation Notes, Objective, T-008: Evidence Retrieval, Validation

### Community 48 - "Community 48"
Cohesion: 0.22
Nodes (8): Acceptance Criteria, Definition Of Done, Definition Of Ready, Handoff Notes, Implementation Notes, Objective, T-009: Research Brief Orchestration, Validation

### Community 49 - "Community 49"
Cohesion: 0.22
Nodes (8): Acceptance Criteria, Definition Of Done, Definition Of Ready, Handoff Notes, Implementation Notes, Objective, T-010: Next.js Analyst Workbench, Validation

### Community 50 - "Community 50"
Cohesion: 0.22
Nodes (8): Acceptance Criteria, Definition Of Done, Definition Of Ready, Handoff Notes, Implementation Notes, Objective, T-011: Hardening, Observability, And Security, Validation

### Community 51 - "Community 51"
Cohesion: 0.22
Nodes (8): Acceptance Criteria, Definition Of Done, Definition Of Ready, Handoff Notes, Implementation Notes, Objective, T-012: Portfolio Ship, Validation

### Community 52 - "Community 52"
Cohesion: 0.25
Nodes (8): title, type, HealthEnvelope, additionalProperties, properties, required, type, caveats

### Community 53 - "Community 53"
Cohesion: 0.25
Nodes (8): EvidenceSearchEnvelope, additionalProperties, properties, required, type, request_id, title, type

### Community 54 - "Community 54"
Cohesion: 0.25
Nodes (8): PriceHistoryEnvelope, additionalProperties, properties, required, type, source, title, type

### Community 55 - "Community 55"
Cohesion: 0.25
Nodes (8): 1. The MCP gateway (`services/mcp-gateway-go/`), 2. The analytics core (`services/analytics-python/src/marketsage_core/`), 3. The client (`clients/mcp-cli/src/index.ts`), 4. The workbench (`apps/web/`), 5. Contracts (`packages/contracts/marketsage.schema.json`), 6. Security and provenance (`docs/security-and-ops.md`, `docs/research/source-notes.md`, `docs/third-party-notices.md`), 7. The gate (`package.json`, `npm run check`), Feature tour

### Community 56 - "Community 56"
Cohesion: 0.25
Nodes (7): Blockers, Decisions, Deviations, Next, Now, State, Task Log

### Community 57 - "Community 57"
Cohesion: 0.29
Nodes (7): additionalProperties, required, title, type, $defs, ConfigSummary, ResearchBriefEnvelope

### Community 58 - "Community 58"
Cohesion: 0.29
Nodes (7): 1. Validate The Repo, 2. Show MCP Discovery And Tool Calls, 3. Show The Analyst Workbench, 4. Show Enterprise Controls, 5. Show The Numbers, 6. Show Auditability, Demo Script

### Community 59 - "Community 59"
Cohesion: 0.29
Nodes (6): Audit Events, Residual Risks, Runtime Posture, Security And Operations, Stdio Discipline, Validation Evidence

### Community 60 - "Community 60"
Cohesion: 0.29
Nodes (6): Built Scope, Known Limitations, Reviewer Story, Ship Report, Source And License Notes, Validation Evidence

### Community 61 - "Community 61"
Cohesion: 0.29
Nodes (6): Hugging Face Datasets, Hugging Face Models, Implementation Signals, MCP, OpenBB, Source Notes

### Community 62 - "Community 62"
Cohesion: 0.33
Nodes (6): $ref, data, warnings, properties, title, type

### Community 63 - "Community 63"
Cohesion: 0.33
Nodes (6): Honest limits, MarketSage — Overview, The design, The setting, What is measured, Where it sits among the other projects

### Community 64 - "Community 64"
Cohesion: 0.33
Nodes (5): Core Libraries, Data Provenance Rules, Hugging Face Assets, Publishing Recommendation, Third-Party Notices

### Community 65 - "Community 65"
Cohesion: 0.33
Nodes (5): Acceptance, Goal, Not done, on purpose, Scope, T-013: Offline Evaluation Harness

### Community 66 - "Community 66"
Cohesion: 0.40
Nodes (5): additionalProperties, required, title, type, DatasetEntry

### Community 67 - "Community 67"
Cohesion: 0.40
Nodes (5): EvidenceSearchData, additionalProperties, required, title, type

### Community 68 - "Community 68"
Cohesion: 0.40
Nodes (5): EvidenceSnippet, additionalProperties, required, title, type

### Community 69 - "Community 69"
Cohesion: 0.40
Nodes (5): MarketSnapshotData, additionalProperties, required, title, type

### Community 70 - "Community 70"
Cohesion: 0.40
Nodes (5): PriceHistoryData, additionalProperties, required, title, type

### Community 71 - "Community 71"
Cohesion: 0.40
Nodes (5): ResearchBriefData, additionalProperties, required, title, type

### Community 72 - "Community 72"
Cohesion: 0.40
Nodes (5): source_url, anyOf, default, title, type

### Community 73 - "Community 73"
Cohesion: 0.40
Nodes (5): MarketSage — Showcase, Questions this project answers, and where, Ten minutes, Things worth noticing, Twenty minutes, with the workbench

### Community 74 - "Community 74"
Cohesion: 0.60
Nodes (4): GET(), POST(), proxy(), RouteContext

### Community 75 - "Community 75"
Cohesion: 0.40
Nodes (3): required, root, rootPath

### Community 76 - "Community 76"
Cohesion: 0.50
Nodes (4): format, title, type, as_of

### Community 77 - "Community 77"
Cohesion: 0.83
Nodes (3): decodeStrict(), TestContractFixturesDecodeWithoutUnknownFields(), T

## Knowledge Gaps
- **561 isolated node(s):** `Envelope`, `DependencyStatus`, `HealthData`, `DatasetEntry`, `DatasetStatusData` (+556 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `$defs` connect `Community 57` to `Community 66`, `Community 67`, `Community 36`, `Community 68`, `Community 6`, `Community 69`, `Community 37`, `Community 70`, `Community 71`, `Community 15`, `Community 52`, `Community 53`, `Community 22`, `Community 54`, `Community 27`, `Community 28`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `properties` connect `Community 19` to `Community 68`, `Community 72`, `Community 20`, `Community 23`, `Community 27`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `properties` connect `Community 31` to `Community 32`, `Community 36`, `Community 71`, `Community 27`, `Community 29`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 56 inferred relationships involving `Settings` (e.g. with `BriefSection` and `FastAPI`) actually correct?**
  _`Settings` has 56 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `MarketDataError` (e.g. with `BriefSection` and `HealthData`) actually correct?**
  _`MarketDataError` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `TickerRequest` (e.g. with `BriefSection` and `HealthData`) actually correct?**
  _`TickerRequest` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `ResearchBriefRequest` (e.g. with `BriefSection` and `HealthData`) actually correct?**
  _`ResearchBriefRequest` has 32 INFERRED edges - model-reasoned connections that need verification._