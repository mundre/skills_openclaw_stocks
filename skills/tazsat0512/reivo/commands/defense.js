const { DashboardClient } = require("../lib/dashboard-client");

const DASHBOARD_URL = "https://app.reivo.dev";

function getApiKey() {
  const key = process.env.REIVO_API_KEY;
  if (!key) {
    throw new Error(
      "REIVO_API_KEY is not set. Get your key at https://app.reivo.dev/settings"
    );
  }
  return key;
}

async function execute() {
  let data;
  try {
    const client = new DashboardClient(getApiKey());
    data = await client.get("/defense-status");
  } catch (err) {
    return [
      "Could not fetch defense status from Reivo.",
      `Error: ${err.message}`,
      "",
      `Check your dashboard: ${DASHBOARD_URL}`,
    ].join("\n");
  }

  const lines = [
    "Reivo - Defense Status",
    "=".repeat(25),
  ];

  // Budget
  if (data.budgetLimit) {
    const pct = data.budgetPercent ?? 0;
    const filled = Math.round(pct / 5);
    const bar = "\u2588".repeat(filled) + "\u2591".repeat(20 - filled);
    lines.push("");
    lines.push("Budget");
    lines.push("-".repeat(20));
    lines.push(`  ${bar} ${pct}%`);
    lines.push(`  $${data.budgetUsed.toFixed(2)} / $${data.budgetLimit.toFixed(2)}`);
  } else {
    lines.push("");
    lines.push("Budget: not set");
  }

  // Loops
  lines.push("");
  lines.push("Loop Detection");
  lines.push("-".repeat(20));
  lines.push(`  Today:     ${data.loopsToday} loops detected`);
  lines.push(`  This week: ${data.loopsWeek} loops detected`);

  // Blocked
  lines.push("");
  lines.push("Blocked Requests");
  lines.push("-".repeat(20));
  lines.push(`  Today:     ${data.blockedToday} blocked`);
  lines.push(`  This week: ${data.blockedWeek} blocked`);

  lines.push("");
  lines.push(`Full details: ${DASHBOARD_URL}/loops`);

  return lines.join("\n");
}

module.exports = { execute, description: "View budget, loop detection, and blocked request status" };
