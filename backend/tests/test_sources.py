import pytest

from backend.app import db
from backend.app.ingest import arbeitnow, arxiv, remotive
from backend.app.ingest.common import iso_utc


def test_iso_utc_handles_every_source_format():
    assert iso_utc(1792464920) == "2026-10-20T02:55:20+00:00"
    assert iso_utc("2026-10-17T16:04:29") == "2026-10-17T16:04:29+00:00"      # naive = UTC
    assert iso_utc("2026-10-17T16:04:29Z") == "2026-10-17T16:04:29+00:00"
    assert iso_utc("2026-10-17T18:04:29+02:00") == "2026-10-17T16:04:29+00:00"


def test_arbeitnow_store_normalises_and_dedupes(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    jobs = [{"slug": "a-1", "title": "Data analyst", "tags": ["Data"], "job_types": ["full-time"],
             "description": "<p>SQL</p>", "url": "https://x/a-1", "created_at": 1792464920}]
    assert arbeitnow.store(conn, jobs) == 1
    assert arbeitnow.store(conn, jobs) == 0
    row = conn.execute("SELECT * FROM postings").fetchone()
    assert row["id"] == "arbeitnow:a-1" and row["published_at"].endswith("+00:00")


def test_remotive_store_normalises_naive_dates(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    jobs = [{"id": 7, "title": "QA", "tags": [], "description": "", "url": "u",
             "publication_date": "2026-10-17T16:04:29"}]
    assert remotive.store(conn, jobs) == 1
    assert conn.execute("SELECT published_at FROM postings").fetchone()[0].endswith("+00:00")


SKILLS = [{"id": "s", "arxiv_query": "all:x"}, {"id": "no_query", "arxiv_query": None}]


def test_arxiv_stops_on_rate_limit_and_resumes(tmp_path, monkeypatch):
    conn = db.connect(tmp_path / "t.db")
    monkeypatch.setattr(arxiv.time, "sleep", lambda s: None)
    calls = {"n": 0}

    def flaky(client, query, y, m):
        calls["n"] += 1
        if calls["n"] > 2:
            raise arxiv.RateLimited("429")
        return 10

    monkeypatch.setattr(arxiv, "count_for_month", flaky)
    assert arxiv.fetch_monthly_counts(conn, SKILLS, months=5) == 2

    monkeypatch.setattr(arxiv, "count_for_month", lambda *a: 7)
    assert arxiv.fetch_monthly_counts(conn, SKILLS, months=5) == 3   # only the missing months
    assert sorted(arxiv.load_counts(conn, "s").values()) == [7, 7, 7, 10, 10]


def test_arxiv_backs_off_on_429_then_raises(monkeypatch):
    class Resp:
        status_code = 429

    class Client:
        def get(self, *a, **k):
            return Resp()

    waits = []
    monkeypatch.setattr(arxiv.time, "sleep", waits.append)
    with pytest.raises(arxiv.RateLimited):
        arxiv.count_for_month(Client(), "all:x", 2025, 9)
    assert waits == [20.0, 40.0, 80.0]


class FakeResp:
    def __init__(self, status, data=None):
        self.status_code, self._data = status, data or []

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)

    def json(self):
        return {"data": self._data}


class FakeClient:
    def __init__(self, responses):
        self.responses = iter(responses)

    def get(self, *a, **k):
        return next(self.responses)


def test_arbeitnow_keeps_pages_already_fetched_on_429(monkeypatch):
    monkeypatch.setattr(arbeitnow.time, "sleep", lambda s: None)
    client = FakeClient([FakeResp(200, [{"slug": "a"}]), FakeResp(200, [{"slug": "b"}]), FakeResp(429)])
    assert [j["slug"] for j in arbeitnow.fetch_pages(client)] == ["a", "b"]


def test_arbeitnow_stops_at_empty_page(monkeypatch):
    monkeypatch.setattr(arbeitnow.time, "sleep", lambda s: None)
    client = FakeClient([FakeResp(200, [{"slug": "a"}]), FakeResp(200, [])])
    assert len(arbeitnow.fetch_pages(client)) == 1


def test_arbeitnow_429_on_first_page_is_an_error(monkeypatch):
    with pytest.raises(RuntimeError):
        arbeitnow.fetch_pages(FakeClient([FakeResp(429)]))
