---
name: encode
version: "2.0.0"
author: BytesAgain
homepage: https://bytesagain.com
source: https://github.com/bytesagain/ai-skills
license: MIT-0
tags: [encode, tool, utility]
description: "Encode text to base64, URL-safe strings, and HTML entity formats. Use when encoding payloads, escaping URLs, converting HTML entities."
---

# Encode

A devtools toolkit for checking, validating, generating, formatting, linting, explaining, converting, templating, diffing, previewing, fixing, and reporting on encoded data — all from the command line.

## Commands

| Command | Description |
|---------|-------------|
| `encode check <input>` | Check encoding validity — log check results for encoded payloads |
| `encode validate <input>` | Validate encoding format — record validation outcomes |
| `encode generate <input>` | Generate encoded output — log generation parameters and results |
| `encode format <input>` | Format encoded data for readability — track formatting operations |
| `encode lint <input>` | Lint encoding for common issues — save lint findings |
| `encode explain <input>` | Explain encoding format or structure — record explanations |
| `encode convert <input>` | Convert between encoding formats — log conversion details |
| `encode template <input>` | Create or apply encoding templates — track template operations |
| `encode diff <input>` | Diff two encoded values — log comparison results |
| `encode preview <input>` | Preview decoded or re-encoded output — record preview sessions |
| `encode fix <input>` | Fix encoding issues — log fix operations and outcomes |
| `encode report <input>` | Generate encoding analysis reports — save report specifications |
| `encode stats` | Show summary statistics across all command categories |
| `encode export json\|csv\|txt` | Export all logged data in JSON, CSV, or plain text format |
| `encode search <term>` | Search across all log entries for a keyword |
| `encode recent` | Show the 20 most recent activity entries |
| `encode status` | Health check — version, data directory, entry count, disk usage, last activity |
| `encode help` | Show available commands and usage |
| `encode version` | Show version (v2.0.0) |

Each domain command (check, validate, generate, etc.) works in two modes:
- **Without arguments**: displays the 20 most recent entries from that category
- **With arguments**: logs a new timestamped entry and shows the running total

## Data Storage

All data is stored locally in `~/.local/share/encode/`. Each command writes to its own log file (e.g., `check.log`, `validate.log`, `convert.log`) and a shared `history.log` tracks all activity with timestamps. No cloud sync, no external API calls — everything stays on your machine.

## Requirements

- Bash 4+ (uses `set -euo pipefail`)
- Standard Unix utilities: `date`, `wc`, `du`, `grep`, `head`, `tail`, `basename`
- No external dependencies or API keys required

## When to Use

1. **Debugging encoded API payloads** — Use `check` and `validate` to verify base64 or URL-encoded strings, `explain` to understand the encoding structure, and `fix` to log corrections
2. **Converting between encoding formats** — Use `convert` to track format conversions (base64 ↔ URL encoding ↔ HTML entities) and `diff` to compare before/after results
3. **Building encoding pipelines** — Use `template` to define reusable encoding patterns, `generate` to produce encoded output, and `format` to ensure consistent presentation
4. **Code review and linting** — Use `lint` to record encoding issues found during review, `preview` to verify decoded output, and `report` to summarize findings for the team
5. **Maintaining an encoding operations log** — Use `stats` to see how many encoding operations you've performed, `search` to find specific entries, and `export` to back up your history

## Examples

```bash
# Check if a base64 string is valid
encode check "SGVsbG8gV29ybGQ= — valid base64, decodes to Hello World"

# Validate URL encoding
encode validate "%E4%BD%A0%E5%A5%BD — valid UTF-8 URL encoding for 你好"

# Convert between formats
encode convert "base64 to hex: SGVsbG8= → 48656c6c6f"

# Lint for common issues
encode lint "Found double-encoded URL: %2520 should be %20"

# Explain an encoding format
encode explain "JWT token structure: header.payload.signature, each base64url"

# Generate encoded output
encode generate "URL-encode query params: name=张三&city=北京"

# Diff two encoded values
encode diff "v1: dXNlcg== vs v2: YWRtaW4= — different decoded values"

# Export all data to JSON
encode export json

# View statistics
encode stats
```

## How It Works

Encode uses a simple append-only log architecture. Each command appends a timestamped, pipe-delimited entry (`YYYY-MM-DD HH:MM|value`) to its category-specific log file. The `stats` command aggregates line counts across all logs, `search` runs case-insensitive grep across all files, and `export` serializes everything into your chosen format (JSON, CSV, or plain text). The `status` command gives a quick system health overview including version, total entries, disk usage, and last activity timestamp.

---

*Powered by BytesAgain | bytesagain.com | hello@bytesagain.com*
