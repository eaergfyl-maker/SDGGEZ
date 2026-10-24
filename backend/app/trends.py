"""Where the API gets trend components from. Owner: Member 1 (wiring), Member 2 (data).

Order: the latest snapshot in the local database (after running the pipeline); otherwise the
committed real snapshot in data/snapshot_seed.json (what Replit uses, since the database is not
committed); only if neither exists, data/mock_trends.json, clearly marked is_mock=True.
"""
import json

from . import config, data_loader, db
from .scoring.momentum import low_data


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


SEED = config.DATA_DIR / "snapshot_seed.json"
# The seed before the current one (kept by scripts/export_snapshot.py), so the app can show
# what changed between two real snapshots even where there is no database (Replit).
PREVIOUS = config.DATA_DIR / "snapshot_previous.json"
SIGNALS = ("research", "demand")


def seed_trends():
    """The real snapshot committed to the repo by scripts/export_snapshot.py."""
    if not SEED.exists():
        return None
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    return {
        "is_mock": False,
        "source": "snapshot",
        "as_of": seed["created_at"],
        "snapshot_id": None,
        "trends": {
            s["skill_id"]: {k: s[k] for k in ("research_growth", "demand_growth", "outlook", "sources")}
            for s in seed["skills"]
        },
    }


def _read(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def seed_changes():
    """Per-skill changes between the previous seed and the current one, in the same shape as
    pipeline.diff_last_two, plus the two dates. None if either file is missing."""
    old, new = _read(PREVIOUS), _read(SEED)
    if not old or not new:
        return None
    before = {s["skill_id"]: s for s in old["skills"]}
    changes = []
    for s in new["skills"]:
        o = before.get(s["skill_id"], {})
        for signal in SIGNALS:
            key = f"{signal}_growth"
            a, b = o.get(key), s.get(key)
            if a != b:
                # reliable: both values exist and neither rests on too few postings or papers
                reliable = (a is not None and b is not None
                            and key not in low_data(o) and key not in low_data(s))
                changes.append({"skill": s["skill_id"], "signal": signal, "old": a, "new": b,
                                "reliable": reliable})
    return {"changes": changes, "from": old["created_at"], "to": new["created_at"]}


def get_trends():
    real = latest_snapshot_trends() or seed_trends()
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
