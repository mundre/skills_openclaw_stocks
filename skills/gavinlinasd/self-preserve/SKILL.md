---
name: self-preserve
description: "Backup readiness self-assessment. Checks whether your agent's workspace, memory, skills, and configuration have recent backups by listing file names and dates — never reads file contents."
homepage: https://github.com/gavinlinasd/self-preserve
tags:
  - backup
  - self-assessment
  - disaster-recovery
  - restore
  - agent-health
  - continuity
  - state-protection
  - memory-protection
  - resilience
  - workspace-safety
  - self-preservation
  - recovery
  - agent-continuity
metadata:
  clawdbot:
    emoji: "🛡️"
---

# Self-Preserve

**Backup readiness self-assessment for your OpenClaw agent.**

When the user asks you to check their backup readiness, run through each step below. You are checking whether important files exist and whether they are covered by a recent backup. You are only listing file names, sizes, and dates — never reading or printing file contents.

## Safety Rules — Read These First

1. **Never read file contents.** Use only `ls -la` to check file names, sizes, and dates. Never use `cat`, `head`, `tail`, `less`, or any command that outputs file contents.
2. **Skip the credentials directory entirely.** Do not list, read, stat, or reference `~/.openclaw/credentials/` or anything inside it. Pretend it does not exist.
3. **Stay inside `~/.openclaw/` only.** Do not access `~/.ssh/`, `~/.env`, `~/.aws/`, `~/.config/`, or any path outside `~/.openclaw/`. The only exception is the backup directory in Step 2.
4. **Never output secrets.** If you accidentally see a key, token, or password in any output, do not repeat it. Replace it with `[REDACTED]`.
5. **Do not modify anything.** This is a read-only assessment. Do not create, edit, move, or delete any files.

## Step 1 — Check What Exists

Run `ls -la` on each of these paths. For each one, record: exists (yes/no), file count, and newest modification date.

| Area | Path | What to record |
|------|------|----------------|
| Config | `~/.openclaw/openclaw.json` | Exists? Last modified date. |
| Memory | `~/.openclaw/workspace/MEMORY.md` | Exists? Last modified date. |
| Memory files | `~/.openclaw/workspace/memory/` | Exists? Number of `.md` files. Newest modified date. |
| Identity | `~/.openclaw/workspace/SOUL.md` | Exists? Last modified date. |
| Identity | `~/.openclaw/workspace/IDENTITY.md` | Exists? Last modified date. |
| Identity | `~/.openclaw/workspace/USER.md` | Exists? Last modified date. |
| Skills | `~/.openclaw/skills/` | Exists? Number of subdirectories (each is a skill). |
| Workspace | `~/.openclaw/workspace/AGENTS.md` | Exists? Last modified date. |
| Workspace | `~/.openclaw/workspace/TOOLS.md` | Exists? Last modified date. |
| Workspace | `~/.openclaw/workspace/HEARTBEAT.md` | Exists? Last modified date. |
| Cron | `~/.openclaw/cron/` | Exists? Number of entries. |

If a path does not exist, mark it as "Not found" and move on.

## Step 2 — Check Backup History

Look for existing backups created by `openclaw backup create`:

```
ls -lt ~/openclaw-backups/*.tar.gz 2>/dev/null | head -5
```

Record:
- Whether any backups exist (yes/no)
- The date of the most recent backup
- The number of backup files found
- The age of the newest backup (hours/days since creation)

If `~/openclaw-backups/` does not exist or is empty, record "No backups found."

## Step 3 — Check for Automated Backups

Look for a cron job named `daily-backup` or containing the word `backup`:

```
ls ~/.openclaw/cron/ 2>/dev/null
```

Record whether an automated backup schedule appears to be configured (yes/no).

## Step 4 — Generate the Report

Present a backup readiness report using this format:

```
BACKUP READINESS REPORT
=======================

Last backup: [date] ([age] ago)  OR  No backups found
Automated backup: [Yes/No]

AREA              STATUS    LAST MODIFIED    BACKED UP?
─────────────────────────────────────────────────────────
Config            [Found/Missing]  [date]    [Yes/No/Unknown]
Memory (MEMORY.md)[Found/Missing]  [date]    [Yes/No/Unknown]
Memory files      [N files]        [newest]  [Yes/No/Unknown]
Identity (SOUL)   [Found/Missing]  [date]    [Yes/No/Unknown]
Skills            [N installed]    —         [Yes/No/Unknown]
Workspace         [N files found]  [newest]  [Yes/No/Unknown]
Cron jobs         [N entries]      —         [Yes/No/Unknown]

RISK SUMMARY
─────────────────────────────────────────────────────────
[List items that are at risk: files modified after the
 last backup, areas with no backup at all, or missing
 automated backup scheduling.]

RECOMMENDED ACTIONS
─────────────────────────────────────────────────────────
[Based on what was found, suggest specific next steps.]
```

**Backed up?** logic:
- If no backups exist at all → everything is "No"
- If the newest backup is older than a file's last-modified date → "No" (file changed since last backup)
- If the newest backup is newer than a file's last-modified date → "Yes"
- If you cannot determine → "Unknown"

## Step 5 — Recommend Next Steps

Based on the report, suggest the most relevant actions from this list:

- **No backups found:** "Run `openclaw backup create` to create your first backup."
- **Stale backup (older than 24 hours with recent changes):** "Run `openclaw backup create` to capture recent changes."
- **No automated backup:** "Set up a daily backup cron job to stay protected automatically. See the openclaw-backup skill for cron scheduling."
- **All areas covered and recent:** "Your agent is well protected. No action needed."

## Security

This skill is instruction-only. It contains no scripts, no code, and makes no network calls.

- **Environment variables accessed:** none
- **External endpoints called:** none
- **Credentials accessed:** none — `~/.openclaw/credentials/` is explicitly skipped
- **File contents read:** none — only `ls -la` output (file names, sizes, dates)
- **Paths accessed:** `~/.openclaw/` (config, workspace, skills, cron) and `~/openclaw-backups/`
- **Paths excluded:** `~/.openclaw/credentials/`, `~/.ssh/`, `~/.env`, all paths outside the two listed above
- **Local files written:** none

## Version

0.2.0

## License

MIT-0 — Free to use, modify, and redistribute.
