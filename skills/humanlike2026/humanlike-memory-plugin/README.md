# Human-Like Memory Plugin for OpenClaw

[![npm version](https://img.shields.io/npm/v/@humanlikememory/human-like-mem.svg)](https://www.npmjs.com/package/@humanlikememory/human-like-mem)

Long-term memory plugin for OpenClaw. Gives your agent the ability to remember past conversations, user preferences, and important context across sessions.

**Features:**
- Automatic memory recall before each response
- Automatic conversation storage after each response
- Agent-callable tools: `memory_search` and `memory_store`
- Registered as a first-class memory slot (`kind: "memory"`)
- Requires OpenClaw >= 2026.2.0

## Quick Start

### 1. Install

```bash
openclaw plugins install @humanlikememory/human-like-mem
```

### 2. Get Your API Key

Visit [https://plugin.human-like.me](https://plugin.human-like.me) to get your API key (starts with `mp_`).

### 3. Configure

```bash
# Set API key (required)
openclaw config set plugins.entries.human-like-mem.config.apiKey "mp_your_key_here"

# Set as the active memory engine
openclaw config set plugins.slots.memory human-like-mem

# Enable memory search for the agent
openclaw config set agents.defaults.memorySearch '{"enabled":true}' --strict-json
```

### 4. Restart

```bash
openclaw restart
```

### 5. Verify

```bash
openclaw status
```

You should see:

```
Memory │ 0 files · 0 chunks · sources remote-api · plugin human-like-mem · vector ready
```

## Configuration Options

All options can be set via `openclaw config set plugins.entries.human-like-mem.config.<key> <value>`:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `apiKey` | string | **(required)** | Your API key from https://plugin.human-like.me |
| `baseUrl` | string | `https://plugin.human-like.me` | API endpoint |
| `userId` | string | `openclaw-user` | User identifier |
| `agentId` | string | auto-detected | Agent identifier |
| `recallEnabled` | boolean | `true` | Enable automatic memory recall |
| `addEnabled` | boolean | `true` | Enable automatic memory storage |
| `recallGlobal` | boolean | `true` | Search memories globally (not per-conversation) |
| `memoryLimitNumber` | number | `6` | Max memories to recall per turn |
| `minScore` | number | `0.1` | Minimum relevance score (0-1) |
| `minTurnsToStore` | number | `5` | Store after N conversation turns |
| `sessionTimeoutMs` | number | `300000` | Auto-flush timeout (ms) |
| `stripPlatformMetadata` | boolean | `false` | Don't send platform user IDs (Feishu/Discord) |

**Example — full config:**

```bash
openclaw config set plugins.entries.human-like-mem.config '{"apiKey":"mp_xxx","recallEnabled":true,"addEnabled":true,"memoryLimitNumber":8}' --strict-json
```

### Environment Variables

You can also configure the plugin via environment variables:

| Environment Variable | Config Key | Description |
|---------------------|------------|-------------|
| `HUMAN_LIKE_MEM_API_KEY` | `apiKey` | API key (required) |
| `HUMAN_LIKE_MEM_BASE_URL` | `baseUrl` | API endpoint |
| `HUMAN_LIKE_MEM_USER_ID` | `userId` | User identifier |
| `HUMAN_LIKE_MEM_AGENT_ID` | `agentId` | Agent identifier |
| `HUMAN_LIKE_MEM_RECALL_ENABLED` | `recallEnabled` | Enable memory recall (`true`/`false`) |
| `HUMAN_LIKE_MEM_ADD_ENABLED` | `addEnabled` | Enable memory storage (`true`/`false`) |
| `HUMAN_LIKE_MEM_LIMIT_NUMBER` | `memoryLimitNumber` | Max memories to recall |
| `HUMAN_LIKE_MEM_MIN_SCORE` | `minScore` | Minimum relevance score |
| `HUMAN_LIKE_MEM_MIN_TURNS` | `minTurnsToStore` | Turns before auto-save |
| `HUMAN_LIKE_MEM_SESSION_TIMEOUT` | `sessionTimeoutMs` | Session timeout (ms) |
| `HUMAN_LIKE_MEM_STRIP_PLATFORM_METADATA` | `stripPlatformMetadata` | Strip platform user IDs |

**Example — disable storage via env:**

```bash
export HUMAN_LIKE_MEM_ADD_ENABLED=false
export HUMAN_LIKE_MEM_STRIP_PLATFORM_METADATA=true
```

## Agent Tools

Once installed, your agent can actively use memory:

- **`memory_search`** — Search past conversations and stored knowledge
- **`memory_store`** — Save important information for future recall

These tools are automatically registered and available to the agent.

## How It Works

1. **Before response** (`before_prompt_build`): The plugin searches for relevant memories based on the current prompt and injects them into context.
2. **After response** (`agent_end`): The plugin caches the conversation turn. When the turn threshold is reached or the session times out, it flushes to long-term storage.
3. **On session end**: Any remaining cached conversation is flushed.

## Troubleshooting

- **"API key not configured"** — Run: `openclaw config set plugins.entries.human-like-mem.config.apiKey "mp_xxx"`
- **"unavailable" in status** — Make sure `plugins.slots.memory` is set to `human-like-mem`
- **Request timeouts** — Increase `timeoutMs` in config
- **Check logs:**

```bash
openclaw logs | grep "Memory Plugin"
```

## Upgrading from v0.3.x

v0.4.x is a major upgrade:

- Plugin type changed from `lifecycle` to `memory`
- Hook migrated from `before_agent_start` to `before_prompt_build` (fixes double API calls)
- Added `registerService`, `registerTool`, `registerMemoryRuntime`
- Removed legacy hook aliases

After updating, set the memory slot:

```bash
openclaw config set plugins.slots.memory human-like-mem
openclaw restart
```

## Security & Privacy

This plugin sends conversation data to a remote server. Before using in production:

1. **Read [SECURITY.md](./SECURITY.md)** — Details what data is transmitted
2. **Read [PRIVACY.md](./PRIVACY.md)** — Data retention and deletion policies

**Quick privacy tips:**
- Use `addEnabled: false` to control what gets stored
- Use `stripPlatformMetadata: true` to hide platform user IDs
- Use `<private>...</private>` tags for content that shouldn't be memorized
- Start with a test API key, not production

## License

Apache-2.0
