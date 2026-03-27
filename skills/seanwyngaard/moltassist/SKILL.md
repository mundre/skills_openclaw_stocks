---
name: moltassist
description: "Unified event-driven notification backbone for OpenClaw. Handles routing, formatting, quiet hours, rate limiting, and optional LLM enrichment across Telegram, WhatsApp, and Discord. Use when: (1) a skill needs to fire a notification to the user, (2) checking notification status or logs, (3) configuring notification routing/categories. NOT for: direct channel messaging without the notification pipeline."
homepage: https://github.com/seanwyngaard/moltassist
metadata: { "openclaw": { "emoji": "bell", "description_long": "Unified event-driven notification backbone for OpenClaw. Handles routing, formatting, quiet hours, rate limiting, and optional LLM enrichment. Installs a scheduler (launchd/cron) for background polling. Includes an opt-in localhost-only dashboard on port 7430. Delegates all message delivery to OpenClaw's existing channel credentials -- no tokens stored.", "requires": { "bins": ["moltassist", "openclaw"], "python": ">=3.10", "openclaw": ">=2026.1.8" }, "permissions": { "channels": "read", "scheduler": "install", "network": "localhost", "filesystem": "write" }, "install": [{ "id": "uv", "kind": "uv", "package": "git+https://github.com/seanwyngaard/moltassist.git@v1.0.59", "bins": ["moltassist"], "label": "Install MoltAssist (uv)" }] } }
---

# MoltAssist -- Skill Interface

MoltAssist is OpenClaw's shared notification layer. Skills call `notify()` to send alerts -- MoltAssist handles routing, formatting, dedup, quiet hours, rate limiting, and optional LLM enrichment.

**MoltAssist is a notification backbone.** It receives events from other skills and delivers them via your configured channel. It can also run background pollers via an opt-in scheduler (launchd/cron) -- scheduler installation is always a manual, user-initiated step.

## Security & Permissions

- **No credentials stored.** Delivery uses `openclaw message send` -- MoltAssist delegates entirely to OpenClaw's existing channel credentials. It never reads, stores, or handles API tokens or bot tokens.
- **Local web server is opt-in, localhost-only.** The `/moltassist config` command starts a plain HTTP server on `127.0.0.1:7430` on demand. It is not accessible outside your machine. It auto-closes after 30 minutes. It only reads and writes `moltassist/config.json`.
- **File writes are scoped to OPENCLAW_WORKSPACE.** All files written by MoltAssist are under `~/.openclaw/workspace/moltassist/` (config, logs, queue, custom pollers) or `~/.openclaw/workspace/memory/` (scheduler state, poll log). Nothing is written outside the OpenClaw workspace.
- **No network calls except through OpenClaw.** The only outbound calls MoltAssist makes are: (1) `openclaw message send` for delivery, (2) `openclaw agent --local` for LLM enrichment (optional, uses your existing model). No data is sent to any MoltAssist server -- there is no MoltAssist server.
- **Reads OpenClaw channel config** via `openclaw channels list --json` to detect available delivery channels during onboarding.
- **Scheduler jobs are user-initiated** via `/moltassist scheduler install`. Installs a launchd plist (macOS) or cron job (Linux) for background polling.
- **All files written under `OPENCLAW_WORKSPACE/moltassist/`** -- config, logs, queue, custom pollers, and scheduler state.

---

## Agent Instructions -- How to Handle Slash Commands

**These instructions are for the AI agent.** When a user sends a slash command (e.g. `/moltassist onboard`), the agent handles the flow entirely. Some steps run CLI commands (e.g. `openclaw channels list`, `moltassist config &`) and some steps involve in-chat interaction. The `moltassist` CLI handles role detection, suggestion generation, and config writing.

### [!] CLI Invocation -- Critical

**Always call `moltassist <command>` directly.** Do not use `python3 -m moltassist`. The binary is installed at `~/.local/bin/moltassist` via `uv tool install` and is always on PATH.

```bash
# [ok] Correct
moltassist config &
moltassist status
moltassist scheduler install

# Wrong -- will fail
python3 -m moltassist config &
```

### Channel Awareness -- Read This First

The agent should detect the current channel and adapt accordingly:

| Channel | Buttons? | Format |
|---------|----------|--------|
| Telegram | Yes -- use `message` tool with `buttons=[[...]]` | MarkdownV2 or plain |
| WhatsApp | No buttons -- use numbered list | Plain text, no markdown |
| iMessage | No buttons -- use numbered list | Plain text |
| Slack | Yes -- use interactive blocks if available | Markdown |
| Discord | Yes -- use components/buttons | Markdown |
| SMS / Signal | No buttons -- use numbered list | Plain text |
| Unknown / fallback | Assume no buttons -- use numbered list | Plain text |

