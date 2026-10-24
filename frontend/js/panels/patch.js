// Patch-notes banner: shows what changed since the last data snapshot. Owner: Member 5.
// Lists the three biggest reliable changes (both values present, neither based on too few
// postings or papers), with skill names and dates; the radar's "What changed" has the rest.
import { api } from "../api.js";
import { esc } from "../util.js";
import { t } from "../i18n.js";

const el = document.getElementById("patch");
const pct = (v) => `${v > 0 ? "+" : ""}${v}%`;

export async function renderPatchNotes() {
  if (!el) return;
  let ch, trends;
  try {
    [ch, trends] = await Promise.all([api.changes(), api.trends("moderate")]);
  } catch {
    el.hidden = true;
    return;
  }
  const names = Object.fromEntries(trends.skills.map((s) => [s.skill, s.name]));
  const shown = (ch.changes || [])
    .filter((c) => c.reliable !== false && c.old != null && c.new != null)
    .sort((a, b) => Math.abs(b.new - b.old) - Math.abs(a.new - a.old))
    .slice(0, 3);
  if (!shown.length || !ch.from) { el.hidden = true; return; }

  const items = shown.map((c) => `<li>${esc(t("patch.line", {
    name: names[c.skill] || c.skill, signal: t(`radar.signal.${c.signal}`), from: pct(c.old), to: pct(c.new) }))}</li>`).join("");
  el.hidden = false;
  el.innerHTML = `<p><b>${esc(t("patch.title", { from: ch.from.slice(0, 10), to: ch.to.slice(0, 10) }))}</b></p>
    <ul>${items}</ul>
    <p class="muted">${esc(t("patch.note"))}</p>`;
}
