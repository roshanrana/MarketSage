"""Named failure scenarios for NFR-007: degrade honestly, never fabricate.

Each scenario injects one fault, drives the API in-process and classifies the
observed behaviour as ``honest_fallback`` (served with an explicit warning or a
degraded status) or ``clean_error`` (a 4xx/5xx with a detail message and, where
the handler ran, an error audit row). ``passed`` is whether the observed
behaviour matches what the scenario expects. The harness reports the count and
the test suite asserts every one.
"""

import os
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest import mock

import duckdb
from fastapi.testclient import TestClient

from marketsage_api.app import create_app
from marketsage_core import openbb_adapter, sentiment

HONEST_FALLBACK = "honest_fallback"
CLEAN_ERROR = "clean_error"


@dataclass(frozen=True)
class Outcome:
    name: str
    expected: str
    observed: str
    detail: str

    @property
    def passed(self) -> bool:
        return self.expected == self.observed


@dataclass(frozen=True)
class Scenario:
    name: str
    expected: str
    description: str
    run: Callable[[Path], tuple[str, str]]


def _env(data_dir: Path, **extra: str) -> dict[str, str]:
    env = {
        "MARKETSAGE_DATA_DIR": str(data_dir),
        "MARKETSAGE_MODE": "seeded",
        "MARKETSAGE_ENABLE_MODEL_DOWNLOADS": "false",
    }
    env.update(extra)
    return env


@contextmanager
def _client(data_dir: Path, **extra: str) -> Iterator[TestClient]:
    env = _env(data_dir, **extra)
    with mock.patch.dict(os.environ, env, clear=False):
        os.environ.pop("MARKETSAGE_HTTP_TOKEN", None)
        yield TestClient(create_app())


def _error_rows(data_dir: Path) -> list[tuple[str, str]]:
    db = data_dir / "marketsage.duckdb"
    if not db.exists():
        return []
    with duckdb.connect(str(db)) as conn:
        return conn.execute(
            "select tool_name, detail from audit_event where status = 'error'"
        ).fetchall()


def _fail_openbb() -> Any:
    raise openbb_adapter.MarketDataError("simulated provider outage")


def _live_unavailable_live_mode(tmp: Path) -> tuple[str, str]:
    with mock.patch.object(openbb_adapter, "_load_openbb", _fail_openbb), _client(tmp) as api:
        response = api.post("/market/snapshot", json={"ticker": "MSFT", "provider_mode": "live"})
    rows = _error_rows(tmp)
    if response.status_code == 503 and rows and "outage" in (rows[0][1] or ""):
        return CLEAN_ERROR, f"503 with detail and {len(rows)} error audit row"
    return "unexpected", f"status {response.status_code}, audit rows {rows}"


def _live_unavailable_hybrid_mode(tmp: Path) -> tuple[str, str]:
    with mock.patch.object(openbb_adapter, "_load_openbb", _fail_openbb), _client(tmp) as api:
        response = api.post("/market/snapshot", json={"ticker": "MSFT", "provider_mode": "hybrid"})
    body = response.json()
    if (
        response.status_code == 200
        and any("seeded fallback" in warning for warning in body["warnings"])
        and "illustrative" in body["data"]["source_name"]
    ):
        return HONEST_FALLBACK, "200, seeded data labelled illustrative, fallback warning present"
    return "unexpected", f"status {response.status_code}, warnings {body.get('warnings')}"


def _malformed_live_payload_hybrid_mode(tmp: Path) -> tuple[str, str]:
    def broken_quote(**_: Any) -> dict[str, Any]:
        return {"results": [{"symbol": "MSFT", "note": "no price fields at all"}]}

    fake_obb = mock.Mock()
    fake_obb.equity.price.quote.side_effect = broken_quote
    with (
        mock.patch.object(openbb_adapter, "_load_openbb", lambda: fake_obb),
        _client(tmp) as api,
    ):
        response = api.post("/market/snapshot", json={"ticker": "MSFT", "provider_mode": "hybrid"})
    body = response.json()
    if response.status_code == 200 and any("seeded fallback" in w for w in body["warnings"]):
        return HONEST_FALLBACK, "malformed live quote rejected, seeded fallback with warning"
    return "unexpected", f"status {response.status_code}, body {str(body)[:200]}"


def _model_download_failure(tmp: Path) -> tuple[str, str]:
    def fail(_request: Any) -> Any:
        raise RuntimeError("simulated model download failure")

    with (
        mock.patch.object(sentiment, "_score_with_finbert", fail),
        _client(tmp, MARKETSAGE_ENABLE_MODEL_DOWNLOADS="true") as api,
    ):
        response = api.post(
            "/sentiment/text",
            json={"text": "Revenue growth was strong.", "model_preference": "finbert"},
        )
    body = response.json()
    if (
        response.status_code == 200
        and body["data"]["fallback"] is True
        and any("FinBERT unavailable" in w for w in body["warnings"])
    ):
        return HONEST_FALLBACK, "lexicon fallback flagged with fallback=true and a warning"
    return "unexpected", f"status {response.status_code}, body {str(body)[:200]}"


