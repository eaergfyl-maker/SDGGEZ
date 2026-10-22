# Guide 3: Scoring and matching engine

You decide what the skill tree contains and what the numbers mean. Judges will ask you "why is
this role ranked here?" and "why is this skill rising?". Your code and data have to answer both
in one sentence. This is the core of Innovation and Problem-Solution Fit.

Time budget: about 3 hours Wednesday (data), 3 hours Thursday (scoring), 2 hours Friday
(pathway), then tuning.

## Status (2026-10-22)
Steps 1 to 7 are done on the `part-3` branch: real ids, O*NET references, families, capped
components, low-data flag, role outlook and range, a clearer `why`, shared courses counted once,
week estimates, and tests. What is left for Member 3 is review and tuning: check the results
with real data once Member 2's snapshot exists, and adjust weights only with a reason in
`docs/DECISIONS.md`. The "Known issue" sections below describe what was fixed and why.

## What you own

| Thing | Where |
|---|---|
| Skills and prerequisites | `data/skills.json` |
| Roles, required skills, importance weights | `data/roles.json` |
| Momentum and scenarios | `backend/app/scoring/momentum.py` |
| Match score and skills gap | `backend/app/scoring/matching.py` |
| Tree states and layout tiers | `backend/app/scoring/tree.py` |
| Pathway ordering | `backend/app/scoring/pathway.py` |
| Scoring tests | `backend/tests/test_scoring.py` |

All of `scoring/` is pure Python: no network, no database. Keep it that way. It is what makes
your part easy to test and easy to explain.

## IDs freeze today (Wed 21 Oct)
Other people key their work on skill and role ids (`ai_tools`, `qa_analyst`): ingestion
keywords, courses, SDG tags, story files, and the frontend. After today, never rename an id.
You can add new ones and edit names, weights and prerequisites. Tell the team when the first
real list is in.

## How the four pieces work today (read the code once, it is short)

### 1. Momentum (`momentum.py`)
Each skill has up to three trend components, each a percent change or `None`:
`research_growth` (arXiv), `demand_growth` (job postings), `outlook` (a cited report).

```
momentum = scale * (sum of weight_i * component_i) / (sum of weight_i for components we have)
```
A missing component is skipped and the remaining weights are renormalised. If nothing is
available the result is `None` (the UI says "no data"). The result is clamped to plus or
minus 100. `direction()` labels it rising (at least +5), declining (at most -5) or stable.

Scenarios change the weights and a scale factor:

| Scenario | research | demand | outlook | scale |
|---|---|---|---|---|
| slow | 0.2 | 0.5 | 0.3 | 0.6 |
| moderate | 0.3 | 0.5 | 0.2 | 1.0 |
| fast | 0.5 | 0.35 | 0.15 | 1.5 |

These numbers are placeholders I chose. They are assumptions, not findings. You must tune them
and write down why (see Step 4).

### 2. Match score (`matching.py`)
```
score = 100 * (sum of importance for role skills the user has) / (sum of importance of all role skills)
```
The gap is the skills the user lacks, sorted by importance, then by momentum. `why` is a
plain sentence ("3 of 5 skills matched, weighted by importance"). It is deliberately simple so
it can be explained to anyone.

### 3. Tree (`tree.py`)
Skill tier = 0 if it has no prerequisites, otherwise 1 + the highest prerequisite tier. A node
is `mastered` if the user owns it, `available` if all prerequisites are owned, else `locked`.
A role sits one tier above its highest required skill and is `available` when all its
`requires` skills are owned.

Note: a role can be `available` while its match score is below 100%. `requires` are the
gate skills; the `skills` list with importance weights is everything the job uses. That is
intentional, but explain it to the team so nobody thinks it is a bug.

### 4. Pathway (`pathway.py`)
Needed skills = the role's skills and required skills, plus all their prerequisites, minus what
the user owns. They are ordered by tier. For each skill it picks the cheapest verified course.
Unverified courses are shown with a warning and never counted in totals.

## Step 1. Choose and declare your skill reference (Wednesday, 30 min)
Do not invent skill names from nothing. Base them on a published taxonomy so you can say where
they came from.

- **O\*NET** (US Department of Labor). The database is published under CC BY 4.0. Attribution
  rule: credit "the O\*NET Database and the U.S. Department of Labor, Employment and Training
  Administration", link to the licence, and say where you changed anything. Source:
  https://www.onetcenter.org/license_db.html (checked 2026-10-21).
