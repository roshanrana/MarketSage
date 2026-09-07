"""In-process checks against the HTTP API: contracts, envelopes, audit, grounding, latency."""

import json
import os
import statistics
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from time import perf_counter
from typing import Any
from unittest import mock

import duckdb
import jsonschema
from fastapi.testclient import TestClient

from marketsage_api.app import create_app
from marketsage_core.briefs import build_research_brief
from marketsage_core.config import Settings
from marketsage_core.contracts import (
    ENDPOINTS,
    build_schema,
    committed_schema,
    envelope_schema,
    render_schema,
    schema_path,
)
from marketsage_core.models import ResearchBriefRequest
from marketsage_core.repo import repo_root

DEMO_TICKER = "MSFT"
SENTIMENT_TEXT = "Revenue growth was strong, but margin pressure and weakness remain."
EVIDENCE_QUERY = "Microsoft cloud revenue growth and operating margin"
LATENCY_RUNS = 5
LATENCY_BUDGET_MS = 2000.0
ENVELOPE_FIELDS = ("request_id", "mode", "generated_at", "source")
VOLATILE_FIELDS = {
    "request_id": "req-fixture",
    "generated_at": "2026-01-01T00:00:00Z",
    "run_id": "run-fixture",
    "created_at": "2026-01-01T00:00:00Z",
}

# The demo tool chain, in the order the MCP CLI drives it. The saved-run read
# is appended once the brief has produced a run id.
TOOL_CHAIN: tuple[tuple[str, str, dict[str, Any] | None], ...] = (
    ("GET", "/health", None),
    ("GET", "/datasets", None),
    ("POST", "/market/snapshot", {"ticker": DEMO_TICKER}),
    (
        "POST",
        "/market/history",
        {"ticker": DEMO_TICKER, "start": "2026-08-25", "end": "2026-08-28"},
    ),
    ("POST", "/sentiment/text", {"text": SENTIMENT_TEXT, "ticker": DEMO_TICKER}),
    ("POST", "/evidence/search", {"query": EVIDENCE_QUERY, "ticker": DEMO_TICKER, "top_k": 3}),
    (
        "POST",
        "/briefs/research",
        {"tickers": [DEMO_TICKER], "horizon": "1w", "provider_mode": "seeded"},
    ),
)


def seeded_settings(data_dir: Path) -> Settings:
    return Settings(
        mode="seeded",
        data_dir=data_dir,
        model_downloads_enabled=False,
        log_level="info",
        http_token=None,
    )


@contextmanager
def seeded_client(data_dir: Path) -> Iterator[TestClient]:
    env = {
        "MARKETSAGE_DATA_DIR": str(data_dir),
        "MARKETSAGE_MODE": "seeded",
        "MARKETSAGE_ENABLE_MODEL_DOWNLOADS": "false",
    }
    with mock.patch.dict(os.environ, env, clear=False):
        os.environ.pop("MARKETSAGE_HTTP_TOKEN", None)
        os.environ.pop("MARKETSAGE_RETRIEVAL_SCORER", None)
        yield TestClient(create_app())


def call(api: TestClient, method: str, path: str, body: dict[str, Any] | None) -> tuple[Any, float]:
    started = perf_counter()
    response = api.get(path) if method == "GET" else api.post(path, json=body)
    elapsed_ms = (perf_counter() - started) * 1000
    return response, elapsed_ms


def run_tool_chain(api: TestClient) -> list[dict[str, Any]]:
    """Drive every tool once and return one record per endpoint."""
    results: list[dict[str, Any]] = []
    for method, path, body in TOOL_CHAIN:
        response, elapsed_ms = call(api, method, path, body)
        results.append(_record(path, response, elapsed_ms))
    run_id = results[-1]["body"]["data"]["run_id"]
    response, elapsed_ms = call(api, "GET", f"/runs/{run_id}", None)
    results.append(_record("/runs/{run_id}", response, elapsed_ms))
    return results


def _record(endpoint: str, response: Any, elapsed_ms: float) -> dict[str, Any]:
    return {
        "endpoint": endpoint,
        "status": response.status_code,
        "body": response.json(),
        "ms": elapsed_ms,
    }


def contracts_report(responses: list[dict[str, Any]]) -> dict[str, Any]:
    fresh = render_schema(build_schema())
    committed_text = schema_path().read_text(encoding="utf-8")
    schema = committed_schema()
    failures: list[dict[str, str]] = []
    validated = 0
    for record in responses:
        validator = jsonschema.Draft202012Validator(envelope_schema(schema, record["endpoint"]))
        errors = sorted(validator.iter_errors(record["body"]), key=lambda e: list(e.path))
        if errors:
            failures.append({"endpoint": record["endpoint"], "error": errors[0].message})
        else:
            validated += 1
    return {
        "schema_in_sync_with_models": fresh == committed_text,
        "endpoints": len(ENDPOINTS),
        "validated": validated,
        "failures": failures,
    }


