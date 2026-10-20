"""Where the API gets trend components from. Owner: Member 1 (wiring), Member 2 (data).

Uses the latest snapshot in the database. Falls back to data/mock_trends.json, clearly marked
is_mock=True, until ingestion has produced a snapshot.
"""
import json

from . import config, data_loader, db


def latest_snapshot_trends():
    if not config.DB_PATH.exists():
        return None
    conn = db.connect()
    try:
        snap = conn.execute("SELECT id, created_at FROM snapshots ORDER BY id DESC LIMIT 1").fetchone()
        if snap is None:
            return None
        rows = conn.execute(
            "SELECT skill_id, research_growth, demand_growth, outlook, sources "
            "FROM skill_trends WHERE snapshot_id = ?",
            (snap["id"],),
        ).fetchall()
    finally:
        conn.close()
    return {
        "is_mock": False,
        "source": "snapshot",
        "as_of": snap["created_at"],
        "snapshot_id": snap["id"],
        "trends": {
            r["skill_id"]: {
                "research_growth": r["research_growth"],
                "demand_growth": r["demand_growth"],
                "outlook": r["outlook"],
                "sources": json.loads(r["sources"]),
            }
            for r in rows
        },
    }


def get_trends():
    real = latest_snapshot_trends()
    if real is not None:
        return real
    mock = data_loader.mock_trends()
    return {
        "is_mock": True,
        "source": mock["source"],
        "as_of": mock["as_of"],
        "snapshot_id": None,
        "trends": mock["trends"],
    }
