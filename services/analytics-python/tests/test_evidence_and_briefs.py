from fastapi.testclient import TestClient

from marketsage_api.app import create_app


def client(tmp_path, monkeypatch) -> TestClient:
    monkeypatch.setenv("MARKETSAGE_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MARKETSAGE_MODE", "seeded")
    monkeypatch.delenv("MARKETSAGE_HTTP_TOKEN", raising=False)
    return TestClient(create_app())


def test_evidence_search_returns_ranked_seeded_snippets(tmp_path, monkeypatch):
    response = client(tmp_path, monkeypatch).post(
        "/evidence/search",
        json={"query": "Apple services revenue margin", "ticker": "AAPL", "top_k": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["retrieval_mode"] == "lexical"
    assert body["data"]["count"] >= 1
    assert body["data"]["results"][0]["ticker"] == "AAPL"
    assert body["data"]["results"][0]["score"] > 0


def test_unknown_dataset_filter_returns_empty_evidence(tmp_path, monkeypatch):
    response = client(tmp_path, monkeypatch).post(
        "/evidence/search",
        json={"query": "Apple services revenue margin", "dataset": "missing/dataset"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["count"] == 0
    assert body["data"]["results"] == []


def test_research_brief_persists_and_returns_saved_run(tmp_path, monkeypatch):
    api = client(tmp_path, monkeypatch)
    brief_response = api.post(
        "/briefs/research",
        json={"tickers": ["AAPL"], "horizon": "1w", "provider_mode": "seeded"},
    )

    assert brief_response.status_code == 200
    brief = brief_response.json()["data"]
    assert brief["run_id"]
    assert brief["market_snapshots"][0]["ticker"] == "AAPL"
    assert brief["evidence"]

    run_response = api.get(f"/runs/{brief['run_id']}")

    assert run_response.status_code == 200
    saved = run_response.json()["data"]
    assert saved["run_id"] == brief["run_id"]
    assert saved["output"]["title"] == "MarketSage brief: AAPL"
