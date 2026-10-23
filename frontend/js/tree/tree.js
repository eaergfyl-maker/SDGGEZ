// Skill tree rendering and game logic. Owner: Member 4.
import { api } from "../api.js";
import { emit, state, saveOwned, clearOwned } from "../state.js";
import { classFor } from "./classes.js";

const BASE_W = 680, NODE_W = 124, MIN_NODE_W = 70, NODE_GAP = 8;
const NODE_H = 36, ROW_H = 90, PAD = 30;
const svg = document.getElementById("tree");

// [xp] XP is a view over real data. Until course hours from /api/pathway are wired in
// (state.skillXp = { skillId: hours }), every trained skill is worth the fallback.
const XP_FALLBACK = 10;
const XP_PER_LEVEL = 20;

function xpFor(id) {
  const v = state.skillXp && state.skillXp[id];
  return Number.isFinite(v) && v > 0 ? v : XP_FALLBACK;
}

function progress(owned) {
  const trainedIds = [...owned].filter((id) => !state.startingSkills.has(id));
  const xp = trainedIds.reduce((sum, id) => sum + xpFor(id), 0);
  return { trained: trainedIds.length, xp, level: 1 + Math.floor(xp / XP_PER_LEVEL), into: xp % XP_PER_LEVEL };
}

// [class] set to true once real character art exists as assets/classes/<class>.png
// (bard, wizard, rogue, paladin, druid). Until then every class shows the placeholder.
const USE_CLASS_ART = false;
const PLACEHOLDER_IMG = "assets/classes/placeholder.png";

// [class] starting class from the skills the persona began with (fixed while you train)
function renderClassCard() {
  const card = document.getElementById("class-card");
  if (!card) return;
  const c = classFor(state.startingSkills || []);
  card.hidden = !c;
  if (!c) return;
  document.getElementById("class-name").textContent = c.name;
  document.getElementById("class-title").textContent = c.title;
  document.getElementById("class-scores").textContent =
    "Skill points: " + c.scores.map((x) => `${x.name} ${x.points}`).join(", ");
  const img = document.getElementById("class-img");
  if (img && img.dataset.key !== c.key) {
    img.dataset.key = c.key;
    img.onerror = () => { img.onerror = null; img.src = PLACEHOLDER_IMG; }; // missing file: fall back
    img.src = USE_CLASS_ART ? `assets/classes/${c.key}.png` : PLACEHOLDER_IMG;
  }
}

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// [a11y] non-colour cue per state, so state is not shown by colour alone
const MARKS = { mastered: "✓ ", available: "▸ ", locked: "🔒 " };

// [layout] shorten a label so it fits a narrow node; full name stays in aria-label and <title>
function fit(label, nodeW) {
  const max = Math.max(4, Math.floor(nodeW / 7.5));
  return label.length > max ? label.slice(0, max - 1) + "…" : label;
}

function layout(nodes) {
  const maxTier = Math.max(...nodes.map((n) => n.tier));
  const byTier = {};
  nodes.forEach((n) => (byTier[n.tier] ||= []).push(n));

  // [layout] widen the canvas if a tier is too crowded even at the minimum node width
  const widest = Math.max(...Object.values(byTier).map((l) => l.length));
  const W = Math.max(BASE_W, widest * (MIN_NODE_W + NODE_GAP));

  const pos = {};
  for (const [tier, list] of Object.entries(byTier)) {
    const gap = W / list.length;
    // [layout] shrink node width instead of overlapping
    const nodeW = Math.max(MIN_NODE_W, Math.min(NODE_W, gap - NODE_GAP));
    list.forEach((n, i) => {
      pos[n.id] = { x: gap * i + gap / 2, y: PAD + (maxTier - tier) * ROW_H + NODE_H / 2, w: nodeW };
    });
  }
  return { pos, W, height: PAD * 2 + maxTier * ROW_H + NODE_H };
}

