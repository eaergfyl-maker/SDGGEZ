"""HTTP API. Owner: Member 1. Response shapes here are shared contracts with the frontend;
change them only after noting it in docs/DECISIONS.md.
"""
import base64
import binascii
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from enum import Enum

import yaml
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Path, Query
from pydantic import BaseModel, Field

from .. import config, data_loader, db, trends
from ..ingest import pipeline
from ..scoring import chat, cv, cv_ai
from ..scoring.momentum import direction, low_data, momentum
from ..scoring.pathway import build_pathway
from ..scoring.tree import build_tree, family_subset, infer_family

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
                      "direction": direction(m), "components": comp, "low_data": low_data(comp)})
    return {"scenario": scenario.value, "is_mock": t["is_mock"], "source": t["source"],
            "as_of": t["as_of"], "skills": items}


class CVText(BaseModel):
    text: str = Field(min_length=1, max_length=cv.MAX_CHARS)


@router.post("/cv/skills")
def cv_skills(body: CVText):
    """Skills found in pasted CV text, each with the evidence that triggered it.

    The text is processed in memory and never stored or logged. Emails and long numbers are
    removed before matching. Use invented CVs only (see /api/cv/samples).
    """
    return cv.match_cv(body.text, data_loader.skills())


class CVFile(BaseModel):
    data: str = Field(min_length=1, max_length=cv.MAX_FILE_BYTES * 4 // 3 + 4)  # base64 of a .docx


@router.post("/cv/file")
def cv_file(body: CVFile):
    """Text of an uploaded Word .docx CV, for the person to review before matching.

    Nothing is stored or logged; the text goes back to the browser only.
    """
    try:
        text = cv.docx_text(base64.b64decode(body.data, validate=True))
    except (ValueError, binascii.Error):
        raise HTTPException(422, "Could not read this file. Save it as .docx or paste the text.")
    return {"text": text[:cv.MAX_CHARS], "truncated": len(text) > cv.MAX_CHARS}


@router.get("/cv/ai")
def cv_ai_status():
    """Whether AI suggestions are switched on (RunPod settings present). Does not call the model."""
    return {"enabled": cv_ai.enabled(), "model": cv_ai.model_name()}


@router.post("/cv/ai")
def cv_ai_suggest(body: CVText):
    """Extra skills suggested by the model, each checked against the skill list and the CV text.

    Slower than /cv/skills (seconds, or up to 90 s on a cold start), so the UI calls it after
    showing the keyword results. Same privacy rules: redacted first, never stored or logged.
    """
    return cv_ai.suggest(body.text, data_loader.skills())


@router.get("/cv/samples")
def cv_samples():
    """Invented sample CVs for trying the CV reader without real personal data."""
    return data_loader.sample_cvs()


@router.get("/families")
def families():
    """Career areas, each with the skill ids its roles use (a skill can be in several areas)."""
    skills, roles = data_loader.skills(), data_loader.roles()
    return [{**f, "skills": [s["id"] for s in family_subset(skills, roles, f["id"])[0]]}
            for f in data_loader.families()]


@router.get("/tree")
def get_tree(persona: str = "aisyah", scenario: Scenario = Scenario.moderate,
             owned: str | None = Query(None, description="comma-separated skill ids"),
             family: str | None = Query(None, description=(
                 "career area id, 'all', or 'auto' (guess from the skills); "
                 "default: the persona's area, or 'auto' for a custom profile"))):
    return _tree_for(persona, scenario, _owned(persona, owned), family)


def _tree_for(persona: str, scenario: Scenario, owned_ids: set[str], family: str | None) -> dict:
    families = data_loader.families()
    if family is None:
        p = data_loader.persona(persona)
        family = p["family"] if p else "auto"

    guess = None
    if family == "auto":
        guess = infer_family(owned_ids, data_loader.skills(), data_loader.roles(), families)
        family = guess["family"]
    extra = {
        "family_inferred": guess is not None,
        "family_ambiguous": bool(guess and guess["ambiguous"]),
        "family_ranked": guess["ranked"] if guess else None,
    }

    if family is None:
        # Nothing to guess from (no skills, or none tied to an area): ask instead of guessing.
        t = trends.get_trends()
        return {"scenario": scenario.value, "is_mock": t["is_mock"], "as_of": t["as_of"],
                "source": t["source"], "nodes": [], "edges": [], "family": None,
                "needs_family": True, **extra}
    if family == "all":
        skills, roles = data_loader.skills(), data_loader.roles()
    elif family in {f["id"] for f in families}:
        skills, roles = family_subset(data_loader.skills(), data_loader.roles(), family)
    else:
        raise HTTPException(404, f"unknown family: {family}")
    tree = build_tree(skills, roles, owned_ids, trends.get_trends(), scenario.value)
    return {**tree, "family": family, "needs_family": False, **extra}


@router.get("/pathway")
def get_pathway(role: str, persona: str = "aisyah", owned: str | None = None,
                hours_per_week: float | None = Query(None, gt=0, le=80,
                                                     description="default: the persona's study hours")):
    r = data_loader.roles_by_id().get(role)
    if r is None:
        raise HTTPException(404, f"unknown role: {role}")
    if hours_per_week is None:
        p = data_loader.persona(persona)
        hours_per_week = p["hours_per_week"] if p else None
    return build_pathway(r, data_loader.skills(), data_loader.courses(), _owned(persona, owned),
                         hours_per_week)


class ChatQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=chat.MAX_QUESTION)
    persona: str = "aisyah"
    owned: list[str] | None = Field(None, max_length=200)
    scenario: Scenario = Scenario.moderate
    family: str | None = None
    role: str | None = None          # the role the user selected, if any
    hours_per_week: float | None = Field(None, gt=0, le=80)
    lang: str = Field("en", pattern="^(en|ms)$")


