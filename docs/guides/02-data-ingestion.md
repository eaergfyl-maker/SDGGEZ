# Guide 2: Data ingestion

You provide the numbers the whole app stands on: which skills are rising or declining, with a
source and a date for every value. If your layer is weak, the radar, the tree and the pathway
are all weak. The brief says hard-coded lists do not count; this is the work that makes it real.

Time budget: about 3 hours Wednesday, about 3 hours Thursday, about 2 hours Friday, then a
daily 10-minute refresh.

## What you own

| Thing | Where |
|---|---|
| Job posting sources | `backend/app/ingest/arbeitnow.py`, `remotive.py`, `common.py` |
| arXiv research counts | `backend/app/ingest/arxiv.py` |
| Skill mention counting | `backend/app/ingest/mentions.py` |
| Snapshots and diffs | `backend/app/ingest/pipeline.py` |
| Database schema | `backend/app/db.py` |
| Source log | `docs/sources.md` |

## The two signals

Each skill gets up to three numbers (percent change). Member 3's scoring combines them.

| Component | Meaning | Source |
|---|---|---|
| `research_growth` | How fast AI research on this topic is growing: arXiv papers in the last 3 full months vs the same 3 months a year earlier | arXiv API |
| `demand_growth` | How the share of job postings mentioning the skill changed: last N days vs the N days before | Arbeitnow (+ Remotive) |
| `outlook` | A published forecast, cited. Not automated: Member 3 or 5 adds it from a report | A report with page cited |

Why a share and not a count: if there are simply more postings this week, every skill would
look "up". The share (postings mentioning the skill divided by all postings in the window)
removes that.

## What I found when I tested the sources (2026-10-21). Read this first.

| Source | Finding | Consequence |
|---|---|---|
| **Remotive** | Always returns only about 10 postings, whatever `limit` or `category` you pass | Too thin to measure a trend. Kept only as a small extra source |
| **Arbeitnow** | 300 postings per page, about 25 pages, roughly 6,000 postings spanning about a week | This is our main job signal. History is short, so windows are 5 days (`DEMAND_WINDOW_DAYS`) |
| **Arbeitnow** | Starts answering HTTP 429 after about 26 fast requests | We pause 3 s between pages, cache for 3 hours, and keep partial results if 429 hits |
| **arXiv** | The date-range query returned HTTP 429 from my machine, so it is **not confirmed** to work | Your first job is to run the probe and fix the query if needed |
| Postings | Mostly German and European, many in German | The demand signal is not Malaysian. Say so openly in the pitch |
| Older window | Only contains postings still live today, so older months look different from a true history | It is a rough signal, not a time series. Say so |

These limits are not failures; they are exactly the "hardest risk" the rubric asks you to name
and have a fallback for. Fallbacks: the arXiv series (real history) and a cited report.

## Setup (15 min)

```bash
git clone https://github.com/eaergfyl-maker/SDGGEZ.git && cd SDGGEZ
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env     # set INGEST_CONTACT to a team email, it goes in the User-Agent
pytest                   # all tests must pass before you change anything
git checkout -b data/ingest-first-run
```
The database is `data/app.db` and is git-ignored. Your database stays on your machine.

## Step 1. Check the terms (20 min)
Read, and write the key lines into `docs/sources.md`:
- arXiv API terms of use (one request every 3 seconds, one connection at a time).
- Remotive: link back, name Remotive, about 4 requests a day, no redistributing listings.
- Arbeitnow: the API says "free public API, do not abuse, linking back appreciated" and points
  to the terms on arbeitnow.com. Read those terms before you rely on it.

## Step 2. Probe the sources (10 min)
```bash
python scripts/probe_sources.py
```
It prints PASS or FAIL for arXiv, Arbeitnow and Remotive.

If arXiv says `RateLimited` or `429`: wait 10 to 15 minutes and try again. Do not loop. If it
still fails, try from a different network (phone hotspot, or from Replit). The code backs off,
but a blocked IP cannot be fixed in code.

