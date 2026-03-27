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

async function execute(args) {
  const amount = args ? parseFloat(args.trim().replace("$", "")) : NaN;

  // If no amount provided, show current budget status
  if (isNaN(amount)) {
    let data;
    try {
      const client = new DashboardClient(getApiKey());
      data = await client.get("/defense-status");
    } catch (err) {
      return [
        "Could not fetch budget status.",
        `Error: ${err.message}`,
        "",
        `Check dashboard: ${DASHBOARD_URL}/settings`,
      ].join("\n");
    }

    if (data.budgetLimit) {
      const pct = data.budgetPercent ?? 0;
      const filled = Math.round(pct / 5);
      const bar = "\u2588".repeat(filled) + "\u2591".repeat(20 - filled);
      return [
        "Budget Status",
        "",
        `  ${bar} ${pct}%`,
        `  $${data.budgetUsed.toFixed(2)} / $${data.budgetLimit.toFixed(2)} this month`,
        "",
        "To change: /reivo budget <amount>",
        "To remove: /reivo budget 0",
        "",
        `Manage: ${DASHBOARD_URL}/settings`,
      ].join("\n");
    }

    return [
      "Budget: not set",
      "",
      "Usage: /reivo budget <amount>",
      "  e.g. /reivo budget 50",
      "",
      `Or set in dashboard: ${DASHBOARD_URL}/settings`,
    ].join("\n");
  }

  // Set budget
  const val = amount <= 0 ? null : amount;
  try {
    const client = new DashboardClient(getApiKey());
    await client.post("/settings", { budgetLimitUsd: val });
  } catch (err) {
    return `Failed to set budget: ${err.message}`;
  }

  if (val === null) {
    return "Budget cap removed. Requests will no longer be blocked by budget.";
  }

  return [
    `Budget set to $${val.toFixed(2)}/month`,
    "",
    "You'll receive alerts at 50%, 80%, and 100%.",
    "Requests will be blocked when the limit is reached.",
  ].join("\n");
}

module.exports = { execute, description: "View or set monthly budget cap" };
