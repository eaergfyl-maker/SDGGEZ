from backend.app.scoring.matching import match_role
from backend.app.scoring.momentum import direction, momentum
from backend.app.scoring.pathway import build_pathway
from backend.app.scoring.tree import build_tree, skill_tiers

SKILLS = [
    {"id": "a", "name": "A", "prereqs": [], "keywords": ["a"], "sdg": [8]},
    {"id": "b", "name": "B", "prereqs": ["a"], "keywords": ["b"], "sdg": [4]},
    {"id": "c", "name": "C", "prereqs": ["b"], "keywords": ["c"], "sdg": [9]},
]
ROLE = {
    "id": "r", "name": "Role", "short_name": "Role", "requires": ["c"], "sdg": [8],
    "skills": [{"skill": "a", "importance": 1}, {"skill": "b", "importance": 3},
               {"skill": "c", "importance": 2}],
}
TRENDS = {"is_mock": True, "source": "MOCK", "as_of": "2026-10-20",
          "trends": {"a": {"demand_growth": -10}, "b": {"demand_growth": 40}, "c": {}}}


def course(cid, skill, verified=True, hours=5, cost=0):
    return {"id": cid, "title": cid, "provider": "p", "url": "https://example.org" if verified else None,
            "hours": hours if verified else None, "cost_myr": cost if verified else None,
            "skills": [skill], "funding_note": None, "verified": verified,
            "checked_on": "2026-10-20" if verified else None}


def test_momentum_uses_only_available_components():
    assert momentum({"demand_growth": 20, "research_growth": None}) == 20.0


def test_momentum_none_without_data():
    assert momentum({}) is None


def test_fast_scenario_amplifies_change():
    comp = {"demand_growth": 20}
    assert momentum(comp, "fast") > momentum(comp, "moderate") > momentum(comp, "slow")


def test_momentum_is_clamped():
    assert momentum({"demand_growth": 500}, "fast") == 100.0


def test_direction():
    assert direction(12) == "rising" and direction(-12) == "declining"
    assert direction(1) == "stable" and direction(None) == "unknown"


def test_match_score_is_importance_weighted():
    result = match_role(ROLE, {"a", "b"}, {})
    assert result["score"] == round(100 * 4 / 6)
    assert [m["skill"] for m in result["missing"]] == ["c"]


def test_gap_sorted_by_importance_then_momentum():
    result = match_role(ROLE, set(), {"a": 50, "b": 10, "c": 90})
    assert [m["skill"] for m in result["missing"]] == ["b", "c", "a"]


def test_tiers_follow_prerequisites():
    assert skill_tiers(SKILLS) == {"a": 0, "b": 1, "c": 2}


def test_tree_states():
    tree = build_tree(SKILLS, [ROLE], {"a"}, TRENDS, "moderate")
    states = {n["id"]: n["state"] for n in tree["nodes"]}
    assert states == {"a": "mastered", "b": "available", "c": "locked", "r": "locked"}
    role = next(n for n in tree["nodes"] if n["id"] == "r")
    assert role["tier"] == 3
    assert tree["is_mock"] is True


def test_pathway_orders_by_tier_and_skips_owned():
    path = build_pathway(ROLE, SKILLS, [course("cb", "b"), course("cc", "c")], {"a"})
    assert [s["skill"] for s in path["steps"]] == ["b", "c"]
    assert path["total_hours_verified"] == 10


def test_pathway_never_counts_unverified_courses():
    path = build_pathway(ROLE, SKILLS, [course("x", "b", verified=False)], {"a"})
    step_b = path["steps"][0]
    assert step_b["recommended"] is None
    assert path["total_hours_verified"] == 0
    assert set(path["skills_without_verified_course"]) == {"b", "c"}
