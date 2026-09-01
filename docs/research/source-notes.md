# Source Notes

Last checked: 2026-08-31

## OpenBB

- OpenBB ODP Python docs: https://docs.openbb.co/odp/python
  - Notes: ODP Python is documented as a unified API deployable across REST, Python, Jupyter, MCP, Docker, OpenBB Workspace, Excel, and other surfaces.
  - Notes: The docs list Python package support between 3.10 and 3.14; MarketSage proposes Python 3.12 for broad compatibility.
- OpenBB API docs: https://docs.openbb.co/odp/python/extensions/interface/openbb-api
  - Notes: `openbb-platform-api` converts FastAPI instances or OpenAPI JSON into OpenBB Workspace Backends and Widget definitions.
- OpenBB MCP docs: https://docs.openbb.co/odp/python/extensions/interface/openbb-mcp
  - Notes: `openbb-mcp-server` can convert a FastAPI application into a Workspace-ready MCP server and supports stdio, SSE, and streamable HTTP transports.
- OpenBB GitHub repository: https://github.com/OpenBB-finance/OpenBB
  - Notes: Repository describes ODP as infrastructure for AI copilots, research dashboards, MCP servers, REST APIs, Python, Workspace, and Excel.
  - License note: The repository currently states AGPLv3 licensing.

## MCP

- MCP architecture docs: https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture
  - Notes: MCP defines a client-server architecture with hosts, clients, and servers.
  - Notes: The data layer uses JSON-RPC 2.0 and includes tools, resources, prompts, discovery, and notifications.
  - Notes: Stdio and streamable HTTP are both documented transports.
- MCP server guide: https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server
  - Notes: MCP servers expose resources, tools, and prompts.
  - Notes: Stdio servers must not write ordinary logs to stdout because that corrupts JSON-RPC messages.
- MCP SDK docs: https://modelcontextprotocol.io/docs/2026-07-28/sdk
  - Notes: TypeScript, Python, C#, Go, and Rust SDKs are listed as Tier 1.

## Hugging Face Datasets

Dataset metadata was checked with Hugging Face Dataset Viewer API:

- `zeroshot/twitter-financial-news-sentiment`
  - Page: https://huggingface.co/datasets/zeroshot/twitter-financial-news-sentiment
  - Rows: 11,931 total; train 9,543; validation 2,388.
  - License: MIT.
  - Role: seeded sentiment demo and lightweight sentiment fixtures.
- `TheFinAI/fiqa-sentiment-classification`
  - Page: https://huggingface.co/datasets/TheFinAI/fiqa-sentiment-classification
  - Rows: 1,173 total; train 822; test 234; valid 117.
  - License: MIT.
  - Role: sentiment evaluation fixture.
- `mteb/FinanceBenchRetrieval`
  - Page: https://huggingface.co/datasets/mteb/FinanceBenchRetrieval
  - Rows: 445 total; corpus/test 145; qrels/test 150; queries/test 150.
  - License: MIT.
  - Role: evidence retrieval fixture.
- `glopardo/sp500-earnings-transcripts`
  - Page: https://huggingface.co/datasets/glopardo/sp500-earnings-transcripts
  - Rows: 20,681 total; parquet about 562 MB.
  - License: not clearly shown on the Hugging Face page during review.
  - Role: optional sampled transcript corpus after license check.

## Hugging Face Models

- `ProsusAI/finbert`: https://huggingface.co/ProsusAI/finbert
  - Role: financial sentiment classification.
  - Notes: Model card says it outputs positive, negative, and neutral labels.
- `BAAI/bge-small-en-v1.5`: https://huggingface.co/BAAI/bge-small-en-v1.5
  - Role: embeddings for evidence retrieval.
  - License: MIT.
- `sentence-transformers/all-MiniLM-L6-v2`: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
  - Role: lightweight embedding fallback.
  - License: Apache-2.0.
- `nlpaueb/sec-bert-base`: https://huggingface.co/nlpaueb/sec-bert-base
  - Role: optional SEC-domain model for later research experiments.
  - License: CC-BY-SA-4.0, so keep out of MVP until license implications are accepted.

## FDE Role Signals

- OpenAI FDE posting: https://openai.com/careers/forward-deployed-engineer-(fde)-sf-san-francisco/
  - Notes: Emphasizes production deployments, discovery, technical scoping, system design, full-stack systems, customer value, and LLM/generative model experience.
- Palantir FDSE posting: https://jobs.lever.co/palantir/dab396d4-2f14-4796-aac0-0d82883dccf0
  - Notes: Emphasizes architecture/design, data wrangling, AI, custom apps, customer stakeholders, and end-to-end execution.
- Databricks FDE posting: https://www.databricks.com/company/careers/professional-services-operations/sr-forward-deployed-engineer-8362737002
  - Notes: Emphasizes enterprise clients, deployment/integration, data and AI apps, analytics, agents, governance, and customer delivery.
