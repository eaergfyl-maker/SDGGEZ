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
    <details id="cv-box" open>
      <summary>Fill the checklist from a CV (optional)</summary>
      <p class="muted">Paste CV text, load a .txt file, or try a sample. Use invented CVs only.
        The text is checked on the server and never stored; emails and phone numbers are removed first.</p>
      <div class="row">
        <label for="cv-sample" class="muted">Try a sample</label>
        <select id="cv-sample"><option value="">Choose a sample CV</option></select>
        <input type="file" id="cv-file" accept=".txt,text/plain" aria-label="Load a CV as a .txt file">
      </div>
      <textarea id="cv-text" rows="6" maxlength="20000" aria-label="CV text"></textarea>
      <div class="row">
        <button id="cv-scan" type="button">Find my skills</button>
        <span id="cv-status" class="muted" aria-live="polite"></span>
      </div>
      <div id="cv-result"></div>
    </details>
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

  // --- CV reader: fills the checklist below; the person reviews it, then "Use this profile" ---
  const cvText = el.querySelector("#cv-text");
  const cvStatus = el.querySelector("#cv-status");
  const cvResult = el.querySelector("#cv-result");
  const box = (id) => el.querySelector(`#skill-boxes input[value="${CSS.escape(id)}"]`);

  api.cvSamples().then((samples) => {
    const sel = el.querySelector("#cv-sample");
    sel.insertAdjacentHTML("beforeend",
      samples.map((s) => `<option value="${esc(s.id)}">${esc(s.title)}</option>`).join(""));
    sel.addEventListener("change", () => {
      const s = samples.find((x) => x.id === sel.value);
      if (s) cvText.value = s.text;
    });
  }).catch(() => {});

  el.querySelector("#cv-file").addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (!/\.txt$/i.test(file.name) && file.type !== "text/plain") {
      cvStatus.textContent = "Only .txt files for now. Paste the text instead.";
      return;
    }
    const reader = new FileReader();
    reader.onload = () => { cvText.value = String(reader.result).slice(0, 20000); cvStatus.textContent = ""; };
    reader.readAsText(file);
  });

  const line = (r, checkable) => `<li>${checkable
    ? `<label><input type="checkbox" data-skill="${esc(r.skill)}"> <b>${esc(r.name)}</b></label>`
    : `<b>${esc(r.name)}</b>`}: <q>${esc(r.evidence)}</q>${r.note ? ` <span class="muted">(${esc(r.note)})</span>` : ""}</li>`;

  el.querySelector("#cv-scan").addEventListener("click", async () => {
    const text = cvText.value.trim();
    if (!text) { cvStatus.textContent = "Paste some CV text first."; return; }
    cvStatus.textContent = "Reading…";
    let r;
    try { r = await api.cvSkills(text); } catch {
      cvStatus.textContent = "Couldn't read the CV. Try again or tick skills yourself.";
      return;
    }
    el.querySelectorAll("#skill-boxes input").forEach((b) => { b.checked = false; });
    r.found.forEach((x) => { const b = box(x.skill); if (b) b.checked = true; });
    const removed = r.redactions.emails + r.redactions.numbers;
    cvStatus.textContent = `Ticked ${r.found.length} skills` +
      (removed ? `; removed ${removed} contact detail${removed > 1 ? "s" : ""} first.` : ".");
    cvResult.innerHTML =
      (r.found.length ? `<p><b>Found and ticked</b></p><ul class="cv-list">${r.found.map((x) => line(x, false)).join("")}</ul>` : "") +
      (r.possible.length ? `<p><b>Possible: tick if they fit you</b></p><ul class="cv-list">${r.possible.map((x) => line(x, true)).join("")}</ul>` : "") +
      `<p class="muted">Check the ticks in the list below, then press "Use this profile". You decide; the reader only suggests.</p>`;
    cvResult.querySelectorAll("input[data-skill]").forEach((c) =>
      c.addEventListener("change", () => { const b = box(c.dataset.skill); if (b) b.checked = c.checked; }));
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