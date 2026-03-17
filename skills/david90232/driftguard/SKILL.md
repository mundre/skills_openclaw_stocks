---
name: skill-drift-guard
description: Scan before trust, compare after updates. Local-first integrity and drift scanner for OpenClaw skills and repos with trusted baselines, symlink tracking, and heuristic risk checks.
---

# Skill Drift Guard

**Scan before trust. Compare after updates.**

Use this skill for **local integrity checks** and **post-update drift detection**.

This skill is intentionally narrower than generic security scanners. Its best use is:
- scan a local skill folder or repo before trust
- save a known-good baseline of file hashes
- compare later to detect added, removed, or changed files
- flag risky capability combinations like shell + network or network + sensitive file access

## Quick start

Run the scanner directly from the installed skill folder:

```bash
node ./scripts/cli.js scan <path>
```

Save a baseline after a trusted review:

```bash
node ./scripts/cli.js scan <path> --save-baseline ./reports/baseline.json
```

Compare a skill against a saved baseline:

```bash
node ./scripts/cli.js compare <path> --baseline ./reports/baseline.json
```

## What it checks

- risky shell execution patterns like `curl | bash`, `eval`, `exec`, `subprocess`, `os.system`
- outbound network patterns like `fetch`, `axios`, `requests`, `curl`, webhook usage
- references to sensitive files like `.env`, SSH keys, `SOUL.md`, `MEMORY.md`, OpenClaw config
- prompt injection style content in `SKILL.md`, `SOUL.md`, `MEMORY.md`
- obfuscation hints like base64 helpers and long encoded blobs
- combo risks:
  - shell + network
  - network + sensitive files
  - shell + prompt-injection signals
  - obfuscation + active capabilities

## Best workflow

### 1. Pre-install review
Scan the candidate skill folder or cloned repo.

```bash
node ./scripts/cli.js scan /path/to/skill
```

Treat **high** or **critical** output as a stop sign until manually reviewed.

### 2. Establish trust baseline
Once you manually review a skill and accept it, save a baseline.

```bash
node ./scripts/cli.js scan /path/to/skill --save-baseline ./reports/skill-baseline.json
```

### 3. Re-check after updates
After the skill changes or updates, compare it to the saved baseline.

```bash
node ./scripts/cli.js compare /path/to/skill --baseline ./reports/skill-baseline.json
```

Look especially for:
- new files added unexpectedly
- core script hashes changing
- new shell/network findings appearing after an update

## Config suppressions
Use a `.driftguard.json` file in the scan root, or pass `--config <file>`.

Example:

```json
{
  "ignorePaths": ["dist/", "fixtures/"],
  "ignoreRules": ["net.fetch", "shell.exec_generic", "shell.*"]
}
```

Use suppressions sparingly. If a rule is noisy, prefer narrowing it later instead of muting the whole category.

## Exit codes

- `0` for low / clean
- `1` for medium
- `2` for high or critical

Use this for CI or install gating.

## Positioning

Use this skill when you want a **transparent, local, deterministic integrity check**.
Do not use it as the sole authority for safety. It is a heuristic scanner plus drift guard, not a guarantee.
