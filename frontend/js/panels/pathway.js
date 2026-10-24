// Reskilling pathway toward a selected role. Owner: Member 5.
import { api } from "../api.js";
import { state } from "../state.js";
import { esc } from "../util.js";
import { t } from "../i18n.js";

const el = document.getElementById("pathway");
let lastPathway = null;   // kept so we can recompute totals client-side when steps are unticked

function courseLine(c) {
  if (!c.verified) return `<li class="muted">${esc(c.title)} ${esc(t("path.notVerified"))}</li>`;
  const safe = c.url && c.url.startsWith("https://");
  const titleHtml = safe
    ? `<a href="${esc(c.url)}" target="_blank" rel="noopener">${esc(c.title)}</a>`
    : esc(c.title);
  const funding = c.funding_note ? ` <span class="muted">(${esc(c.funding_note)})</span>` : "";
  return `<li>${titleHtml}, ${esc(c.provider)}, ${c.hours} h, RM${c.cost_myr}${funding}</li>`;
}

export function clearPathway() {
  lastPathway = null;
  el.innerHTML = `<h2>${esc(t("path.title"))}</h2><p class="muted">${esc(t("path.empty"))}</p>`;
}

function recomputeTotals() {
  // Sum verified-course hours/cost only for steps whose checkbox is still ticked.
  let hours = 0, cost = 0, missing = 0;
  el.querySelectorAll(".step").forEach((stepEl) => {
    const checked = stepEl.querySelector("input[type=checkbox]").checked;
    if (!checked) return;
    const verifiedCourses = JSON.parse(stepEl.dataset.courses);
    const verified = verifiedCourses.filter((c) => c.verified);
    if (verified.length === 0) missing++;
    verified.forEach((c) => { hours += c.hours; cost += c.cost_myr; });
  });
  el.querySelector("#totals").textContent = t("path.total", { hours, cost, gaps: missing });
}

export async function renderPathway(roleId) {
  const p = await api.pathway(roleId, state.persona, state.owned);
  lastPathway = p;

  const weeksLine = p.estimated_weeks != null
    ? `<p class="muted">Estimated time: about ${p.estimated_weeks} week(s) at your study pace (estimate, not a guarantee).</p>`
    : "";

  const steps = p.steps.map((s, i) => `
    <li class="step" data-courses="${esc(JSON.stringify(s.courses))}">
      <label><input type="checkbox" checked class="step-toggle" />
        <b>${esc(s.name)}</b> <span class="muted">(untick if you already know this)</span></label>
      <ul>${s.courses.length ? s.courses.map(courseLine).join("") : `<li class='muted'>${esc(t("path.noCourse"))}</li>`}</ul>
    </li>`);

  el.innerHTML = `<h2>${esc(t("path.title"))}</h2>
    ${weeksLine}
    <ol>${steps.join("") || `<li>${esc(t("path.allDone"))}</li>`}</ol>
    <p id="totals" class="muted"></p>
    <button id="print-plan">Print or save my plan</button>`;

  el.querySelectorAll(".step-toggle").forEach((box) => box.addEventListener("change", recomputeTotals));
  el.querySelector("#print-plan").addEventListener("click", () => window.print());

  recomputeTotals();
}

