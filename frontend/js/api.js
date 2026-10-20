// All calls to the backend go through here. Owner: Member 1.
async function get(path, params = {}) {
  const query = new URLSearchParams(Object.entries(params).filter(([, v]) => v != null));
  const res = await fetch(`/api/${path}?${query}`);
  if (!res.ok) throw new Error(`${path}: ${res.status}`);
  return res.json();
}

export const api = {
  personas: () => get("personas"),
  sdgs: () => get("sdgs"),
  trends: (scenario) => get("trends", { scenario }),
  tree: (persona, scenario, owned) => get("tree", { persona, scenario, owned: owned && [...owned].join(",") }),
  pathway: (role, persona, owned) => get("pathway", { role, persona, owned: owned && [...owned].join(",") }),
  story: (nodeId) => get(`story/${nodeId}`),
  changes: () => get("changes"),
};
