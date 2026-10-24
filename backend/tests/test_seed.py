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


def test_export_keeps_the_replaced_seed_as_previous(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    out = tmp_path / "snapshot_seed.json"
    out.write_text(json.dumps({"created_at": "2026-10-22", "note": "older", "skills": []}), encoding="utf-8")
    conn.execute("INSERT INTO snapshots (id, created_at, note) VALUES (1, '2026-10-24', 'new')")
    conn.commit()
    export_snapshot.export(conn, out)
    assert json.loads((tmp_path / "snapshot_previous.json").read_text(encoding="utf-8"))["note"] == "older"
    export_snapshot.export(conn, out)   # same snapshot again: previous is not overwritten
    assert json.loads((tmp_path / "snapshot_previous.json").read_text(encoding="utf-8"))["note"] == "older"