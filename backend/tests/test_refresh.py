from fastapi.testclient import TestClient

from backend.app.api import routes
from backend.app.main import app

client = TestClient(app)


def test_refresh_without_token_is_forbidden(monkeypatch):
    monkeypatch.setenv("REFRESH_TOKEN", "secret")
    assert client.post("/api/refresh").status_code == 403


def test_refresh_with_wrong_token_is_forbidden(monkeypatch):
    monkeypatch.setenv("REFRESH_TOKEN", "secret")
    r = client.post("/api/refresh", headers={"X-Refresh-Token": "wrong"})
    assert r.status_code == 403


def test_refresh_is_closed_when_no_token_is_configured(monkeypatch):
    monkeypatch.delenv("REFRESH_TOKEN", raising=False)
    r = client.post("/api/refresh", headers={"X-Refresh-Token": "anything"})
    assert r.status_code == 403


def test_refresh_with_right_token_starts_the_job(monkeypatch):
    monkeypatch.setenv("REFRESH_TOKEN", "secret")
    calls = []
    monkeypatch.setattr(routes, "_refresh_job", lambda: calls.append(1))
    app.dependency_overrides[routes.refresh_cooldown] = lambda: None
    try:
        r = client.post("/api/refresh", headers={"X-Refresh-Token": "secret"})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 202
    assert calls == [1]