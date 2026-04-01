---
name: agentgo-stealth-browser
description: >
  Automate websites using AgentGo’s cloud browser cluster via Playwright
  (pinned to playwright@1.51.0), with stealth-friendly configuration intended
  to reduce automation detection. Use for navigation, form filling,
  screenshots, testing flows, and data extraction on remote Chromium instead of
  a local browser. Requires AGENTGO_API_KEY.
homepage: https://app.agentgo.live/
metadata:
  openclaw:
    emoji: "🧭"
    os: ["darwin", "linux", "win32"]
    requires:
      env: ["AGENTGO_API_KEY"]
      notes: "Playwright must be exactly playwright@1.51.0 (protocol compatibility)"
---

# AgentGo Stealth Browser: Cloud Playwright Automation

AgentGo provides a distributed **cloud browser cluster**. You connect via WebSocket using `chromium.connect()` from **`playwright@1.51.0`**.

> “Stealth” refers to configuration intended to reduce automation detection. Results depend on the target site and cannot be guaranteed.

> Important: **Pin Playwright to `1.51.0`**. Newer versions may be protocol-incompatible with AgentGo’s server.

## When to use / When not to use

**Use this skill when you want:**
- A **remote** browser (cloud) instead of running Chromium locally
- Reliable automation for **navigation**, **form filling**, **screenshots**, **testing**, **scraping/extraction**
- Parallel multi-page workflows

**Don’t use this skill when:**
- A simple HTTP fetch is enough (no JS / no interactions)
- You can’t pin Playwright to `1.51.0`

## Prerequisites

- Node.js environment to run Playwright code
- An AgentGo account (free credits available)
- Environment variable: `AGENTGO_API_KEY`

### Get an API key

Register at https://app.agentgo.live/

```bash
export AGENTGO_API_KEY="your_api_key_here"
```

## Install (must pin Playwright)

```bash
npm install playwright@1.51.0
# or
pnpm add playwright@1.51.0

# Optional: for session management
npm install @agentgo-dev/sdk
```

## Minimal example (open → screenshot → save)

This saves a full-page screenshot to `example.png` in your current working directory.

```typescript
import { chromium } from "playwright"; // must be playwright@1.51.0

const options = { _apikey: process.env.AGENTGO_API_KEY };
const serverUrl = `wss://app.browsers.live?launch-options=${encodeURIComponent(
  JSON.stringify(options)
)}`;

const browser = await chromium.connect(serverUrl);
try {
  const page = await browser.newPage();
  await page.goto("https://example.com", { waitUntil: "domcontentloaded" });
  await page.screenshot({ path: "example.png", fullPage: true });
} finally {
  await browser.close();
}
```

## Quick start

```typescript
import { chromium } from "playwright"; // must be playwright@1.51.0

const options = { _apikey: process.env.AGENTGO_API_KEY };
const serverUrl = `wss://app.browsers.live?launch-options=${encodeURIComponent(
  JSON.stringify(options)
)}`;

const browser = await chromium.connect(serverUrl);
try {
  const page = await browser.newPage();

  await page.goto("https://example.com");
  console.log(await page.title());
} finally {
  await browser.close();
}
```

## Browser sessions (recommended)

If you need better control over lifecycle, concurrency, or reuse, use **AgentGo browser sessions**.

Docs:
- Create a browser session: https://docs.agentgo.live/fundamentals/create-browser-session
- Using a browser session: https://docs.agentgo.live/fundamentals/using-browser-session

Typical flow:
1) Create a browser session using the official SDK (`@agentgo-dev/sdk`)
2) The SDK returns a `connectionUrl` (WebSocket)
3) Connect with Playwright using that URL
4) Run automation, then close the browser to end the session

Session connect example using the SDK:

```typescript
import { AgentGo } from "@agentgo-dev/sdk";
import { chromium } from "playwright"; // must be playwright@1.51.0

const client = new AgentGo({ apiKey: process.env.AGENTGO_API_KEY! });
const session = await client.sessions.create({ region: "us" });

const browser = await chromium.connect(session.connectionUrl);
try {
  const page = await browser.newPage();
  await page.goto("https://example.com", { waitUntil: "domcontentloaded" });
  await page.screenshot({ path: "session-example.png", fullPage: true });
} finally {
  await browser.close();
}
```

> Note: Session creation/usage details can change on the AgentGo side. Always follow the two official docs above for the latest parameters and lifecycle steps.

## Connection helper (recommended)

> The examples below use this helper. Copy it into your project, or inline the connection logic.

```typescript
import { chromium } from "playwright";

export async function connectAgentGo() {
  if (!process.env.AGENTGO_API_KEY) {
    throw new Error("AGENTGO_API_KEY is not set");
  }
  const opts = encodeURIComponent(
    JSON.stringify({ _apikey: process.env.AGENTGO_API_KEY })
  );
  return chromium.connect(`wss://app.browsers.live?launch-options=${opts}`);
}
```

> Pass `_disable_proxy: true` in launch options to bypass the default proxy. See [session-management.md](references/session-management.md) for all connection options.

## Basic interactions

```typescript
const browser = await connectAgentGo(); // see "Connection helper" section above
const page = await browser.newPage();

await page.goto("https://example.com");
await page.click("button#submit");
await page.fill("input[name=email]", "user@example.com"); // for anti-detection, use keyboard.type() instead — see tips-general.md
await page.press("input[name=email]", "Enter");
await page.screenshot({ path: "screenshot.png" });

await browser.close();
```

## Extract data

```typescript
const browser = await connectAgentGo(); // see "Connection helper" section above
const page = await browser.newPage();
await page.goto("https://news.ycombinator.com");

const items = await page.$$eval(".titleline a", els =>
  els.map(a => ({
    title: a.textContent,
    href: a.href,
  }))
);

await browser.close();
console.log(items);
```

## Multiple pages (parallel)

```typescript
const browser = await connectAgentGo(); // see "Connection helper" section above
const [page1, page2] = await Promise.all([browser.newPage(), browser.newPage()]);

await Promise.all([
  page1.goto("https://site-a.com"),
  page2.goto("https://site-b.com"),
]);

await browser.close();
```

## Always close in finally

```typescript
const browser = await connectAgentGo(); // see "Connection helper" section above
try {
  const page = await browser.newPage();
  await doWork(page);
} finally {
  await browser.close();
}
```

## References (deep dive)

- Connection & auth: [references/connection.md](references/connection.md)
- Session management: [references/session-management.md](references/session-management.md)
- Running Playwright code: [references/running-code.md](references/running-code.md)
- Tips & anti-detection (general): [references/tips-general.md](references/tips-general.md)
- Tips for X (Twitter): [references/tips-x-twitter.md](references/tips-x-twitter.md)