def _unknown_seed_ticker(tmp: Path) -> tuple[str, str]:
    with _client(tmp) as api:
        response = api.post("/market/snapshot", json={"ticker": "ZZZZ"})
    rows = _error_rows(tmp)
    if response.status_code == 404 and rows:
        return CLEAN_ERROR, "404 with detail and an error audit row"
    return "unexpected", f"status {response.status_code}, audit rows {rows}"


def _unknown_run_id(tmp: Path) -> tuple[str, str]:
    with _client(tmp) as api:
        response = api.get("/runs/does-not-exist")
    rows = _error_rows(tmp)
    if response.status_code == 404 and rows:
        return CLEAN_ERROR, "404 with detail and an error audit row"
    return "unexpected", f"status {response.status_code}, audit rows {rows}"


def _invalid_ticker_rejected(tmp: Path) -> tuple[str, str]:
    with _client(tmp) as api:
        response = api.post("/market/snapshot", json={"ticker": "$MSFT"})
    if response.status_code == 422:
        return CLEAN_ERROR, "422 from input validation before any handler ran"
    return "unexpected", f"status {response.status_code}"


def _audit_store_unwritable(tmp: Path) -> tuple[str, str]:
    blocker = tmp / "not-a-directory"
    blocker.write_text("occupied", encoding="utf-8")
    with _client(blocker) as api:
        response = api.get("/health")
    body = response.json()
    duckdb_status = next(
        (dep for dep in body["data"]["dependencies"] if dep["name"] == "duckdb"), None
    )
    if (
        response.status_code == 200
        and duckdb_status is not None
        and duckdb_status["status"] == "unavailable"
        and body["data"]["status"] != "ok"
    ):
        return HONEST_FALLBACK, "health served with duckdb unavailable and overall status degraded"
    return "unexpected", f"status {response.status_code}, duckdb {duckdb_status}"


def _evidence_for_uncovered_ticker(tmp: Path) -> tuple[str, str]:
    with _client(tmp) as api:
        response = api.post("/evidence/search", json={"query": "cash flow", "ticker": "XOM"})
    body = response.json()
    if (
        response.status_code == 200
        and body["data"]["count"] == 0
        and any("No committed evidence covers XOM" in w for w in body["warnings"])
    ):
        return HONEST_FALLBACK, "empty result with an explicit coverage warning, nothing invented"
    return "unexpected", f"status {response.status_code}, body {str(body)[:200]}"


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        "live_provider_unavailable_in_live_mode",
        CLEAN_ERROR,
        "OpenBB import fails while provider_mode=live",
        _live_unavailable_live_mode,
    ),
    Scenario(
        "live_provider_unavailable_in_hybrid_mode",
        HONEST_FALLBACK,
        "OpenBB import fails while provider_mode=hybrid",
        _live_unavailable_hybrid_mode,
    ),
    Scenario(
        "malformed_live_payload_in_hybrid_mode",
        HONEST_FALLBACK,
        "Live quote arrives without any price field",
        _malformed_live_payload_hybrid_mode,
    ),
    Scenario(
        "model_download_failure",
        HONEST_FALLBACK,
        "FinBERT requested but the download fails",
        _model_download_failure,
    ),
    Scenario(
        "unknown_seed_ticker",
        CLEAN_ERROR,
        "Ticker with no seeded instrument",
        _unknown_seed_ticker,
    ),
    Scenario(
        "unknown_run_id",
        CLEAN_ERROR,
        "Saved-run resource read for an id that was never written",
        _unknown_run_id,
    ),
    Scenario(
        "invalid_ticker_rejected",
        CLEAN_ERROR,
        "Ticker that fails the symbol pattern",
        _invalid_ticker_rejected,
    ),
    Scenario(
        "audit_store_unwritable",
        HONEST_FALLBACK,
        "Data directory path is occupied by a file",
        _audit_store_unwritable,
    ),
    Scenario(
        "evidence_for_uncovered_ticker",
        HONEST_FALLBACK,
        "Evidence requested for a ticker the corpus does not cover",
        _evidence_for_uncovered_ticker,
    ),
)


def run_scenario(scenario: Scenario, tmp: Path) -> Outcome:
    observed, detail = scenario.run(tmp)
    return Outcome(scenario.name, scenario.expected, observed, detail)


def run_all(base: Path) -> list[Outcome]:
    outcomes = []
    for scenario in SCENARIOS:
        tmp = base / scenario.name
        tmp.mkdir(parents=True, exist_ok=True)
        outcomes.append(run_scenario(scenario, tmp))
    return outcomes
