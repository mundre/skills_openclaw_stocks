# Session Rename

Suggests and applies a name to a session.

## Procedure

### 0. Check Whether a Name Was Specified

- If the user specified a name directly → **skip to step 3** (skip suggestions)
- If no name was specified (e.g. `/session rename`, `suggest a name`) → **start from step 1**

### 1. Generate Name Candidates

Analyze the conversation content and generate 2–4 name candidates.

**Naming rules:**
- **Length**: 20–40 characters recommended
- **Format**: `<topic> + <key action>` (e.g. `feat/76-auth-history + SSO deployment validation`)
- **Language**: English preferred; technical terms in English
- **Avoid**: dates, unnecessary words like "session" or "task"

### 2. Select via AskUserQuestion

```
AskUserQuestion {
  question: "Please select a session name",
  header: "Session Name",
  options: [
    { label: "Candidate 1" },
    { label: "Candidate 2" },
    { label: "Candidate 3" }
  ]
}
```

### 3. Apply the Name

**Claude Code environment (current session):**
```
/rename <selected name>
```

**External session (script):**
```bash
SCRIPT=~/.claude/skills/session/scripts/rename-session.sh

# Assign a name to a specific session (full UUID required)
bash "$SCRIPT" 99f1f311-8c3d-43ba-b212-e3184965fed4 "name"

# Assign a name to the latest session in the current project
bash "$SCRIPT" "name"

# Check the current name
bash "$SCRIPT" --show 99f1f311-8c3d-43ba-b212-e3184965fed4

# List sessions with a name
bash "$SCRIPT" --list
```

## Storage Format

```json
{"type":"custom-title","customTitle":"<title>","sessionId":"<uuid>"}
```

Appended to the end of the session JSONL file.
