# Future-Ready RPG

SDC Hackathon 2026, Domain 1 (Aiversecity Future-Ready Workforce).

A career skill tree that redraws itself as AI and job-market trends change. The user plays a
character, trains skills, unlocks future roles, and sees how each step connects to the UN SDGs.

> Status: scaffold. All trend numbers served by the API are **MOCK** until `backend/app/ingest`
> is wired to real sources. The UI shows a "Mock data" badge whenever mock data is in use.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # fill in only what you need; never commit .env
uvicorn backend.app.main:app --reload --port 8000
```

Open http://localhost:8000 (app) and http://localhost:8000/docs (API docs).

Tests and data checks:

```bash
pytest
python scripts/validate_data.py
```

## On Replit
Import this repo from GitHub. `.replit` runs the same uvicorn command. Put secrets in
**Replit Secrets**, not in files.

## Layout

| Path | What | Owner |
|---|---|---|
| `backend/app/main.py`, `api/` | FastAPI app and endpoints | Member 1 |
| `backend/app/ingest/`, `db.py` | arXiv + job-posting ingestion, SQLite | Member 2 |
| `backend/app/scoring/` | momentum, matching, tree, pathway | Member 3 |
| `data/skills.json`, `roles.json` | skills, roles, prerequisites | Member 3 |
| `frontend/js/tree/`, `frontend/js/main.js` | skill tree and game | Member 4 |
| `frontend/js/panels/` | intake, radar, pathway, SDG panels | Member 5 |
| `data/courses.json`, `sdg_map.json` | verified courses, SDG tags | Member 5 |
| `story/` | story files (parked for now) | later |
| `docs/` | team, tasks, decisions, sources | everyone |

See `docs/TEAM.md`, `docs/TASKS.md`, `CONTRIBUTING.md`, and the role guides in `docs/guides/`.

## Rules we follow
- Public or synthetic data only. No real CVs or personal data.
- Every number shown to a user has a source and a date. Mock data is labelled.
- The pathway can only pick courses from `data/courses.json`. Nothing is invented.
- The app supports career decisions; the user decides.
- No secrets in the repo. Commit daily, small commits.

License: Apache 2.0 (see `LICENSE`).
