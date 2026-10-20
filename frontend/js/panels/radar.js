// Future Skills Radar: rising and declining skills. Owner: Member 5.
// TODO: replace the lists with a chart, and show each skill's sources and dates.
import { api } from "../api.js";
import { state } from "../state.js";

const el = document.getElementById("radar");

export async function renderRadar() {
  const t = await api.trends(state.scenario);
  document.getElementById("mock-badge").hidden = !t.is_mock;
  document.getElementById("as-of").textContent = `Data as of ${t.as_of.slice(0, 10)} (${t.source})`;

  const known = t.skills.filter((s) => s.momentum != null).sort((a, b) => b.momentum - a.momentum);
  const item = (s) => `<li>${s.name}: ${s.momentum > 0 ? "+" : ""}${s.momentum}%</li>`;
  el.innerHTML = `<h2>Future Skills Radar</h2>
    <p class="muted">Scenario: ${t.scenario}. Estimates, not predictions.</p>
    <div class="row" style="align-items:flex-start">
      <div style="flex:1"><b>Rising</b><ol>${known.filter((s) => s.direction === "rising").map(item).join("")}</ol></div>
      <div style="flex:1"><b>Declining</b><ol>${known.filter((s) => s.direction === "declining").map(item).join("")}</ol></div>
    </div>`;
}
