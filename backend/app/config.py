"""Paths and settings shared by the whole backend."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_env_file(path: Path) -> None:
    """Read KEY=value lines from a local .env. Real environment variables (Replit Secrets) win."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


_load_env_file(ROOT / ".env")

DATA_DIR = ROOT / "data"
STORY_DIR = ROOT / "story"
FRONTEND_DIR = ROOT / "frontend"
CACHE_DIR = ROOT / ".cache"

DB_PATH = ROOT / os.environ.get("DB_PATH", "data/app.db")
INGEST_CONTACT = os.environ.get("INGEST_CONTACT", "")
USER_AGENT = f"future-ready-rpg/0.1 ({INGEST_CONTACT})" if INGEST_CONTACT else "future-ready-rpg/0.1"

# Days per window when comparing job-posting skill mentions. Job feeds only reach back about
# a week, so 5 days (recent vs the 5 days before) is what the data supports right now.
DEMAND_WINDOW_DAYS = int(os.environ.get("DEMAND_WINDOW_DAYS", "5"))
