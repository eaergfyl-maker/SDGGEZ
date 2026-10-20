// Persona picker and starting skills. Owner: Member 5.
// TODO: add a skills checklist so users can build their own (synthetic) profile.
import { api } from "../api.js";
import { emit, state } from "../state.js";

const el = document.getElementById("intake");

export async function renderIntake() {
  const personas = await api.personas();
  el.innerHTML = `<h2>Choose a character</h2>
    <div class="row">${personas.map((p) => `<button data-id="${p.id}">${p.name}</button>`).join("")}</div>
    <p id="persona-info" class="muted"></p>`;

  const select = (p) => {
    state.persona = p.id;
    state.startingSkills = new Set(p.skills);
    state.owned = new Set(p.skills);
    el.querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.id === p.id));
    el.querySelector("#persona-info").textContent =
      `${p.current_role}, ${p.hours_per_week} hours a week to study. Synthetic persona.`;
    emit("persona-changed", p);
  };

  el.addEventListener("click", (e) => {
    const p = personas.find((x) => x.id === e.target.dataset.id);
    if (p) select(p);
  });
  select(personas.find((p) => p.id === state.persona) || personas[0]);
}
