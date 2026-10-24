// Refresh the data and show what moved. Owner: Member 4.
import { state, on } from "../state.js";
import { refreshTree, setMoved, clearMoved } from "./tree.js";
import { diffTrees } from "../diff.js";
import { esc } from "../util.js";

// POST /api/refresh, protected by the REFRESH_TOKEN secret sent in the X-Refresh-Token header.
// The server starts the refresh in the background and answers 202 at once, so after that we
// wait for a newer snapshot (its date changes) before showing what moved.
const REFRESH_URL = "/api/refresh";
const authHeaders = (token) => ({ "X-Refresh-Token": token });
const WAIT_MS = 180000, POLL_MS = 5000;
const wait = (ms) => new Promise((r) => setTimeout(r, ms));

let token = null; // kept in memory only: never saved, never in the repo

const btn = document.getElementById("refresh-data");
const note = document.getElementById("refresh-note");
const result = document.getElementById("refresh-result");

// Only for the team: the button shows when the page is opened with ?admin, so judges and users
// never meet a token prompt. (.row sets display:flex, which would override the hidden attribute.)
const admin = new URLSearchParams(location.search).has("admin");
if (!admin) {
  const row = btn?.closest(".row");
  if (row) row.style.display = "none";
}

const signed = (v) => (v == null ? "no data" : `${v > 0 ? "+" : ""}${v}%`);
const plain = (v) => (v == null ? "no data" : `${v}%`);

function line(c) {
  const f = c.kind === "match" ? plain : signed;
  const label = c.kind === "match" ? "match score" : c.kind;
  return `<li>${esc(c.name)} ${label}: ${f(c.from)} → ${f(c.to)} (${c.dir})</li>`;
}

function show(before, after) {
  const changes = diffTrees(before, after);
  const map = new Map();
  for (const c of changes) if (!map.has(c.id)) map.set(c.id, c.dir);
  setMoved(map);

  const asOf = after.as_of
    ? ` Data as of ${before.as_of && before.as_of !== after.as_of ? `${before.as_of} → ` : ""}${after.as_of}.`
    : "";
  note.textContent = `Refreshed.${asOf}`;

  if (!changes.length) {
    result.innerHTML = `<p>No change: the numbers match the previous snapshot.</p>`;
    return;
  }
  const shown = changes.slice(0, 12).map(line).join("");
  const more = changes.length > 12 ? `<p class="muted">…and ${changes.length - 12} more.</p>` : "";
  result.innerHTML = `<p><b>What moved (${changes.length})</b></p><ul>${shown}</ul>${more}
    <button id="dismiss-moved" type="button">Clear highlights</button>`;
}

async function run() {
  if (!state.tree) { note.textContent = "Choose a persona first."; return; }
  if (!token) {
    const t = window.prompt("Enter the refresh token:");
    if (!t) return;
    token = t.trim();
  }
  btn.disabled = true;
  note.textContent = "Refreshing data…";
  result.innerHTML = "";
  const before = state.tree;
  try {
    const res = await fetch(REFRESH_URL, { method: "POST", headers: authHeaders(token) });
    if (res.status === 401 || res.status === 403) { token = null; throw new Error("The refresh token was not accepted."); }
    if (res.status === 404) throw new Error("The refresh endpoint is not available yet.");
    if (res.status === 429) throw new Error("A refresh ran in the last 30 minutes; try again later.");
    if (!res.ok) throw new Error(`The refresh failed (${res.status}).`);
    // the fetch runs in the background on the server: wait until a newer snapshot appears
    note.textContent = "Fetching new job data… this can take a minute or two.";
    const start = Date.now();
    let fresh = false;
    while (Date.now() - start < WAIT_MS) {
      await wait(POLL_MS);
      const t = await fetch("/api/trends").then((r) => r.json()).catch(() => null);
      if (t && t.as_of !== before.as_of) { fresh = true; break; }
    }
    if (!fresh) throw new Error("Still fetching on the server. Reload the page in a few minutes to see the new data.");
    await refreshTree();
    // refreshTree keeps the old tree if its request fails: never report "no change" in that case
    if (state.tree === before) throw new Error("Data refreshed, but the tree could not be reloaded.");
    show(before, state.tree);
  } catch (e) {
    note.textContent = e instanceof TypeError ? "Couldn't reach the server." : e.message;
  } finally {
    btn.disabled = false;
  }
}

btn?.addEventListener("click", run);
result?.addEventListener("click", (e) => {
  if (e.target.id === "dismiss-moved") { setMoved(new Map()); result.innerHTML = ""; }
});
on("persona-changed", () => {
  clearMoved();
  if (result) result.innerHTML = "";
  if (note) note.textContent = "";
});