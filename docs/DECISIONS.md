# Decisions

One line per decision: date, who, what, why.

| Date | Who | Decision | Why |
|---|---|---|---|
| 2026-10-20 | Team | Python 3.11 + FastAPI + SQLite backend, vanilla JS + SVG frontend | No build step, simple Replit deploy |
| 2026-10-20 | Team | Trend data is mock until ingestion lands; UI labels it | Never show unlabelled invented numbers |
| 2026-10-20 | Team | Courses only from `data/courses.json` with `verified: true` | Brief forbids invented courses |
| 2026-10-21 | Member 3 | Skill and role ids frozen: add new ids, never rename | Ingestion, courses, SDG tags, stories and the frontend key on them |
| 2026-10-21 | Member 3 | Four families (service-ai, data, industry, green-energy), one per persona. `family` is set on roles only; a family's skills are derived from its roles plus prerequisites | Keeps each tree at most 5 nodes per tier (tested) and avoids skills and roles disagreeing |
| 2026-10-21 | Member 3 | `/api/tree` takes `family` (or `all`); default is the persona's family. New `GET /api/families` | Frontend keeps working without changes; Member 4 can add a selector |
| 2026-10-21 | Member 3 | Importance rubric: 3 core (cannot do the job without it), 2 important (used most days), 1 helpful | Makes the match score explainable |
| 2026-10-21 | Member 3 | Every role and persona has `based_on`: an O*NET occupation code and title, `match` direct or closest | Skills come from a published taxonomy, not invented. Closest means no exact O*NET occupation exists |
| 2026-10-21 | Member 3 | `prompting` prerequisite changed from crm_tools to communication; `empathy` SDG tag changed from 3, 10 to 8 | Clearer learning logic; the health link was not justifiable |
| 2026-10-21 | Member 3 | SDGs 7, 11, 12, 13 added to `sdg_map.json` with reason TBD | Clean-energy and ESG roles use them. Member 5 must add targets and reasons |
