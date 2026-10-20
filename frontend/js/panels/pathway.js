// Reskilling pathway toward a selected role. Owner: Member 5.
import { api } from "../api.js";
import { state } from "../state.js";

const el = document.getElementById("pathway");

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function courseLine(c) {
  if (!c.verified) return `<li class="muted">${esc(c.title)} (not yet verified, not counted)</li>`;
  return `<li><a href="${esc(c.url)}" target="_blank" rel="noopener">${esc(c.title)}</a>,
    ${esc(c.provider)}, ${c.hours} h, RM${c.cost_myr}</li>`;
}

export function clearPathway() {
  el.innerHTML = `<h2>Pathway</h2><p class="muted">Select a role in the tree and choose "Show pathway".</p>`;
}

export async function renderPathway(roleId) {
  const p = await api.pathway(roleId, state.persona, state.owned);
  const steps = p.steps.map((s) => `<li><b>${esc(s.name)}</b>
      <ul>${s.courses.length ? s.courses.map(courseLine).join("") : "<li class='muted'>No course in the catalogue yet</li>"}</ul></li>`);
  el.innerHTML = `<h2>Pathway</h2>
    <ol>${steps.join("") || "<li>You already have every skill for this role.</li>"}</ol>
    <p class="muted">Verified total: ${p.total_hours_verified} h, RM${p.total_cost_myr_verified}.
    Skills without a verified course: ${p.skills_without_verified_course.length}.</p>`;
}
