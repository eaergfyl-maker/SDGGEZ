# Sources

Every dataset, API, report, and course provider we use. This feeds the Tech Declaration.

| Name | Type | URL | Licence / terms | Accessed | Notes |
|---|---|---|---|---|---|

| arXiv API | API (research trend) | https://export.arxiv.org/api/query | Check arXiv API terms of use | 2026-10-20 | Returns total result counts and dates |

| Remotive API | API (job postings) | https://remotive.com/api/remote-jobs | Must link back and name Remotive; ~4 requests/day; jobs delayed 24h; no redistribution to job boards | 2026-10-21 | Returns only ~10 postings whatever the limit/category: supplementary only |

| Arbeitnow API | API (job postings) | https://www.arbeitnow.com/api/job-board-api | Response says: free public API, do not abuse, link back appreciated, ToS on arbeitnow.com apply. Read the ToS before the final submission | 2026-10-21 | Main job signal. 300 postings/page, ~25 pages (~6,000 postings, ~1 week). Rate limits (HTTP 429) after ~26 fast requests. Mostly German/European postings |

| Hays Asia Salary Guide 2025 | Report | TBD | Cite only | TBD | 56% use AI tools, 26% trained (quoted in Domain 1 brief) |

| O*NET Database | Skills taxonomy (reference) | https://www.onetcenter.org/license_db.html | CC BY 4.0: credit the O*NET Database and the U.S. Department of Labor, Employment and Training Administration; link the licence; note changes | 2026-10-21 | US occupations; record version used and which occupations each of our roles is based on |

| ESCO | Skills taxonomy (alternative) | https://esco.ec.europa.eu | NOT CONFIRMED: licence page did not load on 2026-10-21 | TBD | Do not use until terms are read |

| Simplilearn SkillUp | Course provider | https://www.simplilearn.com/free-google-sheets-course-skillup | Free course, no licence terms stated beyond platform ToS | 2026-10-22 | Spreadsheets course, 1 hour, free, certificate on completion |

| Alison | Course provider | https://alison.com/course/understanding-spreadsheets | Free course, CPD-accredited, platform ToS apply | 2026-10-22 | Spreadsheets course, provider states "1.5-3 Hours" range, used upper bound (3) per our honesty rule |

| Tableau | Course provider | https://www.tableau.com/learn/data-literacy | Free, requires a free Tableau account login | 2026-10-22 | Data literacy course, 5+ hours stated on page, covers stats/data types/storytelling |

| Simplilearn SkillUp | Course provider | https://www.simplilearn.com/prompt-engineering-free-course-skillup | Free course, no licence terms stated beyond platform ToS | 2026-10-22 | Prompt engineering course, 1 hour, free, certificate on completion |

| Anthropic (Claude Academy) | Course provider | https://anthropic-partners.skilljar.com/claude-code-101 | Free, official Anthropic course, no licence terms beyond Skilljar platform ToS | 2026-10-22 | Claude Code 101, 12 lessons; hours (1.5) sourced from a third-party listing (Stanford AI Catalyst, 81 min) since the course's own page states no duration — flagged here for transparency |

| Simplilearn SkillUp | Course provider | https://www.simplilearn.com/learn-data-analytics-for-beginners-skillup | Free course, no licence terms beyond platform ToS | 2026-10-22 | Data analytics course, free, certificate; hours (2) computed by summing the page's own listed lesson lengths (~2.2h total), since the FAQ states no fixed duration |

| Alison | Course provider | https://alison.com/course/working-as-an-it-support-technician | Free, CPD-accredited, platform ToS apply | 2026-10-22 | IT support technician course, provider states "3-4 Hours" range, used upper bound (4) per our honesty rule |

| — | Gap (not a source) | — | — | 2026-10-22 | No clean, verified free course found for chatbot_qa — options checked were paid/instructor-led (QA.com) or not ddQA-specific (general ChatGPT usage courses on Alison). Flagged for team / revisit if time allows. |

| Simplilearn SkillUp | Course provider | https://www.simplilearn.com/learn-uipath-course-skillup | Free course, no licence terms beyond platform ToS | 2026-10-22 | UiPath RPA course, free, certificate; page states both "4 Hours" (course info) and "3 hours" (FAQ) — used upper bound (4) per our honesty rule |

| Alison | Course provider | https://alison.com/course/introduction-to-responsible-ai-use-and-design | Free, CPD-accredited, platform ToS apply | 2026-10-22 | Responsible AI course, provider states "1-2h" range, used upper bound (2) per our honesty rule |
## O*NET occupations used as references

O*NET 31.0 Database (version named on the licence page), U.S. Department of Labor, Employment and Training Administration, used under CC BY 4.0. Codes and titles copied from https://www.onetonline.org/find/all on 2026-10-21. We changed the content: our skill lists are simplified selections, not O*NET's own lists. "closest" means O*NET has no exact match for our role.

