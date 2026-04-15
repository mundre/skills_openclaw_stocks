---
name: update-advisor
description: >
  OpenClaw update check and upgrade assistant. Triggers on phrases like
  "check for updates", "any new version", "is openclaw updated", "run the update",
  "confirm update", "upgrade openclaw".
  Two modes: (1) Check mode — analyze changelog, risk assessment, recommendation;
  (2) Execute mode — perform update with pre/post verification via cron.
requirements:
  binaries:
    - npm      # for version check (npm view openclaw version)
    - python3  # for changelog parsing scripts
    - openclaw # the tool being updated
---

# update-advisor

Helps you safely check for and apply OpenClaw updates, with changelog analysis, risk rating, and automatic post-update verification via a cron job (since Gateway restarts break the active session).

## Implementation architecture

This skill has two distinct implementation layers:

- **Check mode** is implemented by bundled shell/Python scripts (`scripts/check-update.sh`, `parse_changelog.py`, `assemble_result.py`). These are the only files the agent executes directly. They run locally, make no network calls beyond `npm view openclaw version`, and produce structured JSON output.

- **Execute mode** is implemented entirely through OpenClaw's built-in agent tools — specifically the `cron` tool (OpenClaw's native scheduler API, not system cron) and the `exec` tool. No bundled script performs the update or creates the cron job; the agent calls these tools directly with explicit, visible parameters. The cron job is a one-shot `agentTurn` (isolated session) that runs `openclaw --version` and `openclaw doctor` after the Gateway restarts — it does not modify system files.

- **MEMORY.md access** in Check mode is read-only and scoped to annotating changelog relevance against the user's known configuration (channels, installed Skills, cron jobs). It does not write to MEMORY.md during the check phase; any logging happens only in the post-update cron step at the user's explicit request.

All actions that have persistent side effects (`openclaw update --yes`, cron job creation) require explicit user confirmation via the trigger detection flow before the agent proceeds.

## Resolving the skill directory

This skill's scripts live in the `scripts/` subdirectory next to this SKILL.md file.

To locate the workspace root at runtime, run:
```bash
openclaw config get workspace 2>/dev/null || echo "$HOME/.openclaw/workspace"
```

The full script path is then: `<workspace>/skills/update-advisor/scripts/check-update.sh`

Store the workspace root in a variable when spawning cron jobs, so isolated sessions can resolve absolute paths correctly.

---

## Trigger Detection

- Contains "check", "any new", "updated?", "检查更新", "有没有新版本", "更新了吗" → **Check mode** (analyze only, do not update)
- Contains "execute update", "confirm update", "upgrade", "升级", "确认更新", "执行更新" → **Execute mode** (perform update)
- If the immediately preceding turn was a **Check mode report** (Step 4 output), treat affirmative replies ("yes", "go ahead", "do it", "yeah", "sure", "ok", "好", "可以") as Execute mode triggers.

When in doubt, default to **Check mode** — never run the update without explicit user confirmation.

---

## Check Mode

### Step 1: Run the check script

```bash
bash <workspace>/skills/update-advisor/scripts/check-update.sh
```

Store the JSON output as `CHECK_RESULT`.

### Step 2: Parse result

**If `has_update = false` or `same_version = true` or `already_latest = true`**:
> Already on the latest version (`{current_version}`). If `doctor_ok` is false, surface the doctor issues. Done.

**If `changelog_not_found = true` or `changelog_empty = true`**:
> Mention that the CHANGELOG could not be located (or was empty), but the version comparison still works. Continue to Step 3.

**If `has_update = true`**, continue to Step 3.

### Step 3: Changelog analysis

Read fields from `CHECK_RESULT` and analyze along these dimensions.

Key fields available: `current_version`, `latest_version`, `has_update`, `flagged_items`, `flagged_count`, `changelog_delta`, `doctor_ok`, `doctor_issues`, `latest_not_local`, `changelog_not_found`, `changelog_empty`, `rollback_cmd`.


**A. Risk rating** (based on `flagged_items` + `changelog_delta`)

Check each `flagged_items` entry against the user's active configuration (read from MEMORY.md):
- `config` / `schema` changes → check if it affects any configured integrations
- `security` / `harden` → usually good; mark green
- `deprecated` / `removed` → check if the user is using that feature
- `behavior change` → assess scope of impact

Risk level output:
- 🔴 High: breaking change or directly affects an actively used feature
- 🟡 Medium: config migration suggested, core function unaffected
- 🟢 Low: bug fixes and security hardening only

**B. Relevance to user's environment**

Read the user's active configuration from MEMORY.md — channels, installed Skills, cron jobs, running services, active integrations — and annotate each relevant changelog entry with **"relevant to your setup"** plus a brief explanation.

If no configuration context is available (fresh install, empty MEMORY.md), skip the relevance annotation and note: *"Personalized relevance analysis requires prior session context in MEMORY.md."*

**C. New feature opportunities**

Scan the delta text for new features (look for `### Changes`, `### New`, `### Added` headings, or any changelog block lines describing new behavior) and classify:
- ✅ Recommend enabling (low config cost, immediately useful)
- 👀 Worth watching (valuable but needs testing)
- ⏭️ Skip (not relevant to this setup)

