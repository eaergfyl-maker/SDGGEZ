"""Job postings from the Remotive public API (small supplementary signal). Owner: Member 2.

Checked 2026-10-21: the public endpoint returns only the latest ~10 postings no matter what
limit or category is passed, so it is far too thin to measure a trend on its own. We keep it as
an extra source and for attribution.

Remotive's terms: link back to Remotive and name it as the source, about 4 requests per day at
most, jobs are delayed 24h, and do not resubmit listings to other job sites.
"""
import json
import time

import httpx

from .. import config
from .common import insert_postings

API = "https://remotive.com/api/remote-jobs"
CACHE_FILE = config.CACHE_DIR / "remotive.json"
MIN_SECONDS_BETWEEN_FETCHES = 6 * 60 * 60  # keeps us at or under 4 requests a day


def fetch(force: bool = False) -> list[dict]:
    if CACHE_FILE.exists() and not force:
        if time.time() - CACHE_FILE.stat().st_mtime < MIN_SECONDS_BETWEEN_FETCHES:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))["jobs"]
    resp = httpx.get(API, headers={"User-Agent": config.USER_AGENT}, timeout=60)
    resp.raise_for_status()
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(resp.text, encoding="utf-8")
    return resp.json()["jobs"]


def store(conn, jobs: list[dict]) -> int:
    return insert_postings(conn, [
        {
            "id": f"remotive:{j['id']}",
            "source": "remotive",
            "title": j.get("title", ""),
            "tags": j.get("tags", []),
            "description": j.get("description", ""),
            "url": j.get("url", ""),
            "published_at": j["publication_date"],
        }
        for j in jobs
    ])
