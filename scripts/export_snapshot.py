"""Export the newest snapshot to data/snapshot_seed.json. Owner: Member 2."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app import db

SEED = Path(__file__).resolve().parents[1] / "data" / "snapshot_seed.json"


def export(conn, path: Path = SEED) -> dict:
    snap = conn.execute(
        "SELECT id, created_at, note FROM snapshots ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if snap is None:
        raise SystemExit("no snapshots to export")
    rows = conn.execute(
        "SELECT skill_id, research_growth, demand_growth, outlook, sources "
        "FROM skill_trends WHERE snapshot_id = ? ORDER BY skill_id",
        (snap["id"],),
    ).fetchall()
    seed = {
        "created_at": snap["created_at"],
        "note": snap["note"],
        "skills": [
            {
                "skill_id": r["skill_id"],
                "research_growth": r["research_growth"],
                "demand_growth": r["demand_growth"],
                "outlook": r["outlook"],
                "sources": json.loads(r["sources"]),
            }
            for r in rows
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(seed, indent=2, ensure_ascii=False), encoding="utf-8")
    return seed


if __name__ == "__main__":
    export(db.connect())
    print(f"seed written to {SEED}")