"""Build the skill tree the frontend draws. Owner: Member 3 (logic), Member 4 (consumer).

Node states:
  mastered   the user has the skill
  available  all prerequisites mastered, can be trained next
  locked     at least one prerequisite missing
Roles sit one tier above their required skills and use the same states.
"""
from .matching import match_role
from .momentum import SCENARIOS, direction, low_data, momentum


def skill_tiers(skills: list[dict]) -> dict[str, int]:
    by_id = {s["id"]: s for s in skills}
    tiers: dict[str, int] = {}

    def tier(sid):
        if sid not in tiers:
            prereqs = by_id[sid]["prereqs"]
            tiers[sid] = 0 if not prereqs else 1 + max(tier(p) for p in prereqs)
        return tiers[sid]

    for s in skills:
        tier(s["id"])
    return tiers


def family_subset(skills: list[dict], roles: list[dict], family: str) -> tuple[list[dict], list[dict]]:
    """The roles in one family plus every skill they use, including all prerequisites.

    Keeps each tree small enough to draw (at most 5 nodes per tier; a data test checks it).
    """
    fam_roles = [r for r in roles if r["family"] == family]
    by_id = {s["id"]: s for s in skills}
    todo = {i["skill"] for r in fam_roles for i in r["skills"]}
    todo |= {sid for r in fam_roles for sid in r["requires"]}
    needed: set[str] = set()
    while todo:
        sid = todo.pop()
        if sid not in needed:
            needed.add(sid)
            todo |= set(by_id[sid]["prereqs"])
    return [s for s in skills if s["id"] in needed], fam_roles


def role_outlook(role: dict, mom: dict[str, float | None]) -> float | None:
    """Importance-weighted average momentum of the role's skills: is this role growing?

    Kept separate from the match score: match says how well you fit today, outlook says
    whether the role's skills are rising. Skills without data are left out.
    """
    pairs = [(i["importance"], mom.get(i["skill"])) for i in role["skills"]]
    pairs = [(w, m) for w, m in pairs if m is not None]
    if not pairs:
        return None
    return round(sum(w * m for w, m in pairs) / sum(w for w, _ in pairs), 1)


def outlook_range(role: dict, components: dict) -> dict | None:
    """Role outlook under every scenario, so the UI can show a range instead of one guess."""
    values = {}
    for scenario in SCENARIOS:
        mom = {i["skill"]: momentum(components.get(i["skill"], {}), scenario) for i in role["skills"]}
        values[scenario] = role_outlook(role, mom)
    known = [v for v in values.values() if v is not None]
    if not known:
        return None
    return {"min": min(known), "max": max(known), "by_scenario": values}


def _state(owned: set[str], node_id: str, needs: list[str]) -> str:
    if node_id in owned:
        return "mastered"
    return "available" if all(n in owned for n in needs) else "locked"


def build_tree(skills, roles, owned: set[str], trends: dict, scenario: str) -> dict:
    tiers = skill_tiers(skills)
    components = trends["trends"]
    mom = {s["id"]: momentum(components.get(s["id"], {}), scenario) for s in skills}
    names = {s["id"]: s["name"] for s in skills}

    nodes, edges = [], []
    for s in skills:
        nodes.append({
            "id": s["id"],
            "kind": "skill",
            "name": s["name"],
            "tier": tiers[s["id"]],
            "state": _state(owned, s["id"], s["prereqs"]),
            "momentum": mom[s["id"]],
            "direction": direction(mom[s["id"]]),
            "components": components.get(s["id"], {}),
            "low_data": low_data(components.get(s["id"], {})),
            "sdg": s["sdg"],
        })
        edges += [{"from": p, "to": s["id"]} for p in s["prereqs"]]

    for r in roles:
        nodes.append({
            "id": r["id"],
            "kind": "role",
            "name": r["short_name"],
            "full_name": r["name"],
            "tier": 1 + max(tiers[sid] for sid in r["requires"]),
            "state": "available" if all(sid in owned for sid in r["requires"]) else "locked",
            "match": match_role(r, owned, mom, names),
            "outlook": role_outlook(r, mom),
            "outlook_range": outlook_range(r, components),
            "sdg": r["sdg"],
            "based_on": r.get("based_on"),
        })
        edges += [{"from": sid, "to": r["id"]} for sid in r["requires"]]

    return {
        "scenario": scenario,
        "is_mock": trends["is_mock"],
        "as_of": trends["as_of"],
        "source": trends["source"],
        "nodes": nodes,
        "edges": edges,
    }
