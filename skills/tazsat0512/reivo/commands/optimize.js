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

function formatUsd(n) {
  if (n < 0.01) return `$${n.toFixed(4)}`;
  return `$${n.toFixed(2)}`;
}

const SEVERITY_ICON = { high: "!!!", medium: "!!", low: "!" };

async function execute() {
  let data;
  try {
    const client = new DashboardClient(getApiKey());
    data = await client.get("/optimization");
  } catch (err) {
    return [
      "Could not fetch optimization tips from Reivo.",
      `Error: ${err.message}`,
      "",
      `Check your dashboard: ${DASHBOARD_URL}/optimization`,
    ].join("\n");
  }

  if (!data.tips || data.tips.length === 0) {
    return [
      "Reivo - Optimization",
      "=".repeat(25),
      "",
      `Analyzed ${data.analyzedRequests} requests from the last 7 days.`,
      "",
      "No optimization tips found. Your usage looks efficient!",
      "",
      `Full details: ${DASHBOARD_URL}/optimization`,
    ].join("\n");
  }

  const lines = [
    "Reivo - Optimization Tips",
    "=".repeat(30),
    "",
    `Analyzed ${data.analyzedRequests} requests (last 7 days)`,
    `Potential savings: ${formatUsd(data.totalEstimatedSavingsUsd)}/week`,
    "",
  ];

  for (const tip of data.tips) {
    const icon = SEVERITY_ICON[tip.severity] || "!";
    lines.push(`[${icon}] ${tip.title} (${tip.severity})`);
    lines.push(`    ${tip.description}`);
    if (tip.estimatedSavingsUsd > 0) {
      lines.push(`    Estimated savings: ${formatUsd(tip.estimatedSavingsUsd)}/week`);
    }
    lines.push(`    Affected: ${tip.affectedRequests} requests`);
    lines.push("");
  }

  lines.push(`Full details: ${DASHBOARD_URL}/optimization`);

  return lines.join("\n");
}

module.exports = { execute, description: "Show cost optimization recommendations" };
