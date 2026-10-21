# Guide 1: Lead (API, integration, deploy)

You make sure the pieces fit, the app is live on Replit, and everything the judges need is in
place on time. You write less feature code than the others; you unblock them.

Time budget: about 2 hours tonight, then about 1 hour a day for integration, plus Saturday QA.

## What you own

| Thing | Where |
|---|---|
| App entry and routing | `backend/app/main.py`, `backend/app/api/routes.py` |
| Wiring trends into the API | `backend/app/trends.py` |
| Replit project and deployment | `.replit`, Replit Secrets |
| Tests and CI | `backend/tests/`, `.github/workflows/` (you add this) |
| Team process | GitHub collaborators, Projects board, PR reviews, `docs/DECISIONS.md` |
| Submission mechanics | Tech Declaration proof, public repo, collaborators, final link test |

## How the app fits together (learn this; you will be asked)

```
Browser (frontend/js)  --fetch-->  FastAPI (routes.py)
                                      |-- trends.py  --> SQLite snapshot (real) or data/mock_trends.json (fallback, is_mock=true)
                                      |-- scoring/*  --> momentum, matching, tree, pathway (pure functions)
                                      |-- data_loader.py --> data/*.json (skills, roles, courses, SDGs, personas)
Ingestion (ingest/pipeline.py) writes snapshots into SQLite. /api/refresh triggers it.
```

Key idea: the scoring code never touches the network or the database. `routes.py` gathers inputs
and hands them to pure functions. That is why it is easy to test and easy to explain.

## Tonight (Tue 20 to Wed 21 Oct)

### 1. Get everyone into the repo (10 min)
Repo: https://github.com/eaergfyl-maker/SDGGEZ (private).

```bash
gh api -X PUT repos/eaergfyl-maker/SDGGEZ/collaborators/THEIR_GITHUB_USERNAME
```
Run it once per teammate. They accept the invitation by email or on github.com.
Then fill in the names in `docs/TEAM.md`.

### 2. Make the board (10 min)
GitHub repo, Projects tab, New project, Board. Columns: To do, Doing, Review, Done.
Create one issue per line in `docs/TASKS.md` and assign each to its owner.

Branch protection: Settings, Branches, add a rule for `main` that requires a pull request. On a
private repo with a free account GitHub may show an upgrade prompt instead. If so, skip it and
enforce the rule by habit: nobody pushes directly to `main`.

### 3. Run it locally and read the code (30 min)
```bash
git clone https://github.com/eaergfyl-maker/SDGGEZ.git && cd SDGGEZ
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest                                                # expect everything to pass
python scripts/validate_data.py                       # expect OK plus one unverified-course warning
uvicorn backend.app.main:app --reload --port 8000
```
Open http://localhost:8000 and http://localhost:8000/docs. In `/docs` try every endpoint.
Read, in order: `main.py`, `api/routes.py`, `trends.py`, `scoring/tree.py`.

### 4. Replit (45 min). Do this by Wednesday.
The handbook requires Replit in your project, with proof from your own account (a live Replit
URL, a project link with history, or a screenshot of credit used).

1. Claim the Replit credit on the hackathon portal first (the handbook says the team lead gets
   access for all members within 24 hours before the round).
