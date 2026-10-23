"""Read the JSON files in data/. Cached, since they only change between deploys."""
import json
from functools import lru_cache

from . import config


def _read(name):
    return json.loads((config.DATA_DIR / f"{name}.json").read_text(encoding="utf-8"))


@lru_cache
def skills():
    return _read("skills")["skills"]


@lru_cache
def roles():
    return _read("roles")["roles"]


@lru_cache
def families():
    return _read("roles")["families"]


@lru_cache
def courses():
    return _read("courses")["courses"]


@lru_cache
def sdg_map():
    return _read("sdg_map")["sdgs"]


@lru_cache
def personas():
    return _read("personas")["personas"]


def mock_trends():
    return _read("mock_trends")


def skills_by_id():
    return {s["id"]: s for s in skills()}


def roles_by_id():
    return {r["id"]: r for r in roles()}


def persona(persona_id):
    return next((p for p in personas() if p["id"] == persona_id), None)
