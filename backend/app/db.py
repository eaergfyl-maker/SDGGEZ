"""SQLite storage for ingested data. Owner: Member 2."""
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
