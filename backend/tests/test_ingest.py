import json
from datetime import date, datetime, timedelta, timezone

from backend.app import db
from backend.app.ingest import arxiv, mentions, pipeline


def test_previous_months_skips_current_month():
    assert arxiv.previous_months(3, date(2026, 2, 15)) == [(2025, 11), (2025, 12), (2026, 1)]


def test_month_bounds_handles_month_lengths():
    assert arxiv._month_bounds(2024, 2) == ("202402010000", "202402292359")
    assert arxiv._month_bounds(2025, 12) == ("202512010000", "202512312359")


def test_research_growth_compares_same_months_a_year_apart():
    counts = {f"2025-{m:02d}": 100 for m in range(1, 13)}
    counts.update({"2026-01": 100, "2026-02": 100, "2026-03": 100})
    counts.update({"2025-01": 50, "2025-02": 50, "2025-03": 50})
    assert arxiv.research_growth(counts) == 100.0


def test_research_growth_needs_enough_history():
    assert arxiv.research_growth({"2026-01": 5}) is None


def test_research_growth_works_with_only_the_six_months_it_needs():
    keys = [f"{y:04d}-{m:02d}" for y, m in arxiv.growth_months(date(2026, 10, 24))]
    assert keys == ["2025-07", "2025-08", "2025-09", "2026-07", "2026-08", "2026-09"]
    counts = dict(zip(keys, [10, 10, 10, 15, 15, 15]))
    assert arxiv.research_growth(counts) == 50.0
    del counts["2025-08"]
    assert arxiv.research_growth(counts) is None


def test_mentions_matches_whole_words():
    assert mentions.mentions("Experience with SQL required", ["sql"])
    assert not mentions.mentions("mysqlish", ["sql"])


def _insert(conn, n, published, text):
    for i in range(n):
        conn.execute(
            "INSERT INTO postings VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (f"t:{published.isoformat()}:{text}:{i}", "test", text, json.dumps([]), "", "",
             published.isoformat(), published.isoformat()),
        )


def test_demand_growth_uses_share_not_count(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    now = datetime(2026, 10, 20, tzinfo=timezone.utc)
    prev, recent = now - timedelta(days=20), now - timedelta(days=5)
    _insert(conn, 5, prev, "python sql")      # 5 of 25 mention sql = 20%
    _insert(conn, 20, prev, "python")
    _insert(conn, 20, recent, "python sql")   # 20 of 50 mention sql = 40%
    _insert(conn, 30, recent, "python")
    growth, details = mentions.demand_growth(conn, ["sql"], now=now)
    assert growth == 100.0
    assert details["recent_postings"] == 50 and details["previous_postings"] == 25


def test_demand_growth_none_when_sample_small(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    now = datetime(2026, 10, 20, tzinfo=timezone.utc)
    _insert(conn, 3, now - timedelta(days=2), "sql")
    growth, _ = mentions.demand_growth(conn, ["sql"], now=now)
    assert growth is None


def test_pipeline_snapshot_and_diff_without_network(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    first = pipeline.run(conn, refresh_arxiv=False, refresh_jobs=False)
    conn.execute("UPDATE skill_trends SET demand_growth = 5 WHERE snapshot_id = ?", (first,))
    conn.commit()
    pipeline.run(conn, refresh_arxiv=False, refresh_jobs=False)
    changes = pipeline.diff_last_two(conn)
    assert changes and all(c["signal"] == "demand" and c["old"] == 5 for c in changes)
