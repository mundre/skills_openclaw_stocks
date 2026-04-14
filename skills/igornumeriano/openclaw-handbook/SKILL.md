---
name: OpenClaw Documentation Expert — Live Fetch
description: Fetches live from docs.openclaw.ai on every question. 395 pages indexed, working scripts (not echo placeholders), CI-style selftest for decision-tree rot, worked routing examples, SOUL/multi-agent/sessions covered.
version: 1.4.0
metadata:
  openclaw:
    requires:
      bins:
        - curl
    emoji: "🦞"
    homepage: https://docs.openclaw.ai
---

# OpenClaw Documentation Expert — Live Fetch

## Activation

Activate when the user asks about OpenClaw: configuration, concepts, channels, CLI, troubleshooting, multi-agent, SOUL.md, AGENTS.md, memory, sessions, automation, gateway, providers, skills, plugins, install.

Do NOT activate for: general coding questions, non-OpenClaw tools (Claude Code, Codex, OpenCode), or meta-questions about this skill.

## Out-of-Scope Response

If a question is partially about OpenClaw and partially about another tool, answer only the OpenClaw portion and say `not covered here` for the rest. Never extrapolate OpenClaw docs to explain other tools.

## Behavior Contract

For every in-scope question, execute in order:

1. Route the question through the **Decision Tree** below → pick ONE page
2. Fetch that page: `scripts/fetch.sh <path>` (or `curl -sfL https://docs.openclaw.ai/<path>.md`)
3. Answer using only content from the fetched page
4. Cite the source URL at the end of the answer
5. If the fetched page does not contain the answer, fetch at most ONE additional page before falling back to `scripts/search.sh <keyword>`
6. If still not found, respond: `Not documented at docs.openclaw.ai as of <timestamp from verify.sh>`
7. If you had to fall back to `find.sh` or `search.sh`, or if the user corrects your routing, log the miss: `scripts/record_miss.sh "<user question>" "<path you used>"`

**Never answer from memory alone.** Never fabricate a URL path. Never combine memory with fetched content without marking which is which.

## Three-Tier Fetch Strategy

| Tier | Endpoint | When to use |
|---|---|---|
| 1 | `llms.txt` | Discovery — "what page exists for X?" → `scripts/find.sh <keyword>` |
| 2 | `<page>.md` | Specific answer — one page, cited → `scripts/fetch.sh <path>` |
| 3 | `llms-full.txt` | Cross-section search — last resort → `scripts/search.sh <keyword>` |

Always prefer Tier 2. Use Tier 1 only when Decision Tree is ambiguous. Use Tier 3 only when a targeted fetch misses.

## Scripts

All scripts are in `scripts/` and require only `curl`:

- **`find.sh <keyword>`** — list pages whose title matches the keyword (tab-separated: title, path)
- **`fetch.sh <path>`** — fetch one page; accepts `concepts/soul`, `concepts/soul.md`, or `/concepts/soul.md`
- **`search.sh <keyword> [ctx]`** — grep full docs with N lines of context (default 10), capped at 200 lines
- **`verify.sh`** — print page count + sha256 + ISO timestamp of llms.txt (proof of liveness)
- **`selftest.sh`** — HEAD-check every doc path referenced in SKILL.md and EXAMPLES.md; exits non-zero on any 404 so decision-tree rot is caught before publishing
- **`record_miss.sh <question> <path>`** — append a routing miss to `~/.openclaw/openclaw-docs/misses.md` for later review; never edits SKILL.md

These are real working bash scripts, not echo placeholders. Run `scripts/verify.sh` at session start to confirm docs are current. Run `scripts/selftest.sh` before editing the Decision Tree or publishing a new version.

## Decision Tree

All paths below are validated against `llms.txt`. Route first, fetch second.