- **ESCO** (European Commission). I could not load its licence page, so its exact terms are
  **unconfirmed**. Only use it if you read and record its terms yourself.

Recommendation: use O\*NET as the reference. Use it for names, descriptions and which skills a
role needs. You do not need to download all of it: pick the 15 to 25 occupations you care
about and note their O\*NET codes in a `source` comment in your notes (`docs/sources.md`).
Add the credit line to the Tech Declaration and to the app footer. Add a row to
`docs/sources.md` with the version and date accessed.

Caveat to state: O\*NET describes US occupations. Say that the taxonomy is a reference, and
that Malaysian relevance comes from our personas and the cited Malaysian figures.

## Step 2. Design the skill and role set (Wednesday, 2 hours)

Do not try to cover the economy. Cover a few believable journeys well.

1. Pick 3 or 4 personas (Aisyah the customer service executive is already there). Add for
   example a fresh graduate and a manufacturing worker. Personas are synthetic. They live in
   `data/personas.json`: ask Member 5 to add them, or add them yourself.
2. For each persona, sketch 2 or 3 target roles that make sense (a "bridge" role and a
   "stretch" role).
3. List the skills those roles need, then the prerequisites between skills.
4. Count. Aim for about 40 to 60 skills and 15 to 25 roles in total.

### Constraints enforced by `scripts/validate_data.py`
Run it after every edit: `python scripts/validate_data.py`.

| Rule | Why |
|---|---|
| Skill `name` and role `short_name` at most 16 characters | They must fit a node in the tree |
| `id` is lowercase letters, digits and underscores | Used in URLs and story file names |
| Every `prereqs`, `requires` and role skill must exist | No dangling references |
| No cycles in prerequisites | The tree would never unlock |
| Role `importance` is 1, 2 or 3 | See the rubric below |
| Every SDG number you use must exist in `data/sdg_map.json` | Coordinate with Member 5 |
| `keywords` has at least 1 entry | Ingestion counts these in job postings |

### Importance rubric (write this in `DECISIONS.md`)
| Value | Meaning |
|---|---|
| 3 | Core: you cannot do the job without it |
| 2 | Important: used most days |
| 1 | Helpful: used sometimes |

### Layout warning: do not put 60 skills in one tree
The frontend spreads each tier's nodes evenly across 680 px and each node is 124 px wide. At
6 or more nodes in the same tier they overlap. With 50 skills in 4 tiers, most tiers would have
more than 10.

Fix (agree this with Member 4 and Member 1 on Wednesday, then record in `DECISIONS.md`):
1. Add a `family` field to roles (done 2026-10-21: `service-ai`, `data`, `industry`,
   `green-energy`). A family's skills are derived from its roles plus all prerequisites, so
   skills need no family field and cannot disagree with the roles.
2. `/api/tree` takes `family` (or `all`) and defaults to the persona's family (done).
3. Keep each tree to about 15 to 25 nodes, at most 5 per tier. `test_data.py` fails if a
   family breaks this.

The user then sees the path for their persona, which is also a better story than a wall of
nodes. A schema change is a contract change: write it in `DECISIONS.md` first.

### Writing keywords (with Member 2)
Member 2 counts these in job postings. Use 3 to 6 specific phrases per skill, lowercase, such
as `power bi`, not generic words like `data` or `communication`. After Member 2's first run,
ask for the per-keyword match counts and remove any keyword that matches a large share of all
postings for no good reason.

## Step 3. Write the data (Wednesday evening to Thursday)
Add skills and roles in small commits, validating each time. Example role entry:

```json
{
  "id": "qa_analyst",
  "name": "Conversational-AI QA analyst",
  "short_name": "QA analyst",
  "requires": ["chatbot_qa"],
  "skills": [
    {"skill": "ai_tools", "importance": 3},
    {"skill": "prompting", "importance": 3},
    {"skill": "chatbot_qa", "importance": 3},
    {"skill": "communication", "importance": 2},
    {"skill": "empathy", "importance": 1}
  ],
  "sdg": [8, 9]
}
```
Keep a short note per role in `docs/sources.md` saying which O\*NET occupation it was based on.
Do not copy long text from any source.