If arXiv answers but the count looks wrong (for example 0 for a topic you know exists): open
this in a browser and read the raw XML:
```
https://export.arxiv.org/api/query?search_query=all:%22prompt%20engineering%22&max_results=1
```
Look for `opensearch:totalResults`. If the plain query works but the date-range one does not, the
problem is in `_month_bounds` or the `submittedDate:[...]` syntax in `count_for_month`. Fix it,
and add a test in `backend/tests/test_ingest.py`.

## Step 3. First real snapshot (10 min)
```bash
python -m backend.app.ingest.pipeline --note "first real snapshot"
```
This downloads about 26 pages from Arbeitnow (about 80 seconds), stores about 6,000 postings,
and writes a snapshot. Run it once, not repeatedly: it is cached for 3 hours on purpose.

Inspect the result:
```bash
python - <<'EOF'
import json
from backend.app import db
c = db.connect()
print(dict(c.execute("select count(*) n, min(published_at) lo, max(published_at) hi from postings").fetchone()))
for r in c.execute("select skill_id, research_growth, demand_growth, sources from skill_trends where snapshot_id=(select max(id) from snapshots)"):
    d = json.loads(r["sources"])["demand"]
    print(r["skill_id"], r["research_growth"], r["demand_growth"], d["recent_postings"], d["previous_postings"])
EOF
```
Then start the app (`uvicorn backend.app.main:app --reload`) and open `/api/trends`. It should
say `"is_mock": false`. The "Mock data" badge disappears in the UI.

My test run gave, for example: empathy +24%, data_literacy +12%, communication +12%,
ai_tools -21%, case_handling -20%. Treat these as a first look, not as truth (see Step 4).

## Step 4. Check the keywords (the most important quality step, 1 hour)
The numbers are only as good as the keyword lists in `data/skills.json`. Member 3 owns the
skill list, but you will see the problems first. Example check: which postings match
`ai_tools`?

