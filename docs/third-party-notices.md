# Third-Party Notices

Last updated: 2026-09-01

This file records the source posture for the portfolio MVP. It is not legal advice.

## Core Libraries

| Component | Role | License posture |
| --- | --- | --- |
| OpenBB Platform | Optional live market data path | OpenBB repository reviewed as AGPLv3; MarketSage is licensed as AGPL-3.0-only. |
| Hugging Face datasets/models | Finance sentiment, retrieval fixtures, optional models | Use only reviewed assets in the MVP. Gated or unclear-license assets stay out of default runs. |
| MCP Go SDK | Go MCP gateway | See upstream module metadata before public release. |
| MCP TypeScript SDK | Demo MCP client | See upstream package metadata before public release. |
| FastAPI, DuckDB, Pydantic, Ruff, Pytest | Analytics API, local persistence, validation | Standard Python ecosystem dependencies; transitive package metadata is tracked by `uv.lock`. |
| Next.js, React, lucide-react, TypeScript | Analyst workbench | Standard TypeScript frontend dependencies; transitive package metadata is tracked by `package-lock.json`. |

## Hugging Face Assets

| Asset | Use | Rows tracked | License | MVP status |
| --- | --- | ---: | --- | --- |
| `zeroshot/twitter-financial-news-sentiment` | Sentiment examples | 11,931 | MIT | Metadata-ready |
| `TheFinAI/fiqa-sentiment-classification` | Sentiment evaluation fixture | 1,173 | MIT | Metadata-ready |
| `mteb/FinanceBenchRetrieval` | Evidence retrieval fixture | 445 | MIT | Metadata-ready |
| `ProsusAI/finbert` | Optional sentiment model | n/a | Model card review required before bundled release | Opt-in download |
| `BAAI/bge-small-en-v1.5` | Optional embeddings | n/a | MIT | Planned optional enhancement |
| `sentence-transformers/all-MiniLM-L6-v2` | Optional embedding fallback | n/a | Apache-2.0 | Planned optional enhancement |
| `nlpaueb/sec-bert-base` | Optional SEC-domain experiment | n/a | CC-BY-SA-4.0 | Excluded from MVP |
| `glopardo/sp500-earnings-transcripts` | Optional transcript corpus | 20,681 | License unclear during review | Blocked pending license review |

## Data Provenance Rules

- Seeded market data is illustrative and committed only for deterministic demos.
- Live market data must be labeled with provider/source metadata and mode.
- Generated briefs must include caveats and warning counts in audit logs.
- Large or unclear-license assets must remain outside default setup and committed fixtures.

## Publishing Recommendation

MarketSage uses `AGPL-3.0-only` while OpenBB remains first-class. If you want a permissive license later, isolate OpenBB behind an optional external service boundary and confirm compatibility before changing the repository license.