**Telegram-specific:** For buttons, send a single row per choice group using the `message` tool's `buttons` parameter: `[[{text, callback_data}]]`. Never ask the user to type a number if buttons are available on their channel.

**WhatsApp / iMessage / plain-text channels:** Present options as a numbered list. Accept the user's reply as a number or the full option name.

---

### /moltassist onboard

Browser-first onboarding. The onboarding flow runs in the browser dashboard -- the agent opens the browser and waits for the user to complete it there.

> Open `http://localhost:7430` in the browser to start onboarding.
> Note: `moltassist onboard` from the CLI is a terminal fallback only and does not start the browser server.
> The correct sequence is: start the server (`moltassist config &`), then open the browser (`open http://localhost:7430`).

#### Step 0 -- Check existing config

Check if `~/.openclaw/workspace/moltassist/config.json` exists.

- If config exists: respond with "MoltAssist is already configured. Re-run to overwrite, or use `/moltassist config` to adjust." Add a confirm button on Telegram (`[Yes, reset] [Cancel]`), or ask yes/no on plain-text channels. If user cancels, stop. If confirmed, proceed.
- If no config: proceed immediately to Step 1.

#### Step 1 -- Auto-detect channel & start server

1. **Auto-detect channel:** The user is already talking to the agent on a channel -- use THAT channel. The channel name and chat ID are available in the inbound message metadata (trusted context injected by OpenClaw). Use those directly. Run `openclaw channels list --json` only if the inbound metadata is unavailable.

2. **Kill any existing MoltAssist server on port 7430** (do this first to avoid "Address already in use"):
```bash
ps aux | grep 'moltassist' | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null; sleep 1
```

3. **Start the MoltAssist server in the background:**
```bash
moltassist config &
sleep 2
```
Wait 2 seconds, then verify it's up: `curl -s http://localhost:7430/ | head -1`. If no response, report the error to the user and stop.

4. **Open the onboard page in the browser -- always the root `/`, not `/onboard`:**
```bash
open http://localhost:7430
```
> Note: `http://localhost:7430` is the onboarding root. Dashboard is at `http://localhost:7430/dashboard`.

5. **Send ONE message to the user -- nothing else:**
> "Opening your MoltAssist setup page... Complete it in your browser, then come back and type **done**."

That's it. Do not ask "What do you do for work?" or any other question. The browser page handles role detection, category selection, quiet hours -- everything.

#### Step 2 -- Wait for "done"

Wait for the user to reply "done" (or "confirmed", "ready", anything affirmative). Do not prompt, nag, or ask follow-up questions while waiting.

#### Step 3 -- Write config & install scheduler

Once the user says "done":

