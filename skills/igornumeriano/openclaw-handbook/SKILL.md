---
name: OpenClaw Documentation Expert
description: The clawddocs replacement. Fetches live from docs.openclaw.ai — never stale, no fake shell scripts. Three-tier strategy (llms.txt index → page.md → llms-full.txt), 395 pages, decision tree routing, SOUL/multi-agent/sessions covered.
version: 1.2.0
metadata:
  openclaw:
    requires:
      bins:
        - curl
    emoji: "🦞"
    homepage: https://docs.openclaw.ai
---

# OpenClaw Documentation Expert

**The only OpenClaw docs skill that fetches before it answers.**

395 pages. 26 categories. One decision tree that routes any question to the exact right page in seconds. Built from the official OpenClaw documentation endpoints — not cached guesses from a model trained on old Clawdbot docs.

> clawddocs hasn't been updated since Jan 2026, its scripts are echo placeholders, and users are asking for it to be deleted. This fetches live — it's always current.

---

## Three-Tier Fetch Strategy

Use the right tool for each job:

### Tier 1 — Index (`llms.txt`)
Compact list of every page with human-readable titles and exact `.md` URLs. Use this when you need to **discover** what pages exist or find the right page name.

```bash
curl -sL https://docs.openclaw.ai/llms.txt
```

Output format: `- [Page Title](https://docs.openclaw.ai/<category>/<page>.md)`

### Tier 2 — Single page (`.md`)
Fetch one page's full content. Use this for **specific answers**. Always append `.md` to the URL.

```bash
curl -sL https://docs.openclaw.ai/concepts/soul.md
curl -sL https://docs.openclaw.ai/concepts/multi-agent.md
curl -sL https://docs.openclaw.ai/channels/telegram.md
# Pattern: https://docs.openclaw.ai/<category>/<page>.md
```

### Tier 3 — Full text (`llms-full.txt`)
All 395 pages concatenated. Use only when you need to **search across** the entire documentation or the question spans multiple sections.

```bash
curl -sL https://docs.openclaw.ai/llms-full.txt | grep -A 20 "keyword"
```

**Default workflow:** Decision Tree → Tier 2 fetch → answer with source URL.
Use Tier 1 when unsure which page to fetch. Use Tier 3 only as a last resort.

---

## Decision Tree

Route every query here first. Then fetch only the relevant page (Tier 2).

```
Is the question about...

IDENTITY / PERSONALITY
  └─ SOUL.md, tone, agent voice          → concepts/soul.md

MULTI-AGENT / AGENT ISOLATION
  └─ Multiple agents, routing, workspaces → concepts/multi-agent.md
  └─ Delegate architecture               → concepts/delegate-architecture.md

MEMORY
  └─ How memory works (general)          → concepts/memory.md
  └─ Built-in memory                     → concepts/memory-builtin.md
  └─ QMD (vector search)                 → concepts/memory-qmd.md
  └─ Honcho (external memory)            → concepts/memory-honcho.md
  └─ Search memory                       → concepts/memory-search.md
  └─ Active memory                       → concepts/active-memory.md
  └─ Dreaming / consolidation            → concepts/dreaming.md

SESSIONS
  └─ Session model, history              → concepts/session.md
  └─ Session pruning                     → concepts/session-pruning.md
  └─ Session tool                        → concepts/session-tool.md
  └─ Context / compaction                → concepts/context.md, concepts/compaction.md

AGENT LOOP / RUNTIME
  └─ How the agent loop works            → concepts/agent-loop.md
  └─ Agent runtime                       → concepts/agent.md
  └─ Agent workspace (AGENTS.md etc)     → concepts/agent-workspace.md
  └─ System prompt structure             → concepts/system-prompt.md

GATEWAY
  └─ Start, stop, config                 → gateway/index.md
  └─ Sandboxing                          → gateway/sandboxing.md

AUTOMATION / CRON
  └─ Scheduled tasks, cron syntax        → automation/cron-jobs.md
  └─ Hooks                               → automation/hooks.md
  └─ Standing orders                     → automation/standing-orders.md
  └─ Task flow                           → automation/taskflow.md
  └─ Background tasks                    → automation/tasks.md

CHANNELS (messaging platforms)
  └─ Telegram                            → channels/telegram.md
  └─ Discord                             → channels/discord.md
  └─ WhatsApp                            → channels/whatsapp.md
  └─ Slack                               → channels/slack.md
  └─ iMessage (BlueBubbles)              → channels/bluebubbles.md
  └─ Signal                              → channels/signal.md
  └─ Matrix                              → channels/matrix.md
  └─ Microsoft Teams                     → channels/msteams.md
  └─ IRC, LINE, Nostr, Twitch, Zalo...   → channels/<name>.md
  └─ Channel routing                     → channels/channel-routing.md
  └─ Pairing / allowlist                 → channels/pairing.md
  └─ Groups                              → channels/groups.md
  └─ Troubleshooting                     → channels/troubleshooting.md

TOOLS
  └─ Skills (create, install, share)     → tools/skills.md
  └─ All tools overview                  → tools/index.md

PROVIDERS (AI models)
  └─ Anthropic, OpenAI, Gemini, etc      → providers/<name>.md

CLI REFERENCE
  └─ Any CLI command                     → cli/<command>.md
  └─ Full CLI index                      → cli/index.md

INSTALL / SETUP
  └─ Quick start                         → start/index.md
  └─ VPS setup                           → vps/index.md
  └─ Raspberry Pi                        → pi/index.md
  └─ Ansible                             → install/ansible.md
  └─ Platforms / Docker                  → platforms/index.md

PLUGINS
  └─ Install, write plugins              → plugins/index.md

DEBUGGING / TROUBLESHOOTING
  └─ Diagnostics                         → diagnostics/index.md
  └─ Logging                             → logging/index.md
  └─ Network issues                      → network/index.md
  └─ Channel issues                      → channels/troubleshooting.md

SECURITY / AUTH
  └─ Auth credential semantics           → auth-credential-semantics.md
  └─ OAuth                               → concepts/oauth.md
  └─ Security                            → security/index.md

WEB / API
  └─ Web interface                       → web/index.md
  └─ OpenAPI spec                        → api-reference/openapi.json

NODES
  └─ Node system                         → nodes/index.md
```

