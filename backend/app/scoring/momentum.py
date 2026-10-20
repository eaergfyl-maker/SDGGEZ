"""Combine trend components into one momentum score per skill. Owner: Member 3.

Each component is a % change (or None when we have no data):
  research_growth  arXiv papers, last 3 months vs same 3 months a year earlier
  demand_growth    share of job postings mentioning the skill, recent window vs previous window
  outlook          a published forecast (cite the report), if we have one

Scenarios are assumptions, not predictions. They change how much each signal counts and how
strongly change is amplified. Tune the numbers and write the reasoning in docs/DECISIONS.md.
"""

COMPONENTS = ("research_growth", "demand_growth", "outlook")

SCENARIOS = {
    "slow": {"research_growth": 0.2, "demand_growth": 0.5, "outlook": 0.3, "scale": 0.6},
    "moderate": {"research_growth": 0.3, "demand_growth": 0.5, "outlook": 0.2, "scale": 1.0},
    "fast": {"research_growth": 0.5, "demand_growth": 0.35, "outlook": 0.15, "scale": 1.5},
}


def momentum(components: dict, scenario: str = "moderate") -> float | None:
    """Weighted average of the components we have, scaled by the scenario, clamped to ±100."""
    weights = SCENARIOS[scenario]
    present = {k: components[k] for k in COMPONENTS if components.get(k) is not None}
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