| Our id | Kind | O*NET code | O*NET title | Match |
|---|---|---|---|---|
| `it_support_specialist` | role | 15-1232.00 | Computer User Support Specialists | direct |
| `qa_analyst` | role | 15-1253.00 | Software Quality Assurance Analysts and Testers | closest |
| `ai_ops_lead` | role | 15-1211.00 | Computer Systems Analysts | closest |
| `automation_specialist` | role | 13-1111.00 | Management Analysts | closest |
| `cx_insights_analyst` | role | 13-1161.00 | Market Research Analysts and Marketing Specialists | closest |
| `data_analyst` | role | 15-2051.01 | Business Intelligence Analysts | direct |
| `esg_analyst` | role | 13-1199.05 | Sustainability Specialists | direct |
| `junior_data_scientist` | role | 15-2051.00 | Data Scientists | direct |
| `automation_technician` | role | 17-3024.01 | Robotics Technicians | direct |
| `process_improvement_tech` | role | 17-3026.00 | Industrial Engineering Technologists and Technicians | direct |
| `maintenance_technician` | role | 49-9041.00 | Industrial Machinery Mechanics | closest |
| `vision_qc_technician` | role | 19-4099.01 | Quality Control Analysts | closest |
| `solar_pv_technician` | role | 47-2231.00 | Solar Photovoltaic Installers | direct |
| `solar_designer` | role | 17-2199.11 | Solar Energy Systems Engineers | closest |
| `energy_efficiency_analyst` | role | 47-4011.01 | Energy Auditors | closest |
| `ev_charger_technician` | role | 47-2111.00 | Electricians | closest |
| `aisyah` | persona (current job) | 43-4051.00 | Customer Service Representatives | direct |
| `arjun` | persona (current job) | 43-3031.00 | Bookkeeping, Accounting, and Auditing Clerks | direct |
| `mei_ling` | persona (current job) | 51-2022.00 | Electrical and Electronic Equipment Assemblers | direct |
| `hafiz` | persona (current job) | 47-2111.00 | Electricians | direct |

## Probe Test (Gavin)
PASS arXiv: 73 papers matched in 2025-09
PASS Arbeitnow: 300 postings on page 1, fields ['company_name', 'created_at', 'description', 'job_types', 'location']...
PASS Remotive: 9 postings (expected to be small, about 10)

## Source terms (checked 2026-10-23)

### arXiv API
Read: https://info.arxiv.org/help/api/tou.html and https://info.arxiv.org/help/api
- Max one request every 3 seconds, one connection at a time. Our code pauses 3 s between requests.
- Metadata is CC0. Reuse is allowed. Link back to arXiv when republishing records.
- Acknowledge arXiv with: "Thank you to arXiv for use of its open access interoperability."
- Do not use the names or logos "arXiv" or "arXiv.org" to suggest arXiv endorses the project.
- Our use: we store monthly paper counts per skill, not the papers themselves.
- Not confirmed: how strict the rate limit is in practice. We have seen HTTP 429 and the code backs off.

### Remotive API
Read: https://remotive.com/api/remote-jobs (terms are noted on the API page)
- Name Remotive as the source and link back to the Remotive URL.
- Remotive delays its jobs by 24 hours.
- Do not submit Remotive jobs to third-party sites (Jooble, Google Jobs, LinkedIn) or show them behind a sign-up wall.
- Guidance is at most about 4 requests a day. Our code caches for 6 hours.
- Our use: we count skill mentions in postings. We do not show the listings.

### Arbeitnow API
Read: https://www.arbeitnow.com/api/job-board-api and https://www.arbeitnow.com/terms (section 11, API)
- The API is provided "as is", with no warranties. It may be interrupted or changed.
- Required: provide a link back to arbeitnow.com on our platform.
- Arbeitnow may revoke API permission at any time.
- Section 2 of the website terms licenses website materials for personal, non-commercial viewing and bars mirroring them. We treat this project as non-commercial and store only the counts we need.
- Our use: we count skill mentions in postings and do not show the listings. Our code pauses 3 s between pages, caches for 3 hours and keeps partial results if rate limited. [Check against backend/app/ingest/arbeitnow.py before committing.]
- Open item: the app footer does not yet link back to Arbeitnow. [Fix before the demand data goes public.]

### Limitations
- Job data is mostly German and European, not Malaysian.
- About one week of history, so windows are short.
- The older window only holds postings still live today.

| Qwen3-8B | Open language model (runtime) | https://huggingface.co/Qwen/Qwen3-8B | Apache 2.0 | 2026-10-24 | Served with vLLM (RunPod worker-vllm) on our own RunPod Serverless endpoint. Used for CV skill suggestions and the "Ask your guide" chat; output is checked in code before it is shown |

| RunPod Serverless | GPU hosting | https://www.runpod.io/legal/terms-of-service | RunPod terms of service; paid per second of GPU time (event credit) | 2026-10-24 | Hosts the Qwen3-8B endpoint. Receives only redacted CV text or facts the app computed; nothing is stored by our app |

| Dreamstime: "Brown seamless pattern, D&D dice" (image 259770746) | Image (page background) | https://www.dreamstime.com/brown-seamless-pattern-d-dice-board-games-image259770746 | Royalty-free licence through a Dreamstime free-trial download; credited in the footer. TBD: confirm the licensed file replaced the committed one, and that keeping it in a public repo is allowed | 2026-10-24 | `frontend/assets/background/dice.png` |

| Class illustrations (Bard, Wizard, Paladin, Druid) | Images | (in repo) `frontend/assets/classes/*.svg` | TBD: lift77 to confirm whether self-made or from a source, and its licence | 2026-10-24 | Shown on the class selector, class card and character sheet |
