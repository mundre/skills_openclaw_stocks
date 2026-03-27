const { ProxyClient } = require("../lib/proxy-client");

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

async function execute() {
  let data;
  try {
    const client = new ProxyClient(getApiKey());
    const res = await fetch(`${client.baseUrl}/v1/stats`, {
      headers: client._headers(),
    });
    if (!res.ok) throw new Error(`${res.status}`);
    data = await res.json();
  } catch (err) {
    return [
      "Could not fetch stats from Reivo proxy.",
      `Error: ${err.message}`,
      "",
      `View your stats at: ${DASHBOARD_URL}`,
    ].join("\n");
  }

  const s = data.summary;
  const m = data.month;
  const r = data.routing;

  const lines = [
    "Reivo - 30 Day Summary",
    "=".repeat(30),
    "",
    `Total Cost:      ${formatUsd(s.totalCost)}`,
    `Requests:        ${s.totalRequests.toLocaleString()}`,
    `Input Tokens:    ${s.totalInputTokens.toLocaleString()}`,
    `Output Tokens:   ${s.totalOutputTokens.toLocaleString()}`,
  ];

  if (r.routedRequests > 0) {
    lines.push("");
    lines.push("Smart Routing");
    lines.push("-".repeat(20));
    lines.push(`Routed:          ${r.routedRequests} requests`);
    lines.push(`Saved:           ${formatUsd(r.savedUsd)}`);
  }

  if (data.topModels && data.topModels.length > 0) {
    lines.push("");
    lines.push("Top Models");
    lines.push("-".repeat(20));
    for (const m of data.topModels.slice(0, 3)) {
      lines.push(`  ${m.model}: ${formatUsd(m.cost)} (${m.count} reqs)`);
    }
  }

  if (data.topAgents && data.topAgents.filter((a) => a.agentId).length > 0) {
    lines.push("");
    lines.push("Top Agents");
    lines.push("-".repeat(20));
    for (const a of data.topAgents.filter((a) => a.agentId).slice(0, 3)) {
      lines.push(`  ${a.agentId}: ${formatUsd(a.cost)} (${a.count} reqs)`);
    }
  }

  if (data.budgetLimitUsd) {
    lines.push("");
    lines.push(`Budget: ${formatUsd(m.totalCost)} / ${formatUsd(data.budgetLimitUsd)} this month`);
  }

  lines.push("");
  lines.push(`Full dashboard: ${DASHBOARD_URL}`);

  return lines.join("\n");
}

module.exports = { execute, description: "Monthly cost and savings summary" };
