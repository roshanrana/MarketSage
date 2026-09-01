import duckdb
from fastapi.testclient import TestClient

from marketsage_api.app import create_app
from marketsage_core import openbb_adapter, sentiment


def configure_seeded(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("MARKETSAGE_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MARKETSAGE_MODE", "seeded")
    monkeypatch.delenv("MARKETSAGE_HTTP_TOKEN", raising=False)
    monkeypatch.delenv("MARKETSAGE_ENABLE_MODEL_DOWNLOADS", raising=False)


def test_http_token_is_required_when_configured(tmp_path, monkeypatch):
    monkeypatch.setenv("MARKETSAGE_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MARKETSAGE_MODE", "seeded")
    monkeypatch.setenv("MARKETSAGE_HTTP_TOKEN", "local-test-token")
    api = TestClient(create_app())

    rejected = api.get("/health")
    accepted = api.get("/health", headers={"authorization": "Bearer local-test-token"})

    assert rejected.status_code == 401
    assert rejected.headers["www-authenticate"] == "Bearer"
    assert accepted.status_code == 200
    assert accepted.json()["data"]["config"]["http_auth_required"] is True


def test_successful_response_writes_structured_audit_event(tmp_path, monkeypatch):
    configure_seeded(tmp_path, monkeypatch)
    api = TestClient(create_app())

    response = api.post("/market/snapshot", json={"ticker": "AAPL"})

    assert response.status_code == 200
    request_id = response.json()["request_id"]
    with duckdb.connect(str(tmp_path / "marketsage.duckdb")) as conn:
        row = conn.execute(
            """
            select request_id, tool_name, status, duration_ms, mode, warning_count
            from audit_event
            where request_id = ?
            """,
            [request_id],
        ).fetchone()

    assert row is not None
    assert row[0] == request_id
    assert row[1] == "marketsage.analytics.market.snapshot"
    assert row[2] == "ok"
    assert row[3] >= 0
    assert row[4] == "seeded"
    assert row[5] == 0


def test_live_provider_failure_records_error_audit_event(tmp_path, monkeypatch):
    configure_seeded(tmp_path, monkeypatch)

    def fail_openbb():
        raise openbb_adapter.MarketDataError("simulated live provider unavailable")

    monkeypatch.setattr(openbb_adapter, "_load_openbb", fail_openbb)
    api = TestClient(create_app())

    response = api.post(
        "/market/snapshot",
        json={"ticker": "AAPL", "provider_mode": "live"},
    )

    assert response.status_code == 503
    with duckdb.connect(str(tmp_path / "marketsage.duckdb")) as conn:
        row = conn.execute(
            """
            select tool_name, status, detail
            from audit_event
            where status = 'error'
            order by created_at desc
            limit 1
            """
        ).fetchone()

    assert row is not None
    assert row[0] == "marketsage.analytics.market.snapshot"
    assert row[1] == "error"
    assert "simulated live provider unavailable" in row[2]


def test_finbert_unavailable_falls_back_to_local_sentiment(tmp_path, monkeypatch):
    configure_seeded(tmp_path, monkeypatch)
    monkeypatch.setenv("MARKETSAGE_ENABLE_MODEL_DOWNLOADS", "true")

    def fail_finbert(request):
        del request
        raise RuntimeError("simulated model download failure")

    monkeypatch.setattr(sentiment, "_score_with_finbert", fail_finbert)
    response = TestClient(create_app()).post(
        "/sentiment/text",
        json={
            "text": "Revenue growth was strong but margin pressure remains.",
            "model_preference": "finbert",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["fallback"] is True
    assert any("FinBERT unavailable" in warning for warning in body["warnings"])
