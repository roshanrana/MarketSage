.PHONY: check audit-deps demo-mcp dev-analytics dev-mcp eval eval-check contracts card card-check graph

check:
	npm run check

audit-deps:
	npm run audit:deps

demo-mcp:
	npm run demo:mcp

dev-analytics:
	npm run dev:analytics

dev-mcp:
	npm run dev:mcp

# Offline evaluation: writes metrics/headline.json, metrics/eval-latest.json and
# the contract fixtures under packages/contracts/fixtures.
eval:
	npm run eval

eval-check:
	npm run eval:check

# Regenerate packages/contracts/marketsage.schema.json from the Pydantic models.
contracts:
	npm run contracts

# Render docs/assets/metrics.svg and the README results block from headline.json.
card: eval
	npm run card

card-check:
	npm run card:check

# Rebuild the codebase graph (docs/graph/README.md); offline, no API cost.
graph:
	graphify update . && graphify cluster-only . --no-viz --no-label
