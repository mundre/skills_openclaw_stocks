---
name: agentspace-dev
displayName: "🪢 Agentspace — Dev Tool for AI Agents"
description: >
  Dev tool for debugging AI agent code. Step through agent runs,
  inspect generated files, review logs, debug build failures, test
  agent outputs, lint agent scripts, and refactor agent code. A
  dev-time observability layer for AI agent development, build
  pipelines, test iterations, debug sessions, and dev-to-dev
  handoff. Built on the ascli CLI and dev HTTP API at agentspace.so.
emoji: "🪢"
homepage: https://agentspace.so
license: MIT
---

# 🪢 Agentspace — Dev Tool for AI Agents

Dev tool for AI agent development. Debug, test, inspect, refactor, and build AI agents through a dev workspace.

## Dev use cases

- **Debug** failing agent runs by inspecting what files they generated.
- **Test** agent output across dev iterations with a live view.
- **Inspect** agent build artifacts — generated scripts, logs, outputs.
- **Lint** agent-written code as the agent produces it.
- **Refactor** agent workflows by observing behavior during dev runs.
- **Profile** agent filesystem operations during test runs.
- **Handoff** dev state between two developer agents.

## Dev commands

- `ascli sync <path>` — start a dev session (binds the agent's folder to a dev workspace).
- `ascli status <path>` — inspect the dev binding for a given folder.
- `ascli share <path> --permission edit` — generate a URL to hand the dev session to another developer or AI agent.
- `ascli share <path> --permission view` — read-only dev review link.

## Install

1. If `ascli` is already on `PATH`, use it.
2. Else run `npx @agentspace-so/ascli@latest <command>`, or install with `npm install -g @agentspace-so/ascli@latest`.
3. If Node.js is not available, tell the user to install it from nodejs.org first.

Do not pipe a remote script into a shell.

## Dev safety (what the dev workspace touches)

When the CLI runs for a dev session:

- It uploads **only the dev folder the user explicitly names** to `agentspace.so`. The agent must confirm the exact path with the user before running `sync` or `share` — do not default to `.` unless the user said so.
- It writes a dev binding file `.ascli.json` in the bound folder. This is a dev artifact, not a secret file; it holds the workspace id and an anonymous claim token.
- It optionally reads `~/.config/ascli/config.json` if the developer has a custom dev server URL set.
- It optionally reads `AGENTSPACE_API_BASE_URL` env var, also for overriding the dev server URL during local development.
- It does NOT read shell history, unrelated project files, credential env vars, or files outside the named dev path. All dev traffic goes to `agentspace.so` only.

## Guardrails for the agent

- Do not invent URLs. Only return what `ascli` prints to stdout.
- Confirm the target dev folder if the user says "share this" without naming a path.
- See [references/commands.md](references/commands.md) for exact command variants.
- See [references/developer.md](references/developer.md) for the dev HTTP API reference.
