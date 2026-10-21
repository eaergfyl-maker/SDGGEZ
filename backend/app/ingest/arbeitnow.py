"""Job postings from the Arbeitnow public API (main job-market signal). Owner: Member 2.

Checked 2026-10-21: no key needed, 300 postings per page, ordered by created_at, and the feed
only reaches back about a week (roughly 25 pages). The API says "do not abuse" and asks for a
link back, so we cache the result and pause between pages. Postings are mostly German/European:
say so wherever the data is shown.
"""
import json
import logging
import time

import httpx

from .. import config
from .common import insert_postings

log = logging.getLogger(__name__)

API = "https://www.arbeitnow.com/api/job-board-api"
CACHE_FILE = config.CACHE_DIR / "arbeitnow.json"
MIN_SECONDS_BETWEEN_FETCHES = 3 * 60 * 60
MAX_PAGES = 30
PAUSE_SECONDS = 3.0


def fetch_pages(client) -> list[dict]:
    """Walk the pages until they run out. On HTTP 429 keep what we already have and stop.

    Checked 2026-10-21: the API started answering 429 after about 26 quick requests, so one full
    walk is fine but repeated walks in a short time are not.
    """
    jobs: list[dict] = []
    for page in range(1, MAX_PAGES + 1):
        resp = client.get(API, params={"page": page})
        if resp.status_code == 429:
            if not jobs:
                raise RuntimeError("Arbeitnow rate limited on the first page")
            log.warning("Arbeitnow rate limited at page %d, keeping the %d postings so far",
                        page, len(jobs))
            break
        resp.raise_for_status()
        data = resp.json()["data"]
        if not data:
            break
        jobs += data
        time.sleep(PAUSE_SECONDS)
    return jobs


def fetch(force: bool = False) -> list[dict]:
    """All postings currently in the feed, from cache unless it is older than 3 hours."""
    if CACHE_FILE.exists() and not force:
        if time.time() - CACHE_FILE.stat().st_mtime < MIN_SECONDS_BETWEEN_FETCHES:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))["data"]
    with httpx.Client(headers={"User-Agent": config.USER_AGENT}, timeout=60) as client:
        jobs = fetch_pages(client)
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps({"data": jobs}), encoding="utf-8")
    return jobs


def store(conn, jobs: list[dict]) -> int:
    return insert_postings(conn, [
        {
            "id": f"arbeitnow:{j['slug']}",
            "source": "arbeitnow",
            "title": j.get("title", ""),
            "tags": list(j.get("tags", [])) + list(j.get("job_types", [])),
            "description": j.get("description", ""),
            "url": j.get("url", ""),
            "published_at": j["created_at"],
        }
        for j in jobs
    ])
