// Persona picker and starting skills. Owner: Member 5.
import { api } from "../api.js";
import { emit, state } from "../state.js";
import { esc } from "../util.js";
import { t } from "../i18n.js";
import { classFor } from "../tree/classes.js";
import { classImage, PLACEHOLDER_IMG } from "../tree/tree.js";

const el = document.getElementById("intake");

// Notes come from the API in English; show them in the chosen language.
function noteText(note) {
  if (!note) return "";
  if (note.includes("suggested by AI")) return t("cv.note.ai");
  if (note.includes("negation")) return t("cv.note.negation");
  if (note.includes("learned")) return t("cv.note.intent");
  if (note.includes("similar")) return t("cv.note.similar");
  return note;
}

// The checklist, grouped: skills used in several career areas first, then each area's own.
// Areas come from /api/families (with the skills their roles use); if that fails, one plain list.
function skillGroups(skills, families) {
  const box = (s) => `<label><input type="checkbox" value="${esc(s.skill)}"> ${esc(s.name)}</label>`;
  const group = (title, items) => items.length ? `<fieldset class="skill-group">
      <legend>${esc(title)} <span class="muted">(${items.length})</span></legend>
      <div class="skill-group-items">${items.map(box).join("")}</div></fieldset>` : "";
  const count = {};
  families.forEach((f) => (f.skills || []).forEach((id) => { count[id] = (count[id] || 0) + 1; }));
  if (!Object.keys(count).length) return group(t("intake.skillsAll"), skills);
  const shared = skills.filter((s) => count[s.skill] > 1);
  const other = skills.filter((s) => !count[s.skill]);
  return group(t("intake.skillsShared"), shared)
    + families.map((f) => group(f.name, skills.filter((s) => count[s.skill] === 1 && f.skills.includes(s.skill)))).join("")
    + group(t("intake.skillsOther"), other);
}

