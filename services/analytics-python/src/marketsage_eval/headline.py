"""Assemble and validate metrics/headline.json from the evaluation results."""

import json
import re
from pathlib import Path
from typing import Any

ACCENTS = {"teal", "blue", "amber", "violet", "red"}
STATUSES = {"ok", "pending", "blocked"}
KPI_KEY = re.compile(r"^[a-z][a-z0-9_]*$")


def build(results: dict[str, Any]) -> dict[str, Any]:
    retrieval = results["retrieval"]
    bm25, overlap, scoped = retrieval["bm25"], retrieval["overlap"], retrieval["bm25_ticker_scoped"]
    sentiment = results["sentiment"]
    grounding = results["grounding"]
    contracts = results["contracts"]
    scenarios = results["scenarios"]
    audit = results["audit"]
    envelopes = results["envelopes"]
    latency = results["latency"]
    surface = results.get("mcp_surface")
    manifest = results["fixtures"]

    pct = _pct
    committed_rows = int(round(sentiment["coverage"] * sentiment["rows"]))
    kpis = {
        "retrieval_recall_at_5": {
            "label": "Evidence recall@5, ticker given",
            "value": pct(scoped["recall"]["5"]),
            "note": (
                f"BM25 over {bm25['corpus_size']} FinanceBench filing excerpts, "
                f"{bm25['queries']} labelled queries; without the ticker hint recall@5 is "
                f"{pct(bm25['recall']['5'])} (MRR {bm25['mrr']:.2f}, nDCG@10 "
                f"{bm25['ndcg_at_10']:.2f}), so the structured hint does the heavy lifting"
            ),
            "accent": "teal",
        },
        "sentiment_coverage": {
            "label": "Sentiment fallback commits on",
            "value": pct(sentiment["coverage"]),
            "note": (
                f"{sentiment['model_id']} matched {committed_rows} of {sentiment['rows']} FiQA "
                f"test sentences and was right on {pct(sentiment['accuracy_when_committed'])} of "
                f"those; accuracy over every row {pct(sentiment['accuracy'])} against a "
                f"{pct(sentiment['majority_class_accuracy'])} majority baseline; ECE "
                f"{sentiment['expected_calibration_error']:.2f}; FinBERT is the real path and "
                "is pending"
            ),
            "accent": "red",
        },
        "brief_grounding": {
            "label": "Brief claims grounded",
            "value": f"{grounding['grounded']} / {grounding['claim_bullets']}",
            "note": (
                f"claim bullets whose reference resolves to a snapshot, evidence id or sentiment "
                f"hash in the same payload; {len(grounding['tickers'])} tickers, "
                f"{len(grounding['tickers']) - grounding['tickers_with_evidence']} with no "
                "committed evidence said so instead of borrowing another company's"
            ),
            "accent": "blue",
        },
        "contract_conformance": {
            "label": "Responses conforming to contract",
            "value": f"{contracts['validated']} / {contracts['endpoints']}",
            "note": (
                "every tool response validated against the JSON Schema generated from the "
                "Pydantic models; Go decodes the same fixtures with unknown fields forbidden"
                + (
                    "; schema file in sync"
                    if contracts["schema_in_sync_with_models"]
                    else "; SCHEMA FILE OUT OF SYNC"
                )
            ),
            "accent": "violet",
        },
        "failure_modes": {
            "label": "Fault injections handled honestly",
            "value": f"{sum(1 for s in scenarios if s['passed'])} / {len(scenarios)}",
            "note": (
                "named scenarios that degraded with an explicit warning or failed with a clean "
                "error and an audit row; none returned invented data"
            ),
            "accent": "teal",
        },
        "audit_completeness": {
            "label": "Tool calls with an audit row",
            "value": f"{audit['request_ids_matched']} / {audit['calls']}",
            "note": (
                f"replayed demo chain; {audit['ok_rows']} ok rows, {audit['orphan_rows']} orphans, "
                f"{envelopes['complete']}/{envelopes['total']} envelopes carry source, mode, "
                "timestamp and caveats"
            ),
            "accent": "blue",
        },
    }

    groups = (
        ("BM25, ticker given", scoped, "teal"),
        ("BM25, no hint", bm25, "blue"),
        ("Term overlap, no hint", overlap, "amber"),
    )
    bars = {
        "title": f"FinanceBench recall by scorer and hint ({bm25['queries']} queries)",
        "rows": [
            {
                "label": f"{name} @{k}",
                "value": round(report["recall"][k] * 100, 1),
                "max": 100,
                "display": pct(report["recall"][k]),
                "accent": accent,
            }
            for name, report, accent in groups
            for k in ("1", "5", "10")
        ],
    }

    fixture_rows = ", ".join(
        f"{s['dataset'].split('/')[-1]} {s['config']}/{s['split']} {s['rows']} rows"
        for s in manifest["sources"]
    )
    facts_rows: list[dict[str, str]] = [
        {
            "label": "Committed fixtures",
            "value": f"{fixture_rows}; MIT licensed, sha256-pinned in data/fixtures/manifest.json",
            "status": "ok",
        },
        {
            "label": "Sentiment confidence calibration",
            "value": (
                f"ECE {sentiment['expected_calibration_error']:.2f} on {committed_rows} committed "
                "predictions; the confidence field is a term-count formula, not a probability"
            ),
            "status": "ok",
        },
        {
            "label": "Evidence coverage",
            "value": (
                f"{grounding['tickers_with_evidence']} of {len(grounding['tickers'])} seeded "
                f"tickers have filing excerpts in the corpus; the rest get an explicit "
                "coverage warning"
            ),
            "status": "ok",
        },
        {
            "label": "Latency budget (NFR-008)",
            "value": (
                f"{latency['within_budget']} of {latency['total']} tools under "
                f"{int(latency['budget_ms'] / 1000)} s p95 in-process over "
                f"{latency['runs_per_endpoint']} runs; timings kept in metrics/eval-latest.json, "
                "not here, because they vary by host"
            ),
            "status": "ok" if latency["within_budget"] == latency["total"] else "pending",
        },
    ]
    if surface:
        facts_rows.append(
            {
                "label": "MCP surface",
                "value": (
                    f"{len(surface['tools'])} tools, {len(surface['prompts'])} prompts, "
                    f"{len(surface['resource_templates'])} resource template, read from "
                    "`marketsage-mcp --describe`"
                ),
                "status": "ok",
            }
        )
    else:
        facts_rows.append(
            {
                "label": "MCP surface",
                "value": "pending: Go toolchain not available to run `marketsage-mcp --describe`",
                "status": "pending",
            }
        )
    facts_rows.extend(
        [
            {
                "label": "FinBERT sentiment accuracy",
                "value": (
                    "pending: needs MARKETSAGE_ENABLE_MODEL_DOWNLOADS=true and a model download; "
                    "the offline harness scores the lexicon fallback only"
                ),
                "status": "pending",
            },
            {
                "label": "Embedding retrieval",
                "value": (
                    "pending: bge-small / MiniLM path is not implemented; lexical scorers only"
                ),
                "status": "pending",
            },
            {
                "label": "Live OpenBB market data",
                "value": (
                    "pending: seeded prices are illustrative and are not scored; live mode needs "
                    "the optional OpenBB dependency and provider configuration"
                ),
                "status": "pending",
            },
        ]
    )

    headline = {
        "kpis": kpis,
        "bars": bars,
        "facts": {"title": "Observed offline, and what is not", "rows": facts_rows},
    }
    validate(headline)
    return headline


