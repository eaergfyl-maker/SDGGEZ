// "How to use" tour: a step-by-step panel that highlights each part of the page in turn.
// Opens by itself on the first visit; the header button reopens it any time.
import { t } from "./i18n.js";

const SEEN = "rpg:guide-seen";

// Each step: text keys guide.<id>.title / guide.<id>.body, and the parts of the page it points at.
const STEPS = [
  { id: "welcome", targets: [] },
  { id: "start", targets: ["#intake"] },
  { id: "scenario", targets: ["#scenario", "#area"], row: true },
  { id: "tree", targets: [".tree-wrap"] },
  { id: "detail", targets: ["#detail", ".stats", ".xp"] },
  { id: "roles", targets: ["#ranked-roles"] },
  { id: "pathway", targets: ["#pathway"] },
  { id: "radar", targets: ["#radar"] },
  { id: "done", targets: ["#profile"] },
];

let panel = null;
let step = 0;
let lastFocus = null;

function targetsOf(s) {
  return s.targets
    .map((sel) => document.querySelector(sel))
    .filter(Boolean)
    .map((el) => (s.row ? el.closest(".row") || el : el))
    .filter((el) => !el.hidden);
}

function clearFocus() {
  document.querySelectorAll(".guide-focus").forEach((el) => el.classList.remove("guide-focus"));
}

function show(i) {
  step = Math.max(0, Math.min(STEPS.length - 1, i));
  const s = STEPS[step];
  clearFocus();
  const els = targetsOf(s);
  els.forEach((el) => el.classList.add("guide-focus"));
  if (els[0]) els[0].scrollIntoView({ block: "start" });  // instant: a smooth scroll can be cut short
  else {
    const at = step;  // after the browser restores scroll, unless the user has moved on
    requestAnimationFrame(() => { if (panel && step === at) window.scrollTo({ top: 0 }); });
  }

  const last = step === STEPS.length - 1;
  panel.innerHTML = `
    <p class="muted guide-count">${t("guide.count", { n: step + 1, total: STEPS.length })}</p>
    <h2 id="guide-title">${t(`guide.${s.id}.title`)}</h2>
    <p id="guide-body">${t(`guide.${s.id}.body`)}</p>
    <div class="row guide-nav">
      <button type="button" data-go="back" ${step === 0 ? "disabled" : ""}>${t("guide.back")}</button>
      <button type="button" data-go="next" class="on">${t(last ? "guide.finish" : "guide.next")}</button>
      ${last ? "" : `<button type="button" data-go="close" class="guide-skip">${t("guide.skip")}</button>`}
    </div>`;
  panel.querySelector('[data-go="next"]').focus({ preventScroll: true });
}

export function closeGuide() {
  if (!panel) return;
  clearFocus();
  panel.remove();
  panel = null;
  document.removeEventListener("keydown", onKey);
  try { localStorage.setItem(SEEN, "1"); } catch {}
  lastFocus?.focus?.({ preventScroll: true });
}

function onKey(e) {
  if (e.key === "Escape") closeGuide();
  else if (e.key === "ArrowRight" && !e.target.matches("input, select, textarea")) show(step + 1);
  else if (e.key === "ArrowLeft" && !e.target.matches("input, select, textarea")) show(step - 1);
}

export function openGuide(at = 0) {
  if (panel) return show(at);
  lastFocus = document.activeElement;
  panel = document.createElement("aside");
  panel.className = "guide";
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-labelledby", "guide-title");
  panel.setAttribute("aria-describedby", "guide-body");
  panel.addEventListener("click", (e) => {
    const go = e.target.closest("button[data-go]")?.dataset.go;
    if (go === "back") show(step - 1);
    else if (go === "close") closeGuide();
    else if (go === "next") step === STEPS.length - 1 ? closeGuide() : show(step + 1);
  });
  document.body.appendChild(panel);
  document.addEventListener("keydown", onKey);
  show(at);
}

document.getElementById("guide-open")?.addEventListener("click", () => openGuide(0));

export function openGuideOnFirstVisit() {
  let seen = false;
  try { seen = localStorage.getItem(SEEN) === "1"; } catch {}
  if (!seen) openGuide(0);
}
