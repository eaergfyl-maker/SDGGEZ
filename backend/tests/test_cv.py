import base64
import io
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app import config, data_loader
from backend.app.main import app
from backend.app.scoring.cv import MAX_CHARS, docx_text, match_cv, redact
from backend.app.scoring.tree import infer_family

SKILLS = [
    {"id": "sql", "name": "SQL", "keywords": ["sql"], "cv_terms": ["database queries"]},
    {"id": "excel", "name": "Spreadsheets", "keywords": ["excel"], "cv_terms": ["pivot table"]},
    {"id": "cases", "name": "Case handling", "keywords": ["case management"],
     "cv_terms": ["complaint handling"]},
]


def ids(result, level):
    return {r["skill"] for r in result[level]}


def test_exact_phrase_any_case_and_plural():
    r = match_cv("Built PIVOT TABLES in Excel every week.", SKILLS)
    assert ids(r, "found") == {"excel"}
    assert r["found"][0]["evidence"].lower().count("excel") == 1


def test_whole_words_only():
    assert ids(match_cv("Excellent mysqlish skills", SKILLS), "found") == set()


def test_similar_wording_is_only_possible():
    r = match_cv("I handled complaints from customers every day.", SKILLS)
    assert ids(r, "found") == set()
    assert ids(r, "possible") == {"cases"}
    assert "similar wording" in r["possible"][0]["note"]


def test_negation_and_intent_are_not_counted_as_having_the_skill():
    r = match_cv("No experience with SQL. Currently learning Excel.", SKILLS)
    assert ids(r, "found") == set()
    assert ids(r, "possible") == {"sql", "excel"}


def test_intent_a_few_words_back_still_counts():
    r = match_cv("Want to learn how to use SQL for reports.", SKILLS)
    assert ids(r, "found") == set() and ids(r, "possible") == {"sql"}


def test_a_plain_mention_elsewhere_still_counts():
    r = match_cv("No SQL at my first job. Later I wrote SQL reports daily.", SKILLS)
    assert ids(r, "found") == {"sql"}


def test_contact_details_are_removed_before_matching():
    text = "Email jo@example.com, phone 012-345 6789, IC 900101-14-5678. Used SQL 2019 - 2023."
    clean, counts = redact(text)
    assert "@" not in clean and "6789" not in clean and "5678" not in clean
    assert "2019 - 2023" in clean                       # years are kept
    assert counts == {"emails": 1, "numbers": 2}
    r = match_cv(text, SKILLS)
    assert all("@" not in x["evidence"] and "6789" not in x["evidence"] for x in r["found"])


# --- the invented sample CVs (also used in the demo) -------------------------------------

SAMPLES = Path(config.DATA_DIR) / "sample_cvs"
EXPECTED = {  # what a person reading each CV would tick; measured, not tuned to pass
    "customer_service": ({"case_handling", "crm_tools", "spreadsheets", "ai_tools", "communication", "empathy"}, "service-ai"),
    "accounts_graduate": ({"bookkeeping", "spreadsheets", "statistics"}, "data"),
    "production_operator": ({"machine_operation", "quality_checks", "safety_procedures", "lean_methods"}, "industry"),
    "electrician": ({"electrical_wiring", "technical_drawing", "safety_procedures", "solar_pv_install"}, "green-energy"),
}


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_sample_cvs_find_the_core_skills_and_the_right_area(name):
    core, area = EXPECTED[name]
    r = match_cv((SAMPLES / f"{name}.txt").read_text(encoding="utf-8"), data_loader.skills())
    found = ids(r, "found")
    assert core <= found, f"missed {core - found}"
    guess = infer_family(found, data_loader.skills(), data_loader.roles(), data_loader.families())
    assert guess["family"] == area


def test_sample_cvs_do_not_tick_wanted_skills():
    r = match_cv((SAMPLES / "electrician.txt").read_text(encoding="utf-8"), data_loader.skills())
    assert "ev_charging" in ids(r, "possible") and "ev_charging" not in ids(r, "found")


# --- API ----------------------------------------------------------------------------------

@pytest.fixture
def client():
    return TestClient(app)


def test_cv_endpoint(client):
    body = client.post("/api/cv/skills", json={"text": "Five years using Zendesk and MS Excel."}).json()
    assert {"crm_tools", "spreadsheets"} <= ids(body, "found")
    assert body["redactions"] == {"emails": 0, "numbers": 0}


def test_cv_endpoint_rejects_empty_and_huge_text(client):
    assert client.post("/api/cv/skills", json={"text": ""}).status_code == 422
    assert client.post("/api/cv/skills", json={"text": "x" * (MAX_CHARS + 1)}).status_code == 422


def test_sample_cvs_endpoint_serves_invented_cvs(client):
    samples = client.get("/api/cv/samples").json()
    assert {s["id"] for s in samples} == set(EXPECTED)
    assert all("invented" in s["text"].lower() for s in samples)


# --- Word .docx upload --------------------------------------------------------------------

def make_docx(*paragraphs):
    ns = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
    body = "".join(f"<w:p><w:r><w:t>{p}</w:t></w:r></w:p>" for p in paragraphs)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("word/document.xml", f"<w:document {ns}><w:body>{body}</w:body></w:document>")
    return buf.getvalue()


def test_docx_text_keeps_paragraphs():
    assert docx_text(make_docx("SAMPLE (invented)", "Five years using Zendesk.")) == \
        "SAMPLE (invented)\nFive years using Zendesk."


def test_docx_endpoint_returns_text_and_rejects_other_files(client):
    data = base64.b64encode(make_docx("Five years using Zendesk and MS Excel.")).decode()
    assert client.post("/api/cv/file", json={"data": data}).json() == \
        {"text": "Five years using Zendesk and MS Excel.", "truncated": False}
    not_docx = base64.b64encode(b"%PDF-1.7 not a word file").decode()
    assert client.post("/api/cv/file", json={"data": not_docx}).status_code == 422
    assert client.post("/api/cv/file", json={"data": "not base64!"}).status_code == 422
