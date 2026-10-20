"""Ordered reskilling pathway toward a role. Owner: Member 3 (order), Member 5 (courses).

Only courses from data/courses.json are ever returned. Unverified courses are flagged, and
totals only count verified courses, so the app never presents unchecked information as fact.
"""
from .tree import skill_tiers


def needed_skills(role: dict, skills_by_id: dict, owned: set[str]) -> set[str]:
    """Role skills and required skills, plus all their prerequisites, minus what the user has."""
    todo = {i["skill"] for i in role["skills"]} | set(role["requires"])
    needed: set[str] = set()
    while todo:
        sid = todo.pop()
        if sid in needed or sid in owned:
            continue
        needed.add(sid)
        todo |= set(skills_by_id[sid]["prereqs"])
    return needed


def build_pathway(role: dict, skills: list[dict], courses: list[dict], owned: set[str]) -> dict:
    by_id = {s["id"]: s for s in skills}
    tiers = skill_tiers(skills)
    needed = sorted(needed_skills(role, by_id, owned), key=lambda sid: (tiers[sid], sid))

    steps, total_hours, total_cost, gaps = [], 0.0, 0.0, []
    for sid in needed:
        options = [c for c in courses if sid in c["skills"]]
        options.sort(key=lambda c: (not c["verified"], c["cost_myr"] or 0, c["hours"] or 0))
        best = next((c for c in options if c["verified"]), None)
        if best:
            total_hours += best["hours"]
            total_cost += best["cost_myr"]
        else:
            gaps.append(sid)
        steps.append({
            "skill": sid,
            "name": by_id[sid]["name"],
            "tier": tiers[sid],
            "courses": options,
            "recommended": best["id"] if best else None,
        })

    return {
        "role_id": role["id"],
        "steps": steps,
        "total_hours_verified": total_hours,
        "total_cost_myr_verified": total_cost,
        "skills_without_verified_course": gaps,
    }