export async function renderIntake() {
  const personas = await api.personas();
  const trends = await api.trends(state.scenario);
  const families = await api.families().catch(() => []);

  // Each sample persona is offered as a starting class (Bard, Wizard, ...): the class comes from
  // its skills, and its job is shown as the background. The persona data itself is unchanged.
  const kit = (p) => {
    const c = classFor(p.skills);
    // Image follows USE_CLASS_ART in tree.js: the placeholder for now, real art later.
    return `<button class="kit" data-id="${esc(p.id)}">` +
      `<img class="kit-img" src="${esc(classImage(c && c.key))}" alt="" width="48" height="48">` +
      `<span><b>${esc(c ? c.name : p.name)}</b><small>${esc(p.current_role)}</small></span></button>`;
  };
  el.innerHTML = `<h2>${esc(t("intake.title"))}</h2>
    <p class="muted">${esc(t("intake.kitNote"))}</p>
    <div class="row">${personas.map(kit).join("")}</div>
    <p id="persona-info" class="muted"></p>

    <h2>${esc(t("intake.describe"))}</h2>
    <p class="muted">${esc(t("intake.sampleNote"))}</p>
    <details id="cv-box" open>
      <summary>${esc(t("cv.summary"))}</summary>
      <p class="muted">${esc(t("cv.note"))}</p>
      <div class="row">
        <label for="cv-sample" class="muted">${esc(t("cv.try"))}</label>
        <select id="cv-sample"><option value="">${esc(t("cv.choose"))}</option></select>
        <input type="file" id="cv-file" accept=".txt,.docx,text/plain,application/vnd.openxmlformats-officedocument.wordprocessingml.document" aria-label="${esc(t("cv.fileAria"))}">
      </div>
      <textarea id="cv-text" rows="6" maxlength="20000" aria-label="${esc(t("cv.textAria"))}"></textarea>
      <div class="row">
        <button id="cv-scan" type="button">${esc(t("cv.scan"))}</button>
        <span id="cv-status" class="muted" aria-live="polite"></span>
      </div>
      <div id="cv-result"></div>
    </details>
    <label for="hours-input">${esc(t("intake.hours"))}
      <input type="number" id="hours-input" min="1" max="40" value="6" />
    </label>
    <div id="skill-boxes">${skillGroups(trends.skills, families)}</div>
    <button id="use-profile">${esc(t("intake.use"))}</button>`;

  const select = (p) => {
    state.persona = p.id;
    state.startingSkills = new Set(p.skills);
    state.owned = new Set(p.skills);
    el.querySelectorAll(".kit").forEach((b) => b.classList.toggle("on", b.dataset.id === p.id));
    const c = classFor(p.skills);
    el.querySelector("#persona-info").textContent = p.id === "custom"
      ? t("intake.customInfo", { n: p.skills.length, hours: p.hours_per_week })
      : t("intake.kitInfo", { name: c ? c.name : p.name, title: c ? c.title : "",
                              role: p.current_role, hours: p.hours_per_week });
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

  // .txt is read in the browser; .docx is sent to the server, which returns its text to review.
  el.querySelector("#cv-file").addEventListener("change", async (e) => {
    const input = e.target;
    const file = input.files[0];
    input.value = "";  // so choosing the same file again still triggers a change
    if (!file) return;
    cvText.value = "";
    cvResult.innerHTML = "";
    try {
      if (/\.txt$/i.test(file.name) || file.type === "text/plain") {
        cvText.value = (await file.text()).slice(0, 20000);
      } else if (/\.docx$/i.test(file.name)) {
        if (file.size > 2_000_000) throw new Error("too big");
        cvStatus.textContent = t("cv.loading");
        const bytes = new Uint8Array(await file.arrayBuffer());
        let bin = "";
        for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
        cvText.value = (await api.cvFile(btoa(bin))).text;
      } else {
        cvStatus.textContent = t("cv.fileType", { name: file.name });
        return;
      }
      cvStatus.textContent = cvText.value.trim() ? t("cv.loaded", { name: file.name }) : t("cv.fileEmpty");
    } catch {
      cvStatus.textContent = t("cv.fileError", { name: file.name });
    }
  });

  const line = (r, checkable) => {
    const note = noteText(r.note);
    return `<li>${checkable
      ? `<label><input type="checkbox" data-skill="${esc(r.skill)}"> <b>${esc(r.name)}</b></label>`
      : `<b>${esc(r.name)}</b>`}: <q>${esc(r.evidence)}</q>${note ? ` <span class="muted">(${esc(note)})</span>` : ""}</li>`;
  };

  // A ticked "possible" item ticks the same skill in the checklist (keyword and AI lists alike).
  cvResult.addEventListener("change", (e) => {
    const c = e.target.closest("input[data-skill]");
    const b = c && box(c.dataset.skill);
    if (b) b.checked = c.checked;
  });

  // AI suggestions are optional: only offered when the server has RunPod settings.
  const aiOn = api.cvAiStatus().then((s) => s.enabled).catch(() => false);
  let scanId = 0;  // ignore a slow AI reply that belongs to an earlier scan

  const askAi = async (text, id) => {
    if (!(await aiOn)) return;
    cvResult.insertAdjacentHTML("beforeend", `<div id="cv-ai"><p><b>${esc(t("cv.ai.title"))}</b></p>
      <p class="muted" aria-live="polite">${esc(t("cv.ai.waiting"))}</p></div>`);
    const ai = cvResult.querySelector("#cv-ai");
    let r;
    try { r = await api.cvAi(text); } catch { r = { status: "error", possible: [] }; }
    if (id !== scanId) return;
    const msg = r.status !== "ok" ? t("cv.ai.error") : r.possible.length ? t("cv.ai.note") : t("cv.ai.none");
    ai.innerHTML = `<p><b>${esc(t("cv.ai.title"))}</b></p><p class="muted">${esc(msg)}</p>` +
      (r.possible.length ? `<ul class="cv-list">${r.possible.map((x) => line(x, true)).join("")}</ul>` : "");
  };

  el.querySelector("#cv-scan").addEventListener("click", async () => {
    const text = cvText.value.trim();
    if (!text) { cvStatus.textContent = t("cv.empty"); return; }
    const id = ++scanId;
    cvStatus.textContent = t("cv.reading");
    let r;
    try { r = await api.cvSkills(text); } catch {
      cvStatus.textContent = t("cv.error");
      return;
    }
    if (id !== scanId) return;
    el.querySelectorAll("#skill-boxes input").forEach((b) => { b.checked = false; });
    r.found.forEach((x) => { const b = box(x.skill); if (b) b.checked = true; });
    const removed = r.redactions.emails + r.redactions.numbers;
    cvStatus.textContent = t("cv.ticked", { n: r.found.length }) +
      (removed ? t("cv.removed", { n: removed }) : ".");
    cvResult.innerHTML =
      (r.found.length ? `<p><b>${esc(t("cv.found"))}</b></p><ul class="cv-list">${r.found.map((x) => line(x, false)).join("")}</ul>` : "") +
      (r.possible.length ? `<p><b>${esc(t("cv.possible"))}</b></p><ul class="cv-list">${r.possible.map((x) => line(x, true)).join("")}</ul>` : "") +
      `<p class="muted">${esc(t("cv.review"))}</p>`;
    askAi(text, id);
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
