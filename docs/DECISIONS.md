# Decisions

One line per decision: date, who, what, why.

| Date | Who | Decision | Why |
|---|---|---|---|
| 2026-10-20 | Team | Python 3.11 + FastAPI + SQLite backend, vanilla JS + SVG frontend | No build step, simple Replit deploy |
| 2026-10-20 | Team | Trend data is mock until ingestion lands; UI labels it | Never show unlabelled invented numbers |
| 2026-10-20 | Team | Courses only from `data/courses.json` with `verified: true` | Brief forbids invented courses |
| 2026-10-22 | Member 5 (Aman) | Dropped SDG 3 from sdg_map.json | Not used in skills.json/roles.json; confirmed with Member 3, logged in their docs/DECISIONS.md too |
| 2026-10-21 | Member 3 | Skill and role ids frozen: add new ids, never rename | Ingestion, courses, SDG tags, stories and the frontend key on them |
| 2026-10-21 | Member 3 | Four families (service-ai, data, industry, green-energy), one per persona. `family` is set on roles only; a family's skills are derived from its roles plus prerequisites | Keeps each tree at most 5 nodes per tier (tested) and avoids skills and roles disagreeing |
| 2026-10-21 | Member 3 | `/api/tree` takes `family` (or `all`); default is the persona's family. New `GET /api/families` | Frontend keeps working without changes; Member 4 can add a selector |
| 2026-10-21 | Member 3 | Importance rubric: 3 core (cannot do the job without it), 2 important (used most days), 1 helpful | Makes the match score explainable |
| 2026-10-21 | Member 3 | Every role and persona has `based_on`: an O*NET occupation code and title, `match` direct or closest | Skills come from a published taxonomy, not invented. Closest means no exact O*NET occupation exists |
| 2026-10-21 | Member 3 | `prompting` prerequisite changed from crm_tools to communication; `empathy` SDG tag changed from 3, 10 to 8 | Clearer learning logic; the health link was not justifiable |
| 2026-10-21 | Member 3 | SDGs 7, 11, 12, 13 added to `sdg_map.json` with reason TBD | Clean-energy and ESG roles use them. Member 5 must add targets and reasons |
| 2026-10-22 | Member 3 | `ai_tools` prerequisite is now communication only (was communication and empathy) | Data-science paths were asking learners to take an empathy course before AI tools |
| 2026-10-22 | Member 3 | Each momentum component is capped at plus or minus 100 before averaging | One exploding signal (for example +400% research growth from a small base) must not swamp the others |
| 2026-10-22 | Member 3 | Demand growth is ignored, and the skill flagged `low_data`, when fewer than 20 postings mention the skill in either window | 3 mentions vs 1 reads as +200%; that is noise, not a trend |
| 2026-10-22 | Member 3 | Roles show two separate numbers: match (how well you fit today) and outlook (importance-weighted momentum of the role's skills), plus the outlook range across scenarios | Never blend fit and growth into one mystery number; the range is the brief's multi-scenario output |
| 2026-10-22 | Member 3 | Pathway counts a course once even if it covers several skills, and estimates weeks as verified hours divided by the person's weekly study hours, rounded up | Totals were double counting; the brief asks for estimated time |
| 2026-10-22 | Member 3 | Scoring uses skills only, never name, age, gender or ethnicity; a test proves identical skills give identical results | Fairness and the human-centred rule |

## Scenario assumptions (Member 3, 2026-10-22)

These are adjustable assumptions, not measurements or predictions.

| Scenario | What we assume | Weights (research / demand / outlook) | Scale |
|---|---|---|---|
| Slow | AI adoption in Malaysian workplaces is gradual. Today's job ads matter most; research leads take longer to reach jobs | 0.2 / 0.5 / 0.3 | 0.6: changes are dampened |
| Moderate | The current pace continues | 0.3 / 0.5 / 0.2 | 1.0: baseline |
| Fast | AI capability and adoption accelerate, so research trends reach jobs sooner | 0.5 / 0.35 / 0.15 | 1.5: changes are amplified |

Why the scale: in a fast world both growth and decline happen sooner, so the same signal means
more. "Why 1.5?" The honest answer: it is a chosen assumption, shown to the user as a range,
and anyone can change it in `backend/app/scoring/momentum.py`.
| 2026-10-24 | Member 3 | CV reader is keyword-based (no AI): exact phrase = ticked; similar wording, negation ('no SQL') or intent ('learning Python') = possible, unticked; evidence shown for every result | Explainable and testable; the person confirms every tick |
| 2026-10-24 | Member 3 | Skills gain an optional `cv_terms` list (CV-style wording), used only by the CV reader; job-posting ingestion still uses `keywords` | CVs and job adverts word skills differently |
| 2026-10-24 | Member 3 | CV text is processed in memory, never stored or logged; emails and numbers with 9+ digits are removed first; four invented sample CVs in `data/sample_cvs/` | Brief forbids real CVs; demo and tests use invented ones |
