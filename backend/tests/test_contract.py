from fastapi.testclient import TestClient

from backend.app import trends
from backend.app.api import routes
from backend.app.main import app

client = TestClient(app)


def test_families_lists_ids():
    r = client.get("/api/families")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and data
    assert all("id" in f for f in data)


def test_sdgs_returns_data():
    r = client.get("/api/sdgs")
    assert r.status_code == 200
    assert r.json()


def test_changes_without_a_database_compare_the_two_committed_snapshots(monkeypatch, tmp_path):
    monkeypatch.setattr(routes.config, "DB_PATH", tmp_path / "missing.db")
    r = client.get("/api/changes")
    assert r.status_code == 200
    body = r.json()
    assert body["from"] < body["to"] and body["changes"]
    assert all({"skill", "signal", "old", "new"} <= set(c) and c["old"] != c["new"] for c in body["changes"])


def test_changes_empty_without_a_database_or_seeds(monkeypatch, tmp_path):
    monkeypatch.setattr(routes.config, "DB_PATH", tmp_path / "missing.db")
    monkeypatch.setattr(trends, "PREVIOUS", tmp_path / "missing.json")
    assert client.get("/api/changes").json() == {"changes": [], "from": None, "to": None}