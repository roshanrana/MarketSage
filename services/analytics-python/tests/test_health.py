from fastapi.testclient import TestClient

from marketsage_api.app import create_app


def test_health_reports_seeded_mode_and_duckdb(tmp_path, monkeypatch):
    monkeypatch.setenv("MARKETSAGE_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MARKETSAGE_MODE", "seeded")
    monkeypatch.delenv("MARKETSAGE_HTTP_TOKEN", raising=False)

    response = TestClient(create_app()).get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "seeded"
    assert body["source"] == "marketsage.analytics.health"
    assert body["data"]["service"] == "marketsage-analytics"
    assert body["data"]["status"] == "ok"
    assert body["data"]["config"]["data_dir"] == str(tmp_path)
    assert body["data"]["config"]["http_auth_required"] is False
    assert any(
        dep["name"] == "duckdb" and dep["status"] == "ok"
        for dep in body["data"]["dependencies"]
    )
    assert (tmp_path / "marketsage.duckdb").exists()


def test_invalid_mode_raises_clear_error(monkeypatch):
    monkeypatch.setenv("MARKETSAGE_MODE", "banana")
    monkeypatch.delenv("MARKETSAGE_HTTP_TOKEN", raising=False)

    response = TestClient(create_app()).get("/health")

    assert response.status_code == 500
