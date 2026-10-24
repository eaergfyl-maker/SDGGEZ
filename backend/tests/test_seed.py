import importlib.util
import json
from pathlib import Path

from backend.app import db

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("export_snapshot", ROOT / "scripts" / "export_snapshot.py")
export_snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export_snapshot)


def test_export_writes_newest_snapshot(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    conn.execute("INSERT INTO snapshots (id, created_at, note) VALUES (1, '2026-10-21', 'old')")
    conn.execute("INSERT INTO snapshots (id, created_at, note) VALUES (2, '2026-10-24', 'new')")
    conn.execute("INSERT INTO skill_trends VALUES (1, 'sql', NULL, 5.0, NULL, '{}')")
    conn.execute("INSERT INTO skill_trends VALUES (2, 'sql', NULL, 9.0, NULL, '{}')")
    conn.commit()

    out = tmp_path / "seed.json"
    seed = export_snapshot.export(conn, out)

    assert seed["note"] == "new"
    assert seed["skills"][0]["demand_growth"] == 9.0
    assert json.loads(out.read_text(encoding="utf-8"))["note"] == "new"

def test_load_seed_if_empty_loads_when_no_snapshots(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    seed_path = tmp_path / "snapshot_seed.json"
    seed_path.write_text(json.dumps({
        "created_at": "2026-10-24T00:00:00+00:00",
        "note": "test seed",
        "skills": [
            {"skill_id": "sql", "research_growth": None, "demand_growth": 5.0,
             "outlook": None, "sources": {}},
        ],
    }), encoding="utf-8")

    loaded = db.load_seed_if_empty(conn, seed_path)

    assert loaded is True
    snap = conn.execute("SELECT id, note FROM snapshots").fetchone()
    assert "seed" in snap["note"]
    row = conn.execute("SELECT skill_id, demand_growth FROM skill_trends").fetchone()
    assert row["skill_id"] == "sql"
    assert row["demand_growth"] == 5.0


def test_load_seed_if_empty_skips_when_snapshot_exists(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    conn.execute("INSERT INTO snapshots (created_at, note) VALUES ('2026-10-20', 'real run')")
    conn.commit()
    seed_path = tmp_path / "snapshot_seed.json"
    seed_path.write_text(json.dumps({
        "created_at": "2026-10-24T00:00:00+00:00", "note": "test seed", "skills": [],
    }), encoding="utf-8")

    loaded = db.load_seed_if_empty(conn, seed_path)

    assert loaded is False
    count = conn.execute("SELECT count(*) n FROM snapshots").fetchone()["n"]
    assert count == 1


def test_load_seed_if_empty_returns_false_when_no_seed_file(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    loaded = db.load_seed_if_empty(conn, tmp_path / "does_not_exist.json")
    assert loaded is False