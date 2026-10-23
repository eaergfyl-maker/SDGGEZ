"""Monthly arXiv paper counts per skill (AI-advancement signal). Owner: Member 2.

Uses the public arXiv API (read its terms of use; it asks for one request every 3 seconds).
Only skills with an "arxiv_query" in data/skills.json are fetched.

Status 2026-10-21: the plain query worked from one machine, but the date-range query below
returned HTTP 429 (rate limited) from another, so it has NOT been confirmed end to end. Test it
first with scripts/probe_sources.py. The fetch below backs off on 429, saves what it has, and
resumes on the next run instead of starting again.
"""
import logging
import time
from datetime import date, datetime, timezone

import feedparser
import httpx

from .. import config

log = logging.getLogger(__name__)

API = "https://export.arxiv.org/api/query"
PAUSE_SECONDS = 3.0
RETRY_BASE_SECONDS = 20.0
MAX_ATTEMPTS = 3


class RateLimited(Exception):
    """arXiv kept answering 429 after backing off."""


def previous_months(n: int, today: date | None = None) -> list[tuple[int, int]]:
    """The last n complete months, oldest first (the current month is incomplete, so skipped)."""
    today = today or date.today()
    y, m = today.year, today.month
    months = []
    for _ in range(n):
        m -= 1
        if m == 0:
            y, m = y - 1, 12
        months.append((y, m))
    return list(reversed(months))


def _month_bounds(year: int, month: int) -> tuple[str, str]:
    start = f"{year:04d}{month:02d}010000"
    ny, nm = (year + 1, 1) if month == 12 else (year, month + 1)
    end_day = (date(ny, nm, 1) - date(year, month, 1)).days
    return start, f"{year:04d}{month:02d}{end_day:02d}2359"


def count_for_month(client: httpx.Client, query: str, year: int, month: int) -> int:
    start, end = _month_bounds(year, month)
    params = {"search_query": f"({query}) AND submittedDate:[{start} TO {end}]", "max_results": 1}
    for attempt in range(MAX_ATTEMPTS):
        resp = client.get(API, params=params, timeout=30)
        if resp.status_code == 429:
            wait = RETRY_BASE_SECONDS * 2 ** attempt
            log.warning("arXiv 429, waiting %.0fs (attempt %d/%d)", wait, attempt + 1, MAX_ATTEMPTS)
            time.sleep(wait)
            continue
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        return int(feed.feed.get("opensearch_totalresults", 0))
    raise RateLimited(f"arXiv rate limited {query!r} {year}-{month:02d}")


def fetch_monthly_counts(conn, skills: list[dict], months: int = 24) -> int:
    """Fill arxiv_counts for every skill with a query. Returns rows written.

    Months already stored are skipped, so after a rate-limit stop you can simply run it again.
    """
    now = datetime.now(timezone.utc).isoformat()
    written = 0
    with httpx.Client(headers={"User-Agent": config.USER_AGENT}) as client:
        for s in skills:
            if not s.get("arxiv_query"):
                continue
            for y, m in previous_months(months):
                month = f"{y:04d}-{m:02d}"
                if conn.execute("SELECT 1 FROM arxiv_counts WHERE skill_id = ? AND month = ?",
                                (s["id"], month)).fetchone():
                    continue
                try:
                    n = count_for_month(client, s["arxiv_query"], y, m)
                except RateLimited as err:
                    log.warning("stopping arXiv fetch: %s", err)
                    conn.commit()
                    return written
                except httpx.HTTPError as err:
                    log.warning("skipping %s %s: %s", s["id"], month, err)
                    continue
                conn.execute("INSERT OR REPLACE INTO arxiv_counts VALUES (?, ?, ?, ?, ?)",
                             (s["id"], month, n, s["arxiv_query"], now))
                conn.commit()
                written += 1
                time.sleep(PAUSE_SECONDS)
    return written


def research_growth(monthly: dict[str, int]) -> float | None:
    """% change: last 3 months vs the same 3 months one year earlier. None if not enough data."""
    if len(monthly) < 15:
        return None
    months = sorted(monthly)
    recent = sum(monthly[m] for m in months[-3:])
    year_ago = sum(monthly[m] for m in months[-15:-12])
    if year_ago == 0:
        return None
    return round(100 * (recent - year_ago) / year_ago, 1)


def load_counts(conn, skill_id: str) -> dict[str, int]:
    rows = conn.execute("SELECT month, count FROM arxiv_counts WHERE skill_id = ?", (skill_id,))
    return {r["month"]: r["count"] for r in rows}
