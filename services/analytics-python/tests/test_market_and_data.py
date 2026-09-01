from fastapi.testclient import TestClient

from marketsage_api.app import create_app


def client(tmp_path, monkeypatch) -> TestClient:
    monkeypatch.setenv("MARKETSAGE_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MARKETSAGE_MODE", "seeded")
    monkeypatch.delenv("MARKETSAGE_HTTP_TOKEN", raising=False)
    return TestClient(create_app())


def test_dataset_manifest_records_reviewed_assets(tmp_path, monkeypatch):
    response = client(tmp_path, monkeypatch).get("/datasets")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["count"] >= 8
    ids = {entry["dataset_id"] for entry in body["data"]["datasets"]}
    assert "zeroshot/twitter-financial-news-sentiment" in ids
    assert "mteb/FinanceBenchRetrieval" in ids
    assert any(
        entry["local_status"] == "blocked-license-review"
        for entry in body["data"]["datasets"]
    )


def test_seeded_market_snapshot(tmp_path, monkeypatch):
    response = client(tmp_path, monkeypatch).post("/market/snapshot", json={"ticker": "AAPL"})

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "seeded"
    assert body["data"]["ticker"] == "AAPL"
    assert body["data"]["price"] > 0
    assert body["data"]["source_name"] == "MarketSage illustrative seed data"


def test_seeded_price_history_can_filter_dates(tmp_path, monkeypatch):
    response = client(tmp_path, monkeypatch).post(
        "/market/history",
        json={"ticker": "SPY", "start": "2026-08-27", "end": "2026-08-28"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["ticker"] == "SPY"
    assert [row["date"] for row in body["data"]["observations"]] == [
        "2026-08-27",
        "2026-08-28",
    ]


def test_unknown_seed_ticker_returns_not_found(tmp_path, monkeypatch):
    response = client(tmp_path, monkeypatch).post("/market/snapshot", json={"ticker": "ZZZZ"})

    assert response.status_code == 404
    assert "No seeded data" in response.json()["detail"]


def test_invalid_ticker_input_is_rejected(tmp_path, monkeypatch):
    response = client(tmp_path, monkeypatch).post("/market/snapshot", json={"ticker": "$AAPL"})

    assert response.status_code == 422


def test_fallback_sentiment_is_deterministic(tmp_path, monkeypatch):
    response = client(tmp_path, monkeypatch).post(
        "/sentiment/text",
        json={
            "ticker": "MSFT",
            "text": "Revenue growth was strong, but margin pressure and weakness remain.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["fallback"] is True
    assert body["data"]["label"] == "neutral"
    assert "growth" in body["data"]["matched_terms"]
    assert "pressure" in body["data"]["matched_terms"]
