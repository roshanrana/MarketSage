.PHONY: check audit-deps demo-mcp dev-analytics dev-mcp

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