def envelope_report(responses: list[dict[str, Any]]) -> dict[str, Any]:
    complete = 0
    incomplete: list[str] = []
    for record in responses:
        body = record["body"]
        fields_present = all(body.get(field) for field in ENVELOPE_FIELDS)
        caveats_present = isinstance(body.get("caveats"), list) and bool(body["caveats"])
        if record["status"] == 200 and fields_present and caveats_present:
            complete += 1
        else:
            incomplete.append(record["endpoint"])
    return {"total": len(responses), "complete": complete, "incomplete": incomplete}


def audit_report(data_dir: Path, responses: list[dict[str, Any]]) -> dict[str, Any]:
    with duckdb.connect(str(data_dir / "marketsage.duckdb")) as conn:
        rows = conn.execute(
            "select request_id, tool_name, status, warning_count from audit_event"
        ).fetchall()
    ok_ids = {row[0] for row in rows if row[2] == "ok"}
    response_ids = {record["body"]["request_id"] for record in responses}
    return {
        "calls": len(responses),
        "ok_rows": sum(1 for row in rows if row[2] == "ok"),
        "error_rows": sum(1 for row in rows if row[2] == "error"),
        "request_ids_matched": len(response_ids & ok_ids),
        "orphan_rows": len(ok_ids - response_ids),
        "tools_seen": sorted({row[1] for row in rows}),
    }


def grounding_report(settings: Settings) -> dict[str, Any]:
    seed_path = repo_root() / "data" / "seed" / "market_seed.json"
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    tickers = sorted(seed["instruments"])
    per_ticker: list[dict[str, Any]] = []
    totals = {"claim_bullets": 0, "grounded": 0, "policy_bullets": 0, "absence_bullets": 0}
    for ticker in tickers:
        brief, warnings = build_research_brief(
            ResearchBriefRequest(tickers=[ticker], provider_mode="seeded"), settings
        )
        snapshot_ids = {f"snapshot:{item.ticker}" for item in brief.market_snapshots}
        evidence_ids = {f"evidence:{item.id}" for item in brief.evidence}
        sentiment_id = f"sentiment:{brief.sentiment.text_hash}" if brief.sentiment else None
        counts = {"claim_bullets": 0, "grounded": 0, "policy_bullets": 0, "absence_bullets": 0}
        for section in brief.sections:
            if len(section.references) != len(section.bullets):
                raise RuntimeError(f"{ticker}: references do not pair with bullets")
            for reference in section.references:
                if reference == "":
                    counts["absence_bullets"] += 1
                elif reference.startswith("policy:"):
                    counts["policy_bullets"] += 1
                else:
                    counts["claim_bullets"] += 1
                    if reference in snapshot_ids | evidence_ids or reference == sentiment_id:
                        counts["grounded"] += 1
        for key, value in counts.items():
            totals[key] += value
        per_ticker.append(
            {
                "ticker": ticker,
                **counts,
                "evidence_count": len(brief.evidence),
                "coverage_warning": any("No committed evidence covers" in w for w in warnings),
            }
        )
    return {
        "tickers": tickers,
        **totals,
        "tickers_with_evidence": sum(1 for row in per_ticker if row["evidence_count"]),
        "per_ticker": per_ticker,
    }


def latency_report(api: TestClient, run_id: str) -> dict[str, Any]:
    chain = [*TOOL_CHAIN, ("GET", f"/runs/{run_id}", None)]
    rows: list[dict[str, Any]] = []
    for method, path, body in chain:
        samples = [call(api, method, path, body)[1] for _ in range(LATENCY_RUNS)]
        samples.sort()
        p95 = samples[min(len(samples) - 1, int(round(0.95 * (len(samples) - 1))))]
        rows.append(
            {
                "endpoint": "/runs/{run_id}" if path.startswith("/runs/") else path,
                "p50_ms": round(statistics.median(samples), 2),
                "p95_ms": round(p95, 2),
                "within_budget": p95 < LATENCY_BUDGET_MS,
            }
        )
    return {
        "runs_per_endpoint": LATENCY_RUNS,
        "budget_ms": LATENCY_BUDGET_MS,
        "endpoints": rows,
        "within_budget": sum(1 for row in rows if row["within_budget"]),
        "total": len(rows),
    }


def pinned_fixtures(responses: list[dict[str, Any]], data_dir: Path) -> dict[str, str]:
    """Contract fixtures for the Go decoder test, with volatile ids and paths pinned."""
    fixtures: dict[str, str] = {}
    scrub = (str(data_dir), data_dir.as_posix())
    for record in responses:
        envelope_name = ENDPOINTS[record["endpoint"]][0]
        name = envelope_name.removesuffix("Envelope")
        file_name = "".join(f"_{c.lower()}" if c.isupper() else c for c in name).lstrip("_")
        pinned = _pin(record["body"], scrub)
        fixtures[f"{file_name}.json"] = json.dumps(pinned, indent=2) + "\n"
    return fixtures


def _pin(value: Any, scrub: tuple[str, ...]) -> Any:
    if isinstance(value, dict):
        return {
            key: VOLATILE_FIELDS[key] if key in VOLATILE_FIELDS else _pin(item, scrub)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_pin(item, scrub) for item in value]
    if isinstance(value, str):
        for path in scrub:
            value = value.replace(path, "<data_dir>")
        # Windows writes a backslash after the scrubbed prefix; keep fixtures platform-neutral.
        return value.replace("<data_dir>\\", "<data_dir>/")
    return value
