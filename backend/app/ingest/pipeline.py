"""Run ingestion and save a snapshot of skill trends. Owner: Member 2.

    python -m backend.app.ingest.pipeline               # job postings only (cached)
    python -m backend.app.ingest.pipeline --arxiv       # also fetch arXiv counts (slow, resumable)
    python -m backend.app.ingest.pipeline --no-jobs     # recompute from what is already stored

Every snapshot row records where each number came from, so the UI can cite it.
"""
import argparse
import json
import logging
from datetime import datetime, timezone

from .. import config, data_loader, db
from . import arbeitnow, arxiv, mentions, remotive

log = logging.getLogger(__name__)
JOB_SOURCES = (("arbeitnow", arbeitnow), ("remotive", remotive))


def run(conn, refresh_arxiv: bool = False, refresh_jobs: bool = True, note: str = "") -> int:
    skills = data_loader.skills()
    if refresh_arxiv:
        arxiv.fetch_monthly_counts(conn, skills)
    if refresh_jobs:
        for name, source in JOB_SOURCES:
            try:
                new = source.store(conn, source.fetch())
                log.info("%s: %d new postings", name, new)
            except Exception as err:  # one source being down must not stop the snapshot
                log.warning("%s failed, continuing without it: %s", name, err)

    created = datetime.now(timezone.utc).isoformat()
    snap_id = conn.execute(
        "INSERT INTO snapshots (created_at, note) VALUES (?, ?)", (created, note)
    ).lastrowid

    for s in skills:
        counts = arxiv.load_counts(conn, s["id"])
        research = arxiv.research_growth(counts)
        demand, demand_details = mentions.demand_growth(
            conn, s["keywords"], window_days=config.DEMAND_WINDOW_DAYS)
        sources = {
            "research": {"name": "arXiv API", "months": len(counts),
                         "latest_month": max(counts) if counts else None},
            "demand": {"name": "Arbeitnow + Remotive job postings",
                       "caveat": ("mostly German/European postings; about one week of history; the older window "
                                  "only holds postings still live today"),
                       **demand_details},
            "outlook": None,
        }
        conn.execute(
            "INSERT INTO skill_trends VALUES (?, ?, ?, ?, ?, ?)",
            (snap_id, s["id"], research, demand, None, json.dumps(sources)),
        )
    conn.commit()
    return snap_id


def diff_last_two(conn) -> list[dict]:
    """Per-skill changes between the two most recent snapshots (for the patch-notes banner)."""
    snaps = [r["id"] for r in conn.execute("SELECT id FROM snapshots ORDER BY id DESC LIMIT 2")]
    if len(snaps) < 2:
        return []
    new_id, old_id = snaps
    rows = conn.execute(
        """SELECT n.skill_id,
                  o.research_growth AS old_research, n.research_growth AS new_research,
                  o.demand_growth AS old_demand, n.demand_growth AS new_demand
           FROM skill_trends n JOIN skill_trends o
             ON o.skill_id = n.skill_id AND o.snapshot_id = ?
           WHERE n.snapshot_id = ?""",
        (old_id, new_id),
    )
    changes = []
    for r in rows:
        for field in ("research", "demand"):
            old, new = r[f"old_{field}"], r[f"new_{field}"]
            if old != new:
                changes.append({"skill": r["skill_id"], "signal": field, "old": old, "new": new})
    return changes


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--arxiv", action="store_true", help="fetch arXiv counts (slow, resumable)")
    parser.add_argument("--no-jobs", action="store_true", help="skip fetching job postings")
    parser.add_argument("--note", default="")
    args = parser.parse_args()
    conn = db.connect()
    snap = run(conn, refresh_arxiv=args.arxiv, refresh_jobs=not args.no_jobs, note=args.note)
    print(f"snapshot {snap} saved")


if __name__ == "__main__":
    main()
