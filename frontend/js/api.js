// All calls to the backend go through here. Owner: Member 1.
async function get(path, params = {}) {
  const query = new URLSearchParams(Object.entries(params).filter(([, v]) => v != null));
  const res = await fetch(`/api/${path}?${query}`);
  if (!res.ok) throw new Error(`${path}: ${res.status}`);
  return res.json();
}

async function post(path, body) {
  const res = await fetch(`/api/${path}`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${path}: ${res.status}`);
  return res.json();
}

export const api = {
  personas: () => get("personas"),
  sdgs: () => get("sdgs"),
  trends: (scenario) => get("trends", { scenario }),
  families: () => get("families"),
  tree: (persona, scenario, owned, family) =>
    get("tree", { persona, scenario, owned: owned && [...owned].join(","), family }),
  pathway: (role, persona, owned) => get("pathway", { role, persona, owned: owned && [...owned].join(",") }),
  changes: () => get("changes"),
  cvSkills: (text) => post("cv/skills", { text }),
  cvSamples: () => get("cv/samples"),
  cvFile: (data) => post("cv/file", { data }),
  cvAiStatus: () => get("cv/ai"),
  cvAi: (text) => post("cv/ai", { text }),
  chatStatus: () => get("chat"),
  chat: (body) => post("chat", body),
};
