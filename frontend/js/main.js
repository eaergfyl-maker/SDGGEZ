// Wires the panels together. Owner: Member 4.
import { applyStatic, setLang } from "./i18n.js";
import { on, state, loadOwned } from "./state.js";
import { refreshTree } from "./tree/tree.js";
import "./tree/refresh.js";
import "./tree/profile.js";
import "./tree/area.js";
import "./tree/roles.js"; // Ranked roles component for Member 4
import { renderIntake } from "./panels/intake.js";
import { renderRadar } from "./panels/radar.js";
// import { renderChat } from "./panels/chat.js";
import { clearPathway, renderPathway } from "./panels/pathway.js";

on("persona-changed", () => {
  // Clear selection and restore saved progress specifically for this persona/profile
  state.selected = null;
  const saved = loadOwned(state.persona);
  if (saved) {
    state.owned = new Set([...state.startingSkills, ...saved]);
  } else {
    state.owned = new Set(state.startingSkills);
  }
  clearPathway();
  refreshTree();
});

on("scenario-changed", () => renderRadar());
on("role-selected", (roleId) => renderPathway(roleId));

// language first, so every panel renders in it
applyStatic();
document.getElementById("lang")?.addEventListener("click", (e) => {
  const b = e.target.closest("button[data-lang]");
  if (b) setLang(b.dataset.lang);
});

clearPathway();
renderRadar();
renderIntake();
// renderChat();