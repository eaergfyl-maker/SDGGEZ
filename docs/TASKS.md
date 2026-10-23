# Tasks (code only)

Copy each line into a GitHub issue on the Projects board. Tick here or on the board, not both.

## Member 1: Lead, API, integration, deploy
- [ ] Tue: push scaffold, add teammates, create Projects board, protect `main`
- [ ] Wed: Replit project from GitHub, public URL serving `/api/health`
- [ ] Wed: confirm mock endpoints work for frontend (`/api/tree`, `/api/trends`, `/api/pathway`)
- [ ] Thu: switch `/api/trends` from mock to DB once Member 2 has data
- [ ] Fri: `/api/refresh` triggers ingestion + new snapshot; integration bug triage
- [ ] Sat: feature freeze, full QA, logged-out link test, add committee GitHub accounts

## Member 2: Data ingestion
- [ ] Tue: check arXiv + Remotive access, read their terms, log them in `docs/sources.md`
- [ ] Wed: `ingest/arxiv.py` monthly counts for each skill's `arxiv_query`, saved to `arxiv_counts`
- [ ] Thu: `ingest/remotive.py` postings saved to `postings` (max ~4 requests/day, cached)
- [ ] Thu: `ingest/mentions.py` weekly keyword counts per skill
- [ ] Fri: `ingest/pipeline.py` writes `skill_trends` + a `snapshots` row; diff for patch notes

## Member 3: Scoring and matching
- [x] Tue: freeze skill and role IDs in `data/skills.json` and `data/roles.json`
- [x] Wed: grow to ~40-60 skills, ~15-25 roles; pick ESCO or O*NET and check its licence
- [x] Thu: tune `scoring/momentum.py` weights and scenarios; tests
- [x] Thu: `scoring/matching.py` fit score, gap, "why" strings; tests
- [x] Fri: `scoring/pathway.py` ordering and course selection; tests

## Member 4: Frontend A, skill tree and game
- [ ] Tue: run the app, read `frontend/js/tree/tree.js`
- [ ] Wed: node layout per tier, unlock on click, XP and level
- [ ] Thu: scenario selector, role "boss" panel with match score and gap
- [ ] Fri: animations, mobile layout, story hook (`/api/story/{id}`, shows nothing if empty)

## Member 5: Frontend B + content data
- [ ] Tue: persona picker + skills checklist in `frontend/js/panels/intake.js`
- [ ] Wed: radar panel (rising/declining) from `/api/trends`
- [ ] Thu: pathway panel from `/api/pathway`
- [ ] Thu: fill `data/courses.json` with real, checked courses (`verified: true`)
- [ ] Fri: `data/sdg_map.json` justifications, SDG badges, patch-notes banner

## Later (re-split on Thursday)
- [ ] Story files
- [ ] Submission Template, Tech Declaration, deck, video
