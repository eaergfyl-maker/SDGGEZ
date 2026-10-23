// Shared comparison of two /api/tree responses. Owner: Member 4.
// Used by the tree highlight (refresh.js). The patch-notes banner can import it too,
// so both places agree on what counts as "moved".

const EPS = 0.05; // ignore rounding noise below this many percentage points

function moved(a, b) {
  if (a == null && b == null) return false;
  if (a == null || b == null) return true;
  return Math.abs(a - b) >= EPS;
}

// Returns [{ id, name, kind: "momentum" | "outlook" | "match", from, to, dir: "up" | "down" }]
export function diffTrees(oldTree, newTree) {
  const out = [];
  if (!oldTree || !newTree || !oldTree.nodes || !newTree.nodes) return out;
  const before = new Map(oldTree.nodes.map((n) => [n.id, n]));
  const add = (n, kind, from, to) =>
    out.push({ id: n.id, name: n.full_name || n.name, kind, from, to, dir: (to ?? 0) > (from ?? 0) ? "up" : "down" });

  for (const n of newTree.nodes) {
    const o = before.get(n.id);
    if (!o) continue;
    if (n.kind === "skill") {
      if (moved(o.momentum, n.momentum)) add(n, "momentum", o.momentum, n.momentum);
    } else {
      if (moved(o.outlook, n.outlook)) add(n, "outlook", o.outlook, n.outlook);
      const a = o.match && o.match.score, b = n.match && n.match.score;
      if (moved(a, b)) add(n, "match", a, b);
    }
  }
  return out;
}