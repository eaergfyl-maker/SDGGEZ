// Career area picker. Owner: Member 4.
// A career area is a group of related roles and the skills that lead to them; the tree shows one
// area at a time so it stays readable. A starting class opens in its own area. A custom profile
// starts on "Best match": the backend guesses the area from the ticked skills, and asks when the
// skills don't point anywhere. Choosing an area in the dropdown always overrides the guess.
import { api } from "../api.js";
import { on, state } from "../state.js";
import { esc } from "../util.js";
import { refreshTree } from "./tree.js";

const select = document.getElementById("area");
const note = document.getElementById("area-note");
let families = [];

const ready = api.families().then((list) => {
  families = list;
  select.innerHTML = `<option value="auto">Best match for my skills</option>` +
    list.map((f) => `<option value="${esc(f.id)}">${esc(f.name)}</option>`).join("");
}).catch(() => {
  note.textContent = "Couldn't load the career areas.";
});

const areaName = (id) => (families.find((f) => f.id === id) || {}).name || id;

// Runs before main.js refreshes the tree (this module is imported first).
on("persona-changed", (p) => {
  state.family = p.id === "custom" ? "auto" : null;  // null: the class's own area
});

select.addEventListener("change", () => {
  state.family = select.value;
  refreshTree();
});

on("tree-updated", async (tree) => {
  await ready;
  select.value = state.family === "auto" ? "auto" : (tree.family || "auto");
  if (tree.needs_family) {
    note.textContent = "Your skills don't point to one career area yet. " +
      "Pick an area above, or tick a few more specific skills.";
  } else if (tree.family_inferred) {
    const second = tree.family_ambiguous ? tree.family_ranked[1] : null;
    note.textContent = `Matched from your skills: ${areaName(tree.family)}.` +
      (second ? ` ${second.name} is a close second; switch above if it fits you better.` : "");
  } else {
    note.textContent = "";
  }
});