def validate(headline: dict[str, Any]) -> None:
    if set(headline) != {"kpis", "bars", "facts"}:
        raise ValueError(f"top-level keys must be kpis, bars, facts; got {sorted(headline)}")
    for key, tile in headline["kpis"].items():
        if not KPI_KEY.match(key):
            raise ValueError(f"kpi key {key!r} is not snake_case")
        if set(tile) != {"label", "value", "note", "accent"}:
            raise ValueError(f"kpi {key!r} has keys {sorted(tile)}")
        if tile["accent"] not in ACCENTS:
            raise ValueError(f"kpi {key!r} accent {tile['accent']!r}")
    for row in headline["bars"]["rows"]:
        if set(row) != {"label", "value", "max", "display", "accent"}:
            raise ValueError(f"bar row keys {sorted(row)}")
        if not 0 <= row["value"] <= row["max"]:
            raise ValueError(f"bar {row['label']!r} value outside [0, max]")
        if row["accent"] not in ACCENTS:
            raise ValueError(f"bar {row['label']!r} accent {row['accent']!r}")
    for row in headline["facts"]["rows"]:
        if set(row) != {"label", "value", "status"}:
            raise ValueError(f"fact row keys {sorted(row)}")
        if row["status"] not in STATUSES:
            raise ValueError(f"fact {row['label']!r} status {row['status']!r}")


def render(headline: dict[str, Any]) -> str:
    return json.dumps(headline, indent=2, ensure_ascii=False) + "\n"


def write(headline: dict[str, Any], path: Path) -> None:
    validate(headline)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(headline), encoding="utf-8", newline="\n")


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"
