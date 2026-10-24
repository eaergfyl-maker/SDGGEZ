from fastapi.testclient import TestClient

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


def test_changes_has_expected_shape_without_a_database(monkeypatch, tmp_path):
    monkeypatch.setattr(routes.config, "DB_PATH", tmp_path / "missing.db")
    r = client.get("/api/changes")
    assert r.status_code == 200
    assert r.json() == {"changes": []}