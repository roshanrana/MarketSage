import json

import pytest

from marketsage_core.repo import repo_root
from marketsage_eval import __main__ as harness
from marketsage_eval import api_eval, headline, retrieval_eval, sentiment_eval


@pytest.fixture(scope="module")
def results(tmp_path_factory):
    base = tmp_path_factory.mktemp("eval")
    return harness.collect(base, skip_go=True)


def test_headline_validates_and_is_deterministic(results):
    stripped = {k: v for k, v in results.items() if k != "contract_fixtures"}

    first = headline.build(stripped)
    second = headline.build(stripped)

    assert first == second
    assert list(first["kpis"]) == [
        "retrieval_recall_at_5",
        "sentiment_coverage",
        "brief_grounding",
        "contract_conformance",
        "failure_modes",
        "audit_completeness",
    ]


def test_committed_headline_matches_a_fresh_build(results):
    committed = json.loads(
        (repo_root() / "metrics" / "headline.json").read_text(encoding="utf-8")
    )
    stripped = {k: v for k, v in results.items() if k != "contract_fixtures"}
    fresh = headline.build(stripped)
    # The MCP surface row needs Go; compare everything else.
    committed["facts"]["rows"] = _without_surface(committed)
    fresh["facts"]["rows"] = _without_surface(fresh)

    assert committed == fresh, "run `npm run eval` and commit metrics/headline.json"


def _without_surface(card):
    return [row for row in card["facts"]["rows"] if row["label"] != "MCP surface"]


def test_retrieval_metrics_are_bounded_and_bm25_beats_overlap():
    report = retrieval_eval.run()

    for scorer in ("bm25", "overlap"):
        for value in report[scorer]["recall"].values():
            assert 0.0 <= value <= 1.0
    assert report["bm25"]["recall"]["5"] >= report["overlap"]["recall"]["5"]


def test_sentiment_report_counts_every_row(tmp_path):
    report = sentiment_eval.run(api_eval.seeded_settings(tmp_path))

    assert report["rows"] == 234
    assert sum(report["confusion"].values()) == 234
    assert 0.0 <= report["expected_calibration_error"] <= 1.0


def test_brief_claims_all_resolve_to_payload_artefacts(tmp_path):
    report = api_eval.grounding_report(api_eval.seeded_settings(tmp_path))

    assert report["claim_bullets"] > 0
    assert report["grounded"] == report["claim_bullets"]
    assert report["tickers_with_evidence"] >= 1


@pytest.mark.parametrize(
    "mutation",
    [
        lambda h: h["kpis"].__setitem__("Bad-Key", h["kpis"]["failure_modes"]),
        lambda h: h["kpis"]["failure_modes"].__setitem__("accent", "green"),
        lambda h: h["bars"]["rows"][0].__setitem__("value", 500),
        lambda h: h["facts"]["rows"][0].__setitem__("status", "maybe"),
        lambda h: h.__setitem__("extra", {}),
    ],
)
def test_validate_rejects_schema_violations(results, mutation):
    stripped = {k: v for k, v in results.items() if k != "contract_fixtures"}
    card = headline.build(stripped)
    mutation(card)

    with pytest.raises(ValueError):
        headline.validate(card)
