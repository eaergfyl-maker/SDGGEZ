"""'Ask your guide': answers questions about the user's own results. Owner: Member 3.

The model (the same Qwen3-8B RunPod endpoint as the CV reader) never answers from its own
knowledge. For every question the backend writes out the facts the app has already computed for
this user: their skills, their best roles with match scores and gaps, each skill's trend with its
source and date, and the courses on their pathway. The model is told to answer only from those
facts. Then the code checks the answer: every number in it must appear in the facts. If one does
not, the answer is not shown, because the brief forbids invented statistics.

Nothing is stored or logged: not the question, not the answer.
"""
import logging
import re

from . import cv_ai
from .momentum import low_data

MAX_QUESTION = 500
TOP_ROLES = 5
SMALL_NUMBERS = set(range(0, 11))     # list numbering and "2 skills" style counts are fine
NUMBER = re.compile(r"(?<![\w.])\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")
IMPORTANCE = {3: "core", 2: "important", 1: "useful"}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]

log = logging.getLogger(__name__)

SYSTEM = """You are the guide in Future-Ready RPG, a career planning game for workers whose jobs \
are changing because of AI. Answer the user's question using ONLY the facts below about their \
own results.
Rules:
- If the facts do not cover the question, say you do not have data on that. Only point to a \
part of the app if it really shows that thing. The app has: a skill tree (skills the user has, \
can learn, or must unlock first; roles at the top), a best-roles list (match % and outlook), a \
pathway (courses, hours, cost, weeks) and a Future Skills Radar (rising and falling skills with \
their sources). It has no salaries, job openings, employers or locations.
- The role outlook is the combined trend of the skills a role needs. It is not job growth or a \
number of jobs; never describe it that way.
- Never invent jobs, courses, numbers, dates or sources. Copy any number exactly as written in \
the facts, including the % sign.
- When you use a trend number, say where it comes from (job postings or arXiv research) and \
that it is an estimate.
- The user makes the decisions. Explain options; do not tell them what they must do.
- Only say the user has a skill if it is under "Skills the user ALREADY HAS". Skills under "can \
learn next" are ones they do NOT have yet.
- For pathway questions, use only the steps listed under "Learning pathway".
- Plain language, at most 120 words. No markdown headings.
- {language}"""

LANGUAGE = {"en": "Reply in English.", "ms": "Reply in Bahasa Malaysia (Malay)."}


def _date(iso: str | None) -> str:
    """'2026-10-19' -> '19 October 2026', '2026-09' -> 'September 2026' (models misread ISO dates)."""
    if not iso:
        return "an unknown date"
    parts = [int(x) for x in str(iso)[:10].split("-")]
    month = f"{MONTHS[parts[1] - 1]} {parts[0]}"
    return f"{parts[2]} {month}" if len(parts) == 3 else month


def _pct(v) -> str:
    return "no data" if v is None else f"{'+' if v > 0 else ''}{v}%"


def _trend_line(n: dict) -> str:
    c = n.get("components") or {}
    src = c.get("sources") or {}
    if n.get("momentum") is None and low_data(c):
        return (f"{n['name']}: no trend score, because too few postings or papers mention it to "
                f"trust a figure")
    parts = [f"{n['name']}: momentum {_pct(n.get('momentum'))} ({n.get('direction', 'unknown')})"]
    d = src.get("demand") or {}
    if c.get("demand_growth") is not None and d:
        parts.append(f"job demand {_pct(c['demand_growth'])} from {d.get('name')}: mentioned in "
                     f"{d.get('mentions_recent')} of {d.get('recent_postings')} postings since "
                     f"{_date(d.get('recent_from'))}, vs {d.get('mentions_previous')} in the 5 days before")
    r = src.get("research") or {}
    if c.get("research_growth") is not None and r.get("papers_recent") is not None:
        parts.append(f"research {_pct(c['research_growth'])} from arXiv: {r['papers_recent']} papers "
                     f"in the 3 months to the end of {_date(r.get('latest_month'))}, vs {r.get('papers_year_ago')} a year earlier")
    return "; ".join(parts)


