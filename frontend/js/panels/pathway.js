// Reskilling pathway toward a selected role. Owner: Member 5.
import { api } from "../api.js";
import { state } from "../state.js";
import { t } from "../i18n.js";

const el = document.getElementById("pathway");

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function courseLine(c) {
  if (!c.verified) return `<li class="muted">${esc(c.title)} ${esc(t("path.notVerified"))}</li>`;
  return `<li><a href="${esc(c.url)}" target="_blank" rel="noopener">${esc(c.title)}</a>,
    ${esc(c.provider)}, ${c.hours} h, RM${c.cost_myr}</li>`;
}

export function clearPathway() {
  el.innerHTML = `<h2>${esc(t("path.title"))}</h2><p class="muted">${esc(t("path.empty"))}</p>`;
}

export async function renderPathway(roleId) {
  const p = await api.pathway(roleId, state.persona, state.owned);
  const steps = p.steps.map((s) => `<li><b>${esc(s.name)}</b>
      <ul>${s.courses.length ? s.courses.map(courseLine).join("") : `<li class='muted'>${esc(t("path.noCourse"))}</li>`}</ul></li>`);
  el.innerHTML = `<h2>${esc(t("path.title"))}</h2>
    <ol>${steps.join("") || `<li>${esc(t("path.allDone"))}</li>`}</ol>
    <p class="muted">${esc(t("path.total", { hours: p.total_hours_verified, cost: p.total_cost_myr_verified,
                                          gaps: p.skills_without_verified_course.length }))}</p>`;
}
