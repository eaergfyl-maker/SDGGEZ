# Guide 5: Frontend B and content data

You build everything around the tree: who the user is, what is rising and declining, the
reskilling pathway, and the SDG connection. You also own the two data files that decide whether
the pathway and the SDG story are real: the course catalogue and the SDG map. Judges check
exactly these ("every recommendation cites a source", "the SDG link is meaningful rather than
decorative"), so your work carries a lot of the score.

Time budget: about 3 hours Wednesday, 4 hours Thursday (courses take time), 3 hours Friday.

## What you own

| Thing | Where |
|---|---|
| Intake (who is the user) | `frontend/js/panels/intake.js` |
| Future Skills Radar | `frontend/js/panels/radar.js` |
| Pathway | `frontend/js/panels/pathway.js` |
| SDG panel, patch-notes banner (you create these) | `frontend/js/panels/` |
| Course catalogue | `data/courses.json` |
| SDG map | `data/sdg_map.json` |

Member 4 owns the tree and `main.js`. You share `state.js`, `index.html` and `style.css`: pull
before you edit them, commit small, and tell Member 4 when you change them.

## Setup (15 min)
```bash
git clone https://github.com/eaergfyl-maker/SDGGEZ.git && cd SDGGEZ
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --port 8000
python scripts/validate_data.py                        # run after every data edit
```
Open http://localhost:8000 with the DevTools console open. No build step: edit and refresh.

## How panels work (read once)
Panels do not call each other. They share `state` and listen for events:

```js
import { state, on, emit } from "../state.js";
on("role-selected", (roleId) => ...);     // another panel announced something
emit("persona-changed", persona);         // you announce something
```
Data comes from `api.js` (`api.trends`, `api.pathway`, `api.sdgs`, `api.changes`, ...). Escape any
text you put into `innerHTML` with the `esc()` helper (copy it into a shared
`frontend/js/util.js`: it exists in both `tree.js` and `pathway.js`).

## Part A: The data files (do these first, they take the longest)

### A1. Course catalogue: `data/courses.json`
Today it holds one placeholder. Every pathway step with no verified course shows "No course in
the catalogue yet", so an empty catalogue makes the pathway look hollow in the demo.

**Target:** at least one verified course for every skill on the demo persona's path (about 8
to 12 courses), then more for the other personas. Ask Member 3 which skills are on each path.

**Where to look** (use public pages you can open without logging in):
- Free-to-learn pages from established providers (university and company learning sites, open
  course platforms).
- Malaysian programmes: the brief mentions HRD Corp-claimable programmes. Check the provider
  page for the exact conditions and do not assume anyone is eligible.
- Prefer free or low cost; the brief asks for "free or low-cost resources".

**Verification checklist** (all must be true before you set `"verified": true`):
1. You opened the URL in a private browser window and the page exists.
2. Title and provider match what you wrote.
3. **Hours** come from the provider's page (or the sum of the listed modules). Do not guess.
   If the page gives no duration, do not use the course.
4. **Cost** is stated on the page. The field is `cost_myr`: use `0` only if the page says free.
   If the price is in another currency, convert at a stated rate and note the date in
   `funding_note`, or prefer courses priced in MYR.
5. `skills` lists only skill ids from `data/skills.json` that the course really teaches.
6. `funding_note` mentions a funding scheme only if the provider's own page says so.
7. `checked_on` is today's date (YYYY-MM-DD).

Format (values here are for shape only, never paste an example into the real file):
```json
{
  "id": "provider_short_title",
  "title": "<exact title from the page>",
  "provider": "<provider name>",
  "url": "https://...",
  "hours": 12,
  "cost_myr": 0,
  "skills": ["ai_tools"],
  "funding_note": null,
  "verified": true,
  "checked_on": "2026-10-22"
}
```
`validate_data.py` enforces that a verified course has `url`, `hours`, `cost_myr` and
`checked_on`. Run it after every few entries. Do not copy course descriptions, only facts.
Keep a line per provider in `docs/sources.md` (name, URL, date checked).

Never invent a course, a price or a duration. If you cannot verify something, leave it out: the
app handles an empty skill honestly. A gap shown honestly scores better than a fabricated entry.

### A2. SDG map: `data/sdg_map.json`
Every SDG number used in `skills.json` or `roles.json` needs an entry with a **specific
target** and a **reason**. Right now several have `"reason": "TBD"` and empty `targets`.

1. List the SDGs used: `python scripts/validate_data.py` fails if one is missing.
2. For each, find the exact target on the official UN SDG site (sdgs.un.org) and copy the
   target number. The Domain 1 brief itself names 4.3, 4.4, 8.2 and 8.5. Use the official
   wording, not a paraphrase from memory.
3. Write one reason sentence tying the **skill or role** to the target: why does learning this
   contribute? Example of the pattern: "Skills in X help workers move into jobs the target
   describes." Make each reason specific; if all reasons read the same, the SDG link looks
   decorative.
4. Targets must look like `4.4` (digits, a dot, digits or a letter). The validator checks this.

