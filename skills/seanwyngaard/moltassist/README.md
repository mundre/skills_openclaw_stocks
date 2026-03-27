# MoltAssist

**Tell it what you do. It figures out what to watch.**

OpenClaw waits to be asked. MoltAssist is the other half — it watches your world in the background and reaches out the moment something needs your attention. An overdue invoice, a Linear ticket sitting unreviewed, an F1 race about to start, a PR open for 48 hours, a Slack mention you missed. It finds you on whatever channel you already use, before you even know to ask.

The part that makes it different: **you don't configure it upfront.**

Run `/moltassist onboard`. Tell it what you do in a few sentences. It analyses your role, generates 20–30 notification suggestions tailored to what you said, asks you a few follow-up questions about the tools you use, and presents everything in a clean browser UI for you to confirm. Most setups take under 10 minutes.

No dashboards to check. No feeds to refresh. **It comes to you.**

---

## Install

```bash
clawhub install moltassist
```

Then message your OpenClaw agent:

```
/moltassist onboard
```

**Requirements:**
- [OpenClaw](https://openclaw.ai) v2026.1.8 or later
- Python 3.10+
- At least one channel configured (Telegram, WhatsApp, or Discord)

---

## How onboarding works

### Step 1 — Tell it about yourself

A browser page opens. Type freely — your job, side projects, hobbies, tools you use, things you want to stay on top of. The more context, the better the suggestions.

### Step 2 — Answer a few follow-up questions

Based on what you wrote, MoltAssist asks targeted questions: what issue tracker do you use, which gaming platforms, which social platforms, what calendar tool. These shape which skills get assigned to each notification.

The questions support multi-select — if you use both Slack and Discord, pick both. MoltAssist maps each answer to the correct skill.

### Step 3 — Review your personalised suggestions

A list of 20–30 notification ideas, grouped by priority (High / Medium / Low), pre-checked on the most relevant ones. Each suggestion shows:

- What it watches and when it fires
- Which skill powers it (e.g. `linear`, `gog`, `github`, `slack`)
- Whether that skill is installed
- If no skill exists: **⚒ build needed** — meaning you can ask your OpenClaw agent to build a custom poller

Uncheck anything you don't want. Confirm.

### Step 4 — Done

Come back to your chat and type `done`. MoltAssist finalises your config, installs the scheduler, and starts watching.

---

## The dashboard

`/moltassist config` opens a settings page at `http://localhost:7430`.

It's personalised to you — built from your onboarding data, not a generic template:

- **Your Notifications** — every notification you selected, with its description, on/off toggle, priority, and skill badges. Skill chips show green (installed) or red (missing) based on what's actually installed on your machine.
- **Your role and context** — your actual words from onboarding, your follow-up answers, displayed at the top so you know exactly what the system was configured from.
- **Category Settings** — only shows categories where you have the required skill installed. No dead toggles. Locked categories are collapsed under "Get more categories" with the exact `clawhub install` command to unlock each.
- **Delivery** — channels, urgency routing. Fully dynamic — only shows channels you actually have configured.
- **Schedule** — quiet hours, timezone, morning digest, rate limits.
- **Update My Notifications** — two options:
  - *Add to my notifications*: describe what's changed (new job, new tool, new hobby) and regenerate additively on top of what you have
  - *Reset onboarding*: start completely fresh while preserving delivery settings

Closes automatically after 30 minutes of inactivity.

---

## What it looks like in practice

> **Sprint at risk — morning check**
> *1 of 4 tickets shipping Friday. Auth module is the blocker — no activity in 2 days.*
>
> Skill: `github` or `linear`

---

> **Invoice overdue**
> *Invoice #089 overdue 47 days — $12,000. Client: Meridian Group.*
>
> Skill: `gog` (Gmail scan for payment confirmations)

---

> **Race weekend starting soon**
> *F1 qualifying starts in 30 minutes — get settled.*
>
> Skill: `gog` (calendar feed subscription)

---

> **PR waiting for review 24h**
> *Pull request open on your repo with no review activity for more than 24 hours.*
>
> Skill: `github`

---

> **Breaking news — no skill yet**
> *Major announcement posted for a game/product you're following.*
>
> Skill: ⚒ build needed (requires a custom RSS/web watcher — ask your OpenClaw agent to build one)

---

> **Client gone quiet**
> *No reply from a key client in 5 days.*
>
> Skill: `gog` (Gmail)

---

## Skill assignment logic

MoltAssist uses a three-layer approach to assign the right skill to each notification:

1. **AI reasoning** — the AI is instructed to think through *where the data actually comes from* before assigning a skill. It has a known skills list and explicit rules: `gog` is Gmail + Google Calendar only, `linear` is Linear only, `github` is GitHub only, `slack` is Slack only, and so on.

2. **Answer overrides** — your follow-up answers (what issue tracker, what gaming platform, etc.) are applied as direct overrides. If you said "Linear", Linear-related suggestions get `linear`. If you said "Slack + Discord", both skills are assigned.

3. **Text-based safety net** — a post-processing pass scans every suggestion's title and description. If "Linear" appears in the text, it gets `linear`. If "Slack" appears, it gets `slack`. This catches any AI errors regardless of what the AI decided.

For anything that requires web scraping, RSS feeds, Reddit monitoring, social platform watching, or any API without a known skill: `__build_needed__` is set and shown clearly in the UI.

---

## Who uses it

| Who | What they get notified about |
|---|---|
| **Developer / QA** | Linear tickets, GitHub PRs, CI failures, daily run-through prompts |
| **Freelancer** | Overdue invoices, client gone quiet, contract renewals, tax deadlines |
| **Gamer** | Game release date reminders, breaking news (build needed), platform sales |
| **Sports fan** | Race/match start times, qualifying sessions, fixture reminders (Google Calendar integration) |
| **Community manager** | Slack mentions, Discord alerts, review monitoring |
| **Traveller** | Flight confirmations, travel advisories, passport expiry |
| **Restaurant owner** | Staff no-shows, licence renewals, negative reviews |
| **Anyone** | Morning email digest, calendar conflicts, quiet hours, rate limiting |

*...and so much more. If you can describe what you do, MoltAssist can figure out what to watch.*

---

## Security & permissions

- **No credentials stored.** All delivery goes through `openclaw message send` — MoltAssist delegates entirely to OpenClaw's existing channel credentials. It never touches API tokens or bot tokens.
- **Local web server is opt-in, localhost-only.** The dashboard runs on `127.0.0.1:7430` on demand, is not externally accessible, and shuts down after 30 minutes.
- **File writes are scoped to `OPENCLAW_WORKSPACE/moltassist/`.** Config, logs, queue, and scheduler state all live here. Nothing is written outside the OpenClaw workspace.
- **No network calls except through OpenClaw.** The only outbound calls: (1) `openclaw message send` for delivery, (2) `openclaw agent` for optional AI enrichment. No data is ever sent to any MoltAssist server — there is no MoltAssist server.
- **Scheduler is user-initiated.** Background polling is installed only when you confirm during onboarding. It runs via launchd (macOS) or cron (Linux).

---

## Slash commands

| Command | What it does |
|---|---|
| `/moltassist onboard` | Run onboarding (prompts to reset if already configured) |
| `/moltassist config` | Open settings dashboard (localhost:7430) |
| `/moltassist status` | Enabled categories, connected skills, AI mode |
| `/moltassist test` | Fire a test notification |
| `/moltassist log` | Last 24h of alerts |
| `/moltassist log [category]` | Filter by category |
| `/moltassist snooze [category] [duration]` | Snooze a category (e.g. `email 2h`) |
| `/moltassist scheduler status` | Installed/not, last run per category |
| `/moltassist poll now [category]` | Run a poller immediately |
| `/moltassist uninstall` | Remove scheduler, workspace files, and print removal steps |

---

## Plugging in from a skill

```python
try:
    from moltassist import notify
    MOLTASSIST = True
except ImportError:
    MOLTASSIST = False

if MOLTASSIST:
    notify(
        message="Invoice #089 overdue 47 days — $12,000",
        urgency="high",
        category="finance",
        source="xero_skill",
        action_hint="Follow up with Meridian",
        llm_hint=True,
    )
```

Skills degrade gracefully when MoltAssist isn't installed.

## Urgency levels

| Level | Behaviour |
|---|---|
| `low` | Queued during quiet hours, included in morning digest |
| `medium` | Fires immediately during active hours |
| `high` | Time-sensitive, fires immediately |
| `critical` | Always fires, ignores quiet hours |

---

## Uninstalling

```
/moltassist uninstall
```

Or manually:

```bash
moltassist uninstall          # removes scheduler + workspace files
uv tool uninstall moltassist  # removes the binary
clawhub uninstall moltassist  # removes the skill
```

MoltAssist does not modify your OpenClaw config, channel setup, or any existing skill. Everything it creates is isolated to `~/.openclaw/workspace/moltassist/`.

---

## Contributing

**New role profile:** Add one JSON entry to `data/role_profiles.json` — no code changes needed.

**New channel:** Implement `deliver_<channel>()` in `moltassist/channels.py`.

**New built-in poller:** Implement `poll_<category>(config: dict)` in `moltassist/poll.py` and add a schedule entry to `config.py`.

---

## Licence

MIT-0

---

*Built with [OpenClaw](https://openclaw.ai). Designed and coded with Claude Sonnet and Opus by [@seanwyngaard](https://github.com/seanwyngaard).*
