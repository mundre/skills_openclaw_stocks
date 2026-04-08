# Human-Like Memory Skill for OpenClaw

Skill providing long-term memory capabilities for OpenClaw, allowing AI assistants to remember past conversations.

[中文文档](README.md)

## Features

- **Memory Recall** - Automatically retrieve relevant historical memories based on current conversation
- **Memory Storage** - Save important conversation content to long-term memory
- **Memory Search** - Explicitly search for memories on specific topics

## Installation

### From ClawHub (Recommended)

```bash
openclaw skill install human-like-memory
```

### Manual Installation

```bash
# Clone repository
git clone https://gitlab.ttyuyin.com/personalization_group/human-like-mem-openclaw-skill.git

# Copy to OpenClaw skills directory
cp -r human-like-mem-openclaw-skill ~/.openclaw/workspace/skills/human-like-memory
```

## Configuration

### 1. Get API Key

Visit [plugin.human-like.me](https://plugin.human-like.me) → Register → Copy your `mp_xxx` key

### 2. Configure API Key

**Option A: Auto-configuration on Install**

When installing via ClawHub, OpenClaw will display a configuration form for you to enter the API Key.

**Option B: Run Setup Script (Recommended)**

```bash
sh ~/.openclaw/workspace/skills/human-like-memory/scripts/setup.sh
```

**Option C: Manual Configuration**

Edit `~/.openclaw/secrets.json`:

```json
{
  "human-like-memory": {
    "HUMAN_LIKE_MEM_API_KEY": "mp_your_key_here"
  }
}
```

### 3. Verify

```bash
node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs config
```

Output `apiKeyConfigured: true` means success.

## Configuration Reference

| Config | Required | Default | Description |
|--------|----------|---------|-------------|
| `HUMAN_LIKE_MEM_API_KEY` | Yes | - | API Key |
| `HUMAN_LIKE_MEM_BASE_URL` | No | `https://plugin.human-like.me` | API endpoint |
| `HUMAN_LIKE_MEM_USER_ID` | No | `openclaw-user` | User identifier |

## Usage

After installation and configuration, the skill triggers automatically when:

1. You ask "Do you remember what we discussed..."
2. You say "Remember this..."
3. You need to review past conversations

## CLI Testing

> **Note**: When installed via ClawHub, OpenClaw automatically replaces `{baseDir}` with the actual installation path. For manual testing, use the full path.

```bash
# Check configuration
node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs config

# Recall memories
node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs recall "what projects am I working on"

# Save memory
node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs save "I'm developing a memory plugin" "Got it, I'll remember that"

# Search memories
node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs search "meeting notes"
```

## Security Notes

This skill needs to read configuration files and send network requests to implement memory functionality, which may be flagged as suspicious by security scanners.

For detailed security notes, see [SECURITY.md](./SECURITY.md).

**Summary:**
- Only reads API Key from `~/.openclaw/secrets.json`
- Only sends conversation content to the user-configured memory server
- Does not read or transmit any other local files or system information
- All code is open source and auditable

## License

Apache-2.0
