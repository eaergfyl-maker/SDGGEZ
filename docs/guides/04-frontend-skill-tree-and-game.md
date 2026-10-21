# Guide 4: Frontend A (skill tree and game)

You build the part people see first and remember last: the skill tree, XP, levels, unlocking,
the scenario switch and the role "boss" panel. If it feels good and clearly shows the data
changing, the demo works. If it is confusing, the best backend in the world is invisible.

Time budget: about 3 hours Wednesday, 3 hours Thursday, 3 hours Friday, then polish.

## What you own

| Thing | Where |
|---|---|
| Tree drawing, layout, click handling, unlock logic | `frontend/js/tree/tree.js` |
| Shared state and event bus | `frontend/js/state.js` |
| Wiring panels together | `frontend/js/main.js` |
| Page shell and styles | `frontend/index.html`, `frontend/css/style.css` |

Member 5 owns the other panels (`frontend/js/panels/`). You share `state.js`, `index.html` and
`style.css`, so pull before you edit them, commit small, and tell Member 5 when you change them.

## Setup (15 min)
```bash
git clone https://github.com/eaergfyl-maker/SDGGEZ.git && cd SDGGEZ
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```
Open http://localhost:8000. Keep the browser DevTools console open at all times: red errors
mean something is broken. There is no build step: edit a file, refresh the page.

You do not need the real data to work. The API serves clearly labelled mock numbers until
Member 2's snapshot exists, so you can build everything against mock data.

## How the frontend works (learn this; you will be asked)

```
index.html loads js/main.js (an ES module)
main.js listens to events and calls the panels
state.js   : one shared object (persona, scenario, owned skills, selected node) + on()/emit()
api.js     : every call to /api/... goes through here
tree.js    : GET /api/tree -> draws SVG nodes and edges, handles clicks and training
```
Events (from `state.js`): `persona-changed`, `scenario-changed`, `tree-updated`,
`role-selected`. A panel announces something happened with `emit(...)`; others react with
`on(...)`. No panel calls another directly, which is why you and Member 5 can work in parallel.

The tree data from `/api/tree` is a list of `nodes` (id, kind `skill` or `role`, name, tier,
state, momentum, direction, sdg, and for roles a `match` object) and `edges` (from, to).
Open http://localhost:8000/docs and try `/api/tree` to see the real shape.

How training works today: clicking "Start quest" adds the skill to `state.owned` (in the
browser only) and calls `/api/tree` again with `owned=...`. The backend recomputes which nodes
unlock. There is no login and nothing is saved.

## Step 1. Read and run it (Wednesday, 30 min)
1. Open the page. Click a green node, an amber node, a purple role node.
2. Click "Start quest" on an amber node and watch the tree update.
3. Switch scenario and watch the numbers change in the detail panel.
4. Read `tree.js` top to bottom. It is about 130 lines.

## Step 2. Fix the known problems (Wednesday to Thursday)

### Problem 1: nodes overlap when a tier is crowded
`layout()` spreads a tier's nodes evenly over 680 px and each node is 124 px wide, so 6 or more
nodes in one tier overlap. Member 3 is adding a `family` filter so the API returns a smaller
subtree (about 15 to 25 nodes, at most 5 per tier). Until it exists, test with the 9 mock skills.
When it lands, add a selector (or choose it from the persona) and pass it through `api.tree`.
Also handle the case gracefully: if a tier has more than 5 nodes, reduce node width instead of
overlapping.

### Problem 2: tiny text on phones
The SVG scales with the screen, so on a 375 px phone the 13 px labels render at about 7 px.
Simplest fix: let the tree scroll sideways instead of shrinking.

In `index.html`, wrap the SVG:
```html
<div class="tree-wrap"><svg id="tree" role="img" aria-label="Skill tree"></svg></div>
```
In `style.css`:
```css
.tree-wrap { overflow-x: auto; }
#tree { min-width: 640px; }
```
Test with DevTools device mode (phone size). It is a better result than unreadable text.

### Problem 3: keyboard and screen reader access
Nodes have `tabindex="0"` but no key handling, and state is shown by colour only. Fix both:

```js
svg.addEventListener("keydown", (e) => {
  if (e.key !== "Enter" && e.key !== " ") return;
  const g = e.target.closest(".node");
  if (!g) return;
  e.preventDefault();
  g.dispatchEvent(new MouseEvent("click", { bubbles: true }));
});
```
In `renderTree`, give each node `role="button"` and `aria-label="${name}, ${state}"`, and add a
non-colour cue to the label: for example a check mark prefix for mastered nodes and a lock
mark for locked nodes. About 1 in 12 people have colour vision differences, and judges may test
accessibility.

### Problem 4: progress is lost on refresh
Save trained skills per persona in the browser. Add to `state.js`:

```js
const key = (persona) => `rpg:owned:${persona}`;
export function saveOwned() {
  try { localStorage.setItem(key(state.persona), JSON.stringify([...state.owned])); } catch {}
}
export function loadOwned(persona) {
  try {
    const v = JSON.parse(localStorage.getItem(key(persona)));
    return Array.isArray(v) ? new Set(v) : null;
  } catch { return null; }
}
```
Call `saveOwned()` after `train()`. Ask Member 5 to call `loadOwned()` in the intake panel when
a persona is selected. Keep the try/catch: storage can be blocked and the app must still work.
Add a "Reset progress" button.

## Step 3. Make it feel like a game (Thursday to Friday)
The game layer must stay honest: it decorates real data, it never replaces it.

