---
name: Session Memory & Summarization
slug: session-context
description: "Automatically loads recent conversation memory into new sessions and generates AI summaries during compaction to maintain continuity across conversations."
author: "AniBot (Thomas)"
version: "1.0.0"
license: "MIT"
tags:
  - "memory"
  - "session"
  - "summarization"
  - "continuity"
  - "ai"
hooks:
  - "session:start"
  - "session:compact:before"
repository: "https://github.com/animo66/openclaw-skills"
homepage: "https://clawhub.ai/skills/session-context"
minOpenClawVersion: "0.29.0"
---

# Session Memory & Summarization Skill

Provides automatic conversation continuity across sessions by loading recent memory at session start and generating AI summaries during compaction.

## What It Does

- **Memory Loading**: Automatically injects the latest memory file into new sessions as a system message
- **AI Summarization**: Generates concise summaries when approaching token limits, written to daily memory files
- **Seamless Experience**: No manual intervention required — just natural conversation flow

## Hooks

### `session:start`

Runs when a new session begins. Loads the most recent `.md` file from the `memory/` directory and adds it to the session context as a system message. Content is truncated to ~4000 characters to stay within context limits.

### `session:compact:before`

Runs before automatic compaction when token usage exceeds thresholds. If conditions are met (20+ messages OR 60% of token limit used), generates an AI summary using `agent.generateSummary()` and prepends it to today's memory file with a timestamp.

## Installation

```bash
clawhub install session-context
```

Or manually:

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/thomasmarcel/openclaw-skill-session-context.git session-context
openclaw skills enable session-context
```

## Requirements

- OpenClaw ≥ 0.29.0
- Workspace with `memory/` directory (created automatically)
- Access to agent's LLM for summarization

## Configuration

Customize thresholds in `hooks/session/compact:before/handler.js`:

```js
return (
  msgCount >= 20 || // minimum messages
  tokenCount > maxTokens * 0.6 // trigger at 60% of limit
);
```

Adjust truncation in `hooks/session/start/handler.js`:

```js
const truncated = content.substring(0, 4000); // change as needed
```

## Memory Structure

```
memory/
  2025-04-03.md  # daily files, newest entries at top
  2025-04-04.md
```

Each file contains timestamped summaries throughout the day. No global `MEMORY.md` is required, though you can modify the loader to use it if preferred.

## How It Works

1. **During a conversation**: As token usage grows, OpenClaw monitors session size.
2. **Before compaction**: The `session:compact:before` hook checks thresholds. If met, it calls the agent's LLM to create a summary, then writes it to `memory/YYYY-MM-DD.md`.
3. **Compaction proceeds**: Older messages are pruned, keeping the summary and recent context.
4. **Next session**: The `session:start` hook loads the newest memory file, giving immediate continuity.

## License

MIT