Rule of thumb: tag a skill to an SDG only if you can explain the link in one sentence. Fewer,
honest tags beat many weak ones. Ask Member 3 to remove tags you cannot justify.

## Part B: The panels

### B1. Intake: let users build a profile (Wednesday)
Today you can only pick a persona. The brief asks for a form or questionnaire. Add a skills
checklist so a person can describe themselves, using sample data only.

There is no skills endpoint yet; `/api/trends` returns every skill's `skill` id and `name`, so use that
(or ask Member 1 for a small `/api/skills`).

```js
const t = await api.trends(state.scenario);
const boxes = t.skills.map((s) => `
  <label><input type="checkbox" value="${esc(s.skill)}"> ${esc(s.name)}</label>`).join("");
el.insertAdjacentHTML("beforeend", `<h2>Or describe yourself</h2><div id="skill-boxes">${boxes}</div>
  <button id="use-profile">Use this profile</button>`);

el.querySelector("#use-profile").addEventListener("click", () => {
  const ids = [...el.querySelectorAll("#skill-boxes input:checked")].map((i) => i.value);
  select({ id: "custom", name: "Custom profile", current_role: "Your profile",
           hours_per_week: 6, skills: ids });
});
```
`select` is the function already defined inside `renderIntake`. The backend accepts any
`owned` list, so the custom persona works with an explicit skill list. Empty is valid too.

Rules:
- **No real personal data.** Add a visible note: "Use sample information. We do not store it."
  Nothing here should be sent anywhere except the app's own API, and the app stores nothing.
- Do not add free-text CV upload with real CVs. If you want a text box, use it only to match
  skill keywords in the browser and say it is for sample text.
- Add a "hours per week" input so the pathway can estimate weeks (Member 3 is adding
  `estimated_weeks`).
- Call `loadOwned(persona)` from `state.js` (Member 4 adds it) so progress is restored.

### B2. Future Skills Radar (Thursday)
Today it is two plain lists. Make it a real radar and show where each number comes from.

**Chart without a library** (no new dependency to declare). Horizontal bars:
```js
function bars(items) {
  const row = (s, i) => {
    const w = Math.min(Math.abs(s.momentum), 100) * 2.4;      // 100% = 240px
    const x = s.momentum >= 0 ? 260 : 260 - w;
    const cls = s.momentum >= 0 ? "rising" : "declining";
    return `<g transform="translate(0 ${i * 28})">
      <text x="0" y="14" class="lbl">${esc(s.name)}</text>
      <rect class="${cls}" x="${x}" y="2" width="${w}" height="16" rx="3"/>
      <text x="${s.momentum >= 0 ? x + w + 6 : x - 6}" y="14"
            text-anchor="${s.momentum >= 0 ? "start" : "end"}" class="lbl">
        ${s.momentum > 0 ? "+" : ""}${s.momentum}%</text></g>`;
  };
  return `<svg viewBox="0 0 680 ${items.length * 28}" width="100%">${items.map(row).join("")}</svg>`;
}
```
Add CSS fills for `.rising` and `.declining`. Use different shapes or labels as well as colour.
Skills with `momentum: null` go in a separate "No data yet" line, not silently dropped.

**Source and date per skill.** The `/api/trends` response includes, for each skill,
`components` with `research_growth`, `demand_growth`, `outlook` and, when real data is in use,
a `sources` object (data name, window dates, number of postings, caveats). Show it on demand:
```js
const src = s.components.sources;
const detail = src ? `${esc(src.demand.name)}: ${src.demand.recent_postings} postings,
  from ${esc(src.demand.recent_from)}. ${esc(src.demand.caveat)}` : "Mock data, no source yet";
// put it inside <details><summary>Where does this come from?</summary>...</details>
```
Mock data has no `sources`: say "mock data". Keep the "Mock data" badge logic that
already exists in `radar.js`.

State the limits in the UI: "estimates, not predictions", and the caveat about German and
European postings.

Add a short list "Why is this rising or declining" only if you can write it from the numbers
(for example "job mentions up 12%"), never an invented reason.

### B3. Pathway (Thursday to Friday)
`pathway.js` works. Improve it:

1. **Only link safe URLs.** Course URLs come from a JSON file; render a link only if the URL
   starts with `https://`, otherwise show the title without a link.
   ```js
   const link = c.url && c.url.startsWith("https://") ? `<a href="${esc(c.url)}" ...>` : "";
   ```
2. Show `funding_note` when present, and an "unverified, not counted" label (already there).
3. Show **estimated weeks** when the API returns `estimated_weeks`, labelled as an estimate,
   plus total hours and cost.
4. For skills with no verified course: "No verified course in our catalogue yet". Never
   suggest a generic one.
5. Add a "Print or save my plan" button that calls `window.print()`, with a small print
   stylesheet (`@media print`) that hides everything but the plan. Cheap, and users like it.
6. Show the user's choice: let them untick steps they already know (this keeps the human in
   control) and recompute the totals in the browser.

### B4. SDG panel (Friday, you create `panels/sdg.js`)
This answers "show the user how their chosen career path contributes to the goals".

