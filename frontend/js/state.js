// Shared app state and a tiny event bus so panels stay independent. Owner: Member 4.
export const state = {
  persona: "aisyah",
  scenario: "moderate",
  owned: null,          // Set of skill ids; null until the persona loads
  startingSkills: new Set(),
  selected: null,       // selected node id
  tree: null,           // last /api/tree response
  skillXp: {},          // optional { skillId: course hours }, used for XP
};

const listeners = {};
export function on(event, fn) { (listeners[event] ||= []).push(fn); }
export function emit(event, data) { (listeners[event] || []).forEach((fn) => fn(data)); }

// Save and restore trained skills per persona, in the browser only.
// Storage may be blocked by browser policy, so persistence must not break the app.
const ownedKey = (persona) => `rpg:owned:${persona}`;

export function saveOwned() {
  try {
    localStorage.setItem(ownedKey(state.persona), JSON.stringify([...state.owned]));
  } catch {
    // Progress remains usable in memory when browser storage is unavailable.
  }
}

export function loadOwned(persona) {
  try {
    const value = JSON.parse(localStorage.getItem(ownedKey(persona)));
    return Array.isArray(value) && value.every((id) => typeof id === "string")
      ? new Set(value)
      : null;
  } catch {
    return null;
  }
}

export function clearOwned() {
  try {
    localStorage.removeItem(ownedKey(state.persona));
  } catch {
    // Reset still takes effect in memory when browser storage is unavailable.
  }
}
