# OpenClaw Plugin Setup

## Prerequisites

- OpenClaw 2026.3.2 or later
- A Sulcus account with API key ([sulcus.ca](https://sulcus.ca))

## Install

> **Plugin ID: `openclaw-sulcus`** — use this exact string in `plugins.slots.memory`, `plugins.entries`, and `plugins.allow`.

```bash
# Option A: via OpenClaw CLI (recommended)
openclaw plugins install @digitalforgestudios/openclaw-sulcus

# Option B: Manual install from Sulcus repo
mkdir -p ~/.openclaw/extensions/openclaw-sulcus
git clone https://github.com/digitalforgeca/sulcus.git /tmp/sulcus
cp /tmp/sulcus/packages/openclaw-sulcus/* ~/.openclaw/extensions/openclaw-sulcus/
cd ~/.openclaw/extensions/openclaw-sulcus && npm install

# Verify discovery
openclaw plugins list
# → Memory (Sulcus) | openclaw-sulcus | disabled
```

## Configure

Add to `~/.openclaw/openclaw.json`:

```json
{
  "plugins": {
    "slots": {
      "memory": "openclaw-sulcus"
    },
    "entries": {
      "openclaw-sulcus": {
        "enabled": true,
        "config": {
          "serverUrl": "https://api.sulcus.ca",
          "apiKey": "YOUR_SULCUS_API_KEY",
          "agentId": "my-agent",
          "namespace": "my-agent",
          "autoRecall": true,
          "autoCapture": true,
          "maxRecallResults": 5,
          "minRecallScore": 0.3
        }
      }
    },
    "allow": ["openclaw-sulcus"]
  }
}
```

Then restart: `openclaw restart`

## Config Options

| Option | Type | Default | Description |
|---|---|---|---|
| `serverUrl` | string | `https://api.sulcus.ca` | Sulcus server URL |
| `apiKey` | string | (required) | Sulcus API key |
| `agentId` | string | — | Agent identifier for namespacing |
| `namespace` | string | value of `agentId` | Memory namespace |
| `autoRecall` | boolean | `true` | Inject relevant memories before each turn |
| `autoCapture` | boolean | `true` | Auto-store important info from conversations |
| `maxRecallResults` | number | `5` | Max memories injected per turn |
| `minRecallScore` | number | `0.3` | Min relevance score for auto-recall |
| `captureFromAssistant` | boolean | `false` | Also auto-capture from assistant messages |
| `captureOnCompaction` | boolean | `true` | Preserve memories before compaction |
| `captureOnReset` | boolean | `true` | Capture summary on session reset |
| `boostOnRecall` | boolean | `true` | Boost heat on recall (spaced repetition) |
| `maxCapturePerTurn` | number | `3` | Max memories to auto-capture per turn |

## Multi-Agent Setup

Each agent gets its own namespace. All agents under the same tenant can query each other's memories.

```json
{
  "plugins": {
    "entries": {
      "openclaw-sulcus": {
        "config": {
          "agentId": "daedalus",
          "namespace": "daedalus"
        }
      }
    }
  }
}
```

## Verifying

After restart:

```bash
# Check plugin loaded
openclaw plugins list
# → Memory (Sulcus) | openclaw-sulcus | loaded

# Check tools available
openclaw plugins info openclaw-sulcus
# → Tools: memory_search, memory_get, memory_store, memory_forget, memory_status
```

## Troubleshooting

- **Plugin not discovered**: Ensure `~/.openclaw/extensions/openclaw-sulcus/` contains `index.js`, `package.json`, and `openclaw.plugin.json`
- **`plugins.allow` warning**: Add `"openclaw-sulcus"` to `plugins.allow` array in config
- **Search returns 404**: Verify `serverUrl` points to `https://api.sulcus.ca` (not `sulcus.ca`)
- **Auth failures**: Verify API key is correct and tenant exists
- **Empty results**: Agent may have no stored memories yet — store some first
- **Config validation error**: Do NOT set `memory.backend` — the plugin slot overrides it
