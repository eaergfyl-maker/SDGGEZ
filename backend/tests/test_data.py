import importlib.util

from backend.app import config


def test_data_files_are_valid():
    spec = importlib.util.spec_from_file_location("validate_data", config.ROOT / "scripts" / "validate_data.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.schema_errors() == []
    assert module.reference_errors() == []


def test_each_family_tree_fits_the_layout():
    """The frontend draws at most 5 nodes per tier without overlap."""
    from collections import Counter

    from backend.app import data_loader
    from backend.app.scoring.tree import family_subset, skill_tiers

    for fam in data_loader.families():
        skills, roles = family_subset(data_loader.skills(), data_loader.roles(), fam["id"])
        tiers = skill_tiers(skills)
        counts = Counter(tiers.values())
        counts.update(1 + max(tiers[s] for s in r["requires"]) for r in roles)
        assert max(counts.values()) <= 5, f"{fam['id']}: nodes per tier {dict(counts)}"
        assert len(skills) + len(roles) <= 25, f"{fam['id']}: {len(skills) + len(roles)} nodes"


def test_every_persona_skill_is_in_its_family_tree():
    from backend.app import data_loader
    from backend.app.scoring.tree import family_subset

    for p in data_loader.personas():
        skills, _ = family_subset(data_loader.skills(), data_loader.roles(), p["family"])
        ids = {s["id"] for s in skills}
        assert set(p["skills"]) <= ids, f"{p['id']}: {set(p['skills']) - ids} not in tree"


def test_each_sample_persona_would_be_guessed_into_its_own_area():
    """If someone ticked exactly a sample persona's skills, the guess must land in that persona's
    area. This catches data changes that make the guess unreliable."""
    from backend.app import data_loader
    from backend.app.scoring.tree import infer_family

    for p in data_loader.personas():
        g = infer_family(set(p["skills"]), data_loader.skills(), data_loader.roles(), data_loader.families())
        assert g["family"] == p["family"], f"{p['id']}: guessed {g['family']}"