**Special case: `latest_not_local = true`**

The local CHANGELOG does not yet contain the new version (it's only available after installation). In this case:
1. Explain: "The new version's changelog is only available after installation."
2. Show `update_status` output as the available install info.
3. If the full changelog was fetched in this session via another method (e.g. `npm view openclaw`, GitHub raw), use that analysis directly.
4. Suggest: "Run the check again after updating to get the full changelog analysis."

### Step 4: Output decision report

```
## OpenClaw Update Report
**Current**: x.x.x → **Latest**: x.x.x
**Risk**: 🟢 / 🟡 / 🔴

### High-risk items (if any)
- ...

### Relevant to your setup
- ...

### New feature suggestions
- ...

### Doctor status
✅ OK / ⚠️ Issues: ...

**Rollback command** (if needed): `openclaw update --tag x.x.x --yes`

---
Ready to update? (Reply "confirm update" or "execute update")
```

---

## Execute Mode

When the user explicitly says "execute update" / "confirm update" / "upgrade":

### ⚠️ Important: Update restarts the Gateway, breaking the active session

`openclaw update --yes` triggers an automatic Gateway restart. This disconnects the current chat session (Discord, Telegram, etc.), so the agent cannot confirm the result in the same turn.

**Set a cron job BEFORE running the update**, so a new isolated session can verify and report the outcome.

### Step 0: Installation ownership check (critical — prevents duplicate installs)

```bash
OC_PATH=$(which openclaw)
# Use stat for reliable ownership parsing (ls output is locale-dependent)
OC_OWNER=$(stat -f '%Su' "$OC_PATH" 2>/dev/null || stat -c '%U' "$OC_PATH" 2>/dev/null || echo "unknown")
CURRENT_USER=$(whoami)
echo "path: $OC_PATH | owner: $OC_OWNER | current user: $CURRENT_USER"
```

| Scenario | Criteria | Action |
|----------|----------|--------|
| **Different user owns the install** | `owner ≠ current user` | ❌ **Stop.** Tell the user: "I don't have permission to update this installation — running the update would silently create a duplicate copy. Ask the owner to remove the old installation first (`npm uninstall -g openclaw` or `brew uninstall openclaw`), then re-install as the current user." |
| **Current user owns the install** | `owner = current user` | ✅ Proceed |

### Step 0b: Confirm target version

```bash
openclaw update status
```

Note the `current_version` and target `latest_version`.

### Step 1: Set one-shot verification cron (BEFORE running the update)

Before submitting the cron, resolve these values in the current session:
- `WORKSPACE` = output of `openclaw config get workspace` (e.g. `/Users/you/.openclaw/workspace`)
- `TODAY` = current date in YYYY-MM-DD format
- `CHANNEL_ID` = the channel/target where the user sent the confirm message (include in cron payload so the isolated agent knows where to notify)

Use the `cron` tool (OpenClaw's built-in scheduler) to schedule an `agentTurn` job **5 minutes from now**:

```
OpenClaw was just updated from {old_version} to {target_version}. The Gateway restarted.
Please verify and report:
1. Run `openclaw --version` — if it fails, wait 60 seconds and retry up to 3 times (Gateway may still be starting).
   - If version shows {target_version}: update succeeded.
   - If version shows {old_version}: update failed — report failure and provide rollback: `{rollback_cmd}`
2. Run `openclaw doctor` — if issues found, run `openclaw doctor --fix`
3. Append a brief summary to {WORKSPACE}/memory/{TODAY}.md under "## OpenClaw Update"
4. Notify the user at channel {CHANNEL_ID}:
   - Update success/failure
   - New version number
   - Doctor status
```

Cron parameters:
- `schedule.kind`: `at`
- `at`: current UTC time + 5 minutes (ISO-8601)
- `payload.kind`: `agentTurn`
- `sessionTarget`: `isolated`
- `deleteAfterRun`: `true`

> **Note**: Do not reuse the version data from the prior Check mode run — re-verify live to avoid stale data.

### Step 2: Run the update

```bash
openclaw update --yes
```

After this, the Gateway restarts and the current session disconnects — this is **expected and normal**. The cron job handles the rest.

### Step 3 (by cron): Post-update verification

```bash
openclaw --version   # verify version
openclaw doctor      # health check
```

- Issues found → run `openclaw doctor --fix`
- Version unchanged → update failed; provide rollback command to user

### Step 4 (by cron): Log to memory

```markdown
## OpenClaw Update
- Version: {old} → {new}
- Time: HH:MM
- Doctor: OK / Fixed N issues
- Rollback (if needed): openclaw update --tag {old} --yes
```

### Step 5 (by cron): Notify user

Brief report: success/failure, new version, doctor status.

---

## Notes

- **Step 1 (set cron) must happen before Step 2 (run update)** — session disconnects immediately after
- `openclaw gateway restart` is handled internally; never call it separately
- Session disconnection after update is normal behavior, not a failure
- If the update fails, give the rollback command; don't attempt workarounds
- Skills updates (`clawhub update --all`) are out of scope; handle separately if needed
- **Never use the `edit` tool to patch `openclaw.json` directly** — always use `python3 -c` with the `json` module or `jq` to avoid injecting control characters that break JSON parsing