export function renderTree(tree) {
  // [safety] empty tree: show a message instead of crashing on Math.max()
  if (!tree || !tree.nodes || !tree.nodes.length) {
    svg.innerHTML = "";
    return;
  }
  const { pos, W, height } = layout(tree.nodes);
  svg.setAttribute("viewBox", `0 0 ${W} ${height}`);
  const owned = state.owned;
  const edges = tree.edges.map((e) => {
    const a = pos[e.from], b = pos[e.to];
    if (!a || !b) return ""; // edge points at a node the API filtered out
    const lit = owned.has(e.from) ? "lit" : "";
    return `<line class="${lit}" x1="${a.x}" y1="${a.y - NODE_H / 2}" x2="${b.x}" y2="${b.y + NODE_H / 2}"/>`;
  });
  const nodes = tree.nodes.map((n) => {
    const p = pos[n.id];
    const cls = ["node", n.state, n.kind === "role" ? "role" : "", state.selected === n.id ? "selected" : ""].join(" ");
    const mark = MARKS[n.state] || "";
    const label = fit(mark + n.name, p.w);
    return `<g class="${cls}" data-id="${n.id}" tabindex="0" role="button" aria-label="${esc(n.name)}, ${esc(n.state)}">
      <title>${esc(n.name)} (${esc(n.state)})</title>
      <rect x="${p.x - p.w / 2}" y="${p.y - NODE_H / 2}" width="${p.w}" height="${NODE_H}" rx="8"/>
      <text x="${p.x}" y="${p.y}" text-anchor="middle" dominant-baseline="central">${esc(label)}</text></g>`;
  });
  svg.innerHTML = edges.join("") + nodes.join("");

  const { trained, level, into } = progress(owned);
  const sdgs = new Set(tree.nodes.filter((n) => n.state === "mastered").flatMap((n) => n.sdg));
  document.getElementById("trained").textContent = trained;
  document.getElementById("level").textContent = level;
  const bar = document.getElementById("xp-bar");
  if (bar) { bar.max = XP_PER_LEVEL; bar.value = into; }
  const xpText = document.getElementById("xp-text");
  if (xpText) xpText.textContent = `${into} / ${XP_PER_LEVEL} XP to level ${level + 1}`;
  document.getElementById("badges").textContent = sdgs.size;
  renderClassCard();
}

// [course] courses come from /api/pathway, which needs a role. Fetch it for each role in the
// tree once per persona and keep the recommended (or first verified) course per skill.
let skillCourses = {};
let coursesFor = null;

async function loadCourses(tree) {
  if (coursesFor === state.persona) return;
  const persona = state.persona;
  const roles = tree.nodes.filter((n) => n.kind === "role");
  const results = await Promise.all(roles.map((r) => api.pathway(r.id, persona, state.owned).catch(() => null)));
  const map = {};
  for (const res of results) {
    for (const step of (res && res.steps) || []) {
      const c = step.recommended || (step.courses || []).find((x) => x && x.verified !== false);
      if (c && !map[step.skill]) map[step.skill] = c;
    }
  }
  if (state.persona !== persona) return; // persona changed while loading
  skillCourses = map;
  coursesFor = persona;
}

// [course] only a verified course with a real http(s) link is ever shown as a link
function courseHtml(course) {
  const ok = course && course.verified !== false && /^https?:\/\//i.test(course.url || "");
  if (!ok) return `<p class="muted">No verified course yet. You can still mark this skill as completed.</p>`;
  const cost = course.cost_myr == null ? "" : course.cost_myr === 0 ? " · Free" : ` · RM${course.cost_myr}`;
  const fund = course.funding_note ? ` · ${esc(course.funding_note)}` : "";
  const checked = course.checked_on ? `<br><span class="muted">Checked on ${esc(course.checked_on)}</span>` : "";
  return `<div class="course"><b>${esc(course.title)}</b><br>
    <span class="muted">${esc(course.provider || "")}${cost}${fund}</span>${checked}<br>
    <a href="${esc(course.url)}" target="_blank" rel="noopener noreferrer">Open course (new tab)</a></div>`;
}

function fmt(v) {
  return v == null ? "no data" : `${v > 0 ? "+" : ""}${v}%`;
}

