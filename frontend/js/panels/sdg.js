// SDG panel: shows how a chosen pathway contributes to the SDGs. Owner: Member 5.
import { api } from "../api.js";
import { state, on } from "../state.js";
import { esc } from "../util.js";
import { t } from "../i18n.js";

const el = document.getElementById("sdg");

export function clearSdg() {
  if (el) el.innerHTML = `<h2>SDG contribution</h2><p class="muted">Select a role to see its SDG contribution.</p>`;
}

async function renderSdg(roleId) {
  if (!el) return;   // section not in index.html yet

  const p = await api.pathway(roleId, state.persona, state.owned);
  const counts = {};
  for (const step of p.steps) {
    const node = state.tree.nodes.find((n) => n.id === step.skill);
    (node?.sdg || []).forEach((g) => (counts[g] = (counts[g] || 0) + 1));
  }

  const sdgInfo = await api.sdgs();

  const entries = Object.entries(counts)
    .map(([num, count]) => {
      const info = sdgInfo.find((s) => s.sdg === Number(num));
      if (!info || info.reason === "TBD") return null;   // never show the placeholder
      return { ...info, count };
    })
    .filter(Boolean)
    .sort((a, b) => b.count - a.count);

  if (!entries.length) {
    el.innerHTML = `<h2>SDG contribution</h2><p class="muted">No SDG data available for this path yet.</p>`;
    return;
  }

  const cards = entries.map((e) => `
    <div class="sdg-card">
      <b>SDG ${e.sdg}: ${esc(e.name)}</b>
      <p class="muted">Target${e.targets.length > 1 ? "s" : ""}: ${e.targets.map(esc).join(", ")}</p>
      <p>${esc(e.reason)}</p>
      <p class="muted">Touches ${e.count} skill${e.count > 1 ? "s" : ""} on this path.</p>
    </div>`).join("");

  el.innerHTML = `<h2>SDG contribution</h2>
    <p class="muted">How this path contributes to the UN Sustainable Development Goals.</p>
    ${cards}`;
}

export function initSdg() {
  on("role-selected", (roleId) => renderSdg(roleId));
}