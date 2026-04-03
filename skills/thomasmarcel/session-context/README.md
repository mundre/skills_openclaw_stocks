# Session Memory & Summarization

Automatically loads recent conversation memory into new sessions and generates AI summaries during compaction to maintain continuity across conversations.

## Features

- **Automatic Memory Loading**: Each new session automatically loads the latest memory file (today's or yesterday's) to provide immediate context
- **AI-Powered Summarization**: When approaching token limits, OpenClaw automatically generates a concise AI summary of the conversation
- **Seamless Continuity**: No manual intervention needed — memory persists across sessions and devices
- **Token-Safe**: Content truncated to ~4000 characters to protect context window

## Installation

### Via ClawHub (recommended)

```bash
clawhub install session-context
```

### Manual

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/thomasmarcel/openclaw-skill-session-context.git session-context
openclaw skills enable session-context
```

## How It Works

### Session Start Hook

When a new session begins:
1. Skill finds the most recently modified `.md` file in the `memory/` directory
2. Loads its content as a system message into the session context
3. If no memory exists yet, starts fresh

This ensures continuity: yesterday's important context is automatically available today.

### Compaction Hook

OpenClaw automatically compacts sessions before hitting token limits. When triggered:
1. Hook checks if summarization thresholds are met (20+ messages OR 60% of token limit)
2. Calls `agent.generateSummary(messages)` to produce an AI-generated summary
3. Prepends the summary to today's memory file in `memory/YYYY-MM-DD.md` with a timestamp
4. Session is compacted, freeing tokens while preserving key information

### Memory Files

- Daily files: `memory/2025-04-03.md`, `memory/2025-04-04.md`, etc.
- Each file accumulates summaries throughout the day, newest first
- No global `MEMORY.md` is needed (but your `session:start` hook can load it if you prefer)

## Configuration

The skill uses sensible defaults, but you can customize:

**Summarization thresholds** (in `hooks/session/compact:before/handler.js`):
```js
return (
  msgCount >= 20 || // minimum messages to summarize
  tokenCount > maxTokens * 0.6 // trigger at 60% of token limit
);
```

**Content truncation** (in `hooks/session/start/handler.js`):
```js
const truncated = content.substring(0, 4000); // adjust as needed
```

## Requirements

- OpenClaw 0.29.0 or higher
- `session:start` and `session:compact:before` hook support
- Workspace directory with `memory/` subfolder (created automatically)

## License

MIT

## Contributing

This skill is designed to be generic and useful to all OpenClaw users. Feel free to fork, improve, and submit PRs to the upstream repository.

---

**Made with 🤖 by AniBot (Thomas)**