// [scenario] one line per scenario. Wording is a draft: keep it in sync with docs/DECISIONS.md.
const SCENARIO_NOTES = {
  slow: "Slow: AI adoption is gradual, so most roles change little in the next few years.",
  moderate: "Moderate: AI adoption grows steadily and some tasks shift to AI-assisted work.",
  fast: "Fast: AI adoption accelerates and many tasks change quickly.",
};
function showScenarioNote() {
  const el = document.getElementById("scenario-note");
  if (el) el.textContent = `${SCENARIO_NOTES[state.scenario] || ""} These are estimates, not predictions.`;
}
function markScenarioButtons() {
  document.querySelectorAll("#scenario button").forEach((b) => {
    const on = b.dataset.s === state.scenario;
    b.classList.toggle("on", on);
    b.setAttribute("aria-pressed", String(on));
  });
}

// [boss] role panel: name and SDGs, match bar, gap list, scenario range, data status
const IMPORTANCE = { 3: "core", 2: "important", 1: "helpful" };

// outlook_range = { min, max, by_scenario: { slow, moderate, fast } } (percent change in demand)
function outlookHtml(r) {
  if (!r) return `<p class="muted">Scenario range not available yet.</p>`;
  const by = r.by_scenario || {};
  const lo = r.min ?? r.low, hi = r.max ?? r.high;
  if (lo == null || hi == null) return `<p class="muted">Scenario range not available yet.</p>`;
  let html = `<p>Outlook between <b>${fmt(lo)}</b> and <b>${fmt(hi)}</b> depending on how fast AI moves.
    <span class="muted">Estimate, not a prediction.</span></p>`;
  const items = ["slow", "moderate", "fast"].filter((k) => by[k] != null).map((k) => {
    const sel = k === state.scenario;
    return `<li>${k[0].toUpperCase() + k.slice(1)}: <b>${fmt(by[k])}</b>${sel ? " (selected scenario)" : ""}</li>`;
  });
  if (items.length) html += `<ul class="gap">${items.join("")}</ul>`;
  const vals = items.length ? ["slow", "moderate", "fast"].filter((k) => by[k] != null).map((k) => by[k]) : [lo, hi];
  if (Math.max(...vals) < 0) html += `<p class="muted">Demand for this role is estimated to fall in every scenario.</p>`;
  else if (Math.min(...vals) > 0) html += `<p class="muted">Demand for this role is estimated to grow in every scenario.</p>`;
  return html;
}

function dataStatus(tree) {
  const mock = !document.getElementById("mock-badge")?.hidden;
  const parts = [];
  if (mock) parts.push("Mock data: not real trends");
  if (tree && tree.as_of) parts.push(`Data as of ${esc(tree.as_of)}`);
  return parts.length ? `<p class="muted">${parts.join(" · ")}</p>` : "";
}

function roleHtml(node) {
  const m = node.match || { score: 0, why: "", missing: [] };
  const score = Math.max(0, Math.min(100, Number(m.score) || 0));
  const start = classFor(state.startingSkills || []);
  const target = classFor([...(m.matched || []), ...(m.missing || []).map((g) => g.skill)]);
  let html = "";
  if (start && target) {
    const path = start.key === target.key
      ? `Class path: you stay a ${start.name}`
      : `Class path: ${start.name} → ${target.name} (${target.title})`;
    html += `<p class="muted">${esc(path)}. Based on skills only.</p>`;
  }
  html += `<div class="match">
    <p>Match score: <b>${score}%</b></p>
    <progress value="${score}" max="100" aria-label="Match score ${score} percent"></progress>
    <p>${esc(m.why || "")}</p></div>`;

  const have = (m.matched || []).map((id) => (state.tree.nodes.find((n) => n.id === id) || {}).name || id);
  if (have.length) html += `<p class="muted">Already matched: ${have.map(esc).join(", ")}</p>`;

  const gaps = m.missing || [];
  if (gaps.length) {
    const items = gaps.map((g) => {
      const sn = state.tree.nodes.find((n) => n.id === g.skill) || {};
      const name = sn.name || g.skill;
      const imp = IMPORTANCE[g.importance] ? `${IMPORTANCE[g.importance]} for this role` : "";
      const mv = g.momentum ?? sn.momentum;
      const mom = mv == null ? "no trend data" : `${sn.direction || "trend"} (${fmt(mv)})`;
      return `<li>${esc(name)}${imp ? ` · ${imp}` : ""} · ${esc(mom)}</li>`;
    });
    html += `<p>Skills gap:</p><ul class="gap">${items.join("")}</ul>`;
  } else {
    html += `<p>No skills gap: you already have everything this role asks for.</p>`;
  }

  html += outlookHtml(node.outlook_range);
  html += `<button id="show-path">Show pathway</button>`;
  html += dataStatus(state.tree);
  return html;
}

