// Ranked roles list. Owner: Member 4.
import { state, on, emit } from "../state.js";
import { esc } from "../util.js";

const container = document.getElementById("ranked-roles");

function fmtPercent(v) {
  if (v == null) return "no data";
  return `${v > 0 ? "+" : ""}${v}%`;
}

function outlookText(outlook) {
  if (!outlook) return "Scenario range not available";
  const lo = outlook.min ?? outlook.low;
  const hi = outlook.max ?? outlook.high;
  if (lo == null || hi == null) return "Scenario range not available";
  return `${fmtPercent(lo)} to ${fmtPercent(hi)}`;
}

export function renderRankedRoles() {
  if (!container) return;

  if (!state.tree || !state.tree.nodes) {
    container.innerHTML = `<h2>Your best roles</h2><p class="muted">No roles available.</p>`;
    return;
  }

  const roleNodes = state.tree.nodes.filter((n) => n.kind === "role");

  if (!roleNodes.length) {
    container.innerHTML = `<h2>Your best roles</h2><p class="muted">No roles found for this career area.</p>`;
    return;
  }

  // Rank / sort by match score descending
  const sortedRoles = [...roleNodes].sort((a, b) => {
    const scoreA = (a.match && Number(a.match.score)) || 0;
    const scoreB = (b.match && Number(b.match.score)) || 0;
    return scoreB - scoreA;
  });

  const cardsHtml = sortedRoles.map((role) => {
    const score = role.match ? Math.max(0, Math.min(100, Number(role.match.score) || 0)) : 0;
    const onet = role.onet_occupation || role.onet_title || role.name;
    const range = outlookText(role.outlook_range);

    return `
      <div class="card role-item" style="border: 1px solid var(--border); margin: 8px 0;">
        <div class="row" style="justify-content: space-between; align-items: baseline;">
          <h3 style="margin: 0;">${esc(role.full_name || role.name)}</h3>
          <span class="badge" style="background: var(--role); color: var(--node-text);">Match ${score}%</span>
        </div>
        <p class="muted" style="margin: 4px 0;">Based on O*NET: <b>${esc(onet)}</b></p>
        <div class="match">
          <progress value="${score}" max="100" aria-label="Match score ${score} percent"></progress>
        </div>
        <p style="margin: 6px 0 10px;">Outlook range: <b>${esc(range)}</b> (${esc(state.scenario)} scenario)</p>
        <button type="button" class="role-pathway-btn" data-role-id="${esc(role.id)}">Show pathway</button>
      </div>
    `;
  }).join("");

  container.innerHTML = `
    <h2>Your best roles</h2>
    <p class="muted">Ranked suitable future roles based on your skill match.</p>
    <div class="ranked-roles-list">${cardsHtml}</div>
  `;

  // Attach event handlers for pathway buttons
  container.querySelectorAll(".role-pathway-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const roleId = e.currentTarget.dataset.roleId;
      if (roleId) {
        emit("role-selected", roleId);
        // Scroll smoothly to pathway section
        document.getElementById("pathway")?.scrollIntoView({ behavior: "smooth" });
      }
    });
  });
}

on("tree-updated", renderRankedRoles);
on("scenario-changed", renderRankedRoles);
on("persona-changed", renderRankedRoles);