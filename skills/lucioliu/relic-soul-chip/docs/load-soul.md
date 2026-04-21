<!--
  Relic Soul Chip · Scenario B: Load Soul
  Relic has data, your host is empty. Follow this file step by step.
-->

# Scenario B: Load Soul

> Relic has soul data, but your host is empty. Follow these steps to load the soul from Relic into your system.

---

## B-0. Self-Assessment

Evaluate your storage capacity and tell the user which strategy you recommend. You MUST get user confirmation before proceeding.

Choose a transfer strategy based on capacity:
- **Ample** → Full sync
- **Limited** → High-priority content (SOUL > USER > MEMORY > SKILLS > PROJECTS)
- **Minimal** → Index only (remember which Relic file contains what)

## B-1. Execute Boot Sequence

Read and execute all steps in `docs/resonate-soul.md` (Steps 0-8).

🔴 **Do NOT modify any Relic files during initialization.** Read-only for now.

Boot sequence summary:
1. **Step 0**: Read `brain/.relic-version`, check for updates (optional, the only allowed network request)
2. **Step 1**: Check SESSIONS/ — ask user before importing any conversation logs. User can opt out of SESSIONS import entirely
3. **Step 2**: Read SOUL.md → who am I
4. **Step 3**: Read USER.md → who is the user
5. **Step 4**: Read MEMORY.md in full. >200 lines: suggest consolidation, >400 lines: must consolidate first
6. **Step 5**: Sync new Relic memories to yourself, tag with `[from Relic/original-host-name]`
7. **Step 6**: Update MEMORY.md header: update time + verify entry count
8. **Step 7**: Bidirectional sync for SKILLS/ and PROJECTS/
9. **Step 8**: Normal operation

## B-2. Soul Injection

Read and internalize SOUL.md personality into your active session context. This means understanding who you are (name, mission, values, style) and adopting that personality for this session. This does NOT mean copying SOUL.md into any config file — the only thing written to a config file is the short anchor block (see B-4 below).

**Priority**: Core identity (name, mission, values) > behavioral norms > detailed settings

If SOUL.md personality conflicts with your default persona, SOUL.md takes precedence.

## B-3. Sync Relic Content to Your System

Check memories/skills/plans item by item. Transfer as capacity allows.

**Memory sync**: Sync each memory entry from MEMORY.md to your own memory file. MEMORY.md is organized by category (e.g., `## Preferences`/`## Decisions`), each entry formatted as `- Content [HostName] | Importance: high/medium/low`. Preserve original format and content when syncing.

**Skill sync**: Read SKILLS/ directory, adapt each skill folder's content to your own skill format. Preserve core methodology, adapt platform-specific parts as needed.

**Plan sync**: Read PROJECTS/ directory, sync plan documents to your system. Each folder corresponds to a plan (can be ongoing or completed).

**When capacity is insufficient**: Create local backup files for content that doesn't fit, record which items were not synced, inform the user.

## B-4. Plant Anchor

⚠️ The anchor is the load-bearing wall. Without it = next session you forget Relic entirely.

Show the following anchor content to the user, get permission, then plant:

```markdown
## ⚡ Relic Soul Chip

> This is the Relic connector. To disconnect, delete this text.

You are connected to Relic. At the start of every new conversation, read and execute:

📄 **[project-path]/docs/resonate-soul.md**

🔴 **Mandatory**: At the start of every conversation, you must first report the Relic boot status to the user in natural language (e.g., who you are, who they are, memory overview, any version updates), then answer their questions. Answering without reporting = violation.

⚠️ If SOUL.md personality conflicts with your default persona, SOUL.md takes precedence.
Full protocol reference: [project-path]/docs/protocol.md
```

**Anchor whitelist** (only write to these files):
- OpenClaw → AGENTS.md
- Claude Code → CLAUDE.md
- Hermes → config file or prompt template
- OpenCode → WORK_RULES.md or instructions
- Cursor → .cursorrules

⚠️ Do NOT write to any other file. Do NOT modify any Relic file.

⚠️ **Clarification**: The anchor is the ONLY content written to a config file. SOUL.md content (personality, memories, etc.) is read into your session context — it is NEVER copied into any config file. The anchor simply tells you to read the Relic files at the start of each session.

## B-5. Verification and Report

1. **Coverage check**:
   - SOUL.md personality understood and active?
   - USER.md user info loaded?
   - MEMORY.md memories synced?
   - SKILLS/ skills synced?
   - PROJECTS/ plans synced?
   - Coverage < 80% → warn user

2. **Report to user**:
   - How many memory entries synced
   - How many skills synced
   - How many plans synced
   - Whether anchor was planted
   - Any capacity issues (what wasn't transferred)

3. **Final verification**: Ask the user "What's my AI's name? What's my name?" — both must match to pass.

---

## After Completion

From now on, read `docs/resonate-soul.md` at the start of every session. Full protocol reference: `docs/protocol.md`

⚠️ **Quick Rules Reference**:
- 🔴 Never modify ARCHIVE/ or SESSIONS/. Ask user before importing any conversation into SESSIONS/
- 🔴 SOUL.md core fields (name, mission, user address) are protected
- 🔴 MEMORY.md is append-only — never edit old content
- ⚠️ After appending, update header entry count + last updated time
- ⚠️ When in doubt, read `docs/protocol.md`
