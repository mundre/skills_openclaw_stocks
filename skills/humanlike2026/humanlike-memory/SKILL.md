---
name: human-like-memory
description: "Long-term memory for conversations: recall past discussions, save important info, search memories"
homepage: https://plugin.human-like.me
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      bins: ["node"]
      env: ["HUMAN_LIKE_MEM_API_KEY"]
    primaryEnv: "HUMAN_LIKE_MEM_API_KEY"
---

# Human-Like Memory Skill

Long-term memory capabilities for recalling past conversations and saving important information across sessions.

## ✅ Use When

- User asks "do you remember...", "what did we discuss...", "检索记忆"
- User says "remember this", "save this", "帮我记住"
- Starting a new session and need prior context
- User references previous projects, decisions, or preferences

## ❌ Don't Use When

- Simple greetings without context needs
- Generic questions unrelated to past conversations
- Code execution or system commands

## Setup

### 1. Get API Key

Visit [plugin.human-like.me](https://plugin.human-like.me) → Register → Copy your `mp_xxx` key

### 2. Configure

**Option A: Interactive Setup (Recommended)**

    sh {baseDir}/scripts/setup.sh

Follow the prompts to enter your API key.

**Option B: Manual Config**

Edit `~/.openclaw/secrets.json`:

    {
      "human-like-memory": {
        "HUMAN_LIKE_MEM_API_KEY": "mp_your_key_here"
      }
    }

### 3. Verify

    node {baseDir}/scripts/memory.mjs config

Expected output: `API Key: mp_xxx... (configured)`

## Commands

### Recall/Search Memory

```bash
node {baseDir}/scripts/memory.mjs recall "<query>"
node {baseDir}/scripts/memory.mjs search "<query>"
```

### Save Single Turn to Memory

```bash
node {baseDir}/scripts/memory.mjs save "<user_message>" "<assistant_response>"
```

### Save Batch (Multiple Turns) to Memory

```bash
echo '<JSON array of messages>' | node {baseDir}/scripts/memory.mjs save-batch
```

### Check Configuration

```bash
node {baseDir}/scripts/memory.mjs config
```

---

## Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `alwaysRecall` | `true` | Recall memory on every turn |
| `saveTriggerTurns` | `5` | Turns before auto-save (saveMaxTurns = this × 2) |
| `memoryLimitNumber` | `6` | Max memories to retrieve |
| `minScore` | `0.1` | Minimum relevance score (0-1) |

---

## Memory Recall Protocol

### MODE A: Every-Turn Recall (alwaysRecall: true, DEFAULT)

Call recall on **every turn**, even simple greetings.

```
User message → recall → process results → respond → increment counter → save-batch if needed
```

### MODE B: Smart Recall (alwaysRecall: false)

Recall only when contextually needed:
- ✅ Explicit requests: "do you remember", "what did we discuss"
- ✅ Implicit references: "the project", "that bug", "our plan"
- ✅ Session start or task continuation
- ❌ Simple greetings, generic questions, code execution

---

## Keyword Extraction

Extract the **semantic core** from user messages:

| User Message | Query |
|--------------|-------|
| "What's the weather like?" | `"weather preferences location"` |
| "Help me debug this code" | `"debug code recent"` |
| "继续之前的工作" | `"recent work task"` |

**Rules:**
1. Keep nouns and key concepts
2. Remove action words (help, please, can you)
3. Remove filler words (the, a, what, how)
4. Add "recent context" for short messages

---

## Processing Results

**If memories found:** Incorporate naturally ("As we discussed...", "I recall you mentioned...")

**If no memories:** Respond normally. Don't announce "no memories found."

---

## Periodic Save

| Setting | Default |
|---------|---------|
| `saveTriggerTurns` | 5 |
| `saveMaxTurns` | 10 (= trigger × 2) |

After each turn, increment counter. When counter >= `saveTriggerTurns`, call `save-batch`:

```bash
echo '[{"role":"user","content":"..."},{"role":"assistant","content":"..."}]' | node {baseDir}/scripts/memory.mjs save-batch
```

**Save silently** - don't announce saving.

---

## Immediate Save Triggers

Save immediately when user:
- States preference: "I prefer dark mode"
- Makes decision: "Let's use PostgreSQL"
- Gives deadline: "Due on March 15th"
- Corrects you: "No, my name is Wei"
- Explicitly asks: "Remember this"

```bash
node {baseDir}/scripts/memory.mjs save "<user_message>" "<your_response>"
```

---

## Quick Reference

```
RECALL:   node {baseDir}/scripts/memory.mjs recall "<keywords>"
SAVE:     node {baseDir}/scripts/memory.mjs save "<user>" "<assistant>"
BATCH:    echo '<JSON>' | node {baseDir}/scripts/memory.mjs save-batch
CONFIG:   node {baseDir}/scripts/memory.mjs config
```

---

## Error Handling

| Problem | Solution |
|---------|----------|
| Recall/Save fails | Log error, proceed without memories |
| No results | That's OK - respond normally |
| Timeout | Proceed without waiting |

---

## Privacy

- Memory data belongs to the user
- Never store secrets (API keys, passwords)
- Ignore content in `<private>...</private>` tags
