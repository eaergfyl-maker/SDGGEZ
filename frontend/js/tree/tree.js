// Skill tree rendering and game logic. Owner: Member 4.
import { api } from "../api.js";
import { emit, state, saveOwned, clearOwned } from "../state.js";

const BASE_W = 680, NODE_W = 124, MIN_NODE_W = 70, NODE_GAP = 8;
const NODE_H = 36, ROW_H = 90, PAD = 30;
const svg = document.getElementById("tree");

// XP is a view over course data. Use a clear fallback until course hours are wired in.
const XP_FALLBACK = 10;
const XP_PER_LEVEL = 20;

function xpFor(id) {
  const value = state.skillXp?.[id];
  return Number.isFinite(value) && value > 0 ? value : XP_FALLBACK;
}

function progress(owned) {
  const trainedIds = [...owned].filter((id) => !state.startingSkills.has(id));
  const xp = trainedIds.reduce((sum, id) => sum + xpFor(id), 0);
  return {
    trained: trainedIds.length,
    level: 1 + Math.floor(xp / XP_PER_LEVEL),
    into: xp % XP_PER_LEVEL,
  };
}

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

const MARKS = { mastered: "✓ ", available: "▸ ", locked: "🔒 " };

function fit(label, nodeW) {
  const max = Math.max(4, Math.floor(nodeW / 7.5));
  return label.length > max ? label.slice(0, max - 1) + "…" : label;
}

function layout(nodes) {
  const maxTier = Math.max(...nodes.map((n) => n.tier));
  const byTier = {};
  nodes.forEach((n) => (byTier[n.tier] ||= []).push(n));

  // Widen the canvas if a tier is too crowded even at the minimum node width
  const widest = Math.max(...Object.values(byTier).map((l) => l.length));
  const W = Math.max(BASE_W, widest * (MIN_NODE_W + NODE_GAP));

  const pos = {};
  for (const [tier, list] of Object.entries(byTier)) {
    const gap = W / list.length;
    // Shrink node width instead of overlapping
    const nodeW = Math.max(MIN_NODE_W, Math.min(NODE_W, gap - NODE_GAP));
    list.forEach((n, i) => {
      pos[n.id] = { x: gap * i + gap / 2, y: PAD + (maxTier - tier) * ROW_H + NODE_H / 2, w: nodeW };
    });
  }
  return { pos, W, height: PAD * 2 + maxTier * ROW_H + NODE_H };
}

export function renderTree(tree) {
  if (!tree || !tree.nodes || !tree.nodes.length) {
    svg.innerHTML = "";
    return;
  }
  const { pos, W, height } = layout(tree.nodes);
  svg.setAttribute("viewBox", `0 0 ${W} ${height}`);
  const owned = state.owned;
  const edges = tree.edges.map((e) => {
    const a = pos[e.from], b = pos[e.to];
    if (!a || !b) return ""; 
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
  if (bar) {
    bar.max = XP_PER_LEVEL;
    bar.value = into;
  }
  const xpText = document.getElementById("xp-text");
  if (xpText) xpText.textContent = `${into} / ${XP_PER_LEVEL} XP to level ${level + 1}`;
  document.getElementById("badges").textContent = sdgs.size;
}

function fmt(v) {
  return v == null ? "no data" : `${v > 0 ? "+" : ""}${v}%`;
}

async function showDetail(node) {
  const el = document.getElementById("detail");
  const tags = node.sdg.map((g) => `<span class="tag">SDG ${g}</span>`).join("");
  let html = `<h2>${esc(node.full_name || node.name)}</h2>${tags}`;

  if (node.kind === "skill") {
    const c = node.components || {};
    html += `<p>Momentum: <b>${fmt(node.momentum)}</b> (${node.direction}).
      Research ${fmt(c.research_growth)}, job demand ${fmt(c.demand_growth)}, outlook ${fmt(c.outlook)}.</p>`;
    if (node.state === "available") html += `<button id="train">Start quest</button>`;
    if (node.state === "locked") html += `<p class="muted">Locked: train the skills below it first.</p>`;
  } else {
    const m = node.match;
    html += `<p>Match score: <b>${m.score}%</b>. ${esc(m.why)}.</p>`;
    if (m.missing.length) html += `<p>Skills gap: ${m.missing.map((g) => esc(g.skill)).join(", ")}</p>`;
    html += `<button id="show-path">Show pathway</button>`;
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
  if (state.selected) {
    const node = state.tree.nodes.find((n) => n.id === state.selected);
    if (node) showDetail(node);
  }
}

// Return focus to a node after the SVG is redrawn (innerHTML wipes focus)
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

// Enter/Space activate the focused node
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
  document.querySelectorAll("#scenario button").forEach((b) => b.classList.toggle("on", b.dataset.s === s));
  refreshTree();
  emit("scenario-changed", s);
});