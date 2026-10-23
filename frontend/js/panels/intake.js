// Persona picker and starting skills. Owner: Member 5.
import { api } from "../api.js";
import { emit, state } from "../state.js";
import { esc } from "../util.js";
import { classFor } from "../tree/classes.js";
import { classImage, PLACEHOLDER_IMG } from "../tree/tree.js";

const el = document.getElementById("intake");

export async function renderIntake() {
  const personas = await api.personas();
  const trends = await api.trends(state.scenario);

  // Each sample persona is offered as a starting class (Bard, Wizard, ...): the class comes from
  // its skills, and its job is shown as the background. The persona data itself is unchanged.
  const kit = (p) => {
    const c = classFor(p.skills);
    // Image follows USE_CLASS_ART in tree.js: the placeholder for now, real art later.
    return `<button class="kit" data-id="${esc(p.id)}">` +
      `<img class="kit-img" src="${esc(classImage(c && c.key))}" alt="" width="48" height="48">` +
      `<span><b>${esc(c ? c.name : p.name)}</b><small>${esc(p.current_role)}</small></span></button>`;
  };
  el.innerHTML = `<h2>Choose your starting class</h2>
    <p class="muted">Each class is a sample starting kit: a typical job and its skills.</p>
    <div class="row">${personas.map(kit).join("")}</div>
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
    const c = classFor(p.skills);
    el.querySelector("#persona-info").textContent = p.id === "custom"
      ? `Your profile: ${p.skills.length} skills ticked, ${p.hours_per_week} hours a week to study.`
      : `${c ? `${c.name}, ${c.title}. ` : ""}Background: ${p.current_role}, ` +
        `${p.hours_per_week} hours a week to study. Sample data, not a real person.`;
    emit("persona-changed", p);
  };

  el.querySelectorAll(".kit-img").forEach((img) =>
    img.addEventListener("error", () => { img.src = PLACEHOLDER_IMG; }, { once: true }));

  el.querySelector(".row").addEventListener("click", (e) => {
    const btn = e.target.closest("button");  // the click can land on the <small> inside
    const p = btn && personas.find((x) => x.id === btn.dataset.id);
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