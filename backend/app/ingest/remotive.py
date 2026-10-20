"""Job postings from the Remotive public API (job-market signal). Owner: Member 2.

Remotive's terms (checked 2026-10-20): link back to Remotive and name it as the source,
about 4 requests per day at most, jobs are delayed 24h, and do not resubmit listings to other
job sites. We store postings only to compute aggregate skill-mention trends.
"""
import json
import time
from datetime import datetime, timezone

import httpx

from .. import config

API = "https://remotive.com/api/remote-jobs"
CACHE_FILE = config.CACHE_DIR / "remotive.json"
MIN_SECONDS_BETWEEN_FETCHES = 6 * 60 * 60  # keeps us at or under 4 requests a day


def fetch(force: bool = False) -> list[dict]:
    """Return postings, from cache unless the cache is older than the minimum interval."""
    if CACHE_FILE.exists() and not force:
        age = time.time() - CACHE_FILE.stat().st_mtime
        if age < MIN_SECONDS_BETWEEN_FETCHES:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))["jobs"]
    resp = httpx.get(API, headers={"User-Agent": config.USER_AGENT}, timeout=60)
    resp.raise_for_status()
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(resp.text, encoding="utf-8")
    return resp.json()["jobs"]


def store(conn, jobs: list[dict]) -> int:
    """Insert new postings. Returns how many were new."""
    now = datetime.now(timezone.utc).isoformat()
    before = conn.total_changes
    for j in jobs:
        conn.execute(
            "INSERT OR IGNORE INTO postings VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                f"remotive:{j['id']}",
                "remotive",
                j.get("title", ""),
                json.dumps(j.get("tags", [])),
                j.get("description", ""),
                j.get("url", ""),
                j.get("publication_date", ""),
                now,
            ),
        )
    conn.commit()
    return conn.total_changes - before
