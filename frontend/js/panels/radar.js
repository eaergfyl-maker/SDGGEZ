// Future Skills Radar: rising and declining skills. Owner: Member 5.
import { api } from "../api.js";
import { state } from "../state.js";
import { esc } from "../util.js";
import { t as tr } from "../i18n.js";

const el = document.getElementById("radar");

// One row per skill: name, a bar whose length is the size of the change (capped at 100%), and the
// value. Rising and declining bars both grow to the right and differ by colour and arrow.
// Plain HTML (not SVG) so the text stays readable on a phone.
function bars(items) {
  const row = (s) => {
    const up = s.momentum >= 0;
    const w = Math.max(Math.min(Math.abs(s.momentum), 100), 1);
    return `<li class="radar-row">
      <span class="radar-name">${esc(s.name)}</span>
      <span class="radar-track"><span class="radar-bar ${up ? "rising" : "declining"}" style="width:${w}%"></span></span>
      <span class="radar-val ${up ? "rising" : "declining"}"><span aria-hidden="true">${up ? "▲" : "▼"}</span>
        ${s.momentum > 0 ? "+" : ""}${s.momentum}%</span></li>`;
  };
  return `<ul class="radar-bars">${items.map(row).join("")}</ul>`;
}

function sourceDetail(s) {
  const src = s.components?.sources;
  if (!src) return `<span class="muted">${esc(tr("radar.mockSource"))}</span>`;
  const c = s.components;
  const pct = (v) => `${v > 0 ? "+" : ""}${v}%`;
  const lines = [];
  const d = src.demand;
  if (d && c.demand_growth != null) {
    lines.push(tr("radar.demand", { name: d.name, pct: pct(c.demand_growth), recent: d.mentions_recent,
      total: d.recent_postings, from: d.recent_from, previous: d.mentions_previous }) + " " + d.caveat);
  }
  const r = src.research;
  if (r && c.research_growth != null) {
    lines.push(tr("radar.research", { pct: pct(c.research_growth), recent: r.papers_recent,
      before: r.papers_year_ago, month: r.latest_month }));
  }
  if (s.low_data?.length) lines.push(tr("radar.lowData"));
  return lines.map((l) => `<p class="muted">${esc(l)}</p>`).join("");
}

// What changed between the last two real snapshots. Only "reliable" changes are listed (both
// values exist and neither rests on too few postings or papers); the rest are counted.
function changesSection(ch, names) {
  if (!ch || !ch.from || !ch.changes?.length) return "";
  const pct = (v) => `${v > 0 ? "+" : ""}${v}%`;
  const shown = ch.changes
    .filter((c) => c.reliable !== false && c.old != null && c.new != null)
    .sort((a, b) => Math.abs(b.new - b.old) - Math.abs(a.new - a.old));
  const rest = ch.changes.length - shown.length;
  const items = shown.map((c) => `<li>${esc(tr("radar.changeLine", {
    name: names[c.skill] || c.skill, signal: tr(`radar.signal.${c.signal}`), from: pct(c.old), to: pct(c.new) }))}</li>`).join("");
  return `<details class="radar-changes">
    <summary>${esc(tr("radar.changesTitle", { from: ch.from.slice(0, 10), to: ch.to.slice(0, 10), n: shown.length }))}</summary>
    <p class="muted">${esc(tr("radar.changesCaveat"))}</p>
    ${items ? `<ul>${items}</ul>` : ""}
    ${rest ? `<p class="muted">${esc(tr("radar.changesRest", { n: rest }))}</p>` : ""}
  </details>`;
}

export async function renderRadar() {
  const [t, ch] = await Promise.all([api.trends(state.scenario), api.changes().catch(() => null)]);
  const names = Object.fromEntries(t.skills.map((s) => [s.skill, s.name]));
  document.getElementById("mock-badge").hidden = !t.is_mock;
  document.getElementById("as-of").textContent = tr("asof", { date: t.as_of.slice(0, 10), source: t.source });

  const known = t.skills.filter((s) => s.momentum != null).sort((a, b) => b.momentum - a.momentum);
  const noData = t.skills.filter((s) => s.momentum == null);
  const rising = known.filter((s) => s.momentum >= 0);
  const declining = known.filter((s) => s.momentum < 0);

  const detailsList = (items) => items.map((s) => `
    <details>
      <summary>${esc(s.name)}: ${s.momentum > 0 ? "+" : ""}${s.momentum}%</summary>
      ${sourceDetail(s)}
    </details>`).join("");

  el.innerHTML = `<h2>${esc(tr("radar.title"))}</h2>
    <p class="muted">${esc(tr("radar.note", { scenario: tr(`scenario.${t.scenario}`) }))}</p>

    <b>${esc(tr("radar.rising"))}</b>
    ${bars(rising)}
    ${detailsList(rising)}

    <b>${esc(tr("radar.declining"))}</b>
    ${bars(declining)}
    ${detailsList(declining)}

    ${noData.length ? `
      <b>${esc(tr("radar.noData"))}</b>
      <ul>${noData.map((s) => `<li class="muted">${esc(s.name)}</li>`).join("")}</ul>
    ` : ""}
    ${changesSection(ch, names)}`;
}