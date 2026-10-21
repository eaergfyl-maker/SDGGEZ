"""Helpers shared by the job-posting sources. Owner: Member 2."""
import json
from datetime import datetime, timezone


def iso_utc(value) -> str:
    """Normalise a unix timestamp or ISO string (naive = UTC) to an ISO 8601 UTC string.

    Sources use different formats; the demand-growth windows compare these as strings, so
    everything stored must look the same.
    """
    if isinstance(value, (int, float)):
        dt = datetime.fromtimestamp(value, tz=timezone.utc)
    else:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def insert_postings(conn, postings: list[dict]) -> int:
    """Insert postings (dicts with id, source, title, tags, description, url, published_at).

    Existing ids are ignored, so re-running never double counts. Returns how many were new.
    """
    now = datetime.now(timezone.utc).isoformat()
    before = conn.total_changes
    for p in postings:
        conn.execute(
            "INSERT OR IGNORE INTO postings VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (p["id"], p["source"], p["title"], json.dumps(p["tags"]), p["description"],
             p["url"], iso_utc(p["published_at"]), now),
        )
    conn.commit()
    return conn.total_changes - before