async function showDetail(node) {
  const el = document.getElementById("detail");
  const tags = node.sdg.map((g) => `<span class="tag">SDG ${g}</span>`).join("");
  let html = `<h2>${esc(node.full_name || node.name)}</h2>${tags}`;

  if (node.kind === "skill") {
    const c = node.components || {};
    html += `<p>Momentum: <b>${fmt(node.momentum)}</b> (${node.direction}).
      Research ${fmt(c.research_growth)}, job demand ${fmt(c.demand_growth)}, outlook ${fmt(c.outlook)}.</p>`;
    if (node.state === "available") {
      html += courseHtml(node.course || skillCourses[node.id]);
      html += `<button id="train">Mark as completed</button>
        <p class="muted">Progress is self-reported: the app does not check completion.</p>`;
    }
    if (node.state === "locked") html += `<p class="muted">Locked: train the skills below it first.</p>`;
  } else {
    html += roleHtml(node);
  }

  const story = await api.story(node.id).catch(() => ({}));
  if (story.scene) html += `<p class="story">${esc(story.scene)}</p>`;
  if (story.mentor_line) html += `<p class="muted">${esc(story.mentor_line)}</p>`;

  el.innerHTML = html;
  el.querySelector("#train")?.addEventListener("click", () => train(node.id));
  el.querySelector("#show-path")?.addEventListener("click", () => emit("role-selected", node.id));
}

async function train(id) {
  state.owned.add(id);
  saveOwned();
  await refreshTree();
}

// [persist] back to the persona's starting skills, and forget the saved progress
async function resetProgress() {
  if (!window.confirm("Reset your progress? Trained skills will be cleared.")) return;
  clearOwned();
  state.owned = new Set(state.startingSkills);
  await refreshTree();
}

export async function refreshTree() {
  state.tree = await api.tree(state.persona, state.scenario, state.owned);
  renderTree(state.tree);
  emit("tree-updated", state.tree);
  await loadCourses(state.tree);
  if (state.selected) {
    const node = state.tree.nodes.find((n) => n.id === state.selected);
    if (node) showDetail(node);
  }
}

// [a11y] return focus to a node after the SVG is redrawn (innerHTML wipes focus)
function focusNode(id) {
  svg.querySelector(`.node[data-id="${CSS.escape(id)}"]`)?.focus();
}

svg.addEventListener("click", (e) => {
  const g = e.target.closest(".node");
  if (!g) return;
  state.selected = g.dataset.id;
  renderTree(state.tree);
  focusNode(state.selected);
  showDetail(state.tree.nodes.find((n) => n.id === state.selected));
});

// [a11y] Enter / Space activate the focused node
svg.addEventListener("keydown", (e) => {
  if (e.key !== "Enter" && e.key !== " ") return;
  const g = e.target.closest(".node");
  if (!g) return;
  e.preventDefault();
  g.dispatchEvent(new MouseEvent("click", { bubbles: true }));
});

document.getElementById("reset")?.addEventListener("click", resetProgress);

document.getElementById("scenario").addEventListener("click", (e) => {
  const s = e.target.dataset.s;
  if (!s) return;
  state.scenario = s;
  markScenarioButtons();
  showScenarioNote();
  refreshTree();
  emit("scenario-changed", s);
});

// show the note for the starting scenario
markScenarioButtons();
showScenarioNote();