2. In Replit, create a project from the GitHub repo (menu names change; look for "Import from
   GitHub"). Replit must be connected to your GitHub account to see a private repo.
3. Check that `.replit` runs `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`.
   Replit should install `requirements.txt`. If it does not, run
   `pip install -r requirements.txt` in the Replit shell.
4. Press Run. The app should show in the preview pane and `/api/health` returns `{"ok": true}`.
   I have not been able to test the `.replit` file on Replit, so expect to adjust it.
5. Secrets: only needed for an LLM key or the refresh token (below). Use the Replit Secrets
   tool, never files.
6. Deploy it (Replit's Deploy / Publish button) and save the public URL. Test it in a private
   browser window.
7. Invite teammates to the Replit project if you want multiplayer editing, but keep GitHub as the
   source of truth: change code in git, then pull into Replit.

Open question to test early: on a deployed Replit app, files written at runtime (like the SQLite
database `data/app.db`) may not survive a restart or redeploy. Test it: run ingestion once,
redeploy, and check whether `/api/trends` still says `is_mock: false`. If the data disappears,
use one of the fixes in "Data persistence" below.

## Wednesday to Friday: integration work

### A. Keep the contract stable
The frontend depends on these shapes. They live in `routes.py` and show up at `/docs`:

| Endpoint | Used by | Notes |
|---|---|---|
| `GET /api/tree?persona=&scenario=&owned=` | tree and panels | `owned` is comma-separated skill ids |
| `GET /api/trends?scenario=` | radar | includes `is_mock` and `as_of` |
| `GET /api/pathway?role=&persona=&owned=` | pathway panel | only verified courses are counted |
| `GET /api/story/{node_id}` | tree detail | returns `{}` if there is no story file |
| `GET /api/changes` | patch notes | diff of the last two snapshots |
| `POST /api/refresh` | refresh button | see "Protect refresh" |

If anyone wants to change a response shape: they add a line to `docs/DECISIONS.md`, tell the
channel, and you update the test in `backend/tests/test_api.py` in the same pull request.

### B. Protect /api/refresh (before the public demo)
Right now anyone can POST to `/api/refresh` repeatedly and hammer the job APIs, which rate
limit (Arbeitnow already answered 429 to us during testing). Add a shared token and a cooldown.
In `routes.py`:

```python
import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, Header

def require_refresh_token(x_refresh_token: str | None = Header(None)):
    expected = os.environ.get("REFRESH_TOKEN")
    if not expected or x_refresh_token != expected:
        raise HTTPException(403, "Refresh is restricted")

def cooldown(minutes: int = 30):
    conn = db.connect()
    try:
        row = conn.execute("SELECT created_at FROM snapshots ORDER BY id DESC LIMIT 1").fetchone()
    finally:
        conn.close()
    if row and datetime.fromisoformat(row["created_at"]) > datetime.now(timezone.utc) - timedelta(minutes=minutes):
        raise HTTPException(429, "A refresh ran recently; try again later")

@router.post("/refresh", status_code=202, dependencies=[Depends(require_refresh_token), Depends(cooldown)])
```
Set `REFRESH_TOKEN` in Replit Secrets and in your local `.env`. Add a test that a request
without the header gets 403. Never put the token in frontend code: for the live demo, either
trigger refresh from `/docs` with the header, or agree a server-side approach with Member 4.

### C. Data persistence on Replit (pick one if the test above fails)
1. **Ingest at startup** when there is no snapshot: add a startup hook in `main.py` that calls
   `pipeline.run(...)` in the background if `trends.latest_snapshot_trends()` is `None`.
   Simple, but every restart makes outbound calls, so rely on the cache files and rate limits.
2. **Seed snapshot**: commit `data/snapshot_seed.json` exported by Member 2 and load it into
   the database when the DB is empty. This also stops teammates seeing mock data locally
   (the `.db` file is git-ignored, so nobody else gets Member 2's data). See Guide 2, task
   "Seed snapshot".
3. Use a Replit database or storage service, and declare it in the Tech Declaration.

Option 2 is the most robust for a live demo. Whatever you pick, note it in `DECISIONS.md`.

### D. Continuous integration (20 min)
Create `.github/workflows/test.yml`:

```yaml
name: tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt
      - run: pytest
      - run: python scripts/validate_data.py
```
Failing tests then show as a red cross on every pull request. The tests make no external
API calls, so CI is fast and never rate limited.

### E. Review duty
Every PR gets a reviewer who is not the author. Your checklist when you review:
1. Tests pass and the app still runs.
2. No secrets, no personal data, no large generated files.
3. New sources are in `docs/sources.md`.
4. The author can explain it. Ask one question about it.

### F. Switching from mock to real data
`trends.py` already prefers the newest database snapshot and falls back to the mock file.
When Member 2 has a snapshot: open `/api/trends`, confirm `is_mock` is `false`, and check the
tree and radar still render. The "Mock data" badge disappears on its own.

## Saturday: freeze and QA

Feature freeze Saturday noon. After that, only bug fixes.

Checklist, in order:
1. `pytest` and `python scripts/validate_data.py` pass on `main`.
2. The deployed Replit URL works in a private window and on a phone.
3. `/api/trends` shows `is_mock: false` (or the badge is clearly visible and explained).
4. No secrets in the repo:
   ```bash
   git log -p | grep -iE "api[_-]?key|secret|token|password" | head
   ```
   Review anything that appears. Rotate any key that was ever committed.
5. `LICENSE` is Apache 2.0 and at the repo root.
6. The commit history is continuous: `git log --format='%an %ad %s' --date=short` should show
   several authors across several days.
7. Add the committee's GitHub account(s) as collaborators (the organisers give the names; check
   Discord or the portal). Then make the repo public: Settings, General, Danger Zone, Change
   visibility. Do this Saturday, not at the last minute.
8. Collect the Replit proof for the Tech Declaration.
9. Submit through sdchack.my the night before the deadline (25 Oct 07:59:59 AM MYT).

## Troubleshooting

| Problem | Likely cause and fix |
|---|---|
| `ModuleNotFoundError: backend` | Run from the repo root and use `uvicorn backend.app.main:app` |
| Frontend blank, console error about modules | Open it through the server, not by double-clicking `index.html` |
| `/api/trends` always mock | No snapshot in the DB. Run `python -m backend.app.ingest.pipeline` |
| Data gone after redeploy on Replit | Runtime files are not persistent. See "Data persistence" |
| Merge conflict in `data/*.json` | Two people edited the same file. Split by section, or pair for 5 minutes |
| 429 from a data source | Rate limited. Wait; never retry in a tight loop |

## What to say to the judges
- "Scoring is pure functions with tests; routes only gather inputs. That keeps it explainable."
- "Trend data comes from real sources with dates. If no snapshot exists, the UI says Mock data."
- "The pathway only uses courses from our verified catalogue; unverified ones are never counted."
- "Refresh is protected and cached so we respect the sources' rate limits."

## Done when
- [ ] All teammates have repo access and the board exists
- [ ] Live Replit URL, tested logged out
- [ ] Refresh endpoint protected and cooled down
- [ ] CI is green
- [ ] Data survives a redeploy (or the fallback is in place)
- [ ] Final QA checklist complete, submitted the night before
