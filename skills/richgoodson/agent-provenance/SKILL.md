---
name: agent-provenance
description: File provenance tracking, authority levels, commit conventions, and governance policies. Ensures accountability for changes to instruction files, tracks review history, and provides clear ownership for agent-maintained documentation. Works with hierarchical-agent-memory and agent-session-state.
---

# Agent Provenance

Instruction files (MEMORY.md, PRINCIPLES.md, SOUL.md, HEARTBEAT.md, LEARNINGS.md, AGENTS.md) guide the agent's behavior. Changes to these files should be tracked and reviewed. This skill provides provenance headers, authority level definitions, commit conventions, and governance policies to ensure accountability and maintainability.

## The Problem

Instruction files evolve over time. Without clear tracking:
- It's unclear who made changes and when
- Review responsibilities become ambiguous
- Agent-written goals can persist indefinitely without validation
- Security boundaries can be eroded gradually
- Audit trails are lost

## Architecture

### Provenance Headers

All instruction files carry an HTML comment header:

```html
<!--
  provenance: human-authored | agent-authored | mixed
  description: what this file is
  last-reviewed: YYYY-MM-DD
  reviewed-by: Human | Agent
-->
```

**provenance types:**
- **human-authored**: Files created by the human user and not modified by the agent without explicit direction (SOUL.md, PRINCIPLES.md, USER.md)
- **agent-authored**: Files created and maintained by the agent (LEARNINGS.md, memory/sessions/*.md, memory/*.md)
- **mixed**: Files with both human policy and agent procedures (AGENTS.md, HEARTBEAT.md)

Only the human user updates `last-reviewed` / `reviewed-by` on human-authored files. During heartbeat maintenance, if any instruction file has `last-reviewed` older than 30 days, flag it to the human user.

### Authority Levels

Files have different sensitivity levels:

**Human-Authored Files** (SOUL.md, PRINCIPLES.md, USER.md)
- The agent does not modify without explicit human direction
- These define the agent's identity and core rules

**Mixed Files** (AGENTS.md, HEARTBEAT.md)
- The human user sets policy, the agent maintains operational procedures
- Changes logged in git

**Agent-Authored Files** (LEARNINGS.md, memory/sessions/*.md, memory/*.md)
- The agent writes freely
- The human user reviews periodically

### Commit Message Convention

Workspace commits (this repo) use a tag prefix:

- `[human-directed]` — The human user explicitly asked for this change
- `[agent-autonomous]` — The agent decided to make this change independently
- `[heartbeat]` — Change made during a heartbeat cycle
- `[cron]` — Change made by a cron job / background task

This makes `git log --oneline <file>` a real audit trail.

**Software project commits** (any external project) use plain descriptive messages with NO provenance tags. Tags like `[human-directed]` are AI fingerprints — they leak that an agent is involved in the project.

### TTL on Agent-Written Goals

Anything the agent writes to a goals, tasks, or backlog section gets a date stamp. If an agent-written goal is older than 14 days and the human user hasn't touched it, the agent does not silently keep following it. Instead: ask the human user whether it's still valid.

### Instruction Diff Reports

Weekly (or on-demand via "diff report"): The agent diffs all instruction files (AGENTS.md, PRINCIPLES.md, LEARNINGS.md, SOUL.md, HEARTBEAT.md) against their state 7 days ago and posts a summary to the configured channel. What changed, who changed it, why. The human user reviews, confirms, or reverts.

## Setup

Ensure git is configured in the workspace:

```bash
git config user.name "Finch"
git config user.email "finch@openclaw.ai"
```

Create a .gitignore if needed to exclude temporary files.

## Daily Provenance Checks

During heartbeat cycles:

1. Check `last-reviewed` date in provenance headers of all instruction files
2. If any file has `last-reviewed` older than 30 days, flag it to the human user in the configured channel
3. Check for agent-written goals/tasks older than 14 days without human user interaction — flag for re-authorization
4. Generate weekly diff report if due (Sunday 9:00 AM CDT)

## Git Integration

### Commit Tags
Use the appropriate tag based on who directed the change:
- `[human-directed]`: The human user said "change this"
- `[agent-autonomous]`: The agent decided independently (e.g., during maintenance)
- `[heartbeat]`: Made during a heartbeat check
- `[cron]`: Made by a scheduled job

### Commit Messages
For workspace commits: include the tag and a clear description.
For external projects: plain descriptive messages only.

Example:
```bash
git commit -m "[heartbeat] Updated MEMORY.md with new project state"
```

### Review Process
When the human user reviews a file, update the `last-reviewed` and `reviewed-by` fields in the provenance header.

## Security Implications

Provenance tracking provides defense in depth:
- Makes unauthorized changes visible in git history
- Enforces regular review of critical files
- Provides accountability for agent actions
- Creates an audit trail for compliance

## Integration with Other Skills

- **hierarchical-agent-memory**: Memory files (MEMORY.md, daily/weekly/monthly/yearly) are agent-authored — the agent maintains freely, but the human user reviews periodically.
- **agent-session-state**: Session state files are agent-authored and subject to TTL and review policies.
- **agent-provenance**: This skill provides the governance framework for all instruction files.

## Best Practices

### For the Agent
- Always include provenance headers on new instruction files
- Update `last-reviewed` after the human user reviews a file
- Use appropriate commit tags
- Flag old content for review during heartbeats
- Ask the human user about stale agent-written goals

### For the Human User
- Review flagged files within 7 days
- Update `last-reviewed` and `reviewed-by` after each review
- Provide clear direction for changes explicitly requested
- Periodically check git history for anomalies

## Further Reading

- [Agent Provenance](https://github.com/openclaw/openclaw/tree/main/skills/agent-provenance) — Tracking and governance
- [Hierarchical Agent Memory](https://github.com/openclaw/openclaw/tree/main/skills/hierarchical-agent-memory) — Memory architecture
- [Agent Session State](https://github.com/openclaw/openclaw/tree/main/skills/agent-session-state) — Per-channel isolation