@router.get("/chat")
def chat_status():
    """Whether the guide is switched on (RunPod settings present). Does not call the model."""
    return {"enabled": cv_ai.enabled(), "model": cv_ai.model_name()}


@router.post("/chat")
def ask_guide(body: ChatQuestion):
    """Answer a question about the user's own results, from facts the app computed.

    The answer is withheld (status "unverified") if it contains a number that is not in those
    facts. Nothing is stored or logged.
    """
    owned_ids = _owned(body.persona, ",".join(body.owned) if body.owned is not None else None)
    tree = _tree_for(body.persona, body.scenario, owned_ids, body.family)
    roles = sorted((n for n in tree["nodes"] if n["kind"] == "role"),
                   key=lambda n: -(n.get("match") or {}).get("score", 0))
    focus = next((n for n in roles if n["id"] == body.role), roles[0] if roles else None)
    hours = body.hours_per_week
    if hours is None:
        p = data_loader.persona(body.persona)
        hours = p["hours_per_week"] if p else None
    path = None
    if focus:
        path = build_pathway(data_loader.roles_by_id()[focus["id"]], data_loader.skills(),
                             data_loader.courses(), owned_ids, hours)
    names = {s["id"]: s["name"] for s in data_loader.skills()}
    facts = chat.build_facts(tree, path, names, hours)
    return {**chat.answer(body.question, facts, body.lang),
            "as_of": tree.get("as_of"), "focus_role": focus and (focus.get("full_name") or focus["name"])}


@router.get("/story/{node_id}")
def get_story(node_id: str = Path(pattern=r"^[a-z0-9_]+$")):
    """Story text for a node, or {} if the writers haven't added one yet."""
    path = config.STORY_DIR / "nodes" / f"{node_id}.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


@router.get("/changes")
def changes():
    """What changed between the last two snapshots (patch notes).

    Uses the local database when it holds two snapshots; otherwise the two committed seed
    snapshots (data/snapshot_previous.json -> data/snapshot_seed.json), so deployments without
    a database still show real changes.
    """
    if config.DB_PATH.exists():
        conn = db.connect()
        try:
            snaps = conn.execute(
                "SELECT created_at FROM snapshots ORDER BY id DESC LIMIT 2").fetchall()
            if len(snaps) == 2:
                return {"changes": pipeline.diff_last_two(conn),
                        "from": snaps[1]["created_at"], "to": snaps[0]["created_at"]}
        finally:
            conn.close()
    return trends.seed_changes() or {"changes": [], "from": None, "to": None}


def _refresh_job():
    conn = db.connect()
    try:
        pipeline.run(conn, note="manual refresh")
    finally:
        conn.close()


REFRESH_COOLDOWN_MINUTES = 30


def require_refresh_token(x_refresh_token: str | None = Header(None)):
    """Only callers who send the secret token in the X-Refresh-Token header may refresh."""
    expected = os.environ.get("REFRESH_TOKEN")
    if not expected or x_refresh_token != expected:
        raise HTTPException(403, "Refresh is restricted")


def refresh_cooldown():
    """Refuse a refresh if a snapshot was saved in the last REFRESH_COOLDOWN_MINUTES."""
    if not config.DB_PATH.exists():
        return
    conn = db.connect()
    try:
        row = conn.execute("SELECT created_at FROM snapshots ORDER BY id DESC LIMIT 1").fetchone()
    except sqlite3.OperationalError:
        return  # no snapshots table yet, so there is nothing to cool down from
    finally:
        conn.close()
    if row is None:
        return
    last = datetime.fromisoformat(row["created_at"])
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    if last > datetime.now(timezone.utc) - timedelta(minutes=REFRESH_COOLDOWN_MINUTES):
        raise HTTPException(429, "A refresh ran recently; try again later")


@router.post("/refresh", status_code=202,
             dependencies=[Depends(require_refresh_token), Depends(refresh_cooldown)])
def refresh(background: BackgroundTasks):
    """Fetch new job data (cached, rate-limited) and save a new snapshot in the background.

    Needs the X-Refresh-Token header, and is limited to one refresh per 30 minutes.
    """
    background.add_task(_refresh_job)
    return {"started": True}
