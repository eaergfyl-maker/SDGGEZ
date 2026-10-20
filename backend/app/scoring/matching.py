"""Explainable role match score and skills gap. Owner: Member 3."""


def match_role(role: dict, owned: set[str], momentum_by_skill: dict[str, float | None]) -> dict:
    """Score = share of the role's importance-weighted skills the user already has (0-100).

    The gap lists missing skills, most important first, then fastest-rising first.
    """
    items = role["skills"]
    total = sum(i["importance"] for i in items)
    have = [i for i in items if i["skill"] in owned]
    score = round(100 * sum(i["importance"] for i in have) / total) if total else 0

    missing = [
        {
            "skill": i["skill"],
            "importance": i["importance"],
            "momentum": momentum_by_skill.get(i["skill"]),
        }
        for i in items
        if i["skill"] not in owned
    ]
    missing.sort(key=lambda m: (-m["importance"], -(m["momentum"] or 0)))

    return {
        "role_id": role["id"],
        "score": score,
        "matched": [i["skill"] for i in have],
        "missing": missing,
        "why": f"{len(have)} of {len(items)} skills matched, weighted by importance",
    }