SDG tags: each tag needs a reason. Do not tag everything to everything. Work with Member 5,
who owns `sdg_map.json` and writes the one-line justification per SDG.

## Step 4. Tune momentum (Thursday, 2 hours)

### Known issue 1: components have different scales
Research growth can easily be +200% (a topic exploding from few papers), while demand share
changes are usually within plus or minus 30%. Today only the final result is clamped, so a huge
research number can swamp everything. Fix: clamp each component before averaging.

In `momentum.py`:
```python
CAP = 100.0

def momentum(components, scenario="moderate"):
    weights = SCENARIOS[scenario]
    present = {k: max(-CAP, min(CAP, components[k]))
               for k in COMPONENTS if components.get(k) is not None}
    ...
```
Add a test: `momentum({"research_growth": 500, "demand_growth": 10})` should equal a value
computed with research capped at 100.

### Known issue 2: tiny samples give wild numbers
A skill with 3 mentions last week and 1 the week before is +200%. Ask Member 2 whether the
demand component can carry a count so you can ignore or down-weight skills below a minimum
sample (for example fewer than 30 postings in the recent window). Show "low data" rather than a
dramatic number.

### Decide and document the scenarios
Scenarios are the "handling uncertainty" must-have. They are assumptions about the world, so
write them as assumptions, not as predictions. In `docs/DECISIONS.md`, one row each:

| Scenario | What we assume | How the numbers change |
|---|---|---|
| Slow | AI adoption in Malaysian workplaces is gradual | Trend signals are dampened (scale 0.6), published outlook counts more |
| Moderate | Current pace continues | Baseline |
| Fast | AI capability and adoption accelerate | Research signal counts more, changes amplified (scale 1.5) |

Change the numbers if you can justify a better choice, and write the reason. A judge will ask
"why 1.5?". An honest answer is "it is an adjustable assumption; here is what it does to the
ranking", which is better than pretending it is measured.

### Show a range, not a single answer
For uncertainty, show how a role's outlook varies across scenarios. Add this helper to
`tree.py` and expose it on role nodes:

```python
from .momentum import SCENARIOS

def role_outlook(role, mom):
    pairs = [(i["importance"], mom[i["skill"]]) for i in role["skills"]
             if mom.get(i["skill"]) is not None]
    if not pairs:
        return None
    return round(sum(w * m for w, m in pairs) / sum(w for w, _ in pairs), 1)

def outlook_range(role, components):
    values = [role_outlook(role, {sid: momentum(c, s) for sid, c in components.items()})
              for s in SCENARIOS]
    values = [v for v in values if v is not None]
    return {"min": min(values), "max": max(values)} if values else None
```
The UI can then say "outlook between +4 and +17 depending on how fast AI moves", which is
the multi-scenario output the brief asks for. Ask Member 4 to show it on the role panel.

Keep the role's match score and its outlook as two separate numbers: "how well do I fit
today" and "is this role growing". Do not blend them into one mystery number. If you want one
combined ranking, show both inputs next to it.

## Step 5. Matching (Thursday)

What exists works. Improvements, in priority order:

1. **A clear "why" for every result.** Extend `why` to name the biggest gap: "4 of 5 skills
   matched; biggest gap: Prompting (core, rising +38%)". Keep it one sentence.
2. **Edge cases.** A role whose skills the user fully owns (score 100, empty gap). A user who
   owns nothing (score 0). A skill with `momentum = None` in the gap list (sorting must not
   crash: it is already handled with `or 0`). Add a test for each.
3. **Partial credit for related skills (optional, only if time).** If a user has `crm_tools`
   and the role needs `data_literacy`, give a small fixed credit through an explicit
   `related` list in the data, not through a model. Keep it explainable, or skip it.
4. **Do not use any personal attribute** (age, gender, ethnicity, name) anywhere in scoring.
   Today none is used. Add a test that proves two users with the same skills get identical
   output regardless of persona name, which backs the optional fairness feature.

## Step 6. Pathway (Friday)

### Known issue 3: shared courses are counted twice
If one course covers two skills, `build_pathway` adds its hours and cost once per skill. Fix by
counting each course once. In `pathway.py`:

```python
seen = set()
for sid in needed:
    ...
    if best:
        if best["id"] not in seen:
            seen.add(best["id"])
            total_hours += best["hours"]
            total_cost += best["cost_myr"]
```
Test: two skills, one course covering both, the total must equal that course's hours once.

