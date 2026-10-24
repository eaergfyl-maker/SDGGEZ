// "Ask your guide": questions about the user's own results. Owner: Member 3.
// The server answers only from facts it computed for this user and checks every number, so this
// panel just sends the current state (skills, scenario, area, selected role) with the question.
// Shown only when the server has the AI switched on.
import { api } from "../api.js";
import { on, state } from "../state.js";
import { esc } from "../util.js";
import { getLang, t } from "../i18n.js";

const el = document.getElementById("chat");
let hours = null;   // study hours of the current profile (a custom profile has its own)
on("persona-changed", (p) => { hours = p.hours_per_week ?? null; });

function selectedRole() {
  const n = state.tree?.nodes?.find((x) => x.id === state.selected);
  return n && n.kind === "role" ? n.id : null;
}

export async function renderChat() {
  if (!el) return;
  const status = await api.chatStatus().catch(() => ({ enabled: false }));
  if (!status.enabled) return;

  el.hidden = false;
  el.innerHTML = `<h2>${esc(t("chat.title"))}</h2>
    <p class="muted">${esc(t("chat.note"))}</p>
    <div class="row chat-suggest">
      ${["chat.q1", "chat.q2", "chat.q3"].map((k) => `<button type="button" class="chip">${esc(t(k))}</button>`).join("")}
    </div>
    <ol id="chat-log" class="chat-log" aria-live="polite"></ol>
    <form id="chat-form" class="row">
      <input id="chat-q" type="text" maxlength="500" autocomplete="off"
             placeholder="${esc(t("chat.placeholder"))}" aria-label="${esc(t("chat.placeholder"))}">
      <button type="submit" id="chat-send">${esc(t("chat.ask"))}</button>
    </form>`;

  const log = el.querySelector("#chat-log");
  const input = el.querySelector("#chat-q");
  const send = el.querySelector("#chat-send");

  const ask = async (question) => {
    question = question.trim();
    if (!question || send.disabled) return;
    input.value = "";
    send.disabled = true;
    log.insertAdjacentHTML("beforeend",
      `<li class="chat-q"><b>${esc(t("chat.you"))}</b> ${esc(question)}</li>
       <li class="chat-a muted">${esc(t("chat.thinking"))}</li>`);
    const slot = log.lastElementChild;
    slot.scrollIntoView({ block: "nearest" });
    let r;
    try {
      r = await api.chat({
        question, persona: state.persona, owned: state.owned ? [...state.owned] : null,
        scenario: state.scenario, family: state.family, role: selectedRole(),
        hours_per_week: hours, lang: getLang(),
      });
    } catch { r = { status: "error" }; }
    send.disabled = false;
    slot.classList.remove("muted");
    if (r.status === "ok") {
      const about = r.focus_role ? t("chat.about", { role: r.focus_role, date: (r.as_of || "").slice(0, 10) }) : "";
      slot.innerHTML = `<b>${esc(t("chat.guide"))}</b> <span class="chat-text">${esc(r.answer)}</span>` +
        (about ? `<small class="muted">${esc(about)}</small>` : "");
    } else {
      slot.classList.add("muted");
      slot.textContent = t(r.status === "unverified" ? "chat.unverified" : "chat.error");
    }
    slot.scrollIntoView({ block: "nearest" });
    input.focus({ preventScroll: true });
  };

  el.querySelector("#chat-form").addEventListener("submit", (e) => { e.preventDefault(); ask(input.value); });
  el.querySelector(".chat-suggest").addEventListener("click", (e) => {
    const b = e.target.closest("button.chip");
    if (b) ask(b.textContent);
  });
}
