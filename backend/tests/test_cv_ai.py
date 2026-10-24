import json

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.scoring import cv_ai
from backend.app.scoring.cv_ai import AIUnavailable, parse_reply, suggest, verify

SKILLS = [
    {"id": "sql", "name": "SQL", "keywords": ["sql"]},
    {"id": "excel", "name": "Spreadsheets", "keywords": ["excel"]},
    {"id": "cases", "name": "Case handling", "keywords": ["case management"]},
]
CV = "Email jo@example.com. Used SQL daily. Sorted out angry customers' problems by phone."


@pytest.fixture
def on(monkeypatch):
    monkeypatch.setenv("RUNPOD_API_KEY", "test-key")
    monkeypatch.setenv("RUNPOD_ENDPOINT_ID", "test-endpoint")


def reply(*picks):
    return lambda messages: json.dumps({"skills": [{"id": i, "quote": q} for i, q in picks]})


def test_off_without_settings(monkeypatch):
    monkeypatch.delenv("RUNPOD_API_KEY", raising=False)
    monkeypatch.delenv("RUNPOD_ENDPOINT_ID", raising=False)
    r = suggest(CV, SKILLS, call=lambda m: pytest.fail("model must not be called"))
    assert r["status"] == "off" and r["possible"] == []


def test_keeps_real_ids_with_real_quotes(on):
    r = suggest(CV, SKILLS, call=reply(("cases", "sorted out angry customers' problems")))
    assert r["status"] == "ok"
    assert [(x["skill"], x["level"], x["source"]) for x in r["possible"]] == [("cases", "possible", "ai")]


def test_drops_invented_skills_invented_quotes_and_keyword_duplicates(on):
    r = suggest(CV, SKILLS, call=reply(
        ("rocket_science", "Used SQL daily"),        # not in the skill list
        ("excel", "built pivot tables in Excel"),    # quote is not in the CV
        ("sql", "Used SQL daily"),                   # keywords already found it
    ))
    assert r["possible"] == [] and r["suggested"] == 3


def test_model_sees_redacted_text_only(on):
    seen = []
    suggest(CV, SKILLS, call=lambda m: seen.append(m) or "{}")
    assert "jo@example.com" not in json.dumps(seen) and "[email removed]" in seen[0][1]["content"]


def test_unreachable_model_is_an_error_not_a_crash(on):
    def down(messages):
        raise AIUnavailable("ConnectError")
    assert suggest(CV, SKILLS, call=down) == {"status": "error", "model": cv_ai.model_name(), "possible": []}


@pytest.mark.parametrize("text", [
    '<think>hmm</think>{"skills": [{"id": "sql", "quote": "x y z"}]}',
    'Sure!\n```json\n{"skills": [{"id": "sql", "quote": "x y z"}]}\n```',
])
def test_parse_reply_tolerates_thinking_and_code_fences(text):
    assert parse_reply(text) == [{"id": "sql", "quote": "x y z"}]


@pytest.mark.parametrize("text", ["not json", '{"skills": "sql"}', "[]"])
def test_parse_reply_drops_garbage(text):
    assert parse_reply(text) == []


def test_quote_check_ignores_case_and_spacing():
    out = verify([{"id": "sql", "quote": "  USED   sql daily. "}], "I used SQL\ndaily.", SKILLS, set())
    assert [x["skill"] for x in out] == ["sql"]


def test_output_formats():
    assert cv_ai._output_text([{"choices": [{"tokens": ["{", "}"]}]}]) == "{}"
    assert cv_ai._output_text({"choices": [{"message": {"content": "{}"}}]}) == "{}"
    with pytest.raises(AIUnavailable):
        cv_ai._output_text(None)


def test_endpoints(on, monkeypatch):
    monkeypatch.setattr(cv_ai, "call_model", reply(("cases", "angry customers' problems")))
    client = TestClient(app)
    assert client.get("/api/cv/ai").json()["enabled"] is True
    body = client.post("/api/cv/ai", json={"text": CV}).json()
    assert body["status"] == "ok"
    assert client.post("/api/cv/ai", json={"text": ""}).status_code == 422
