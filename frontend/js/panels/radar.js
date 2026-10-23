// Future Skills Radar: rising and declining skills. Owner: Member 5.
import { api } from "../api.js";
import { state } from "../state.js";
import { esc } from "../util.js";

const el = document.getElementById("radar");

function bars(items) {
  const row = (s, i) => {
    const w = Math.min(Math.abs(s.momentum), 100) * 2.4;      // 100% = 240px
    const x = s.momentum >= 0 ? 260 : 260 - w;
    const cls = s.momentum >= 0 ? "rising" : "declining";
    const arrow = s.momentum >= 0 ? "▲" : "▼";
    return `<g transform="translate(0 ${i * 28})">
      <text x="0" y="14" class="lbl">${esc(s.name)}</text>
      <rect class="${cls}" x="${x}" y="2" width="${w}" height="16" rx="3"/>
      <text x="${s.momentum >= 0 ? x + w + 6 : x - 6}" y="14"
            text-anchor="${s.momentum >= 0 ? "start" : "end"}" class="lbl">
        ${arrow} ${s.momentum > 0 ? "+" : ""}${s.momentum}%</text></g>`;
  };
  return `<svg viewBox="0 0 680 ${Math.max(items.length, 1) * 28}" width="100%">${items.map(row).join("")}</svg>`;
}

function sourceDetail(s) {
  const src = s.components?.sources;
  if (!src) return `<span class="muted">Mock data, no source yet</span>`;
  const d = src.demand;
  return `${esc(d.name)}: ${d.recent_postings} postings, from ${esc(d.recent_from)}. ${esc(d.caveat)}`;
}

export async function renderRadar() {
  const t = await api.trends(state.scenario);
  document.getElementById("mock-badge").hidden = !t.is_mock;
  document.getElementById("as-of").textContent = `Data as of ${t.as_of.slice(0, 10)} (${t.source})`;

  const known = t.skills.filter((s) => s.momentum != null).sort((a, b) => b.momentum - a.momentum);
  const noData = t.skills.filter((s) => s.momentum == null);
  const rising = known.filter((s) => s.momentum >= 0);
  const declining = known.filter((s) => s.momentum < 0);

  const detailsList = (items) => items.map((s) => `
    <details>
      <summary>${esc(s.name)}: ${s.momentum > 0 ? "+" : ""}${s.momentum}%</summary>
      ${sourceDetail(s)}
    </details>`).join("");

  el.innerHTML = `<h2>Future Skills Radar</h2>
    <p class="muted">Scenario: ${esc(t.scenario)}. These are estimates, not predictions.
      Job-posting data mostly covers German and European postings, so figures may not reflect
      the Malaysian job market directly.</p>

    <b>Rising</b>
    ${bars(rising)}
    ${detailsList(rising)}

    <b>Declining</b>
    ${bars(declining)}
    ${detailsList(declining)}

    ${noData.length ? `
      <b>No data yet</b>
      <ul>${noData.map((s) => `<li class="muted">${esc(s.name)}</li>`).join("")}</ul>
    ` : ""}`;
}