---

## Key Concepts Cheat Sheet

Commonly needed facts — always verify with a Tier 2 fetch before citing in critical answers.

### SOUL.md
- Injected at the **start of every session** (system prompt layer)
- Controls: tone, opinions, brevity, humor, boundaries
- Keep **short and sharp** — long SOUL files dilute effect
- Does NOT belong: life story, changelogs, security policies
- File path: `<workspace>/SOUL.md`
- Full guide: `curl -sL https://docs.openclaw.ai/concepts/soul.md`

### AGENTS.md
- Operational manual — tools, workspace layout, channel usage
- Read on startup alongside SOUL.md
- File path: `<workspace>/AGENTS.md`

### Multi-agent
- Each agent = isolated brain: own workspace + `agentDir` + sessions
- Sessions keyed as `agent:<agentId>:<sessionKey>`
- Default: `agentId = main`, sessions at `~/.openclaw/agents/main/sessions`
- Add agents: `openclaw agents add <id>`
- Never reuse `agentDir` across agents (causes auth/session collision)
- Skills: shared via `~/.openclaw/skills` + per-agent overrides
- Full guide: `curl -sL https://docs.openclaw.ai/concepts/multi-agent.md`

### Session
- Persistent conversation history (JSONL on disk, survives restarts)
- Search history: `sessions_history` tool (sanitized view — strips tool call XML, thinking tags)
- Full guide: `curl -sL https://docs.openclaw.ai/concepts/session.md`

### Memory
- **Active memory**: in-context, fastest
- **QMD**: vector search over past sessions
- **Dreaming**: async consolidation of history into memory
- **Honcho**: external memory service
- Full guide: `curl -sL https://docs.openclaw.ai/concepts/memory.md`

### Skills
- Path: `~/.openclaw/skills/<name>/SKILL.md`
- Shared baseline: `agents.defaults.skills`
- Per-agent override: `agents.list[].skills`
- Full guide: `curl -sL https://docs.openclaw.ai/tools/skills.md`

### Heartbeat / Cron
- `openclaw cron add --name X --cron "*/15 * * * *" --session isolated --message "..."`
- `isolated` = one-shot session, terminates after response (cost-efficient)
- `main` = resumes persistent conversation
- Full guide: `curl -sL https://docs.openclaw.ai/automation/cron-jobs.md`

---

## How to Use This Skill

1. **Identify** the topic → use the Decision Tree
2. **Fetch** the page → `curl -sL https://docs.openclaw.ai/<category>/<page>.md`
3. **Answer** citing the source URL
4. **If unsure which page:** fetch the index → `curl -sL https://docs.openclaw.ai/llms.txt` and grep for keywords
5. **If spanning multiple sections:** `curl -sL https://docs.openclaw.ai/llms-full.txt | grep -A 30 "keyword"`

**Never answer OpenClaw questions from memory alone.** Fetch first, then answer.

**Naming note:** OpenClaw was previously called Clawdbot. Docs: `docs.openclaw.ai` (not `docs.clawd.bot`). CLI: `openclaw` (not `clawdbot`).