### Known issue 4: no time estimate in weeks
The brief asks for an "ordered learning plan with estimated time". Personas already have
`hours_per_week`. Pass it from the route to the function and return weeks:

```python
import math

def build_pathway(role, skills, courses, owned, hours_per_week=None):
    ...
    weeks = math.ceil(total_hours / hours_per_week) if hours_per_week else None
    return {..., "estimated_weeks": weeks}
```
In `routes.py`, look up the persona and pass `persona["hours_per_week"]` (Member 1 reviews the
route change). Label it an estimate in the UI.

### Order
Steps are ordered by tier, so prerequisites come first. Check the result reads naturally for
each persona, and fix prerequisites in the data if it does not.

### Never invent
`build_pathway` only returns courses from `data/courses.json`. Keep it that way. Member 5 adds
and verifies courses; if a skill has none, the response lists it in
`skills_without_verified_course`, and the UI says so. Do not add fallback text like "take any
Python course".

## Step 7. Tests you should have by Friday
Run `pytest backend/tests/test_scoring.py -v`. Add:

- [ ] Each component clamped before averaging
- [ ] Scenario ordering: for a rising skill, fast > moderate > slow; for a declining skill, the reverse
- [ ] Missing components renormalise weights correctly
- [ ] Match: full match, no match, empty gap, `None` momentum in gap
- [ ] Same skills, different persona name gives identical match
- [ ] Tree: a role with several required skills is locked until all are owned
- [ ] Tree: tier depth for a three-level chain
- [ ] Pathway: shared course counted once; unverified course never counted
- [ ] Pathway: weeks estimate rounds up
- [ ] `validate_data.py` passes on the full dataset (`test_data.py` runs it)

## Handoffs
| To | What | When |
|---|---|---|
| Everyone | First real skill and role id list | Wed |
| Member 2 | Keywords per skill, which skills need an arXiv query | Wed |
| Member 4 | `family` filter and the `outlook_range` field on role nodes | Thu |
| Member 5 | Course needs per skill (which skills have no course yet), SDG tags to justify | Thu |
| Member 1 | Route changes for `hours_per_week` and `family` | Fri |

## Commit rhythm
Branches `score/momentum`, `score/pathway`, `data/skills-roles`. Small commits, for example
`data: add customer-ops roles`, `score: clamp components before averaging`. Member 2 reviews
(your backup). At least one commit a day.

## Troubleshooting
| Problem | Fix |
|---|---|
| `validate_data.py` says unknown skill | Typo in an id. Search for it across `skills.json`, `roles.json`, `courses.json`, `personas.json` |
| Cycle error | Two skills require each other, directly or through a chain. Remove one link |
| Tree nodes overlap in the browser | Too many nodes in one tier. Use the `family` filter |
| Everything shows "no data" | No snapshot yet, or a skill has no keywords. Ask Member 2 |
| A role is `available` but the match is 60% | Expected. `requires` is the gate, `skills` is the full job |
| A momentum value looks absurd | Look at the component values and the sample sizes first |

## Limitations to state
1. The skill and role set is a small, curated slice, not the whole labour market.
2. Importance weights and scenario factors are our assumptions, documented in `DECISIONS.md`.
3. Momentum rests on short-history job data (mostly German and European) and arXiv research
   activity; it is a signal, not a forecast.
4. The match score measures overlap with a role's listed skills, not whether someone would
   get hired. People make that decision.

## What to say to the judges
- "The match score is the importance-weighted share of a role's skills you already have. One
  formula, no black box."
- "Momentum blends three cited signals; scenarios change the weights and are labelled
  assumptions."
- "We show a range across scenarios instead of one prediction."
- "Scoring never sees age, gender or name, and a test proves identical skills give identical
  results."
- "Courses come only from a verified catalogue; unverified ones are not counted."

## Done when
- [ ] Skill and role ids shared with the team (today)
- [ ] About 40 to 60 skills and 15 to 25 roles, validated, with O\*NET credited
- [ ] Components clamped, scenarios documented in `DECISIONS.md`
- [ ] Role outlook range available to the UI
- [ ] Pathway counts shared courses once and returns estimated weeks
- [ ] All tests in Step 7 pass
- [ ] You can explain every formula in under a minute each