1. Listen for `role-selected`. Fetch the pathway and read `state.tree.nodes` to get each step's
   skill `sdg` list.
2. Count how many steps and which role tag each SDG appears under.
3. Show, for each SDG: number, name, the target(s), and the **reason** from
   `/api/sdgs`: "This path contributes to SDG 8 (target 8.5) because ...".
4. Add an `<section id="sdg" class="card">` to `index.html` (tell Member 4), and register
   the module in `main.js`.

Aggregate sketch:
```js
const counts = {};
for (const step of pathway.steps) {
  const node = state.tree.nodes.find((n) => n.id === step.skill);
  (node?.sdg || []).forEach((g) => (counts[g] = (counts[g] || 0) + 1));
}
const sdgInfo = await api.sdgs();   // [{sdg, name, targets, reason}, ...]
```
If a reason is still `"TBD"`, show nothing for it rather than the placeholder: finish Part A2 first.

Meaningful, not decorative: the SDG a user picks should change what they see. Ask Member 3
whether a "purpose" filter (highlight roles that contribute to a chosen SDG) is feasible; if
so, add a simple SDG selector.

### B5. Patch-notes banner (Friday, `panels/patch.js`)
This shows the "living map" working. `api.changes()` already exists and returns what moved
between the last two snapshots: `{"changes": [{"skill", "signal", "old", "new"}, ...]}`.

```js
export async function renderPatchNotes() {
  const { changes } = await api.changes();
  const el = document.getElementById("patch");
  if (!changes.length) { el.hidden = true; return; }          // say nothing if nothing changed
  const top = changes.slice(0, 3).map((c) =>
    `${esc(c.skill)} ${c.signal === "demand" ? "job demand" : "research"}:
     ${c.old ?? "no data"}% to ${c.new ?? "no data"}%`);
  el.hidden = false;
  el.innerHTML = `<b>Since the last update:</b> ${top.join("; ")}`;
}
```
Use skill names, not ids, by looking them up from `state.tree`. Never show made-up
changes: if there are fewer than two snapshots, hide it. Share the "highlight what moved" logic with
Member 4 so the tree and the banner agree.

### B6. Quality, accessibility, mobile
- [ ] Every number has a source or date nearby; "Mock data" is visible when it applies
- [ ] Headings in order, buttons are real `<button>`s, form inputs have `<label>`s
- [ ] Not colour alone: rising and declining also have words or arrows
- [ ] Phone width works (cards stack; text at least 14 px)
- [ ] Dark mode readable
- [ ] No console errors on any panel
- [ ] Stretch only if you finish: language toggle (English, Bahasa Malaysia, Chinese) and a
      light "low bandwidth" mode (no animation, no external fonts). These are optional
      points in the brief, not required.

## Handoffs
| From or to | What | When |
|---|---|---|
| Member 3 to you | Final skill ids, which skills sit on each persona's path | Wed |
| You to Member 3 | SDG tags you cannot justify, skills with no course | Thu |
| Member 4 to you | `loadOwned`, shared change-highlight function | Thu |
| Member 1 to you | A `/api/skills` endpoint if you want it | Wed |
| You to the team | Final `courses.json` and `sdg_map.json` | Fri morning |

## Commit rhythm
Branches such as `content/courses-customer-ops`, `ui-panels/radar-chart`, `content/sdg-reasons`.
Small commits: one commit per few verified courses. Member 4 reviews (your backup). At least
one commit a day. Courses and SDG text are data: someone other than you should open at least a
few course links as a second check.

## Troubleshooting
| Problem | Fix |
|---|---|
| `validate_data.py` says course has unknown skill | The skill id is not in `skills.json`. Check spelling, ask Member 3 |
| Verified course fails validation | It needs `url`, `hours`, `cost_myr` and `checked_on` |
| SDG error "used but no entry" | Add that SDG to `sdg_map.json` with target and reason |
| Radar shows nothing | `momentum` is `null` for all skills. No data yet. Show the "No data" state |
| Panel does not react | Missing `on(...)` registration, or the event name does not match `main.js` |
| HTML shows odd characters | You inserted text without `esc()` |

## Limitations to state
1. The catalogue is a small curated list, not every available course.
2. Hours and prices are as published on the date checked and can change.
3. SDG links are our justified mappings, not an official classification of jobs.
4. The profile is a self-reported skills list, not a verified assessment.

## What to say to the judges
- "Every course in the pathway was opened and checked on a stated date; unverified courses are
  never counted and the app says when a skill has no verified course."
- "Each SDG tag has a specific target and a reason. Changing the path changes the SDG view."
- "The profile uses sample data only; nothing is stored or sent anywhere."
- "The radar shows the source, the window and the caveat for each number, and mock data is
  labelled."

## Done when
- [ ] At least one verified course for every skill on the demo persona's path
- [ ] No `TBD` left in `sdg_map.json`; validator passes
- [ ] Skills checklist intake works with sample data
- [ ] Radar chart with a source and date per skill
- [ ] Pathway shows verified totals, weeks, and the human can untick steps
- [ ] SDG panel and patch-notes banner working with real data
- [ ] No console errors, phone and dark mode checked
