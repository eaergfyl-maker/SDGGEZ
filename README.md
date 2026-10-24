> [!IMPORTANT]
> ## 📁 Submission Documents & Templates
> **All required submission templates are in the Google Drive folder below. Download them before you start.**
>
> ### 👉 [**OPEN THE GOOGLE DRIVE FOLDER**](https://drive.google.com/drive/folders/1xw7c2aN8N-at8hPEULzkcU76e_FFb0Ef) 👈

---

# Future-Ready RPG

> A career skill tree for workers whose jobs AI is changing: it shows which skills are rising or
> declining from real, dated data, matches people to future roles, and gives a step-by-step
> reskilling path linked to the UN SDGs.

---

## Team Information

| Field                  | Details                                     |
| ---------------------- | ------------------------------------------- |
| **Team Name**          | TBD                                         |
| **Team Domain**        | Domain 1 — Aiversecity Future-Ready Workforce |
| **SDG Track (1–17)**   | SDG 4 — Quality Education (targets 4.3, 4.4), with SDG 8 — Decent Work and Economic Growth (targets 8.2, 8.5) |
| **Team Leader**        | TBD                                         |
| **University**         | TBD                                         |
| **Number of Members**  | 5                                           |

## Links

| Resource          | Link                                           |
| ----------------- | ---------------------------------------------- |
| GitHub Repository | https://github.com/eaergfyl-maker/SDGGEZ       |
| Replit Project    | TBD                                            |
| Live Demo         | TBD                                            |
| RunPod Endpoint   | Not used: the project has no GPU workload (see [How We Use RunPod](#how-we-use-runpod-required)) |
| Slide Deck        | TBD                                            |
| Demo Video        | TBD                                            |

---

## Overview

### Problem

AI is changing which jobs exist faster than training programmes can keep up. In Malaysia, 56% of
professionals already use AI tools at work but only 26% have had formal training (Hays Asia
Salary Guide 2025), and the Ministry of Science, Technology and Innovation has said more than
600,000 workers will need reskilling within three to five years. Workers don't know which skills
to learn, and learning plans are usually static lists that are out of date when published.

### Solution

Future-Ready RPG tracks signals of AI advancement and job-market change and turns them into a
game-style skill tree. Every skill gets a momentum score from real, dated sources: job postings
(how often a skill is mentioned and whether that share is rising) and arXiv research papers (how
fast research on the topic is growing). The app matches a person to future roles with a score
that shows its working, then builds a reskilling path from a catalogue of courses we have checked
ourselves. Three scenarios (AI moving slowly, moderately or fast) show a range instead of one
prediction, and every role and skill links to an SDG target.

All scoring is deterministic and explainable: no language model makes recommendations, and
the app never invents jobs, courses or statistics. It supports career decisions; the person
makes them.

### Key Features

- **Skills profile** — pick a starting class (Bard, Wizard, Paladin, Druid), each a sample starting kit based on a synthetic persona's job and skills, or describe yourself by ticking skills or by pasting a CV, which fills the checklist with the evidence for each skill (invented CVs only; nothing is stored). The class comes from the skills.
- **Career areas** — 16 roles are grouped into four career areas so each tree stays readable. A starting class opens in its own area; for a custom profile the area is guessed from the ticked skills (shared skills like communication barely count), and the user can always switch.
- **Live trend signals** — skill momentum from Arbeitnow and Remotive job postings and arXiv research counts, each shown with its source and date. Mock data is clearly labelled until a real snapshot exists.
- **Future-role matching** — 16 roles, each based on an O\*NET occupation, with an importance-weighted match score, a skills gap, and a one-sentence explanation.
- **Skill tree and reskilling path** — prerequisites unlock in order; the pathway lists verified courses with hours, cost and an estimated number of weeks.
- **SDG mapping** — every skill and role is tagged to SDGs (4, 7, 8, 9, 10, 11, 12, 13, 16) with a target and a reason.
- **Bahasa Malaysia** — an EN / BM toggle in the header switches the interface language. Skill, role and course names stay in English.
- **Handling uncertainty** — slow, moderate and fast AI scenarios, with each role's outlook shown as a range.
- **Living map** — refreshing the data creates a new snapshot, and the app shows what changed.

### Tech Stack

| Layer         | Technology                   |
| ------------- | ---------------------------- |
| Frontend      | HTML, CSS, vanilla JavaScript (ES modules), SVG skill tree; no build step |
| Backend       | Python, FastAPI, Uvicorn, Pydantic |
| Database      | SQLite                       |
| Data sources  | Arbeitnow and Remotive job APIs, arXiv API, O\*NET 31.0 (occupation reference) |
| AI / Compute  | Deterministic scoring in Python on Replit; no GPU workload, so RunPod is not used |
| Hosting / Dev | Replit                       |
| Tests / CI    | pytest, JSON Schema data validation, GitHub Actions |

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point (serves the API and the frontend)
│   │   ├── api/routes.py        # HTTP endpoints (/api/tree, /api/trends, /api/pathway, ...)
│   │   ├── ingest/              # Job postings (Arbeitnow, Remotive), arXiv counts, snapshots
│   │   ├── scoring/             # Momentum, matching, skill tree, pathway (pure functions)
│   │   ├── trends.py            # Latest snapshot, or labelled mock data
│   │   └── db.py                # SQLite schema
│   └── tests/                   # Unit and API tests
├── data/
│   ├── skills.json              # 39 skills with prerequisites, keywords, SDG tags
│   ├── roles.json               # 16 roles in 4 career families, with O*NET references
│   ├── personas.json            # 4 synthetic personas
│   ├── courses.json             # Verified course catalogue
│   ├── sdg_map.json             # SDG targets and reasons
│   └── schema/                  # JSON Schemas for the files above
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/                      # tree/ (skill tree, classes), panels/ (intake, radar, pathway)
├── docs/                        # Team, tasks, decisions, sources, AI tools log, role guides
├── scripts/
│   ├── validate_data.py         # Schema and cross-reference checks for data/
│   └── probe_sources.py         # Checks each external data source responds as expected
├── story/                       # Story files for skill nodes (optional)
├── submission/                  # Required submission documents (to add)
│   ├── SDC2026_TeamName_Preliminary.pdf      # Preliminary submission
│   ├── SDC2026_TeamName_TechDeclaration.pdf  # Technology declaration
│   └── SDC2026_TeamName_Replit_POU.pdf       # Replit proof of use
├── .env.example                 # Example environment variables
├── .gitignore
├── .replit                      # Replit run configuration
├── replit.md                    # Replit-specific notes
├── LICENSE
├── requirements.txt             # Python dependencies
└── README.md
```

### Architecture

```
User ──► Replit (FastAPI app: API + frontend)
             │
             ├──► Scoring (momentum, matching, tree, pathway) ──► data/*.json
             │
             └──► SQLite snapshot ◄── Ingestion (Arbeitnow, Remotive, arXiv)
                     │                  run on demand / protected /api/refresh
                     └──► falls back to labelled mock data when no snapshot exists
```

---

## How to Run

### Option 1 — Run on Replit (Recommended)

1. Open the Replit project (link above), or import this repository via **Create Repl → Import from GitHub**.
2. Open the **Secrets** tab (🔒) and add the variables you need (see `.env.example`). None are required for the default demo:
   - `REFRESH_TOKEN` — protects the `/api/refresh` endpoint that fetches new data
   - `INGEST_CONTACT` — a team email sent in the User-Agent of outgoing data requests
3. Click **Run**. Replit uses the `.replit` file to start `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 5000`. Replit manages the Python environment, so don't create a virtual environment there.

### Option 2 — Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/eaergfyl-maker/SDGGEZ.git
cd SDGGEZ

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env            # then fill in your values

# 5. Run the app
uvicorn backend.app.main:app --reload --port 8000
```

Open http://localhost:8000 for the app and http://localhost:8000/docs for the API docs.

To fetch real job-posting data and save a snapshot (cached; respect the sources' rate limits):

```bash
python -m backend.app.ingest.pipeline --note "first real snapshot"
```

### Run Tests

```bash
pytest
python scripts/validate_data.py
```

---

## How We Use Replit *(Required)*

- **Development:** the team imports the GitHub repository into a shared Repl. GitHub stays the source of truth: changes go through branches and pull requests.
- **AI assistance:** Replit Agent was used to configure the Replit environment and for some frontend code. Claude Code was used for much of the backend and frontend code. The CV reader can call Qwen3-8B (an open model we host on RunPod) for extra skill suggestions, which the code checks before showing. This is declared in the Technical & Tools Declaration and logged in `docs/ai-tools-log.md`.
- **Hosting:** the app is deployed with Replit Deployments at the Live Demo link above.
- **Secrets:** tokens and keys are stored in Replit Secrets, never in the code.

📄 Proof of use: [`submission/SDC2026_TeamName_Replit_POU.pdf`](submission/SDC2026_TeamName_Replit_POU.pdf)

## How We Use RunPod *(Required)*

We do not use RunPod. The handbook (section 9.4) requires RunPod for work that needs a GPU:
training, fine-tuning, or running a model that needs a GPU. Our scoring is deterministic Python
that runs on Replit's CPU, and we do not train or host any model, so there is no GPU workload.
If we add a GPU workload later, it will run on RunPod and this section will be updated.

---

## Data Sources & Responsible Use

- **Public or synthetic data only.** The personas are invented; the app collects and stores no personal data.
- **Every number has a source and a date.** Job data: [Arbeitnow](https://www.arbeitnow.com) and [Remotive](https://remotive.com). Research data: arXiv. Occupations: O\*NET 31.0 Database, U.S. Department of Labor, Employment and Training Administration, used under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), adapted by us. Full list in [`docs/sources.md`](docs/sources.md).
- **Nothing is invented.** Courses come only from `data/courses.json`, and only entries someone has checked (`verified: true`) are counted.
- **Known limits, stated openly:** the job postings are mostly German and European rather than Malaysian, and cover about one week; scenario weights are documented assumptions ([`docs/DECISIONS.md`](docs/DECISIONS.md)), not predictions.
- **Fair by design:** scoring uses skills only, never name, age, gender or ethnicity, and a test checks that identical skills give identical results.

---

## Challenges & Learnings

- **Thin or rate-limited data sources.** Remotive's public API returns only about 10 postings, Arbeitnow rate-limits after about 26 quick requests, and arXiv rate-limited our date-range queries. We switched to Arbeitnow as the main job source, cache every response, back off on rate limits, keep partial results, and resume instead of restarting.
- **Short history.** With about a week of job data, trends are noisy. We compare shares of postings instead of raw counts, ignore skills with too few mentions, and label every number with its window and caveats.
- **Crowded skill trees.** One tree with every skill was unreadable, so roles are grouped into four career families and a test keeps each tree within the layout limit.
- **Learning:** being explicit about what the data cannot show (region, history, sample size) made the scoring easier to explain and to trust.

## Future Improvements

- [ ] Add a Malaysian job-market data source
- [ ] Grow the verified course catalogue, including programmes claimable through HRD Corp where the provider confirms eligibility
- [ ] Commit a seed snapshot so every deployment starts with real data
- [ ] Story scenes for each skill node
- [ ] Bahasa Malaysia and Chinese language options
- [ ] HR / team view with a workforce skills-gap heatmap

## Team

| Name        | Role                | GitHub                                   |
| ----------- | ------------------- | ---------------------------------------- |
| TBD         | Lead: API, integration, deploy | TBD |
| TBD         | Data ingestion      | TBD |
| TBD         | Scoring and matching | TBD |
| TBD         | Frontend: skill tree and game | TBD |
| TBD         | Frontend: panels and content data | TBD |

Role guides for each member are in [`docs/guides/`](docs/guides/).

---

## Submission Checklist

- [ ] Team name, domain (Domain 1) and SDG track filled in
- [ ] Slide deck link added
- [ ] Demo video link added (5–7 minutes)
- [ ] Replit used, with proof of use in `submission/`
- [ ] RunPod: not used (no GPU workload); confirmed acceptable with the organisers
- [ ] Preliminary submission completed (`SDC2026_TeamName_Preliminary.pdf`)
- [ ] Technology declaration completed (`SDC2026_TeamName_TechDeclaration.pdf`), including Replit Agent and other AI tools
- [ ] Submission files renamed with your team name (replace `TeamName`)
- [ ] "How to Run" steps verified
- [ ] No API keys or secrets committed to the repository
- [ ] Committee GitHub accounts added as collaborators and the repository made public

## License

This project is licensed under the [Apache License 2.0](LICENSE).
