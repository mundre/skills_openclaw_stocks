# ClawList Skill

**Trigger phrases:** task management, to-do list, my list, add task, mark done, focus today, what should I work on, clawlist, what's on my list, show my tasks, finished this week

---

## What This Skill Does

ClawList is a persistent, intelligent task management system for OpenClaw. It reads and writes a JSON task file and provides natural language task management with a beautiful CLI interface.

**Data file:** `/Users/oliverhutchins1/.openclaw/workspace-main/clawlist/tasks.json`  
**Script:** `/Users/oliverhutchins1/.openclaw/workspace-main/clawlist/clawlist.py`

---

## Natural Language Routing

When the user says something matching these patterns, translate to the appropriate command and run it using `exec`:

### "Add [X] to my list"
→ Extract the task title, and any mentioned category/priority
```bash
cd /Users/oliverhutchins1/.openclaw/workspace-main/clawlist
python3 clawlist.py add "Task title" --category <category> --priority <priority>
```
- If no category mentioned → default: `personal`
- If no priority mentioned → default: `normal`
- If urgency implied ("ASAP", "urgent", "today") → `--priority urgent`
- Categories: `personal | business | product | ops | social`

### "What's on my list?" / "Show my tasks"
```bash
cd /Users/oliverhutchins1/.openclaw/workspace-main/clawlist
python3 clawlist.py list
```

### "Mark [X] done" / "I finished [X]" / "Complete [X]"
→ Extract the task reference (partial title or ID)
```bash
cd /Users/oliverhutchins1/.openclaw/workspace-main/clawlist
python3 clawlist.py done "partial title or id"
```

### "What should I focus on today?" / "Today's priorities"
```bash
cd /Users/oliverhutchins1/.openclaw/workspace-main/clawlist
python3 clawlist.py list --today
```

### "Show me product tasks" / "What's in [category]?"
→ Map to the closest category: personal | business | product | ops | social
```bash
cd /Users/oliverhutchins1/.openclaw/workspace-main/clawlist
python3 clawlist.py list --category product
```

### "Morning briefing" / "What's my brief?" / "ClawList brief"
```bash
cd /Users/oliverhutchins1/.openclaw/workspace-main/clawlist
python3 clawlist.py brief
```

### "Show me what I finished this week" / "My stats" / "Progress report"
```bash
cd /Users/oliverhutchins1/.openclaw/workspace-main/clawlist
python3 clawlist.py stats
```

### "Archive done tasks" / "Clean up done"
```bash
cd /Users/oliverhutchins1/.openclaw/workspace-main/clawlist
python3 clawlist.py archive
```

### "Start working on [X]" / "I'm working on [X]"
```bash
cd /Users/oliverhutchins1/.openclaw/workspace-main/clawlist
python3 clawlist.py start "partial title"
```

---

## Agent Routing

### Hutch (main session)
- Handle all real-time task requests from J
- Translate natural language → clawlist.py commands
- Show Rich output directly in the chat reply
- After `add` or `done`, confirm with a brief 1-line acknowledgment
- Don't pad the response — output from the script is the reply

### Steward (daily briefing cron)
- Always include `python3 clawlist.py brief` in the morning briefing
- Embed the output block in the briefing message
- Run after calendar and weather, before the day's recommendations

---

## Execution Pattern

1. Parse the user's intent
2. Map to the closest command
3. Run via `exec` in the clawlist directory
4. Capture and display stdout as the response
5. Add a brief 1-line confirmation only if the output doesn't already confirm

**Always run from the clawlist directory** (or use the full path) so the script finds `tasks.json` correctly.

---

## Priority Mapping (natural language → CLI flag)

| User says | `--priority` |
|---|---|
| urgent, ASAP, critical, today, immediately | urgent |
| high, important, soon | high |
| normal, eventually, sometime | normal |
| low, someday, maybe, nice-to-have | low |

## Category Mapping

| User says | `--category` |
|---|---|
| personal, life, self, me | personal |
| business, GND, client, revenue, sales | business |
| product, KDP, Prayful, build, ship | product |
| ops, system, setup, config, fix | ops |
| social, post, TikTok, Twitter, content | social |

---

## Error Handling

- If `python3 clawlist.py` fails → check if Rich is installed: `pip3 install rich`
- If tasks.json not found → the script creates a fresh one automatically
- If no match for `done` → inform J and show the list so they can pick the right one

---

## Example Session

```
J: Add "Review GND proposal for Parker HVAC" to my list as business, high
→ python3 clawlist.py add "Review GND proposal for Parker HVAC" --category business --priority high

J: What's on my list?
→ python3 clawlist.py list

J: Mark the KDP task done
→ python3 clawlist.py done "KDP"

J: What should I focus on today?
→ python3 clawlist.py list --today
```
