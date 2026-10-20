import pytest
from fastapi.testclient import TestClient

from backend.app import config
from backend.app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "missing.db")
    return TestClient(app)


def test_health(client):
    assert client.get("/api/health").json() == {"ok": True}


def test_trends_are_marked_mock_without_snapshot(client):
    body = client.get("/api/trends").json()
    assert body["is_mock"] is True
    assert {s["skill"] for s in body["skills"]} >= {"ai_tools", "prompting"}


def test_tree_for_persona(client):
    body = client.get("/api/tree", params={"persona": "aisyah", "scenario": "fast"}).json()
    states = {n["id"]: n["state"] for n in body["nodes"]}
    assert states["communication"] == "mastered"
    assert states["ai_tools"] == "available"
    assert states["qa_analyst"] == "locked"


def test_tree_with_owned_override_unlocks_role(client):
    owned = "communication,empathy,crm_tools,ai_tools,prompting,chatbot_qa"
    body = client.get("/api/tree", params={"owned": owned}).json()
    role = next(n for n in body["nodes"] if n["id"] == "qa_analyst")
    assert role["state"] == "available"


def test_tree_rejects_unknown_skill(client):
    assert client.get("/api/tree", params={"owned": "nope"}).status_code == 422


def test_bad_scenario_rejected(client):
    assert client.get("/api/tree", params={"scenario": "chaos"}).status_code == 422


def test_pathway(client):
    body = client.get("/api/pathway", params={"role": "qa_analyst"}).json()
    assert [s["skill"] for s in body["steps"]][:2] == ["ai_tools", "prompting"]


def test_story_missing_is_empty_and_path_is_safe(client):
    assert client.get("/api/story/ai_tools").json() == {}
    assert client.get("/api/story/..%2Fsecrets").status_code in (404, 422)


def test_frontend_served(client):
    assert "Future-Ready RPG" in client.get("/").text
