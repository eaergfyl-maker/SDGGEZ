"""Skill demand growth from stored postings. Owner: Member 2.

demand_growth = % change in the SHARE of postings that mention a skill, recent window vs the
window before it. Using a share (not a raw count) stops "more postings overall" from looking
like "more demand for this skill".
"""
import json
import re
from datetime import datetime, timedelta, timezone

MIN_POSTINGS_PER_WINDOW = 20


def mentions(text: str, keywords: list[str]) -> bool:
    text = text.lower()
    return any(re.search(r"\b" + re.escape(k.lower()) + r"\b", text) for k in keywords)


def _window(conn, start: datetime, end: datetime) -> list[str]:
    rows = conn.execute(
        "SELECT title, tags, description FROM postings WHERE published_at >= ? AND published_at < ?",
        (start.isoformat(), end.isoformat()),
    )
    return [f"{r['title']} {' '.join(json.loads(r['tags']))} {r['description']}" for r in rows]


def demand_growth(conn, keywords: list[str], window_days: int = 14,
                  now: datetime | None = None) -> tuple[float | None, dict]:
    """Returns (growth %, details). Growth is None when either window is too small to trust."""
    now = now or datetime.now(timezone.utc)
    recent_start = now - timedelta(days=window_days)
    prev_start = recent_start - timedelta(days=window_days)
    recent = _window(conn, recent_start, now)
    prev = _window(conn, prev_start, recent_start)

    details = {
        "window_days": window_days,
        "recent_postings": len(recent),
        "previous_postings": len(prev),
        "recent_from": recent_start.date().isoformat(),
        "previous_from": prev_start.date().isoformat(),
    }
    if len(recent) < MIN_POSTINGS_PER_WINDOW or len(prev) < MIN_POSTINGS_PER_WINDOW:
        return None, details

    share_recent = sum(mentions(t, keywords) for t in recent) / len(recent)
    share_prev = sum(mentions(t, keywords) for t in prev) / len(prev)
    details.update(share_recent=round(share_recent, 4), share_previous=round(share_prev, 4))
    if share_prev == 0:
        return None, details
    return round(100 * (share_recent - share_prev) / share_prev, 1), details
