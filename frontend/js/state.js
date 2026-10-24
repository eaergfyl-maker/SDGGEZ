// Shared app state and a tiny event bus so panels stay independent. Owner: Member 4.
export const state = {
  persona: "aisyah",
  scenario: "moderate",
  owned: null,          // Set of skill ids; null until the persona loads
  startingSkills: new Set(),
  selected: null,       // selected node id
  tree: null,           // last /api/tree response
  family: null,         // career area: null = the class's own area, "auto" = guess from skills, or an area id
  skillXp: {},          // optional { skillId: course hours }, used for XP
};

const listeners = {};
export function on(event, fn) { (listeners[event] ||= []).push(fn); }
export function emit(event, data) { (listeners[event] || []).forEach((fn) => fn(data)); }

// Save and restore trained skills per persona, in the browser only.
// Key explicitly evaluates the current persona (or falls back to custom) to prevent state leaks across profiles.
const key = (persona) => `rpg:owned:${persona || state.persona || "custom"}`;

export function saveOwned() {
  try { localStorage.setItem(key(state.persona), JSON.stringify([...state.owned])); } catch {}
}
export function loadOwned(persona) {
  try {
    const v = JSON.parse(localStorage.getItem(key(persona)));
    return Array.isArray(v) ? new Set(v) : null;
  } catch { return null; }
}
export function clearOwned() {
  try { localStorage.removeItem(key(state.persona)); } catch {}
}

// Adventurer name (a nickname): one per browser, not per persona.
export function saveName(name) {
  try { localStorage.setItem("rpg:name", name); } catch {}
}
export function loadName() {
  try { return localStorage.getItem("rpg:name") || ""; } catch { return ""; }
}
// Delete everything this app saved in the browser (name and progress for every persona).
export function clearAllSaved() {
  try {
    const keys = [];
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (k && k.startsWith("rpg:")) keys.push(k);
    }
    keys.forEach((k) => localStorage.removeItem(k));
  } catch {}
}