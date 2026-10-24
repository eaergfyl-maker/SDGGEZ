"""SQLite storage for ingested data. Owner: Member 2."""
import json
import sqlite3
from pathlib import Path

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS postings (
    id TEXT PRIMARY KEY,            -- "<source>:<source id>"
    source TEXT NOT NULL,           -- e.g. "remotive"
    title TEXT NOT NULL,
    tags TEXT NOT NULL,             -- JSON array
    description TEXT NOT NULL,
    url TEXT NOT NULL,
    published_at TEXT NOT NULL,     -- ISO 8601
    fetched_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS arxiv_counts (
    skill_id TEXT NOT NULL,
    month TEXT NOT NULL,            -- "YYYY-MM"
    count INTEGER NOT NULL,
    query TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    PRIMARY KEY (skill_id, month)
);

CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    note TEXT
);

CREATE TABLE IF NOT EXISTS skill_trends (
    snapshot_id INTEGER NOT NULL REFERENCES snapshots(id),
    skill_id TEXT NOT NULL,
    research_growth REAL,           -- % change, NULL if unknown
    demand_growth REAL,             -- % change, NULL if unknown
    outlook REAL,                   -- from a cited report, NULL if none
    sources TEXT NOT NULL,          -- JSON object describing where each value came from
    PRIMARY KEY (snapshot_id, skill_id)
);
"""


def connect(path: Path | None = None) -> sqlite3.Connection:
    path = path or config.DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn

def load_seed_if_empty(conn: sqlite3.Connection, seed_path: Path | None = None) -> bool:
    """If there are no snapshots yet, load data/snapshot_seed.json so a fresh database
    (Replit, a teammate's machine) shows real numbers instead of mock data.
    Returns True if the seed was loaded, False otherwise."""
    seed_path = seed_path or (Path(__file__).resolve().parents[2] / "data" / "snapshot_seed.json")
    if conn.execute("SELECT 1 FROM snapshots LIMIT 1").fetchone():
        return False
    if not seed_path.exists():
        return False
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    snap_id = conn.execute(
        "INSERT INTO snapshots (created_at, note) VALUES (?, ?)",
        (seed["created_at"], (seed.get("note") or "") + " (seed)"),
    ).lastrowid
    for s in seed["skills"]:
        conn.execute(
            "INSERT INTO skill_trends VALUES (?, ?, ?, ?, ?, ?)",
            (
                snap_id,
                s["skill_id"],
                s["research_growth"],
                s["demand_growth"],
                s["outlook"],
                json.dumps(s["sources"]),
            ),
        )
    conn.commit()
    return True