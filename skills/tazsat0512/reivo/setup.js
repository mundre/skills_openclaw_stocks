const readline = require("readline");

const PROXY_BASE = "https://proxy.reivo.dev";
const DASHBOARD_API = "https://app.reivo.dev/api/v1";

function prompt(rl, question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => resolve(answer.trim()));
  });
}

function promptSecret(rl, question) {
  return new Promise((resolve) => {
    // For secret input, we still use regular prompt (terminal handles masking varies)
    rl.question(question, (answer) => resolve(answer.trim()));
  });
}

async function apiCall(apiKey, method, path, body) {
  const opts = {
    method,
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${DASHBOARD_API}${path}`, opts);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status}: ${text}`);
  }
  return await res.json();
}

async function validateKey(apiKey) {
  const res = await fetch(`${PROXY_BASE}/health`, {
    headers: { Authorization: `Bearer ${apiKey}` },
  });
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`);
  }
  return await res.json();
}

async function main() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  try {
    console.log("");
    console.log("Reivo Setup");
    console.log("===========");
    console.log("");

    // Step 1: API Key
    let apiKey = process.env.REIVO_API_KEY;
    if (apiKey) {
      console.log(`1. REIVO_API_KEY: ${apiKey.slice(0, 7)}...${apiKey.slice(-4)}`);
      process.stdout.write("   Validating... ");
      try {
        await validateKey(apiKey);
        console.log("Connected!");
      } catch (err) {
        console.log(`Failed: ${err.message}`);
        apiKey = null;
      }
    }

    if (!apiKey) {
      console.log("1. REIVO_API_KEY not set.");
      console.log("   Sign up at https://reivo.dev and generate a key in Settings.");
      console.log("");
      apiKey = await prompt(rl, "   Enter your Reivo API key (rv_...): ");

      if (!apiKey.startsWith("rv_")) {
        console.error("\n   Error: API key must start with rv_");
        process.exit(1);
      }

      process.stdout.write("   Validating... ");
      try {
        await validateKey(apiKey);
        console.log("Connected!");
      } catch (err) {
        console.error(`Failed: ${err.message}`);
        process.exit(1);
      }
    }

    console.log("");

    // Step 2: Check existing provider keys
    let existingKeys;
    try {
      existingKeys = await apiCall(apiKey, "GET", "/provider-keys");
    } catch {
      existingKeys = { openai: [], anthropic: [], google: [] };
    }

    console.log("2. Provider API Keys (encrypted & stored in Reivo)");
    const providers = [
      { name: "openai", label: "OpenAI", prefix: "sk-" },
      { name: "anthropic", label: "Anthropic", prefix: "sk-ant-" },
      { name: "google", label: "Google", prefix: "" },
    ];

    for (const p of providers) {
      const existing = existingKeys[p.name] || [];
      if (existing.length > 0) {
        const def = existing.find((k) => k.isDefault) || existing[0];
        console.log(`   ${p.label}: ${def.keyPreview} (configured)`);
      } else {
        const key = await promptSecret(
          rl,
          `   ${p.label} API key (Enter to skip): `
        );
        if (key) {
          try {
            await apiCall(apiKey, "POST", "/provider-keys", {
              provider: p.name,
              label: "Default",
              key,
            });
            console.log(`   ${p.label}: saved!`);
          } catch (err) {
            console.log(`   ${p.label}: failed to save (${err.message})`);
          }
        } else {
          console.log(`   ${p.label}: skipped`);
        }
      }
    }

    console.log("");

    // Step 3: Budget
    console.log("3. Monthly Budget Cap");
    const budgetInput = await prompt(
      rl,
      "   Budget in USD (Enter to skip): $"
    );
    if (budgetInput) {
      const val = parseFloat(budgetInput);
      if (!isNaN(val) && val > 0) {
        try {
          await apiCall(apiKey, "POST", "/settings", { budgetLimitUsd: val });
          console.log(`   Budget set to $${val.toFixed(2)}`);
        } catch (err) {
          console.log(`   Failed to set budget: ${err.message}`);
        }
      } else {
        console.log("   Invalid value, skipped");
      }
    } else {
      console.log("   Skipped");
    }

    console.log("");

    // Step 4: Slack
    console.log("4. Slack Notifications");
    console.log("   Get a webhook URL from https://api.slack.com/apps");
    const slackUrl = await prompt(
      rl,
      "   Slack webhook URL (Enter to skip): "
    );
    if (slackUrl) {
      if (slackUrl.startsWith("https://hooks.slack.com/")) {
        try {
          await apiCall(apiKey, "POST", "/settings", {
            slackWebhookUrl: slackUrl,
          });
          console.log("   Slack notifications enabled!");
        } catch (err) {
          console.log(`   Failed: ${err.message}`);
        }
      } else {
        console.log("   Invalid URL (must start with https://hooks.slack.com/)");
      }
    } else {
      console.log("   Skipped");
    }

    // Summary
    console.log("");
    console.log("=".repeat(35));
    console.log("Setup complete!");
    console.log("");
    if (!process.env.REIVO_API_KEY) {
      console.log("Set this environment variable to use Reivo:");
      console.log("");
      console.log(`  export REIVO_API_KEY="${apiKey}"`);
      console.log("");
      console.log(
        "Add it to your shell profile (~/.zshrc, ~/.bashrc) to persist."
      );
      console.log("");
    }
    console.log('Run "/reivo status" to verify connectivity.');
    console.log('Run "/reivo month" to see your cost summary.');
    console.log("");
    console.log("Dashboard: https://app.reivo.dev");
  } finally {
    rl.close();
  }
}

main();
