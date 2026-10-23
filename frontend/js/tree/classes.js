// RPG class from skills. Deterministic: no AI, no randomness. Owner: Member 4.
// The class only decorates real data. It never changes the match score or the pathway.
// TODO: if Member 3 adds a category field to skills.json, replace GROUPS with that.

export const CLASSES = {
  bard: { name: "Bard", title: "The Silver Tongue" },
  wizard: { name: "Wizard", title: "The Data Archmage" },
  rogue: { name: "Rogue", title: "The Shadow Tactician" },
  paladin: { name: "Paladin", title: "The System Shield" },
  druid: { name: "Druid", title: "The Grid Keeper" },
};

// Fixed order: also used to break ties, so the same skills always give the same class.
const ORDER = ["bard", "wizard", "rogue", "paladin", "druid"];

// Every skill id in data/skills.json belongs to exactly one class.
const GROUPS = {
  bard: ["communication", "empathy", "case_handling", "crm_tools"],
  wizard: ["spreadsheets", "data_literacy", "statistics", "sql", "data_viz", "python_basics",
    "ml_basics", "bookkeeping", "ops_analytics", "esg_reporting"],
  rogue: ["tech_support", "ai_tools", "prompting", "chatbot_qa", "process_automation", "responsible_ai"],
  paladin: ["machine_operation", "quality_checks", "safety_procedures", "plc_basics", "lean_methods",
    "preventive_maintenance", "robotics_ops", "sensor_iot", "spc_quality", "predictive_maintenance",
    "machine_vision_qc"],
  druid: ["electrical_wiring", "technical_drawing", "solar_pv_install", "energy_auditing",
    "battery_storage", "pv_system_design", "energy_monitoring", "ev_charging"],
};

const CLASS_OF = {};
for (const [key, ids] of Object.entries(GROUPS)) ids.forEach((id) => (CLASS_OF[id] = key));

// ids: any iterable of skill ids. Each skill counts 1 point (skills.json has no weights).
// Returns null if no skill is recognised, else { key, name, title, scores: [{key, name, points}] }.
export function classFor(ids) {
  const points = {};
  for (const id of ids) {
    const k = CLASS_OF[id];
    if (k) points[k] = (points[k] || 0) + 1;
  }
  const ranked = ORDER.filter((k) => points[k]).sort((a, b) => points[b] - points[a] || ORDER.indexOf(a) - ORDER.indexOf(b));
  if (!ranked.length) return null;
  const top = ranked[0];
  return {
    key: top,
    ...CLASSES[top],
    scores: ranked.map((k) => ({ key: k, name: CLASSES[k].name, points: points[k] })),
  };
}