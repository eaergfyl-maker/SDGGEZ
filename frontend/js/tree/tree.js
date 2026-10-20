// Skill tree rendering and game logic. Owner: Member 4.
import { api } from "../api.js";
import { emit, state } from "../state.js";

const W = 680, NODE_W = 124, NODE_H = 36, ROW_H = 90, PAD = 30;
const svg = document.getElementById("tree");

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function layout(nodes) {
  const maxTier = Math.max(...nodes.map((n) => n.tier));
  const byTier = {};
  nodes.forEach((n) => (byTier[n.tier] ||= []).push(n));
  const pos = {};
  for (const [tier, list] of Object.entries(byTier)) {
    const gap = W / list.length;
    list.forEach((n, i) => {
      pos[n.id] = { x: gap * i + gap / 2, y: PAD + (maxTier - tier) * ROW_H + NODE_H / 2 };
    });
  }
  return { pos, height: PAD * 2 + maxTier * ROW_H + NODE_H };
}

export function renderTree(tree) {
  const { pos, height } = layout(tree.nodes);
  svg.setAttribute("viewBox", `0 0 ${W} ${height}`);
  const owned = state.owned;
  const edges = tree.edges.map((e) => {
    const a = pos[e.from], b = pos[e.to];
    const lit = owned.has(e.from) ? "lit" : "";
    return `<line class="${lit}" x1="${a.x}" y1="${a.y - NODE_H / 2}" x2="${b.x}" y2="${b.y + NODE_H / 2}"/>`;
  });
  const nodes = tree.nodes.map((n) => {
    const p = pos[n.id];
    const cls = ["node", n.state, n.kind === "role" ? "role" : "", state.selected === n.id ? "selected" : ""].join(" ");
    return `<g class="${cls}" data-id="${n.id}" tabindex="0">
      <rect x="${p.x - NODE_W / 2}" y="${p.y - NODE_H / 2}" width="${NODE_W}" height="${NODE_H}" rx="8"/>
      <text x="${p.x}" y="${p.y}" text-anchor="middle" dominant-baseline="central">${esc(n.name)}</text></g>`;
  });
  svg.innerHTML = edges.join("") + nodes.join("");

  const trained = [...owned].filter((id) => !state.startingSkills.has(id)).length;
  const sdgs = new Set(tree.nodes.filter((n) => n.state === "mastered").flatMap((n) => n.sdg));
  document.getElementById("trained").textContent = trained;
  document.getElementById("level").textContent = 1 + trained;
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

svg.addEventListener("click", (e) => {
  const g = e.target.closest(".node");
  if (!g) return;
  state.selected = g.dataset.id;
  renderTree(state.tree);
  showDetail(state.tree.nodes.find((n) => n.id === state.selected));
});

document.getElementById("scenario").addEventListener("click", (e) => {
  const s = e.target.dataset.s;
  if (!s) return;
  state.scenario = s;
  document.querySelectorAll("#scenario button").forEach((b) => b.classList.toggle("on", b.dataset.s === s));
  refreshTree();
  emit("scenario-changed", s);
});
