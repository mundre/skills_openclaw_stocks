# Security Notes

This document explains the security-related code patterns detected by static analysis and why they are necessary for this skill to function.

## Detected Patterns

### 1. File Read + Network Send (`scripts/memory.mjs`)

**What it does:**
- Reads `~/.openclaw/secrets.json` to load user-configured API credentials
- Sends requests to the configured memory server (default: `plugin.human-like.me`)

**Why it's safe:**
- The file read is limited to the OpenClaw secrets store, which is designed for this purpose
- The network destination is explicitly configured by the user
- No local files or secrets are transmitted - only conversation content the user chooses to save

### 2. Environment Variable Access + Network Send (`scripts/memory.mjs`)

**What it does:**
- Reads `HUMAN_LIKE_MEM_API_KEY` and related environment variables as fallback configuration
- Uses these credentials to authenticate with the memory server

**Why it's safe:**
- Environment variables are only used when secrets.json is not configured
- The API key authenticates the user to their own memory service
- The key is sent via secure headers, not in the request body

## Data Flow

```
User Input → Skill → Memory Server → User's Memory Database
                ↑
            API Key (from secrets.json or env vars)
```

## What Data is Transmitted

1. **To Memory Server:**
   - Conversation content (user messages and assistant responses)
   - User ID and Agent ID (configured by user)
   - Session metadata

2. **NOT Transmitted:**
   - Local files
   - System information
   - Other environment variables
   - Anything not explicitly saved via the skill commands

## User Control

- Users control what gets saved via explicit commands (`save`, `save-batch`)
- With `alwaysRecall: true` (default), recall happens automatically but only sends search queries
- Users can set `alwaysRecall: false` to control when recalls happen
- All data belongs to the user's own memory database

## Privacy Recommendations

1. Avoid saving sensitive information (passwords, API keys) in conversations
2. Use `<private>...</private>` tags to mark content that should not be memorized
3. Review the memory server's privacy policy at https://plugin.human-like.me/privacy

## Source Code

This skill is open source. Review the code at:
- GitHub: https://github.com/humanlike2026/humanlike-memory
- ClawHub: https://clawhub.ai/humanlike2026/humanlike-memory