1. **XP and levels.** Level today is 1 plus skills trained. Make XP mean something: use the
   hours of the recommended verified course for the skill (from `/api/pathway`) and fall back to
   a fixed small value when no verified course exists. Show a progress bar to the next level.
2. **Unlock animation.** When a skill becomes mastered, briefly highlight it and the nodes it
   unlocked:
   ```css
   @media (prefers-reduced-motion: no-preference) {
     #tree .node.just-unlocked rect { animation: pop .6s ease-out; }
   }
   @keyframes pop { from { opacity: .3; } to { opacity: 1; } }
   ```
   Add the class for the nodes whose state changed after a training step, and remove it after
   about a second. Keep the effect subtle.
3. **Level-up and badge messages.** A short line such as "Level 3. New SDG badge: SDG 9" shown
   in the stats area (use a polite live region, `aria-live="polite"`, so screen readers hear it).
4. **Scenario "world events".** When the scenario changes, show one line describing the
   assumption ("Fast: AI adoption accelerates"). The text comes from `docs/DECISIONS.md`.
5. **Tone.** Encouraging, never alarming. These users are worried about their jobs. No
   countdowns, no "you are falling behind".
6. **Story hook.** `tree.js` already shows `scene` and `mentor_line` when
   `story/nodes/<id>.yaml` exists. Leave it working; the writers will fill in files later.

## Step 4. The role "boss" panel (Thursday)
When a role node is selected, the detail panel should show, in this order:

1. Role name and the SDG tags.
2. **Match score** as a bar, with the one-sentence `why` from the API.
3. **Skills gap** as a list: each missing skill, its importance, and its momentum with a
   rising or declining word (not colour alone).
4. **Outlook across scenarios** once Member 3 adds `outlook_range`: "Outlook between +4% and
   +17% depending on how fast AI moves". This is the multi-scenario output the brief asks for.
5. A "Show pathway" button (already emits `role-selected`).

Also show the data status near the numbers: the "Mock data" badge (Member 5's radar sets it) and
the `as_of` date from the tree response. Every number needs a source and a date nearby.

## Step 5. Show that the data changes (Friday)
This is the most persuasive thing in the demo. The brief says success is "the output visibly
changes when the trend data changes".

1. Work with Member 1 on a refresh action (it will be protected by a token).
2. After a refresh, call `/api/tree` again and compare the new node values with the old ones.
3. Highlight what moved ("Prompting momentum: +31% to +38%") and show it briefly.
4. Member 5 builds the patch-notes banner from `/api/changes`; you handle the tree
   highlight. Agree on one shared function so both use the same comparison.

Do not fake a change. If two real snapshots show no difference, say so.

## Step 6. Polish checklist (Friday to Saturday)
- [ ] Works in Chrome and one other browser
- [ ] Phone size: tree scrolls, buttons are at least 40 px tall, nothing overflows
- [ ] Dark mode looks right (the CSS variables switch automatically; check contrast)
- [ ] Keyboard only: you can reach and activate every node and button
- [ ] No console errors on load, on persona switch, on scenario switch, on training
- [ ] Loading and error states: if the API fails, show a clear message, not a blank page
- [ ] Every number shown has a source or date nearby
- [ ] Demo path rehearsed: choose persona, train 2 skills, open a role, scenario switch,
      refresh data (2 to 3 minutes)

## Testing without a framework
There are no automated frontend tests. Test by hand using the checklist above, and write down
one or two regressions you hit. Useful: in DevTools, Network tab, reload and check that every
`/api/...` call returns 200.

## Handoffs
| From or to | What | When |
|---|---|---|
| Member 3 to you | `family` filter, `outlook_range`, final skill ids | Wed to Thu |
| You to Member 5 | `saveOwned`/`loadOwned`, the shared change-highlight function | Thu |
| Member 1 to you | How the refresh button should authenticate | Thu |
| You to Member 1 | Any API response change you need (write it in `DECISIONS.md` first) | any time |

## Commit rhythm
Branches such as `ui-tree/keyboard-support`, `ui-tree/boss-panel`. Small commits, for example
`ui-tree: scroll tree on narrow screens`. Member 5 reviews (your backup). At least one commit a day.

## Troubleshooting
| Problem | Fix |
|---|---|
| Blank page | Open DevTools console. Usually a typo in a module or a failed import path |
| `Failed to fetch` | The backend is not running, or you opened `index.html` directly. Use http://localhost:8000 |
| Old behaviour after an edit | Hard refresh (Ctrl+Shift+R); modules can be cached |
| Tree does not update | Check that `refreshTree()` ran and that `state.owned` is a `Set`, not an array |
| Nodes overlap | Too many nodes in a tier. See Problem 1 |
| Text is invisible in dark mode | You hard-coded a colour. Use the CSS variables in `style.css` |

## What to say to the judges
- "The tree is not hard-coded: the backend computes node states and momentum from the data and
  the skills the user already has, and the page just draws it."
- "Panels talk through a small event bus, so each one can change without breaking the others."
- "Locked does not mean forbidden. It shows what comes first, and the user can still explore."
- "Every number has a source and date, and mock data is labelled."
- "The game layer is only a view over the real data: XP comes from real course hours."

## Done when
- [ ] Nodes never overlap, and the tree is readable on a phone
- [ ] Keyboard and non-colour cues work
- [ ] Progress survives a refresh (with a reset button)
- [ ] Role panel shows match, gap and scenario range
- [ ] Data refresh visibly updates the tree
- [ ] Demo path rehearsed with no console errors
