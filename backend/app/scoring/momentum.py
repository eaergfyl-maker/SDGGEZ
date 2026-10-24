"""Combine trend components into one momentum score per skill. Owner: Member 3.

Each component is a % change (or None when we have no data):
  research_growth  arXiv papers, last 3 months vs same 3 months a year earlier
  demand_growth    share of job postings mentioning the skill, recent window vs previous window
  outlook          a published forecast (cite the report), if we have one

Scenarios are assumptions, not predictions. They change how much each signal counts and how
strongly change is amplified. The reasoning is in docs/DECISIONS.md.
"""

COMPONENTS = ("research_growth", "demand_growth", "outlook")

# Each component is capped before averaging, so one exploding signal (e.g. +400% research
# growth from a tiny base) cannot drown out the others.
COMPONENT_CAP = 100.0

# Below this many postings mentioning the skill (in either window), demand growth is noise:
# 3 mentions vs 1 mention reads as +200%. We drop the component and flag it as low data.
MIN_MENTIONS = 20
# Same idea for research: 8 papers vs 1 paper reads as -87%. Below this many arXiv papers in
# either 3-month window, research growth is dropped and flagged as low data.
MIN_PAPERS = 30

SCENARIOS = {
    "slow": {"research_growth": 0.2, "demand_growth": 0.5, "outlook": 0.3, "scale": 0.6},
    "moderate": {"research_growth": 0.3, "demand_growth": 0.5, "outlook": 0.2, "scale": 1.0},
    "fast": {"research_growth": 0.5, "demand_growth": 0.35, "outlook": 0.15, "scale": 1.5},
}


def low_data(components: dict) -> list[str]:
    """Components we have a value for but too small a sample to trust."""
    sources = components.get("sources") or {}
    checks = (("demand_growth", "demand", ("mentions_recent", "mentions_previous"), MIN_MENTIONS),
              ("research_growth", "research", ("papers_recent", "papers_year_ago"), MIN_PAPERS))
    low = []
    for key, src, fields, minimum in checks:
        detail = sources.get(src) or {}
        if components.get(key) is not None and any(
                detail.get(f) is not None and detail[f] < minimum for f in fields):
            low.append(key)
    return low


def usable(components: dict) -> dict[str, float]:
    """The components we trust, each capped to plus or minus COMPONENT_CAP."""
    skip = set(low_data(components))
    return {k: max(-COMPONENT_CAP, min(COMPONENT_CAP, components[k]))
            for k in COMPONENTS if components.get(k) is not None and k not in skip}


def momentum(components: dict, scenario: str = "moderate") -> float | None:
    """Weighted average of the usable components, scaled by the scenario, clamped to plus or minus 100."""
    weights = SCENARIOS[scenario]
    present = usable(components)
    if not present:
        return None
    total = sum(weights[k] for k in present)
    value = sum(weights[k] * v for k, v in present.items()) / total
    value *= weights["scale"]
    return round(max(-100.0, min(100.0, value)), 1)


def direction(value: float | None, threshold: float = 5.0) -> str:
    if value is None:
        return "unknown"
    if value >= threshold:
        return "rising"
    if value <= -threshold:
        return "declining"
    return "stable"
