# Contributing

## Branches
One branch per piece of work, named by area:
`data/ingest-arxiv`, `score/momentum`, `ui-tree/unlock-logic`, `ui-panels/radar`, `api/refresh`.

## Flow
1. Branch from `main`.
2. Commit small and often (at least daily). Clear messages: `ingest: add arXiv monthly counts`.
3. Open a PR. The backup person listed in `docs/TEAM.md` reviews.
4. Merge to `main`. `main` must always run.

The hackathon checks for a realistic, continuous commit history. Do not push everything in one
commit near the deadline.

## Contracts
Files in `data/schema/` and the API shapes in `backend/app/api/routes.py` are shared contracts.
If you need to change one, add a line to `docs/DECISIONS.md` and tell the team first.
Skill and role IDs are frozen after Wednesday 21 Oct.

## Data and AI rules
- Public or synthetic data only. Never real CVs or personal data.
- Every source goes in `docs/sources.md` (URL, licence, date accessed).
- Courses only go into `data/courses.json` after someone opened the link and checked it,
  then set `"verified": true`.
- If you use an AI coding tool, you must be able to explain every line you commit. Log the
  tool in `docs/ai-tools-log.md` as you go; it feeds the Tech Declaration.

## Secrets
Never commit keys. Use `.env` locally and Replit Secrets on Replit.
