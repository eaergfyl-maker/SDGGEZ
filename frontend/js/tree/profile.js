// Character sheet: shows the saved profile (name, class, level, skills, SDG badges). Owner: Member 4.
// Everything is stored in this browser only (localStorage): no account, no server, no personal data.
import { state, on, saveName, loadName, clearAllSaved } from "../state.js";
import { classFor } from "./classes.js";
import { progress, XP_PER_LEVEL, classImage, refreshTree } from "./tree.js";
import { esc } from "../util.js";

const nameInput = document.getElementById("profile-name");
const body = document.getElementById("profile-body");
let lastRole = null; // role the user last opened the pathway for

function nameOf(id) {
  const n = state.tree && state.tree.nodes.find((x) => x.id === id);
  return n ? n.name : id;
}

function chips(ids, mark = "") {
  if (!ids.length) return `<p class="muted">None yet. Complete a skill in the tree to add it here.</p>`;
  return `<ul class="chips">${ids.map((id) => `<li>${mark}${esc(nameOf(id))}</li>`).join("")}</ul>`;
}

function render() {
  if (!body) return;
  if (!state.tree || !state.owned) {
    body.innerHTML = `<p class="muted">Choose a persona to meet your character.</p>`;
    return;
  }
  const c = classFor(state.startingSkills);
  const { xp, level, into } = progress(state.owned);
  const label = (nameInput && nameInput.value.trim()) || "Adventurer";
  const starting = [...state.startingSkills];
  const trained = [...state.owned].filter((id) => !state.startingSkills.has(id));
  const sdgs = [...new Set(state.tree.nodes.filter((n) => n.state === "mastered").flatMap((n) => n.sdg || []))].sort((a, b) => a - b);
  const role = lastRole && state.tree.nodes.find((n) => n.id === lastRole && n.kind === "role");

  body.innerHTML = `
    <div class="class-card">
      <img class="class-img" src="${esc(classImage(c && c.key))}" alt="" width="96" height="96">
      <div>
        <p><b class="char-name">${esc(label)}</b>${c ? ` the ${esc(c.name)}` : ""}</p>
        ${c ? `<p class="muted">${esc(c.title)}</p>` : ""}
        <p>Level <b>${level}</b> · ${xp} XP earned</p>
      </div>
    </div>
    <progress value="${into}" max="${XP_PER_LEVEL}" aria-label="XP to next level: ${into} of ${XP_PER_LEVEL}"></progress>
    <h3>Starting skills (${starting.length})</h3>${chips(starting)}
    <h3>Trained skills (${trained.length})</h3>${chips(trained, "✓ ")}
    <h3>SDG badges (${sdgs.length})</h3>
    ${sdgs.length ? sdgs.map((g) => `<span class="tag">SDG ${g}</span>`).join("") : `<p class="muted">None yet.</p>`}
    ${role ? `<h3>Current quest</h3><p>${esc(role.full_name || role.name)}${role.match ? ` · match ${esc(role.match.score)}%` : ""}</p>` : ""}
    <p class="muted">Viewing the ${esc(state.scenario)} AI scenario. Outlooks are estimates, not predictions.</p>`;
}

function exportProfile() {
  if (!state.owned || !state.tree) return;
  const c = classFor(state.startingSkills);
  const { xp, level } = progress(state.owned);
  const data = {
    app: "Future-Ready RPG",
    exportedAt: new Date().toISOString(),
    note: "Skills and progress only. Stored in your own browser, never sent to a server.",
    name: (nameInput && nameInput.value.trim()) || null,
    persona: state.persona,
    scenario: state.scenario,
    class: c ? { name: c.name, title: c.title } : null,
    level,
    xp,
    startingSkills: [...state.startingSkills],
    trainedSkills: [...state.owned].filter((id) => !state.startingSkills.has(id)),
  };
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = `rpg-profile-${state.persona}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

async function deleteSaved() {
  if (!window.confirm("Delete your saved name and progress from this browser?")) return;
  clearAllSaved();
  if (nameInput) nameInput.value = "";
  lastRole = null;
  if (state.startingSkills) state.owned = new Set(state.startingSkills);
  await refreshTree();
  render();
}

if (nameInput) {
  nameInput.value = loadName();
  nameInput.addEventListener("input", () => { saveName(nameInput.value.trim()); render(); });
}
document.getElementById("profile-export")?.addEventListener("click", exportProfile);
document.getElementById("profile-delete")?.addEventListener("click", deleteSaved);

on("tree-updated", render);
on("role-selected", (id) => { lastRole = id; render(); });
on("persona-changed", () => { lastRole = null; });
render();