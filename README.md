# Future-Ready RPG

> > A fantasy skill-tree game built on real, dated job-market data: pick a starting class, train skills to earn XP and SDG badges, and unlock the future roles AI is creating, each with an explainable match score and a learning path.

---

## Team Information

| Field                  | Details                                     |
| ---------------------- | ------------------------------------------- |
| **Team Name**          | ICEMAN                                      |
| **Team Domain**        | Domain 1 — Aiversecity Future-Ready Workforce |
| **SDG Track (1–17)**   | SDG 4 — Quality Education (targets 4.3, 4.4), with SDG 8 — Decent Work and Economic Growth (targets 8.2, 8.5) |
| **Team Leader**        | Eashwar Singh Sidhu                         |
| **University**         | Asia Pacific University                     |
| **Number of Members**  | 5                                           |

## Links

| Resource          | Link                                           |
| ----------------- | ---------------------------------------------- |
| GitHub Repository | https://github.com/eaergfyl-maker/SDGGEZ       |
| Live Demo         | https://sdggez.replit.app                      |
| RunPod Endpoint   | Serverless vLLM endpoint running Qwen3-8B (see [How We Use RunPod](#how-we-use-runpod-required)); the endpoint ID is kept in Replit Secrets |
| Slide Deck        | https://cloudmails-my.sharepoint.com/:p:/g/personal/tp089363_mail_apu_edu_my/IQBRCcjYK1_GSbslUGWoXqdBAZU072I1Xz3ukY7y2TUQUXw?e=q2TKss  |
| Demo Video        | https://youtu.be/0YJ-Uk3pzz0 |

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

All scoring is deterministic and explainable: momentum, role matches and pathways are plain
Python with a test for each rule, and no language model decides them. An open model (Qwen3-8B,
which we host on RunPod) helps in two places only: it suggests extra skills from a pasted CV,
and it explains a user's own results in a chat. Its output is checked in code before anyone sees
it, so the app never invents jobs, courses or statistics. It supports career decisions; the
person makes them.

### Key Features

- **Skills profile** — pick a starting class (Bard, Wizard, Paladin, Druid), each a sample starting kit based on a synthetic persona's job and skills, or describe yourself by ticking skills or by pasting a CV or loading a .txt or Word file. Keyword rules tick the skills they find and show the evidence; the AI model then suggests skills the keywords missed, each with a quote from the CV, left unticked for the person to confirm (invented CVs only; nothing is stored). The class comes from the skills.
- **Career areas** — 16 roles are grouped into four career areas so each tree stays readable. A starting class opens in its own area; for a custom profile the area is guessed from the ticked skills (shared skills like communication barely count), and the user can always switch.
- **Live trend signals** — skill momentum from Arbeitnow and Remotive job postings and arXiv research counts, each shown with its source and date. Mock data is clearly labelled until a real snapshot exists.
- **Future-role matching** — 16 roles, each based on an O\*NET occupation, with an importance-weighted match score, a skills gap, and a one-sentence explanation.
- **Skill tree and reskilling path** — prerequisites unlock in order; the pathway lists verified courses with hours, cost and an estimated number of weeks.
- **SDG mapping** — every skill and role is tagged to SDGs (4, 7, 8, 9, 10, 11, 12, 13, 16) with a target and a reason.
- **Ask your guide** — a chat that explains the user's own results ("Why is this my best match?", "What should I learn first?"). The model answers only from facts the app computed for that user, and any answer containing a number that is not in those facts is withheld.
- **How to use tour** — a step-by-step guide opens on the first visit and highlights each part of the page; the header button reopens it.
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
| AI / Compute  | Deterministic scoring in Python on Replit; Qwen3-8B served with vLLM on a RunPod Serverless GPU endpoint for CV skill suggestions and the guide chat |
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
2. Open the **Secrets** tab and add the variables you need (see `.env.example`). The app runs without any of them; the AI features appear only when the RunPod ones are set:
   - `RUNPOD_API_KEY` and `RUNPOD_ENDPOINT_ID` — turn on the CV skill suggestions and the "Ask your guide" chat
   - `RUNPOD_MODEL` — optional label for the model (default `Qwen/Qwen3-8B`)
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

## How We Use Replit

- **Development:** the team imports the GitHub repository into a shared Repl. GitHub stays the source of truth: changes go through branches and pull requests.
- **AI assistance:** Replit Agent was used to configure the Replit environment and for some frontend code. Claude Code was used for much of the backend and frontend code. At runtime, the CV reader and the "Ask your guide" chat call Qwen3-8B (an open model we host on RunPod), and the code checks its output before showing it. This is declared in the Technical & Tools Declaration and logged in `docs/ai-tools-log.md`.
- **Hosting:** the app is deployed with Replit Deployments at the Live Demo link above.
- **Secrets:** tokens and keys are stored in Replit Secrets, never in the code.

📄 Proof of use: [`submission/SDC2026_TeamName_Replit_POU.pdf`](submission/SDC2026_TeamName_Replit_POU.pdf)

## How We Use RunPod

Running a language model needs a GPU, so it runs on RunPod; everything else runs on Replit.

- **What runs there:** Qwen3-8B (open model, Apache 2.0) served with vLLM on a RunPod **Serverless** endpoint (24 GB GPU with 48 GB as a fallback, 8,192-token context). Workers scale to zero when idle, so we pay only while it answers.
- **What it does:** (1) suggests skills a pasted CV shows but our keyword rules missed; (2) answers questions in "Ask your guide" about the user's own results.
- **How we keep it honest:** the model only sees redacted text (emails and phone numbers removed) or facts the app computed. CV suggestions must use a real skill id and quote the CV word for word; chat answers are withheld if they contain a number that is not in the user's data. Nothing is stored or logged.
- **How it connects:** the backend calls the endpoint's `/run` and `/status` API with keys from Replit Secrets (`backend/app/scoring/cv_ai.py`, `backend/app/scoring/chat.py`). If RunPod is off or slow, the rest of the app works unchanged.
- **Check it:** `python -m scripts.try_cv_ai` sends an invented sample CV and prints what survives the checks (also a warm-up before a demo).

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
- [ ] Chinese and Tamil language options
- [ ] HR / team view with a workforce skills-gap heatmap

## Team

| Name        | Role                | GitHub                                   |
| ----------- | ------------------- | ---------------------------------------- |
| Jayden Tan Jin Wei | Lead: API, integration, deploy | JDTJW |
| Gavin Wong Yung  | Data ingestion  | mightywound |
| Eashwar Singh Sidhu  | Scoring and matching | eaergfyl-maker |
| Lucas Isaac Fong Tayag | Frontend: skill tree and game | lift77 |
| Abdul Rahman Bin Rahmatullah | Frontend: panels and content data | amaninnit-hub |

Role guides for each member are in [`docs/guides/`](docs/guides/).

---

## Submission Checklist

- [x] Team name, domain (Domain 1) and SDG track filled in
- [x] Slide deck link added
- [x] Demo video link added (5–7 minutes)
- [x] Replit used, with proof of use in `submission/`
- [x] RunPod endpoint running, and `RUNPOD_API_KEY` / `RUNPOD_ENDPOINT_ID` set in Replit Secrets
- [x] Preliminary submission completed (`SDC2026_TeamName_Preliminary.pdf`)
- [x] Technology declaration completed (`SDC2026_TeamName_TechDeclaration.pdf`), including Replit Agent and other AI tools
- [x] Submission files renamed with your team name (replace `TeamName`)
- [x] "How to Run" steps verified
- [x] No API keys or secrets committed to the repository
- [x] Committee GitHub accounts added as collaborators and the repository made public

## License

This project is licensed under the [Apache License 2.0](LICENSE).
