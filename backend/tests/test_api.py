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


def test_tree_defaults_to_persona_family(client):
    body = client.get("/api/tree", params={"persona": "aisyah"}).json()
    assert body["family"] == "service-ai"
    roles = {n["id"] for n in body["nodes"] if n["kind"] == "role"}
    assert "qa_analyst" in roles and "solar_pv_technician" not in roles


def test_tree_family_all_and_unknown(client):
    every = client.get("/api/tree", params={"family": "all"}).json()
    from backend.app import data_loader
    assert every["family"] == "all"
    assert {n["id"] for n in every["nodes"] if n["kind"] == "role"} == set(data_loader.roles_by_id())
    assert client.get("/api/tree", params={"family": "nope"}).status_code == 404


def test_every_persona_tree_loads(client):
    for p in client.get("/api/personas").json():
        body = client.get("/api/tree", params={"persona": p["id"]}).json()
        states = {n["id"]: n["state"] for n in body["nodes"]}
        assert body["family"] == p["family"]
        assert all(states.get(s) == "mastered" for s in p["skills"])


def test_same_skills_same_tree_whatever_the_persona(client):
    owned = "communication,empathy,crm_tools"
    params = {"owned": owned, "family": "service-ai"}
    a = client.get("/api/tree", params={**params, "persona": "aisyah"}).json()
    b = client.get("/api/tree", params={**params, "persona": "hafiz"}).json()
    assert a["nodes"] == b["nodes"]


def test_role_nodes_have_outlook_and_source(client):
    body = client.get("/api/tree", params={"persona": "aisyah"}).json()
    role = next(n for n in body["nodes"] if n["id"] == "qa_analyst")
    assert "outlook" in role and "outlook_range" in role
    assert role["based_on"]["onet_code"] == "15-1253.00"


def test_pathway_uses_persona_study_hours(client):
    body = client.get("/api/pathway", params={"role": "qa_analyst", "persona": "aisyah"}).json()
    assert body["hours_per_week"] == 6
    assert body["estimated_weeks"] is None   # no verified courses yet, so no honest estimate
    assert client.get("/api/pathway", params={"role": "qa_analyst", "hours_per_week": 0}).status_code == 422
