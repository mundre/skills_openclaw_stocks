---
name: moltassist
description: "MoltAssist watches your world in the background and alerts you when something needs attention: email, calendar, crypto, health, GitHub, weather. Tell it what you do, it figures out what to watch. For anything it cannot monitor yet, it builds a custom poller on the spot. No new accounts. No new subscriptions. Runs inside your existing OpenClaw setup."
homepage: https://github.com/seanwyngaard/moltassist
metadata: { "openclaw": { "emoji": "bell", "requires": { "bins": ["moltassist"], "python": ">=3.10", "openclaw": ">=2026.1.8" }, "install": [{ "id": "uv", "kind": "uv", "package": "git+https://github.com/seanwyngaard/moltassist.git", "bins": ["moltassist"], "label": "Install MoltAssist (uv)" }] } }
---

# MoltAssist

Background notification layer for OpenClaw. Watches email, calendar, crypto, health, GitHub, and weather on a schedule and delivers alerts to your configured channel when something crosses a threshold.

Run `/moltassist onboard` to get started. Tell it what you do. It generates a config for your role and offers to build pollers for anything it cannot already monitor.

**Install:** `clawhub install moltassist`  -  handles everything (Python package installed automatically via uv).

Full docs and source: https://github.com/seanwyngaard/moltassist

---

## What it monitors (built-in, no API keys needed)

- Email: important sender arrived, long silence broken (requires gog skill)
- Calendar: meeting in 9 min, deadline today (requires gog skill)
- Crypto: price move past your threshold, overnight digest (built-in, uses CoinGecko public API)
- Weather: rain before an outdoor event (requires weather skill)
- GitHub: PR unreviewed 24h+, CI failure (requires github skill)

For anything else, onboarding detects the gap and builds a purpose-specific poller using your OpenClaw AI.

Credentials: MoltAssist delegates all delivery to `openclaw message send` using your existing OpenClaw channel config. It does not store or handle API tokens itself. The gog, weather, and github skills handle their own credentials independently.

---

## Slash Commands

- `/moltassist onboard` - Always run the full onboarding flow when asked, even if already configured. Follow this exact sequence:
  1. Channel: Run `moltassist status` to check how many channels are active. If only ONE channel is configured, skip asking - just say "I'll use [channel] for your notifications." If MORE than one, ask which to use with buttons.
  2. Everything else happens in the browser - say: "Open this link to finish setup - pick your role, choose what to watch, and I'll configure everything: http://localhost:7430/onboard" then run `moltassist config` to start the dashboard server. Do NOT ask about role, job, or categories in chat. Stop and wait for the user to confirm they're done in the browser.
  3. After user confirms done: run `moltassist scheduler install`, confirm complete.
- `/moltassist status` - Enabled categories, delivery channel, AI mode
- `/moltassist log` - Last 24h of alerts
- `/moltassist log [category]` - Filter by category (email, crypto, calendar, etc.)
- `/moltassist snooze [category] [duration]` - Silence a category (e.g. crypto 2h)
- `/moltassist test` - Send a test notification to verify delivery
- `/moltassist config` - Open settings dashboard at localhost:7430
- `/moltassist scheduler install` - Install background polling (launchd on macOS, cron on Linux)
- `/moltassist scheduler uninstall` - Remove background polling
- `/moltassist scheduler status` - Check scheduler and last run times
- `/moltassist poll now [category]` - Run a poller immediately

---

## notify() for skill developers

```python
try:
    from moltassist import notify
except ImportError:
    notify = None

if notify:
    notify(
        message="Invoice overdue 47 days - $12,000",
        urgency="high",
        category="finance",
        source="my_skill",
        action_hint="Follow up",
    )
```

Urgency levels: low (queued overnight), medium (default), high (immediate), critical (bypasses quiet hours)

Returns: {"sent": bool, "queued": bool, "error": str | None}
