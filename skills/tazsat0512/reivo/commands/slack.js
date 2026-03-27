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
  const webhookUrl = args ? args.trim() : "";

  // If no URL provided, show help
  if (!webhookUrl) {
    return [
      "Slack Notifications",
      "=".repeat(25),
      "",
      "Usage: /reivo slack <webhook_url>",
      "",
      "Quick setup:",
      "  1. Go to https://api.slack.com/apps → Create New App → From scratch",
      "  2. Enable Incoming Webhooks → Add New Webhook to Workspace",
      "  3. Copy the URL and run:",
      "",
      '  /reivo slack https://hooks.slack.com/services/T.../B.../xxx',
      "",
      "You'll receive alerts for:",
      "  - Budget warnings (50%, 80%, 100%)",
      "  - Loop detection",
      "  - Anomaly detection",
      "",
      `Or configure in dashboard: ${DASHBOARD_URL}/settings`,
    ].join("\n");
  }

  // Validate URL format
  if (!webhookUrl.startsWith("https://hooks.slack.com/")) {
    return "Error: Slack webhook URL must start with https://hooks.slack.com/";
  }

  // Save via settings API
  try {
    const client = new DashboardClient(getApiKey());
    await client.post("/settings", { slackWebhookUrl: webhookUrl });
  } catch (err) {
    return [
      "Failed to save Slack webhook URL.",
      `Error: ${err.message}`,
      "",
      `Try setting it manually: ${DASHBOARD_URL}/settings`,
    ].join("\n");
  }

  return [
    "Slack webhook configured!",
    "",
    "You'll now receive alerts for:",
    "  - Budget warnings (50%, 80%, 100%)",
    "  - Loop detection",
    "  - Anomaly detection",
    "",
    `Manage notifications: ${DASHBOARD_URL}/settings`,
  ].join("\n");
}

module.exports = { execute, description: "Configure Slack webhook for alerts" };
