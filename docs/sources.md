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
