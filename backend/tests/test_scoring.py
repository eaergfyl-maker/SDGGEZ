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


# --- Guide 3, steps 4 to 7 -------------------------------------------------------------

from backend.app.scoring.momentum import MIN_MENTIONS, low_data  # noqa: E402
from backend.app.scoring.tree import outlook_range, role_outlook  # noqa: E402


def test_components_are_capped_before_averaging():
    expected = round((0.3 * 100 + 0.5 * 10) / 0.8, 1)
    assert momentum({"research_growth": 500, "demand_growth": 10}) == expected


def test_missing_components_renormalise_weights():
    assert momentum({"research_growth": 20, "outlook": 50}) == round((0.3 * 20 + 0.2 * 50) / 0.5, 1)


def test_scenarios_amplify_decline_too():
    comp = {"demand_growth": -20}
    assert momentum(comp, "fast") < momentum(comp, "moderate") < momentum(comp, "slow")


def _with_mentions(n):
    return {"demand_growth": 50, "sources": {"demand": {"mentions_recent": n, "mentions_previous": n}}}


def test_small_samples_are_flagged_and_ignored():
    assert low_data(_with_mentions(MIN_MENTIONS - 1)) == ["demand_growth"]
    assert momentum(_with_mentions(MIN_MENTIONS - 1)) is None
    assert low_data(_with_mentions(MIN_MENTIONS)) == []
    assert momentum(_with_mentions(MIN_MENTIONS)) == 50.0


def test_small_sample_falls_back_to_other_signals():
    comp = {**_with_mentions(3), "research_growth": 10}
    assert momentum(comp) == 10.0


def test_full_match_and_no_match():
    full = match_role(ROLE, {"a", "b", "c"}, {})
    assert full["score"] == 100 and full["missing"] == [] and "no skills missing" in full["why"]
    none = match_role(ROLE, set(), {})
    assert none["score"] == 0 and len(none["missing"]) == 3


def test_why_names_the_biggest_gap_in_plain_words():
    result = match_role(ROLE, {"a"}, {"b": 38.0}, {"b": "Prompting"})
    assert result["why"] == ("1 of 3 skills matched, weighted by importance; "
                             "biggest gap: Prompting (core, rising +38%)")


def test_gap_with_no_trend_data_does_not_crash():
    result = match_role(ROLE, {"a"}, {"b": None, "c": None})
    assert "no trend data" in result["why"]


def test_identical_skills_give_identical_results_whoever_the_person_is():
    first = match_role(ROLE, {"a", "b"}, {"c": 12.0})
    second = match_role(ROLE, {"b", "a"}, {"c": 12.0})
    assert first == second


def test_role_locked_until_all_required_skills_owned():
    role = {**ROLE, "requires": ["b", "c"]}
    states = lambda owned: {n["id"]: n["state"] for n in build_tree(SKILLS, [role], owned, TRENDS, "moderate")["nodes"]}
    assert states({"a", "b"})["r"] == "locked"
    assert states({"a", "b", "c"})["r"] == "available"


def test_role_outlook_is_importance_weighted_and_skips_missing_data():
    assert role_outlook(ROLE, {"a": 10, "b": 40, "c": None}) == round((1 * 10 + 3 * 40) / 4, 1)
    assert role_outlook(ROLE, {}) is None


def test_outlook_range_covers_every_scenario():
    rng = outlook_range(ROLE, {"b": {"demand_growth": 20}})
    assert set(rng["by_scenario"]) == {"slow", "moderate", "fast"}
    assert rng["min"] == rng["by_scenario"]["slow"] and rng["max"] == rng["by_scenario"]["fast"]
    assert outlook_range(ROLE, {}) is None


def test_shared_course_counted_once():
    shared = {**course("both", "b", hours=5), "skills": ["b", "c"]}
    path = build_pathway(ROLE, SKILLS, [shared], {"a"})
    assert [s["recommended"] for s in path["steps"]] == ["both", "both"]
    assert path["total_hours_verified"] == 5


def test_weeks_estimate_rounds_up():
    path = build_pathway(ROLE, SKILLS, [course("cb", "b", hours=5), course("cc", "c", hours=5)], {"a"},
                         hours_per_week=3)
    assert path["estimated_weeks"] == 4          # 10 hours at 3 a week
    assert build_pathway(ROLE, SKILLS, [], {"a"}, hours_per_week=3)["estimated_weeks"] is None


# --- Career area guess ------------------------------------------------------------------

from backend.app.scoring.tree import infer_family  # noqa: E402

AREA_SKILLS = [
    {"id": "talk", "name": "Talk", "prereqs": [], "keywords": ["t"], "sdg": [8]},
    {"id": "ledger", "name": "Ledger", "prereqs": [], "keywords": ["l"], "sdg": [8]},
    {"id": "solder", "name": "Solder", "prereqs": [], "keywords": ["s"], "sdg": [9]},
    {"id": "weld", "name": "Weld", "prereqs": [], "keywords": ["w"], "sdg": [9]},
]
AREA_ROLES = [
    {"id": "clerk", "family": "office", "requires": ["ledger"], "sdg": [8],
     "skills": [{"skill": "ledger", "importance": 3}, {"skill": "talk", "importance": 1}]},
    {"id": "tech", "family": "factory", "requires": ["solder"], "sdg": [9],
     "skills": [{"skill": "solder", "importance": 3}, {"skill": "talk", "importance": 1}]},
    {"id": "welder", "family": "workshop", "requires": ["weld"], "sdg": [9],
     "skills": [{"skill": "weld", "importance": 3}, {"skill": "talk", "importance": 1}]},
]
AREAS = [{"id": "office", "name": "Office"}, {"id": "factory", "name": "Factory"},
         {"id": "workshop", "name": "Workshop"}]


def guess(owned):
    return infer_family(set(owned), AREA_SKILLS, AREA_ROLES, AREAS)


def test_area_specific_skill_decides_the_area():
    assert guess({"ledger"})["family"] == "office"
    assert guess({"solder", "talk"})["family"] == "factory"


def test_shared_skill_alone_is_not_enough_to_guess():
    assert guess({"talk"})["family"] is None      # every area uses it: ask instead
    assert guess(set())["family"] is None


def test_close_call_is_flagged_and_order_is_stable():
    g = guess({"ledger", "solder"})                # two areas tie, the third scores nothing
    assert g["ambiguous"] is True
    assert g["family"] == "factory"               # tie broken by id, the same every time
    assert [r["id"] for r in g["ranked"]] == ["factory", "office", "workshop"]


def test_tie_across_every_area_asks_instead_of_guessing():
    assert guess({"ledger", "solder", "weld"})["family"] is None


def test_research_from_a_handful_of_papers_is_low_data():
    comp = {"research_growth": -87.5, "demand_growth": 10,
            "sources": {"research": {"papers_recent": 1, "papers_year_ago": 8}}}
    assert low_data(comp) == ["research_growth"]
    assert momentum(comp) == 10.0