def build_facts(tree: dict, pathway: dict | None, skill_names: dict[str, str],
                hours_per_week: float | None) -> str:
    """Everything the guide may say, as plain lines of text."""
    nodes = tree.get("nodes", [])
    skills = [n for n in nodes if n["kind"] == "skill"]
    roles = sorted((n for n in nodes if n["kind"] == "role"),
                   key=lambda n: -(n.get("match") or {}).get("score", 0))
    lines = [
        f"Data as of {_date(tree.get('as_of'))}. Scenario: {tree.get('scenario')} "
        f"(an assumption about how fast AI changes jobs, not a prediction). "
        f"Career area shown: {tree.get('family') or 'not chosen'}.",
        "Job demand data is mostly German/European postings with about one week of history, so it "
        "may not reflect Malaysia directly.",
    ]
    if tree.get("needs_family"):
        lines.append("The user has not chosen a career area yet, so no roles are shown.")

    have = [n["name"] for n in skills if n["state"] == "mastered"]
    lines.append("Skills the user ALREADY HAS: " + (", ".join(have) if have else "none ticked yet") + ".")

    if roles:
        lines.append("Best roles, ranked by how well the user's skills match:")
        for i, n in enumerate(roles[:TOP_ROLES], 1):
            m = n.get("match") or {}
            rng = n.get("outlook_range") or {}
            gaps = ", ".join(
                f"{skill_names.get(g['skill'], g['skill'])} ({IMPORTANCE.get(g.get('importance'), 'needed')}, "
                f"momentum {_pct(g.get('momentum'))})" for g in m.get("missing", [])) or "none"
            lines.append(
                f"{i}. {n.get('full_name') or n['name']}: match {m.get('score')}%; role outlook "
                f"{_pct(n.get('outlook'))} in this scenario (range {_pct(rng.get('min'))} to "
                f"{_pct(rng.get('max'))} across scenarios); missing skills: {gaps}. {m.get('why', '')}")

    can_learn = [n for n in skills if n["state"] == "available"]
    if can_learn:
        lines.append("Skills the user does NOT have yet but can learn next, with their trends:")
        lines += [f"- {_trend_line(n)}" for n in can_learn]
    if have:
        lines.append("Trends for skills the user ALREADY HAS:")
        lines += [f"- {_trend_line(n)}" for n in skills if n["state"] == "mastered"]
    locked = [n["name"] for n in skills if n["state"] == "locked"]
    if locked:
        lines.append("Locked skills the user does NOT have (need easier skills first): " + ", ".join(locked) + ".")

    if pathway:
        role = next((n for n in roles if n["id"] == pathway["role_id"]), None)
        title = (role or {}).get("full_name") or pathway["role_id"]
        lines.append(f"Learning pathway to {title}:")
        for i, s in enumerate(pathway.get("steps", []), 1):
            course = next((c for c in s.get("courses", []) if c["id"] == s.get("recommended")), None)
            lines.append(f"{i}. {s['name']}: " + (
                f"course '{course['title']}' by {course['provider']}, {course['hours']} hours, "
                f"RM{course['cost_myr']}" if course else "no verified course yet"))
        steps = pathway.get("steps", [])
        missing = [s["name"] for s in steps if not s.get("recommended")]
        if pathway.get("estimated_weeks") is not None and len(missing) < len(steps):
            lines.append(f"Time for the steps that have a verified course: "
                         f"{pathway['total_hours_verified']} hours, about {pathway['estimated_weeks']} "
                         f"week(s) at {hours_per_week} hours a week.")
        if missing:
            lines.append(f"{len(missing)} of {len(steps)} steps have no verified course yet ("
                         + ", ".join(missing) + "), so the full pathway will take longer and the app "
                         "does not know how much longer.")
    return "\n".join(lines)


def _value(token: str) -> float:
    return float(token.replace(",", ""))


def unsupported_numbers(answer: str, facts: str) -> list[str]:
    """Numbers in the answer that are not in the facts (rounding a fact to a whole number is ok)."""
    known = {_value(t) for t in NUMBER.findall(facts)}
    known |= {float(round(v)) for v in known} | {float(v) for v in SMALL_NUMBERS}
    return [t for t in NUMBER.findall(answer) if _value(t) not in known]


def answer(question: str, facts: str, lang: str = "en", call=None) -> dict:
    """status: "ok", "off" (no RunPod settings), "error" (model unreachable) or "unverified"
    (the answer used a number that is not in the facts, so it is withheld)."""
    if not cv_ai.enabled():
        return {"status": "off", "answer": None}
    messages = [
        {"role": "system", "content": SYSTEM.format(language=LANGUAGE.get(lang, LANGUAGE["en"]))
         + "\n\nFACTS:\n" + facts},
        {"role": "user", "content": question.strip() + "\n/no_think"},
    ]
    try:
        text = (call or cv_ai.call_model)(messages)
    except cv_ai.AIUnavailable as e:
        log.warning("guide unavailable: %s", e)          # never log the question
        return {"status": "error", "answer": None}
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    if not text:
        return {"status": "error", "answer": None}
    bad = unsupported_numbers(text, facts)
    if bad:
        return {"status": "unverified", "answer": None, "unsupported": bad}
    return {"status": "ok", "answer": text}
