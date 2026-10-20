"""Paths and settings shared by the whole backend."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
STORY_DIR = ROOT / "story"
FRONTEND_DIR = ROOT / "frontend"
CACHE_DIR = ROOT / ".cache"

DB_PATH = ROOT / os.environ.get("DB_PATH", "data/app.db")
INGEST_CONTACT = os.environ.get("INGEST_CONTACT", "")
USER_AGENT = f"future-ready-rpg/0.1 ({INGEST_CONTACT})" if INGEST_CONTACT else "future-ready-rpg/0.1"
