// SDG tags you can click: a small popup says what the goal is, which target we map to, and why.
// Data comes from data/sdg_map.json (via /api/sdgs). Goal names are translated; reasons stay in
// English like the other data texts.
import { api } from "./api.js";
import { esc } from "./util.js";
import { t } from "./i18n.js";

let sdgs = new Map();
const ready = api.sdgs().then((list) => { sdgs = new Map(list.map((s) => [s.sdg, s])); }).catch(() => {});

export function sdgName(g) {
  const key = `sdg.name.${g}`;
  const name = t(key);
  return name !== key ? name : (sdgs.get(g)?.name || "");
}

// A clickable tag for SDG number g.
export function sdgTag(g) {
  const name = sdgName(g);
  return `<button type="button" class="tag sdg-tag" data-sdg="${g}" aria-expanded="false"
    aria-haspopup="dialog" title="${esc(name)}">SDG ${g}</button>`;
}

let pop = null;
let opener = null;

function close() {
  if (!pop) return;
  pop.remove();
  pop = null;
  opener?.setAttribute("aria-expanded", "false");
  opener?.focus({ preventScroll: true });
  opener = null;
}

async function open(btn) {
  close();
  await ready;
  const g = Number(btn.dataset.sdg);
  const s = sdgs.get(g);
  opener = btn;
  btn.setAttribute("aria-expanded", "true");
  pop = document.createElement("div");
  pop.className = "sdg-pop";
  pop.setAttribute("role", "dialog");
  pop.setAttribute("aria-label", `SDG ${g}`);
  pop.innerHTML = `
    <p class="sdg-pop-title"><b>SDG ${g}: ${esc(sdgName(g))}</b></p>
    ${s?.targets?.length ? `<p class="muted">${esc(t("sdg.targets", { targets: s.targets.join(", ") }))}</p>` : ""}
    ${s?.reason ? `<p>${esc(s.reason)}</p>` : ""}
    <p class="muted"><a href="https://sdgs.un.org/goals/goal${g}" target="_blank" rel="noopener">${esc(t("sdg.more"))}</a></p>
    <button type="button" class="sdg-pop-close" aria-label="${esc(t("sdg.close"))}">×</button>`;
  document.body.appendChild(pop);

  // place it under the tag, kept inside the window
  const r = btn.getBoundingClientRect();
  const w = pop.offsetWidth;
  const left = Math.max(8, Math.min(r.left + window.scrollX, window.scrollX + document.documentElement.clientWidth - w - 8));
  pop.style.left = `${left}px`;
  pop.style.top = `${r.bottom + window.scrollY + 6}px`;
  pop.querySelector(".sdg-pop-close").focus({ preventScroll: true });
}

document.addEventListener("click", (e) => {
  const tag = e.target.closest(".sdg-tag");
  if (tag) {
    if (tag === opener) close();
    else open(tag);
    return;
  }
  if (pop && (e.target.closest(".sdg-pop-close") || !e.target.closest(".sdg-pop"))) close();
});
document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
