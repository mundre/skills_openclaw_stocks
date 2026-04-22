---
metadata.openclaw:
  requires:
    anyBins: ["chromium-browser", "chromium", "google-chrome"]
  reason: "Auto-research uses browser automation — requires a Chromium-based browser"
---


# autoresearch — Nightly Research Pipeline

A zero-cost nightly research aggregator that rotates through 3 topic tracks, pulls from 4 independent sources, synthesises a structured markdown report, and prints a 3-line Telegram teaser to stdout.

## Quick Start

```bash
# Dry run — fetches real data, prints teaser, no file writes
cd ~/.openclaw/workspace
uv run --with httpx python skills/autoresearch/scripts/run.py --dry-run

# Full run — writes to memory/ and advances state
uv run --with httpx python skills/autoresearch/scripts/run.py

# Force a specific track
uv run --with httpx python skills/autoresearch/scripts/run.py --track crypto

# Verbose output (debug logs to stderr)
uv run --with httpx python skills/autoresearch/scripts/run.py --dry-run --verbose
```

## Tracks

The pipeline rotates through 3 tracks in order (persisted in `state.json`):

| Track | Display Name | Sources Focus |
|-------|-------------|---------------|
| `ai` | AI & Agents | cs.AI/MA/CL/LG arXiv, Python/Rust/TS GitHub, LLM HN keywords |
| `crypto` | Crypto & DeFi | cs.CR/DC arXiv, Solidity/Rust GitHub, crypto HN keywords |
| `devtools` | Developer Tools | cs.SE/PL arXiv, Rust/Go/TS/Python GitHub, CLI/editor HN keywords |

## Sources

| Source | API | Auth | Fallback |
|--------|-----|------|----------|
| **arXiv** | Atom API (`export.arxiv.org`) | None | Returns `[]` on error |
| **GitHub Trending** | Public HTML scrape | None | Returns `[]` on structure change |
| **Hacker News** | Firebase JSON API | None | Returns partial results |
| **Web Search** | Brave Search API | `BRAVE_API_KEY` env | Skipped silently if no key |

## Output Files

| File | Description |
|------|-------------|
| `memory/autoresearch-latest.md` | **Overwritten each run** — latest report |
| `memory/autoresearch-archive.md` | **Append-only** — all runs with date markers |
| `memory/autoresearch-errors.log` | Stderr from cron runs |

## CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--track ai\|crypto\|devtools` | Rotate | Override track rotation for this run |
| `--dry-run` | off | Fetch + synthesise but skip file writes and state advance |
| `--verbose` | off | Print DEBUG logs to stderr |

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | All sources failed OR disk write failed |
| `2` | Config/state error (config.json missing, bad --track value) |

## Configuration

Edit `config.json` to customise per-track queries:

```json
{
  "tracks": {
    "ai": {
      "arxiv_categories": ["cs.AI", "cs.MA", "cs.CL", "cs.LG"],
      "arxiv_keywords": ["agent", "LLM", ...],
      "github_languages": ["python", "rust", "typescript"],
      "github_topics": ["ai-agent", "llm", ...],
      "hn_keywords": ["AI", "GPT", "Claude", ...],
      "web_queries": ["AI agent framework news 2026", ...]
    }
  }
}
```

## Cron Integration

```bash
# Add to OpenClaw cron: 1 AM Sydney (14:00 UTC previous day)
# The cron wrapper captures stdout and sends to Telegram
0 14 * * * cd ~/.openclaw/workspace && uv run --with httpx python skills/autoresearch/scripts/run.py 2>>~/.openclaw/workspace/memory/autoresearch-errors.log
```

The script prints a 3-line teaser to **stdout**:
```
🔬 **Nightly Research: AI & Agents**
• Top paper: Scaling Laws for Agent Reasoning… — We study how reasoning…
• Trending: microsoft/autogen ⭐342 | HN: Show HN: I built…
```

The cron agent captures stdout and sends it to Telegram via the `message` tool.

## State

State is persisted in `state.json`:

```json
{
  "current_track_index": 1,
  "last_run": "2026-03-15T14:02:31.123456+00:00",
  "last_tracks": ["ai"]
}
```

State only advances on a **successful** run (exit 0). If all sources fail, state stays at the same track so tomorrow retries the same track.

## Dependencies

- **httpx** — all HTTP (via `uv run --with httpx`)
- **xml.etree.ElementTree** — arXiv Atom XML parsing (stdlib)
- **json, re, asyncio, argparse, pathlib** — stdlib

No additional dependencies needed. No pyproject.toml required in the skill dir.

## Integration with Book Draft

Other cron jobs or agents can read the latest report directly:

```bash
cat ~/.openclaw/workspace/memory/autoresearch-latest.md
```

Or in Python:

```python
from pathlib import Path
report = Path.home() / ".openclaw/workspace/memory/autoresearch-latest.md"
content = report.read_text()
```

## File Structure

```
skills/autoresearch/
├── SKILL.md          # This file
├── PLAN.md           # Architecture and spec
├── config.json       # Track definitions + source config
├── state.json        # Runtime state (auto-managed)
└── scripts/
    ├── run.py        # CLI entrypoint (main pipeline)
    ├── sources.py    # Data fetchers (arXiv, GitHub, HN, web)
    ├── synthesise.py # Report builder (markdown synthesis)
    └── state.py      # Track rotation state machine
```