1. Get the `channel` and `chat_id` from the inbound message trusted metadata (e.g. `telegram` and the sender's chat ID).
2. Run:
```bash
moltassist _write-config --channel "<channel>" --chat-id "<chat_id>"
moltassist scheduler install
```

The role and category selections were already saved by the browser dashboard's Confirm button. `_write-config` finalises the channel/chat-id binding. The scheduler install sets up launchd (macOS) or cron (Linux).

#### Step 4 -- Send summary

Send a single summary message:
```
[ok] MoltAssist is set up!

Notifications -> [Channel]
Categories: [list of enabled ones]
Quiet hours: [start]-[end]
Scheduler: installed

Run /moltassist config to fine-tune anytime.
```

On Telegram, add a single button: `[Open dashboard]` with callback `moltassist config`.

#### What the browser page does (so you don't have to)

The onboard page at `http://localhost:7430` handles the full flow:
1. Asks "What do you do for work?" (free text input)
2. Submits role text to `/api/onboard/role` -> gets back suggested notifications
3. Shows category toggles grouped by priority (high/medium/low)
4. Shows quiet hours config (enable/disable, start time, end time)
5. Has a "Confirm & Save" button that POSTs to `/onboard/confirm`
6. Shows a success screen telling the user to go back to chat

#### Edge cases

- **Port 7430 in use:** Kill existing process first (see Step 1.2 above). Use `ps aux | grep moltassist | grep -v grep` to find and kill it. Do not use `lsof` -- it may not be available.
- **User is on mobile with no browser:** Skip the browser step. Run `moltassist _write-config --channel "<channel>" --chat-id "<chat_id>"` with defaults, install scheduler, and tell them to use `/moltassist config` later to fine-tune.
- **`openclaw channels list` fails:** Use the channel and chat ID from the inbound message metadata -- the agent always has this from OpenClaw's trusted context.

---

### /moltassist config

Kill any existing server on port 7430, then start the dashboard:

```bash
ps aux | grep 'moltassist' | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null; sleep 1
moltassist config &
sleep 2
open http://localhost:7430/dashboard
```

Then send the user: "Dashboard running at http://localhost:7430/dashboard -- open it in your browser. Closes automatically after 30 min."

On Telegram, add a button: `[Open dashboard]` linking to `http://localhost:7430/dashboard`.

**Edge cases:**
- If not yet onboarded: responds with "Run /moltassist onboard first to generate your config."

---

### /moltassist status

Run: `moltassist status` and relay the output to the user. Format for the channel (plain text on WhatsApp/iMessage, formatted on Telegram/Discord).

---

### /moltassist log [category|urgency]

Run: `moltassist log [args]` and relay output. Example: `/moltassist log email` -> `moltassist log email`.

---

### /moltassist snooze [category] [duration]

Run: `moltassist snooze <category> <duration>` and relay output.

Duration format: `30m`, `1h`, `2h`, `4h`, `8h`, `12h`, `24h`, or `off` to cancel.

Example: `/moltassist snooze email 2h` -> `moltassist snooze email 2h`

---

### /moltassist test

Run: `moltassist test` and relay the result. A test notification will arrive on the configured channel.

---

### /moltassist scheduler install / uninstall / status

Run: `moltassist scheduler <install|uninstall|status>` and relay output.

---

### /moltassist poll now [category]

Run: `moltassist poll now <category>` and relay output. Runs the named poller immediately.

---

### /moltassist reload

Run: `moltassist reload` and relay output.

---

## Python Interface -- notify()

The `notify()` function is the single entry point for all skill integrations.

### Import Pattern (with graceful fallback)

```python
try:
 from moltassist import notify
 MOLTASSIST = True
except ImportError:
 MOLTASSIST = False

if MOLTASSIST:
 notify(message="...", urgency="medium", category="email")
```

Skills must always work without MoltAssist installed.

### Function Signature

```python
def notify(
 message: str,
 urgency: str = "medium", # "low" | "medium" | "high" | "critical"
 category: str = "custom",
 source: str = "unknown",
 action_hint: str | None = None,
 llm_hint: bool = False,
 event_id: str | None = None,
 dry_run: bool = False,
) -> dict
```

### Return Value

```python
{
 "sent": bool,
 "channel": str | None,
 "queued": bool,
 "dry_run": bool,
 "error": str | None,
}
```

### Pipeline (every notify() call)

1. Config check -- category enabled, urgency threshold met
2. Lockfile -- single instance guard
3. Quiet hours -- queue if inside window (unless critical)
4. Rate limit -- per-category-per-hour cap
5. Dedup -- same event_id never sent twice
6. LLM enrichment -- optional, 10s timeout, fallback to raw message
7. Channel router -- pick channel by urgency routing config
8. Formatter -- Telegram MarkdownV2, WhatsApp plain text
9. Deliver -- via `openclaw message send`, return code verified
10. Failure handling -- log error, clear queue on permanent failure
11. Log -- write to `moltassist/memory/moltassist-log.json`

---

## Example Integrations

### Email alert

```python
try:
 from moltassist import notify
 MOLTASSIST = True
except ImportError:
 MOLTASSIST = False

def on_important_email(sender, subject, last_contact_days):
 msg = f"{sender} emailed: {subject}"
 if last_contact_days and last_contact_days > 30:
 msg += f" -- last contact {last_contact_days} days ago"
 if MOLTASSIST:
 notify(
 message=msg,
 urgency="high",
 category="email",
 source="gog",
 action_hint="Reply now",
 llm_hint=True,
 event_id=f"email_{sender}_{subject[:20]}",
 )
```

---

## Categories

| Category | Emoji | Required Skill | Built-in |
|----------|-------|----------------|----------|
| email | | gog | no |
| calendar | | gog | no |
| health | | health | no |
| weather | | weather | no |
| dev | | github | no |
| finance | | -- | partial |
| compliance | | -- | yes |
| travel | | -- | no |
| staff | | -- | yes |
| social | | -- | yes |
| system | | -- | yes |
| custom | | -- | yes |

## Urgency Levels

| Level | Meaning | Quiet Hours | Rate Limited |
|-------|---------|-------------|-------------|
| low | FYI -- weather, minor updates | Queued | Yes |
| medium | Default -- most alerts | Queued | Yes |
| high | Important -- needs attention | Queued | Yes |
| critical | Emergency -- always fires | Bypasses | Yes |
