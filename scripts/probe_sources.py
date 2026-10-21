"""Check that each data source answers the way our code expects. Run this first.

    python scripts/probe_sources.py

Prints PASS/FAIL per source. Makes about 4 requests in total, so it is safe to re-run.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx  # noqa: E402

from backend.app import config  # noqa: E402
from backend.app.ingest import arxiv  # noqa: E402

H = {"User-Agent": config.USER_AGENT}


def check(name, fn):
    try:
        print(f"PASS {name}: {fn()}")
        return True
    except Exception as err:  # report, don't crash, so every source gets checked
        print(f"FAIL {name}: {err!r}")
        return False


def arxiv_probe():
    with httpx.Client(headers=H) as c:
        n = arxiv.count_for_month(c, 'all:"prompt engineering"', 2025, 9)
    return f"{n} papers matched in 2025-09"


def arbeitnow_probe():
    d = httpx.get("https://www.arbeitnow.com/api/job-board-api", headers=H, timeout=60).json()
    return f"{len(d['data'])} postings on page 1, fields {sorted(d['data'][0])[:5]}..."


def remotive_probe():
    d = httpx.get("https://remotive.com/api/remote-jobs", headers=H, timeout=60).json()
    return f"{len(d['jobs'])} postings (expected to be small, about 10)"


if __name__ == "__main__":
    results = [check("arXiv", arxiv_probe), check("Arbeitnow", arbeitnow_probe),
               check("Remotive", remotive_probe)]
    sys.exit(0 if all(results) else 1)