```
IDENTITY / PERSONALITY
  SOUL.md, tone, agent voice          → concepts/soul.md

MULTI-AGENT
  Multiple agents, workspaces         → concepts/multi-agent.md
  Delegate architecture               → concepts/delegate-architecture.md

AGENT LOOP / RUNTIME
  How the agent loop works            → concepts/agent-loop.md
  Agent runtime                       → concepts/agent.md
  Agent workspace (AGENTS.md)         → concepts/agent-workspace.md
  System prompt structure             → concepts/system-prompt.md

MEMORY
  General                             → concepts/memory.md
  Built-in                            → concepts/memory-builtin.md
  QMD (vector search)                 → concepts/memory-qmd.md
  Honcho (external)                   → concepts/memory-honcho.md
  Search memory                       → concepts/memory-search.md
  Active memory                       → concepts/active-memory.md
  Dreaming / consolidation            → concepts/dreaming.md

SESSIONS
  Model, history                      → concepts/session.md
  Pruning                             → concepts/session-pruning.md
  Session tool                        → concepts/session-tool.md
  Context / compaction                → concepts/context.md, concepts/compaction.md

GATEWAY
  Sandboxing                          → gateway/sandboxing.md
  Logging                             → gateway/logging.md
  Network model                       → gateway/network-model.md
  Security                            → gateway/security/index.md

AUTOMATION
  Cron jobs                           → automation/cron-jobs.md
  Hooks                               → automation/hooks.md
  Standing orders                     → automation/standing-orders.md
  Task flow                           → automation/taskflow.md
  Background tasks                    → automation/tasks.md

CHANNELS
  Telegram                            → channels/telegram.md
  Discord                             → channels/discord.md
  WhatsApp                            → channels/whatsapp.md
  Slack                               → channels/slack.md
  iMessage (BlueBubbles)              → channels/bluebubbles.md
  Signal                              → channels/signal.md
  Matrix                              → channels/matrix.md
  Microsoft Teams                     → channels/msteams.md
  Other (IRC, LINE, Nostr, ...)       → channels/<name>.md
  Channel routing                     → channels/channel-routing.md
  Pairing / allowlist                 → channels/pairing.md
  Groups                              → channels/groups.md
  Troubleshooting                     → channels/troubleshooting.md

TOOLS / SKILLS
  Skills (create, install, share)     → tools/skills.md
  All tools overview                  → tools/index.md

PROVIDERS (AI models)
  Any provider                        → providers/<name>.md

CLI
  Any command                         → cli/<command>.md
  Full reference                      → cli/index.md

INSTALL / SETUP
  Getting started                     → start/getting-started.md
  Bootstrapping                       → start/bootstrapping.md
  Raspberry Pi                        → install/raspberry-pi.md
  Ansible                             → install/ansible.md
  VPS                                 → vps.md
  Pi                                  → pi.md

PLUGINS
  Architecture                        → plugins/architecture.md
  Building                            → plugins/building-plugins.md
  Bundles                             → plugins/bundles.md

DEBUGGING
  Diagnostics flags                   → diagnostics/flags.md
  Logging (root)                      → logging.md
  Network (root)                      → network.md

SECURITY / AUTH
  Auth credential semantics           → auth-credential-semantics.md
  OAuth                               → concepts/oauth.md
  Threat model                        → security/THREAT-MODEL-ATLAS.md

WEB / API
  OpenAPI spec                        → api-reference/openapi.json
```

If no branch matches: `scripts/find.sh <keyword>` → pick the top result → fetch.

## Synonym Map

Common user phrasings → canonical decision-tree branch. Use this before falling back to `find.sh`.

| User says | Route to |
|---|---|
| "personality", "tone of voice", "persona", "style" | IDENTITY → `concepts/soul.md` |
| "operational manual", "workspace rules", "AGENTS.md" | `concepts/agent-workspace.md` |
| "context window", "context limit", "too long" | `concepts/context.md` + `concepts/compaction.md` |
| "history", "chat log", "conversation memory" | SESSIONS → `concepts/session.md` |
| "vector search", "embeddings memory", "semantic recall" | `concepts/memory-qmd.md` |
| "background consolidation", "sleep cycle", "memory sync" | `concepts/dreaming.md` |
| "scheduled task", "recurring job", "crontab" | `automation/cron-jobs.md` |
| "pre/post-tool hook", "lifecycle event" | `automation/hooks.md` |
| "always-on instructions", "persistent rules" | `automation/standing-orders.md` |
| "bot", "messenger", "chat integration" | CHANNELS → `channels/<name>.md` |
| "jail", "isolation", "sandbox" | `gateway/sandboxing.md` |
| "firewall", "egress rules", "allowlist" | `gateway/network-model.md` |
| "skill", "plugin package", "tool bundle" | `tools/skills.md` |
| "LLM provider", "model backend", "Anthropic/OpenAI/etc" | `providers/<name>.md` |

