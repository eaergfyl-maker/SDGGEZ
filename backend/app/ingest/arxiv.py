"""Monthly arXiv paper counts per skill (AI-advancement signal). Owner: Member 2.

Uses the public arXiv API (read its terms of use; it asks for one request every 3 seconds).
Only skills with an "arxiv_query" in data/skills.json are fetched.

Status 2026-10-24: confirmed end to end. The pipeline fetches only the 6 months that
research_growth compares (growth_months), about 70 requests. On HTTP 429 the fetch backs off,
saves what it has, and resumes on the next run instead of starting again.
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


def growth_months(today: date | None = None) -> list[tuple[int, int]]:
    """The 6 months research_growth compares: the last 3 complete months and the same 3 months
    a year earlier. Fetching only these keeps a full run to a few minutes."""
    months = previous_months(15, today)
    return months[:3] + months[-3:]


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


def fetch_monthly_counts(conn, skills: list[dict], months: int | list[tuple[int, int]] = 24) -> int:
    """Fill arxiv_counts for every skill with a query. Returns rows written.

    months is a number of recent months, or an explicit list of (year, month).

    Months already stored are skipped, so after a rate-limit stop you can simply run it again.
    """
    now = datetime.now(timezone.utc).isoformat()
    written = 0
    with httpx.Client(headers={"User-Agent": config.USER_AGENT}) as client:
        for s in skills:
            if not s.get("arxiv_query"):
                continue
            for y, m in (previous_months(months) if isinstance(months, int) else months):
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


def window_totals(monthly: dict[str, int]) -> tuple[int, int] | None:
    """Papers in the latest 3 stored months and in the same 3 months a year earlier, or None
    if any of those 6 months is missing."""
    if not monthly:
        return None
    y, m = map(int, max(monthly).split("-"))
    recent_keys = []
    for _ in range(3):
        recent_keys.append(f"{y:04d}-{m:02d}")
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
    year_ago_keys = [f"{int(k[:4]) - 1:04d}{k[4:]}" for k in recent_keys]
    if any(k not in monthly for k in recent_keys + year_ago_keys):
        return None
    return sum(monthly[k] for k in recent_keys), sum(monthly[k] for k in year_ago_keys)


def research_growth(monthly: dict[str, int]) -> float | None:
    """% change: the latest 3 stored months vs the same 3 months one year earlier.

    None if any of those 6 months is missing or the year-earlier total is zero.
    """
    totals = window_totals(monthly)
    if totals is None or totals[1] == 0:
        return None
    recent, year_ago = totals
    return round(100 * (recent - year_ago) / year_ago, 1)


def load_counts(conn, skill_id: str) -> dict[str, int]:
    rows = conn.execute("SELECT month, count FROM arxiv_counts WHERE skill_id = ?", (skill_id,))
    return {r["month"]: r["count"] for r in rows}
