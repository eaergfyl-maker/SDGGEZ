// Shared app state and a tiny event bus so panels stay independent. Owner: Member 4.
export const state = {
  persona: "aisyah",
  scenario: "moderate",
  owned: null,          // Set of skill ids; null until the persona loads
  startingSkills: new Set(),
  selected: null,       // selected node id
  tree: null,           // last /api/tree response
};

const listeners = {};
export function on(event, fn) { (listeners[event] ||= []).push(fn); }
export function emit(event, data) { (listeners[event] || []).forEach((fn) => fn(data)); }
