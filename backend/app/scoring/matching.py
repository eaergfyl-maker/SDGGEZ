"""Explainable role match score and skills gap. Owner: Member 3.

The score never looks at age, gender, ethnicity or name: only at the skills a person has.
A test checks that two people with the same skills always get the same result.
"""

IMPORTANCE = {3: "core", 2: "important", 1: "helpful"}


def _trend_words(value: float | None) -> str:
    if value is None:
        return "no trend data"
    if value >= 5:
        return f"rising {value:+g}%"
    if value <= -5:
        return f"declining {value:+g}%"
    return f"stable {value:+g}%"


def match_role(role: dict, owned: set[str], momentum_by_skill: dict[str, float | None],
               names: dict[str, str] | None = None) -> dict:
    """Score = share of the role's importance-weighted skills the user already has (0-100).

    The gap lists missing skills, most important first, then fastest-rising first.
    `why` is one plain sentence naming the biggest gap.
    """
    names = names or {}
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

    why = f"{len(have)} of {len(items)} skills matched, weighted by importance"
    if missing:
        top = missing[0]
        label = names.get(top["skill"], top["skill"])
        why += (f"; biggest gap: {label} ({IMPORTANCE[top['importance']]}, "
                f"{_trend_words(top['momentum'])})")
    else:
        why += "; no skills missing"

    return {
        "role_id": role["id"],
        "score": score,
        "matched": [i["skill"] for i in have],
        "missing": missing,
        "why": why,
    }