```bash
python - <<'EOF'
import json, random
from backend.app import db, data_loader
from backend.app.ingest.mentions import mentions
skill = data_loader.skills_by_id()["ai_tools"]
c = db.connect()
rows = c.execute("select title, tags, description from postings").fetchall()
hits = [r for r in rows if mentions(f"{r['title']} {r['tags']} {r['description']}", skill["keywords"])]
print(len(hits), "of", len(rows), "postings match", skill["keywords"])
for kw in skill["keywords"]:
    n = sum(mentions(f"{r['title']} {r['tags']} {r['description']}", [kw]) for r in rows)
    print(f"  {kw!r}: {n}")
for r in random.sample(hits, min(5, len(hits))):
    print("-", r["title"])
EOF
```
Look at the per-keyword counts and the sample titles. If one keyword matches thousands of
unrelated postings (a short word, a common phrase, a boilerplate sentence in every description
such as a company's footer), remove it or make it more specific. Repeat for every skill.
Agree changes with Member 3, who edits `skills.json`. Skills should have 3 to 6 specific keywords.

Also think about language: many postings are German. English keywords miss them. Decide whether
to add German terms for important skills, or simply state the limitation. Either is fine if you
say which.

## Step 5. arXiv history (Wednesday evening, runs in the background)
Only skills with an `arxiv_query` are fetched. Add queries for skills where AI research is a
meaningful signal, for example "prompt engineering", "conversational agent", "process mining".
Not every skill needs one.

```bash
python -m backend.app.ingest.pipeline --arxiv --no-jobs --note "arxiv history"
```
This makes one request per skill per month for 24 months, with a 3 second pause. For 10
skills that is 240 requests and about 12 minutes. If arXiv answers 429, the code waits 20, 40
and 80 seconds, then stops and saves what it has. **Run the same command again later**: it skips
months already stored and carries on.

Check that growth numbers appear: re-run the Step 3 inspection and look at `research_growth`.
It needs at least 15 months stored per skill, otherwise it is `None` (shown as "no data").

## Step 6. Daily snapshots: the living map (Thursday onwards)
The patch-notes banner and "output changes when the data changes" depend on having two or more
snapshots. Every day (morning is fine):
```bash
python -m backend.app.ingest.pipeline --note "daily refresh"
```
Then `GET /api/changes` lists what moved between the last two snapshots. If nothing changed,
tell the team: it does not mean it is broken, the feed may simply not have moved much.
Do not fake a change. If the demo needs a visible diff, show the real one from two real days.

## Step 7. Seed snapshot (Thursday, with the Lead)
Problem: `*.db` is git-ignored, so your teammates and Replit never see your data. Fix: export
the latest snapshot to a committed file, and load it when the database is empty.

Write `scripts/export_snapshot.py`:
1. Read the newest `snapshots` row and its `skill_trends` rows.
2. Write `data/snapshot_seed.json` with `created_at`, a note, and per-skill values and `sources`.
3. Add a loader (for example `db.load_seed_if_empty()`) called by `trends.py` or at startup,
   which inserts the seed when there are no snapshots.
4. Test both with a temporary database.

Commit the seed file only with real numbers, and add the date to `docs/sources.md`.

## Step 8. Tests and quality
```bash
pytest backend/tests/test_ingest.py backend/tests/test_sources.py
```
Tests never call the network. When you change logic, change or add a test in the same commit.
Useful cases to add: a posting with no description, a very short window, a skill whose
previous share is zero (growth should be `None`, not a division error).

## Handoffs
| To | What | When |
|---|---|---|
| Member 3 | Keyword problems, which skills have real arXiv series | Wed evening |
| Member 1 | A working snapshot, then the seed file | Thu |
| Member 5 | The `sources` JSON per skill, so the radar can show source and date | Thu |

## Commit rhythm
Small commits on `data/...` branches, for example `ingest: store arbeitnow postings`,
`ingest: handle arxiv 429`, `data: tune ai_tools keywords`. Open a pull request, ask Member 3 to
review (your backup). At least one commit a day.

## Troubleshooting

| Problem | Fix |
|---|---|
| `429` from arXiv | Wait 10 to 15 minutes, re-run (it resumes). Try another network |
| `429` from Arbeitnow | You ran it too often. Wait a few minutes. Cached data is reused for 3 hours |
| `demand_growth` is `None` for everything | A window has fewer than 20 postings. Fetch jobs first, or lower `DEMAND_WINDOW_DAYS` |
| Growth numbers look huge (+300%) | A rare keyword with tiny counts. Check the keyword (Step 4) |
| `database is locked` | Two processes using the DB. Stop the server while running ingestion, or retry |
| `.cache/` missing | It is created on first fetch. Delete `.cache/` to force a fresh download |

## Limitations to state (judges reward honesty here)
1. Job data is mostly German and European, not Malaysian.
2. About one week of history, so windows are short and noisy.
3. The older window only contains postings still live today.
4. Keyword matching is simple: it misses synonyms and other languages.
5. arXiv measures research activity, not hiring.
Mitigations: we show the source, date, and window next to every number; we combine three
signals instead of trusting one; scenarios are labelled estimates; the pipeline refreshes daily
so the series grows.

## What to say to the judges
- "Demand growth is the change in the share of postings that mention a skill, so a busier week
  does not inflate every skill."
- "We cache and pause between requests, and keep partial results when we are rate limited."
- "Every snapshot stores where each value came from, which the UI shows."
- "Our biggest risk is data depth and region. Here is how we label it, and the arXiv history and
  a cited report anchor the numbers."

## Done when
- [ ] `probe_sources.py` passes for the sources we use (or the failure is documented)
- [ ] A real snapshot exists and `/api/trends` says `is_mock: false`
- [ ] Keyword lists checked for every skill
- [ ] arXiv history stored for skills with a query
- [ ] At least two snapshots on different days, `/api/changes` returns real changes
- [ ] Seed snapshot exported and loadable
- [ ] `docs/sources.md` is complete and the limitations are written down
