// Patch-notes banner: shows what changed since the last data snapshot. Owner: Member 5.
import { api } from "../api.js";
import { state, on } from "../state.js";
import { esc } from "../util.js";

const el = document.getElementById("patch");

export async function renderPatchNotes() {
  if (!el) return;
  const { changes } = await api.changes();
  if (!changes || !changes.length) { el.hidden = true; return; }

  const top = changes.slice(0, 3).map((c) => {
    const node = state.tree?.nodes?.find((n) => n.id === c.skill);
    const name = node ? node.name : c.skill;
    const label = c.signal === "demand" ? "job demand" : "research";
    return `${esc(name)} ${label}: ${c.old ?? "no data"}% to ${c.new ?? "no data"}%`;
  });

  el.hidden = false;
  el.innerHTML = `<b>Since the last update:</b> ${top.join("; ")}`;
}