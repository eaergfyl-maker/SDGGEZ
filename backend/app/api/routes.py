"""HTTP API. Owner: Member 1. Response shapes here are shared contracts with the frontend;
change them only after noting it in docs/DECISIONS.md.
"""
from enum import Enum

import yaml
from fastapi import APIRouter, BackgroundTasks, HTTPException, Path, Query

from .. import config, data_loader, db, trends
from ..ingest import pipeline
from ..scoring.momentum import direction, momentum
from ..scoring.pathway import build_pathway
from ..scoring.tree import build_tree, family_subset

router = APIRouter()


class Scenario(str, Enum):
    slow = "slow"
    moderate = "moderate"
    fast = "fast"


def _owned(persona_id: str, owned: str | None) -> set[str]:
    """Skills the user has: the explicit list if given, otherwise the persona's starting skills."""
    known = data_loader.skills_by_id()
    if owned is not None:
        ids = {s for s in owned.split(",") if s}
        unknown = ids - known.keys()
        if unknown:
            raise HTTPException(422, f"unknown skill ids: {sorted(unknown)}")
        return ids
    p = data_loader.persona(persona_id)
    if p is None:
        raise HTTPException(404, f"unknown persona: {persona_id}")
    return set(p["skills"])


@router.get("/health")
def health():
    return {"ok": True}


@router.get("/personas")
def personas():
    return data_loader.personas()


@router.get("/sdgs")
def sdgs():
    return data_loader.sdg_map()


@router.get("/trends")
def get_trends(scenario: Scenario = Scenario.moderate):
    t = trends.get_trends()
    items = []
    for s in data_loader.skills():
        comp = t["trends"].get(s["id"], {})
        m = momentum(comp, scenario.value)
        items.append({"skill": s["id"], "name": s["name"], "momentum": m,
                      "direction": direction(m), "components": comp})
    return {"scenario": scenario.value, "is_mock": t["is_mock"], "source": t["source"],
            "as_of": t["as_of"], "skills": items}


@router.get("/families")
def families():
    return data_loader.families()


@router.get("/tree")
def get_tree(persona: str = "aisyah", scenario: Scenario = Scenario.moderate,
             owned: str | None = Query(None, description="comma-separated skill ids"),
             family: str | None = Query(None, description="family id, or 'all'; default: the persona's family")):
    if family is None:
        p = data_loader.persona(persona)
        family = p["family"] if p else "all"
    if family == "all":
        skills, roles = data_loader.skills(), data_loader.roles()
    elif family in {f["id"] for f in data_loader.families()}:
        skills, roles = family_subset(data_loader.skills(), data_loader.roles(), family)
    else:
        raise HTTPException(404, f"unknown family: {family}")
    tree = build_tree(skills, roles, _owned(persona, owned), trends.get_trends(), scenario.value)
    return {**tree, "family": family}


@router.get("/pathway")
def get_pathway(role: str, persona: str = "aisyah", owned: str | None = None):
    r = data_loader.roles_by_id().get(role)
    if r is None:
        raise HTTPException(404, f"unknown role: {role}")
    return build_pathway(r, data_loader.skills(), data_loader.courses(), _owned(persona, owned))


@router.get("/story/{node_id}")
def get_story(node_id: str = Path(pattern=r"^[a-z0-9_]+$")):
    """Story text for a node, or {} if the writers haven't added one yet."""
    path = config.STORY_DIR / "nodes" / f"{node_id}.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


@router.get("/changes")
def changes():
    """What changed between the last two snapshots (patch notes)."""
    if not config.DB_PATH.exists():
        return {"changes": []}
    conn = db.connect()
    try:
        return {"changes": pipeline.diff_last_two(conn)}
    finally:
        conn.close()


def _refresh_job():
    conn = db.connect()
    try:
        pipeline.run(conn, note="manual refresh")
    finally:
        conn.close()


@router.post("/refresh", status_code=202)
def refresh(background: BackgroundTasks):
    """Fetch new job data (cached, rate-limited) and save a new snapshot in the background.

    TODO (Member 1): protect this before the public demo so anyone can't trigger it repeatedly.
    """
    background.add_task(_refresh_job)
    return {"started": True}
