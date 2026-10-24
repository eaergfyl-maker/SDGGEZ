# AI tools log

Record every AI tool used to help write code, text, or designs. Needed for the Tech Declaration
(section 4.3). Declaring does not reduce the score; not declaring may.

| Date | Who | Tool and version | Used for | Extent (minor / moderate / major) | How we reviewed it |
|---|---|---|---|---|---|
| 2026-10-20 | Lead | Claude Code (Claude Opus 5.5) | Initial repo scaffold, mock data, skeleton code | moderate | Team to read and walk through every file before building on it |
| 2026-10-21 | Lead | Claude Code (Claude Sonnet 5.5) | Role guides 1 to 5; switching ingestion to Arbeitnow with rate-limit handling; source probe script and tests | moderate | Tested live against the real APIs; owners to review their guide and module |
| 2026-10-21 to 2026-10-22 | Member 3 | Claude Code (Claude Opus 5.5) | Part 3: skill and role data with O*NET references, family trees, scoring changes (caps, low-data flag, outlook range, pathway fixes) and tests | moderate | Member 3 approved before commit; 59 tests pass; to walk through with backup (Member 2) |
| 2026-10 (see git log) | TBD | Replit Agent | Replit environment configuration and docs (`.replit`, `replit.md`); tree component and frontend state logic | TBD | TBD: whoever ran it fills in extent and review |
| 2026-10-23 | Lead | Claude Code (Claude Opus 5.5) | README rewritten to the SDC GitHub template | minor | Every path, number and claim checked against the repo |
| 2026-10-24 | Member 3 | Claude Code (Claude Opus 5.5) | CV reader: matcher, endpoints, CV terms, invented sample CVs, tests, intake panel UI | major | Member 3 reviews before merge; measured on sample CVs; 89 tests pass |
| 2026-10-24 | Member 3 | Claude Code (Claude Opus 5.5) | Bahasa Malaysia translations and language toggle | moderate | Malay text drafted by AI: a fluent speaker should review before the demo |
| 2026-10-24 | Member 3 | Claude Code (Claude Opus 5.5) | CV reader AI layer (backend/app/scoring/cv_ai.py, /api/cv/ai, tests) | major | Member 3 reviews; tested live against the RunPod endpoint on invented CVs |
| 2026-10-24 | Member 3 | Qwen3-8B (open model, self-hosted on RunPod) | Runs inside the app: suggests CV skills from a fixed list with quotes | runtime feature | Every suggestion checked in code (real id, quote present) and confirmed by the user |
| 2026-10-24 | Member 3 | Claude Code (Claude Opus 5.5) | 'Ask your guide' chat: backend facts and number check, endpoint, panel, tests | major | Tested live against RunPod on sample characters; answers reviewed for accuracy |
| 2026-10-24 | Member 3 | Qwen3-8B (open model, self-hosted on RunPod) | Runs inside the app: answers questions about the user's own results | runtime feature | Every number checked in code against the app's data; the user decides |
| 2026-10-21 to 2026-10-24 | Lead | Claude chat on claude.ai (Claude Sonnet 5.5) | Step-by-step guidance on git, GitHub, Replit and deployment; code now in the repo: `/api/refresh` token and 30-minute cooldown in `routes.py`, `backend/tests/test_refresh.py`, minimum dependency versions in `requirements.txt` (for Replit's security scan), single-port mapping in `.replit` | moderate | Ran pytest and CI on every PR; confirmed on the live site that refresh returns 403 without the token; Lead checked the diff before merging |