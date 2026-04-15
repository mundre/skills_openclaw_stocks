# update-advisor

An [OpenClaw](https://openclaw.ai) skill for safely checking and applying OpenClaw updates — with changelog analysis, risk rating, and automatic post-update verification.

## Why this skill?

`openclaw update --yes` restarts the Gateway, which disconnects the active chat session. Without a skill to handle this gracefully, you'd have no way to confirm whether the update succeeded. This skill solves that by:

1. Analyzing the changelog *before* updating (risk rating, relevance to your setup, new features)
2. Setting a cron job *before* restarting, so a fresh session automatically verifies and reports the result
3. Detecting installation ownership issues that would cause duplicate installations in multi-user environments

## Features

- **Check mode**: Fetch latest version, parse changelog delta, flag high-risk items, assess relevance to your config
- **Execute mode**: Safe update flow with pre-flight ownership check + automatic post-update verification via cron
- **Multi-user safety**: Detects when OpenClaw is owned by a different OS user and stops before creating a duplicate installation
- **Dynamic changelog path**: Works regardless of whether OpenClaw is in npm-global, pnpm, or a custom prefix

## Usage

Just talk to your agent naturally:

| Intent | Example phrases |
|--------|----------------|
| Check for updates | "Check for OpenClaw updates" / "Any new version?" |
| Execute update | "Confirm update" / "Execute update" / "Upgrade OpenClaw" |

## Installation

```bash
clawhub install lzyling/update-advisor
```

Or copy the skill directory into `~/.openclaw/workspace/skills/update-advisor/`.

## Requirements

- OpenClaw with skills support (Execute mode requires cron support)
- `npm` available in PATH (used to check latest version)
- `python3` available in PATH (used for changelog parsing)

## How it works

```
check-update.sh
  ├── Gets current + latest version via npm view
  ├── Parses local CHANGELOG.md for delta between versions
  ├── Runs openclaw doctor
  └── Outputs structured JSON

parse_changelog.py   — extracts and flags risky changelog entries
assemble_result.py   — assembles final JSON for the agent
```

The agent reads the JSON, performs analysis, and either reports findings (check mode) or proceeds with the safe update flow (execute mode).

## Multi-user note

If OpenClaw was installed by a different OS user (e.g. via Homebrew under another account), running `openclaw update --yes` as the current user will silently install a second copy instead of updating the original. This skill detects that scenario and stops with clear instructions before anything breaks.

## License

MIT
