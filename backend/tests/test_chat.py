import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.scoring import chat, cv_ai

FACTS = ("1. IT support specialist: match 73%; outlook +62.4%; mentioned in 131 of 3,518 postings "
         "since 2026-10-19. Course: 4 hours, RM0.")


@pytest.fixture
def on(monkeypatch):
    monkeypatch.setenv("RUNPOD_API_KEY", "test-key")
    monkeypatch.setenv("RUNPOD_ENDPOINT_ID", "test-endpoint")


@pytest.fixture
def client():
    return TestClient(app)


def test_numbers_from_the_facts_pass():
    assert chat.unsupported_numbers("You match 73% and the outlook is +62.4%; 131 of 3518 postings.", FACTS) == []


def test_rounding_a_fact_and_small_counts_are_fine():
    assert chat.unsupported_numbers("About 62% outlook, and 2 skills to learn.", FACTS) == []


def test_invented_numbers_are_caught():
    assert chat.unsupported_numbers("Salaries rise 45% and there are 12,000 jobs.", FACTS) == ["45", "12,000"]


def test_answer_with_an_invented_number_is_withheld(on):
    r = chat.answer("q", FACTS, call=lambda m: "Demand will grow 300% by 2030.")
    assert r["status"] == "unverified" and r["answer"] is None


def test_good_answer_is_returned_without_thinking_tags(on):
    r = chat.answer("q", FACTS, call=lambda m: "<think>x</think>You match 73% of IT support.")
    assert r == {"status": "ok", "answer": "You match 73% of IT support."}


def test_model_gets_the_facts_and_the_language(on):
    seen = []
    chat.answer("Kenapa?", FACTS, lang="ms", call=lambda m: seen.append(m) or "Ok.")
    assert FACTS in seen[0][0]["content"] and "Bahasa Malaysia" in seen[0][0]["content"]


def test_off_without_settings(monkeypatch):
    monkeypatch.delenv("RUNPOD_API_KEY", raising=False)
    assert chat.answer("q", FACTS, call=lambda m: pytest.fail("no call"))["status"] == "off"


def test_unreachable_model_is_an_error(on):
    def down(m):
        raise cv_ai.AIUnavailable("ConnectError")
    assert chat.answer("q", FACTS, call=down)["status"] == "error"


def test_endpoint_builds_facts_from_the_users_own_results(on, monkeypatch, client):
    seen = []
    monkeypatch.setattr(cv_ai, "call_model", lambda m: seen.append(m) or "Your best match is 73%.")
    body = client.post("/api/chat", json={"question": "Why IT support?", "persona": "aisyah"}).json()
    facts = seen[0][0]["content"]
    assert body["status"] == "ok" and body["focus_role"] == "IT support specialist"
    assert "Skills the user ALREADY HAS: Communication, Empathy, Case handling, CRM tools." in facts
    assert "Learning pathway to IT support specialist" in facts


def test_endpoint_uses_the_owned_list_and_selected_role(on, monkeypatch, client):
    seen = []
    monkeypatch.setattr(cv_ai, "call_model", lambda m: seen.append(m) or "Ok.")
    body = client.post("/api/chat", json={"question": "q", "owned": ["communication"],
                                          "family": "service-ai", "role": "qa_analyst"}).json()
    assert "Skills the user ALREADY HAS: Communication." in seen[0][0]["content"]
    assert body["focus_role"] == "Conversational-AI QA analyst"


def test_endpoint_validates_input(client):
    assert client.post("/api/chat", json={"question": ""}).status_code == 422
    assert client.post("/api/chat", json={"question": "x" * 501}).status_code == 422
    assert client.post("/api/chat", json={"question": "q", "lang": "fr"}).status_code == 422
    assert client.post("/api/chat", json={"question": "q", "owned": ["nope"]}).status_code == 422