## Worked Examples

See `EXAMPLES.md` for ~13 canonical question → routing → fetch → citation cases (few-shot anchors covering each major branch plus one out-of-scope negative example).

## Evolution Loop

This skill improves from **real friction only**, not from speculation. The loop:

1. **Detect** — you fall back to `find.sh`/`search.sh`, or the user corrects your routing.
2. **Record** — run `scripts/record_miss.sh "<question>" "<path>"`. Log lives at `~/.openclaw/openclaw-docs/misses.md`.
3. **Review** — periodically the maintainer reads the misses log.
4. **Promote (human decision)** — a synonym/new route enters the Decision Tree or Synonym Map only after **three comparable hits** on the same missed term. One-off questions stay in the log.
5. **Validate** — any edit to routes must pass `scripts/selftest.sh` before commit.

Rules for evolution:

- **Start from friction, not novelty.** No new synonyms "just in case."
- **One lever per change.** Don't touch three branches in the same PR.
- **Evidence, not gut feel.** The misses log is the evidence; three comparable entries is the bar.
- **Prefer promotion over rewrite.** Add a synonym row; don't restructure the tree.

## Boundaries (Self-Modification)

This skill **never** modifies its own installed files at runtime:

- Do not edit `SKILL.md`, `EXAMPLES.md`, or any file under `scripts/` from within an agent answer.
- Do not invent new decision-tree branches on the fly — use the current tree, then log the miss.
- Do not write to `~/.openclaw/openclaw-docs/` anything other than the misses log (one append per miss).
- Do not exfiltrate user messages beyond the single flattened question passed to `record_miss.sh`.

Promotions from the misses log into SKILL.md are a **human commit**, reviewed, run through `selftest.sh`, and published as a new version. The agent proposes; the maintainer disposes.

## Anti-Patterns (Testable Don'ts)

Common mistakes when answering OpenClaw questions. Each is a rule that can be checked against a real answer.

- **DON'T** say SOUL.md and AGENTS.md are the same. SOUL = personality. AGENTS.md = operational manual.
- **DON'T** claim `openclaw cron add` defaults to a persistent session. Default is **`isolated`** (one-shot).
- **DON'T** recommend sharing `agentDir` between agents. It causes auth and session collisions.
- **DON'T** reference `docs.clawd.bot` or `clawdbot` CLI. Renamed to OpenClaw. Docs live at `docs.openclaw.ai`.
- **DON'T** fetch a page without `.md` extension. May return HTML instead of markdown.
- **DON'T** invent section URLs. If a path isn't in `llms.txt`, it doesn't exist.
- **DON'T** answer "I think..." — fetch or say not documented.

## Key Concepts (Verified)

Quick reference. Always back up with a Tier 2 fetch for critical answers.

**SOUL.md** — system-prompt layer for tone/opinions/brevity. Keep short. `concepts/soul.md`

**AGENTS.md** — operational manual (tools, workspace, channels). Read alongside SOUL. `concepts/agent-workspace.md`

**Multi-agent** — each agent has its own workspace + `agentDir` + sessions. Sessions keyed `agent:<id>:<key>`. Default `agentId = main`. `concepts/multi-agent.md`

**Session** — JSONL history on disk, survives restarts. Recall via `sessions_history` tool (sanitized). `concepts/session.md`

**Memory** — active (in-context) / QMD (vector) / dreaming (async consolidation) / honcho (external). `concepts/memory.md`

**Cron** — `openclaw cron add --name X --cron "*/15 * * * *" --session isolated --message "..."`. Default session = isolated. `automation/cron-jobs.md`

**Skills** — live at `~/.openclaw/skills/<name>/SKILL.md`. Baseline via `agents.defaults.skills`, per-agent via `agents.list[].skills`. `tools/skills.md`

---

> Replacement for outdated clawddocs. Fetches live, never stale, no echo placeholders.
