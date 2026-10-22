// Wires the panels together. Owner: Member 4.
import { on, state, loadOwned } from "./state.js";
import { refreshTree } from "./tree/tree.js";
import { renderIntake } from "./panels/intake.js";
import { renderRadar } from "./panels/radar.js";
import { clearPathway, renderPathway } from "./panels/pathway.js";

on("persona-changed", () => {
  const saved = loadOwned(state.persona);
  if (saved) state.owned = new Set([...state.startingSkills, ...saved]);
  clearPathway();
  refreshTree();
});
on("scenario-changed", () => renderRadar());
on("role-selected", (roleId) => renderPathway(roleId));

clearPathway();
renderRadar();
renderIntake();
