"""Check data/*.json against data/schema/ and cross-file references.

Run: python scripts/validate_data.py   (exit code 1 on any problem)
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FILES = ["skills", "roles", "courses", "sdg_map", "personas"]


def load(name):
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


def schema_errors():
    errors = []
    for name in FILES:
        schema = json.loads((DATA / "schema" / f"{name}.schema.json").read_text(encoding="utf-8"))
        for err in Draft202012Validator(schema).iter_errors(load(name)):
            path = "/".join(str(p) for p in err.absolute_path)
            errors.append(f"{name}.json [{path}]: {err.message}")
    return errors


def has_cycle(graph):
    state = {}

    def visit(node):
        if state.get(node) == 1:
            return True
        if state.get(node) == 2:
            return False
        state[node] = 1
        if any(visit(p) for p in graph.get(node, [])):
            return True
        state[node] = 2
        return False

    return any(visit(n) for n in graph)


def reference_errors():
    errors = []
    skills = load("skills")["skills"]
    roles = load("roles")["roles"]
    skill_ids = [s["id"] for s in skills]
    role_ids = [r["id"] for r in roles]
    known = set(skill_ids)

    for ids, label in ((skill_ids, "skill"), (role_ids, "role")):
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            errors.append(f"duplicate {label} ids: {sorted(dupes)}")
    clash = known & set(role_ids)
    if clash:
        errors.append(f"ids used for both a skill and a role: {sorted(clash)}")

    for s in skills:
        for p in s["prereqs"]:
            if p not in known:
                errors.append(f"skill {s['id']}: unknown prereq {p}")
    if has_cycle({s["id"]: s["prereqs"] for s in skills}):
        errors.append("skill prerequisites contain a cycle")

    for r in roles:
        for sid in r["requires"]:
            if sid not in known:
                errors.append(f"role {r['id']}: unknown required skill {sid}")
        for item in r["skills"]:
            if item["skill"] not in known:
                errors.append(f"role {r['id']}: unknown skill {item['skill']}")

    families = {f["id"] for f in load("roles")["families"]}
    for r in roles:
        if r["family"] not in families:
            errors.append(f"role {r['id']}: unknown family {r['family']}")
    for p in load("personas")["personas"]:
        if p["family"] not in families:
            errors.append(f"persona {p['id']}: unknown family {p['family']}")

    for c in load("courses")["courses"]:
        for sid in c["skills"]:
            if sid not in known:
                errors.append(f"course {c['id']}: unknown skill {sid}")

    for p in load("personas")["personas"]:
        for sid in p["skills"]:
            if sid not in known:
                errors.append(f"persona {p['id']}: unknown skill {sid}")

    mapped = {e["sdg"] for e in load("sdg_map")["sdgs"]}
    used = {g for item in skills + roles for g in item["sdg"]}
    for g in sorted(used - mapped):
        errors.append(f"SDG {g} is used but has no entry in sdg_map.json")
    return errors


def main():
    errors = schema_errors() + reference_errors()
    for e in errors:
        print("ERROR", e)
    unverified = [c["id"] for c in load("courses")["courses"] if not c["verified"]]
    if unverified:
        print(f"WARNING {len(unverified)} unverified course(s): {unverified}")
    print("OK" if not errors else f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
