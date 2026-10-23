// Persona picker and starting skills. Owner: Member 5.
import { api } from "../api.js";
import { emit, state } from "../state.js";
import { esc } from "../util.js";

const el = document.getElementById("intake");

export async function renderIntake() {
  const personas = await api.personas();
  const trends = await api.trends(state.scenario);

  el.innerHTML = `<h2>Choose a character</h2>
    <div class="row">${personas.map((p) => `<button data-id="${p.id}">${p.name}</button>`).join("")}</div>
    <p id="persona-info" class="muted"></p>

    <h2>Or describe yourself</h2>
    <p class="muted">Use sample information. We do not store it.</p>
    <label for="hours-input">Hours per week you can study:
      <input type="number" id="hours-input" min="1" max="40" value="6" />
    </label>
    <div id="skill-boxes">
      ${trends.skills.map((s) => `
        <label><input type="checkbox" value="${esc(s.skill)}"> ${esc(s.name)}</label>
      `).join("")}
    </div>
    <button id="use-profile">Use this profile</button>`;

  const select = (p) => {
    state.persona = p.id;
    state.startingSkills = new Set(p.skills);
    state.owned = new Set(p.skills);
    el.querySelectorAll(".row button").forEach((b) => b.classList.toggle("on", b.dataset.id === p.id));
    el.querySelector("#persona-info").textContent =
      `${p.current_role}, ${p.hours_per_week} hours a week to study. Synthetic persona.`;
    emit("persona-changed", p);
  };

  el.querySelector(".row").addEventListener("click", (e) => {
    const p = personas.find((x) => x.id === e.target.dataset.id);
    if (p) select(p);
  });

  el.querySelector("#use-profile").addEventListener("click", () => {
    const ids = [...el.querySelectorAll("#skill-boxes input:checked")].map((i) => i.value);
    const hours = Number(el.querySelector("#hours-input").value) || 6;
    select({
      id: "custom",
      name: "Custom profile",
      current_role: "Your profile",
      hours_per_week: hours,
      skills: ids
    });
  });

  select(personas.find((p) => p.id === state.persona) || personas[0]);
}