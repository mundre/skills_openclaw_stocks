# PLAN.md — autoresearch skill

> Nightly research pipeline that rotates through 3 topic tracks, pulls from 4 sources,
> synthesises a structured markdown report, and sends a notification via Telegram.

---

## 1. Architecture Overview

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  CRON (1 AM AEST)  →  uv run python scripts/run.py                 │
└──────────┬──────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────┐
│  state.py            │  Read state.json → determine tonight's track
│  load_track()        │  (ai → crypto → devtools → ai → …)
└──────────┬───────────┘
           │  track: TrackConfig
           ▼
┌──────────────────────┐     ┌────────────────────────────────┐
│  sources.py          │────▶│  4 fetchers run concurrently:  │
│  fetch_all(track)    │     │   ┌─ fetch_arxiv()             │
│                      │     │   ├─ fetch_github_trending()   │
│                      │     │   ├─ fetch_hackernews()        │
│                      │     │   └─ fetch_web_narratives()    │
│                      │     └────────────────────────────────┘
└──────────┬───────────┘
           │  SourceBundle (dataclass)
           ▼
┌──────────────────────┐
│  synthesise.py       │  Merge, deduplicate, rank, format
│  build_report()      │
└──────────┬───────────┘
           │  str (markdown report)
           ▼
┌──────────────────────┐
│  run.py (output)     │
│  1. Write report to  │
│     memory/autoresearch-latest.md  (overwrite)
│  2. Append to        │
│     memory/autoresearch-archive.md (append with date header)
│  3. Update state.json│
│     (advance track index, record timestamp)
│  4. Print 3-line teaser to stdout
│     (caller — cron wrapper or agent — sends to Telegram)
└──────────────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **No LLM synthesis** | Cost: $0/run. Uses structured merging + template. LLM pass is optional future enhancement. |
| **`httpx` for all HTTP** | Already available (`0.28.1`), async-capable, no extra deps. |
| **`xml.etree` for arXiv** | Stdlib, no `feedparser` needed. arXiv Atom is simple. |
| **HTML regex for GitHub trending** | Avoids headless browser. GitHub trending page has stable `<article class="Box-row">` structure. |
| **HN Firebase API** | Official, free, no auth. Top 30 stories → filter by track keywords. |
| **`web_search` via subprocess** | The agent's `web_search` tool isn't available from Python. We shell out to `openclaw` or fall back to scraping. Actually: **use `httpx` + Brave Search API** if `BRAVE_API_KEY` is set, otherwise gracefully degrade (skip web narratives source). |
| **Telegram notification is stdout** | The cron wrapper (agent or `openclaw cron`) reads stdout and sends via message tool. Script stays decoupled. |
| **`uv run --with httpx`** | Single inline dep. No `pyproject.toml` needed in skill dir. |

---

## 2. File Structure & Function Signatures

```
skills/autoresearch/
├── SKILL.md                    # Skill manifest + usage docs
├── PLAN.md                     # This file
├── config.json                 # Track definitions, source config, output paths
├── state.json                  # Runtime state (auto-created on first run)
└── scripts/
    ├── run.py                  # CLI entrypoint
    ├── sources.py              # Data fetchers
    ├── synthesise.py           # Report builder
    └── state.py                # Track rotation state machine
```

### 2.1 `scripts/state.py`

```python
"""Track rotation state machine.

State file: ../state.json (relative to scripts/)
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field

TRACKS = ["ai", "crypto", "devtools"]
STATE_FILE = Path(__file__).parent.parent / "state.json"


@dataclass
class RunState:
    current_track_index: int = 0
    last_run: str | None = None          # ISO 8601
    last_tracks: list[str] = field(default_factory=list)  # last N track names


def load_state() -> RunState:
    """Load state from disk. Returns default state if file missing/corrupt."""
    ...

def save_state(state: RunState) -> None:
    """Persist state to disk (atomic write via tmp + rename)."""
    ...

def get_current_track(state: RunState) -> str:
    """Return the track name for this run (e.g. 'ai')."""
    ...

def advance_track(state: RunState) -> RunState:
    """Advance to next track, update last_run timestamp, append to last_tracks."""
    ...

def override_track(track_name: str) -> str:
    """Validate a manual --track override. Raises ValueError if invalid."""
    ...
```

### 2.2 `scripts/sources.py`

```python
"""Data fetchers for all sources.

Each fetcher returns a list of SourceItem dataclasses.
All HTTP uses httpx with 15s timeouts.
"""
from __future__ import annotations
import httpx
import xml.etree.ElementTree as ET
import re
import json
from dataclasses import dataclass
from datetime import datetime

# --- Data types ---

@dataclass
class SourceItem:
    """Unified item from any source."""
    title: str
    url: str
    source: str              # "arxiv" | "github" | "hackernews" | "web"
    summary: str             # 1-3 sentence description
    score: float             # normalised relevance 0.0-1.0
    date: str | None = None  # ISO date if available
    metadata: dict | None = None  # source-specific extras
        # arxiv: {"authors": [...], "categories": [...]}
        # github: {"stars": int, "language": str, "stars_today": int}
        # hackernews: {"points": int, "comments": int, "hn_id": int}
        # web: {"snippet": str}


@dataclass
class TrackConfig:
    """Per-track query configuration (loaded from config.json)."""
    name: str                        # "ai" | "crypto" | "devtools"
    display_name: str                # "AI & Agents"
    arxiv_categories: list[str]      # ["cs.AI", "cs.MA", "cs.CL"]
    arxiv_keywords: list[str]        # ["agent", "LLM", "autonomous"]
    github_languages: list[str]      # ["python", "rust"]
    github_topics: list[str]         # ["ai-agent", "llm"]
    hn_keywords: list[str]           # ["AI", "GPT", "Claude", "agent"]
    web_queries: list[str]           # ["AI agent framework 2026", ...]
    max_items_per_source: int = 10


def load_track_config(track_name: str, config_path: Path) -> TrackConfig:
    """Load a TrackConfig from config.json for the given track name."""
    ...


# --- Fetchers ---

async def fetch_arxiv(config: TrackConfig, client: httpx.AsyncClient) -> list[SourceItem]:
    """Fetch recent papers from arXiv Atom API.

    Endpoint: https://export.arxiv.org/api/query
    Params: search_query=cat:{category}, sortBy=submittedDate, sortOrder=descending
    Parse: xml.etree.ElementTree (Atom feed)
    Returns: up to config.max_items_per_source items, keyword-filtered.
    Score: 1.0 if keyword in title, 0.7 if keyword in summary, 0.5 otherwise.
    """
    ...

async def fetch_github_trending(config: TrackConfig, client: httpx.AsyncClient) -> list[SourceItem]:
    """Scrape GitHub trending page for relevant repos.

    URLs: https://github.com/trending/{language}?since=daily (one per language)
    Parse: regex on <article class="Box-row"> blocks
    Extract: repo path (from <h2> > <a href="...">), description, stars, language
    Filter: match repo name/description against config.github_topics keywords
    Returns: up to config.max_items_per_source items.
    Score: based on star count (normalised within batch).
    """
    ...

async def fetch_hackernews(config: TrackConfig, client: httpx.AsyncClient) -> list[SourceItem]:
    """Fetch top HN stories filtered by track keywords.

    Step 1: GET https://hacker-news.firebaseio.com/v0/topstories.json → list[int]
    Step 2: For top 60 story IDs, GET /v0/item/{id}.json concurrently (batch of 10)
    Step 3: Filter by keyword match in title
    Returns: up to config.max_items_per_source items, sorted by score desc.
    Score: normalised HN points (points / max_points_in_batch).
    """
    ...

async def fetch_web_narratives(config: TrackConfig, client: httpx.AsyncClient) -> list[SourceItem]:
    """Search for fresh narratives via Brave Search API.

    Requires: BRAVE_API_KEY environment variable.
    Endpoint: https://api.search.brave.com/res/v1/web/search
    Headers: {"X-Subscription-Token": key}
    Params: q={query}, count=5, freshness=pd (past day)
    Runs: one search per config.web_queries entry.
    Returns: up to config.max_items_per_source items total (deduplicated by URL).
    Score: position-based (1.0 for rank 1, decaying).
    Fallback: if no BRAVE_API_KEY, returns empty list + logs warning.
    """
    ...


async def fetch_all(config: TrackConfig, config_path: Path) -> dict[str, list[SourceItem]]:
    """Run all fetchers concurrently via asyncio.gather.

    Returns: {"arxiv": [...], "github": [...], "hackernews": [...], "web": [...]}
    Each source that fails returns [] (logged, not raised).
    """
    ...
```

### 2.3 `scripts/synthesise.py`

```python
"""Synthesise raw source data into a structured markdown report."""
from __future__ import annotations
from datetime import datetime
from dataclasses import dataclass

# Reuses SourceItem from sources.py


@dataclass
class ReportSection:
    """One section of the final report."""
    heading: str             # e.g. "📄 Top Papers (arXiv)"
    items: list[SourceItem]


def deduplicate(items: list[SourceItem]) -> list[SourceItem]:
    """Remove items with duplicate URLs. Keep highest-scored version."""
    ...

def rank_items(items: list[SourceItem], max_items: int = 10) -> list[SourceItem]:
    """Sort by score descending, take top N."""
    ...

def build_section(heading: str, emoji: str, items: list[SourceItem], max_items: int = 5) -> str:
    """Format a section of the report as markdown.

    Format per item:
    - **[Title](url)** (source_tag)
      > summary_text
      _score: 0.85 | date: 2026-03-15_
    """
    ...

def build_teaser(track_display_name: str, sections: dict[str, list[SourceItem]]) -> str:
    """Generate a 3-line Telegram teaser.

    Format:
    🔬 **Nightly Research: {track_display_name}**
    • Top paper: {arxiv[0].title} — {arxiv[0].summary[:80]}
    • Trending: {github[0].title} ⭐ | HN: {hn[0].title}
    """
    ...

def build_report(
    track_display_name: str,
    track_name: str,
    sources: dict[str, list[SourceItem]],
    run_timestamp: str,
) -> tuple[str, str]:
    """Build the full markdown report + teaser.

    Returns: (full_report_markdown, teaser_text)

    Report structure — see §4 Report Output Schema.
    """
    ...
```

### 2.4 `scripts/run.py`

```python
"""Main pipeline entrypoint.

Usage:
    uv run --with httpx python scripts/run.py [--track ai|crypto|devtools] [--dry-run] [--verbose]

Exit codes:
    0  Success
    1  All sources failed (no data)
    2  Config/state error
"""
from __future__ import annotations
import argparse
import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Local imports
from state import load_state, save_state, get_current_track, advance_track, override_track
from sources import fetch_all, load_track_config
from synthesise import build_report

SKILL_DIR = Path(__file__).parent.parent
CONFIG_PATH = SKILL_DIR / "config.json"
MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory"
LATEST_PATH = MEMORY_DIR / "autoresearch-latest.md"
ARCHIVE_PATH = MEMORY_DIR / "autoresearch-archive.md"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments.

    --track TEXT    Override track rotation (ai|crypto|devtools)
    --dry-run       Fetch + synthesise but don't write files or advance state
    --verbose       Print debug info to stderr
    """
    ...

async def main() -> int:
    """Pipeline orchestrator.

    Steps:
    1. Parse args
    2. Load state (state.py)
    3. Determine track (--track override or rotation)
    4. Load track config (config.json)
    5. Fetch all sources (sources.py) — concurrent, per-source fallback
    6. Check: if all sources returned empty → exit 1
    7. Build report + teaser (synthesise.py)
    8. If not --dry-run:
       a. Write LATEST_PATH (overwrite)
       b. Append to ARCHIVE_PATH (with date separator)
       c. Advance state + save
    9. Print teaser to stdout (for Telegram notification)
    10. Return 0
    """
    ...

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

---

## 3. Config Schema (`config.json`)

```json
{
  "version": 1,
  "output": {
    "latest_path": "~/.openclaw/workspace/memory/autoresearch-latest.md",
    "archive_path": "~/.openclaw/workspace/memory/autoresearch-archive.md"
  },
  "defaults": {
    "max_items_per_source": 10,
    "max_report_items_per_section": 5,
    "http_timeout_seconds": 15,
    "hn_scan_depth": 60
  },
  "tracks": {
    "ai": {
      "display_name": "AI & Agents",
      "arxiv_categories": ["cs.AI", "cs.MA", "cs.CL", "cs.LG"],
      "arxiv_keywords": [
        "agent", "autonomous", "LLM", "large language model",
        "multi-agent", "reasoning", "tool use", "planning",
        "RLHF", "self-improvement", "code generation"
      ],
      "github_languages": ["python", "rust", "typescript"],
      "github_topics": [
        "ai-agent", "llm", "autonomous-agent", "langchain",
        "autogen", "crew-ai", "claude", "openai", "reasoning"
      ],
      "hn_keywords": [
        "AI", "GPT", "Claude", "Gemini", "LLM", "agent",
        "autonomous", "reasoning", "transformer", "Anthropic",
        "OpenAI", "DeepMind", "open source model"
      ],
      "web_queries": [
        "AI agent framework news 2026",
        "LLM breakthrough this week",
        "autonomous AI agents latest developments"
      ]
    },
    "crypto": {
      "display_name": "Crypto & DeFi",
      "arxiv_categories": ["cs.CR", "cs.DC", "q-fin.CP"],
      "arxiv_keywords": [
        "blockchain", "DeFi", "decentralized finance",
        "smart contract", "MEV", "zero knowledge",
        "rollup", "consensus", "token economics"
      ],
      "github_languages": ["solidity", "rust", "typescript"],
      "github_topics": [
        "blockchain", "defi", "ethereum", "solana",
        "smart-contract", "web3", "zero-knowledge",
        "rollup", "substrate", "cosmos"
      ],
      "hn_keywords": [
        "crypto", "blockchain", "DeFi", "Ethereum",
        "Bitcoin", "Solana", "zero knowledge", "rollup",
        "stablecoin", "MEV", "token", "web3"
      ],
      "web_queries": [
        "DeFi protocol news this week 2026",
        "blockchain infrastructure developments",
        "crypto regulatory news latest"
      ]
    },
    "devtools": {
      "display_name": "Developer Tools",
      "arxiv_categories": ["cs.SE", "cs.PL"],
      "arxiv_keywords": [
        "developer tools", "IDE", "code completion",
        "static analysis", "build system", "debugging",
        "testing framework", "continuous integration"
      ],
      "github_languages": ["rust", "go", "typescript", "python"],
      "github_topics": [
        "developer-tools", "cli", "terminal", "editor",
        "lsp", "linter", "formatter", "build-tool",
        "testing", "devops", "container", "wasm"
      ],
      "hn_keywords": [
        "developer tool", "CLI", "terminal", "Rust",
        "Go", "IDE", "editor", "neovim", "VSCode",
        "build system", "container", "Docker", "Nix",
        "testing", "CI/CD", "devops", "database"
      ],
      "web_queries": [
        "new developer tools 2026",
        "Rust CLI tools trending",
        "best new open source devtools this week"
      ]
    }
  }
}
```

---

## 4. Report Output Schema

The report written to `autoresearch-latest.md` follows this exact structure:

```markdown
# 🔬 Nightly Research: {track_display_name}

> Generated: {YYYY-MM-DD HH:MM AEST} | Track: {track_name} ({N} of 3)

---

## 📄 Top Papers (arXiv)

1. **[Paper Title](https://arxiv.org/abs/XXXX.XXXXX)**
   > One-sentence summary from the abstract.
   _Authors: A, B, C | Categories: cs.AI, cs.CL | Published: YYYY-MM-DD_

2. ...

_(up to 5 items)_

---

## 🔥 Trending Repos (GitHub)

1. **[owner/repo](https://github.com/owner/repo)** — ⭐ {stars} | 📈 +{today} today | {language}
   > Repository description from GitHub.

2. ...

_(up to 5 items)_

---

## 🗞️ Hacker News Highlights

1. **[Story Title](url)** — {points} pts, {comments} comments
   > _{domain}_

2. ...

_(up to 5 items)_

---

## 🌐 Fresh Narratives (Web)

1. **[Article Title](url)**
   > Snippet from search result.

2. ...

_(up to 5 items; section omitted if no BRAVE_API_KEY)_

---

## 📊 Source Summary

| Source | Items Found | Items Used | Status |
|--------|------------|------------|--------|
| arXiv | {n} | {m} | ✅ / ⚠️ partial / ❌ failed |
| GitHub Trending | {n} | {m} | ✅ / ⚠️ / ❌ |
| Hacker News | {n} | {m} | ✅ / ⚠️ / ❌ |
| Web Search | {n} | {m} | ✅ / ⚠️ / ❌ / ⏭️ skipped |

---

_Next track: {next_track_display_name} | Archive: memory/autoresearch-archive.md_
```

### Archive format (`autoresearch-archive.md`)

Each run appends:

```markdown

---

<!-- autoresearch:{track_name}:{YYYY-MM-DD} -->

{full report markdown (same as latest)}
```

The HTML comment marker enables programmatic extraction by date/track.

### Telegram teaser (stdout)

```
🔬 **Nightly Research: {track_display_name}**
• Top paper: {arxiv[0].title[:60]}… — {arxiv[0].summary[:80]}…
• Trending: {github[0].title} ⭐{stars} | HN: {hn[0].title[:50]}…
```

If a source returned 0 items, its slot in the teaser is replaced with the next available source. If all sources failed, teaser is:

```
⚠️ **Nightly Research: {track_display_name}** — all sources failed. Check logs.
```

---

## 5. Error Handling Strategy

### Per-Source Fallback (Independent Failure)

Each of the 4 sources runs independently via `asyncio.gather(return_exceptions=True)`. A failure in one source does NOT block others.

| Source | Failure Mode | Fallback |
|--------|-------------|----------|
| **arXiv** | HTTP timeout (>15s), XML parse error, rate-limited (503) | Return `[]`, log warning. arXiv is occasionally slow; not critical. |
| **GitHub Trending** | HTTP error, HTML structure change (regex fails) | Return `[]`, log warning. Include a structural canary check: if 0 `<article class="Box-row">` found, log `STRUCTURE_CHANGED` for manual review. |
| **Hacker News** | Firebase API down, item fetch timeout | Return whatever items were fetched before timeout. Use `asyncio.wait_for()` with 30s total budget for HN. |
| **Web Search** | No `BRAVE_API_KEY`, API error, rate limit | If no key: skip silently (expected for most setups). If API error: return `[]`, log warning. |

### Pipeline-Level Failures

| Condition | Behaviour |
|-----------|-----------|
| **All 4 sources return `[]`** | Exit code 1. Print error teaser to stdout. Do NOT write empty report to latest. Do NOT advance state (so same track retries next night). |
| **config.json missing/corrupt** | Exit code 2. Print `ERROR: config.json not found or invalid JSON` to stderr. |
| **state.json corrupt** | Reset to default state (track_index=0). Log warning. Continue. |
| **Disk write fails** | Exit code 1. Log error. Do NOT advance state. |
| **--dry-run** | Fetch + synthesise + print. No file writes, no state change. Exit 0. |

### Logging

- All log output goes to **stderr** (teaser/output goes to stdout).
- Format: `[autoresearch] {LEVEL} {timestamp} {message}`
- Levels: `INFO` (source counts, track selection), `WARN` (source failures, degraded), `ERROR` (pipeline failures).
- `--verbose` flag adds `DEBUG` level (raw API responses, timing).

### Retry Policy

- **No retries within a single run.** Sources are best-effort, nightly. A transient failure will self-heal next run.
- Rationale: Keeps run time predictable (<60s). Nightly cadence means tomorrow fixes today's transient failure.

---

## 6. Test Plan

### 6.1 Unit Tests (pytest, `scripts/test_*.py`)

| Test File | What It Tests |
|-----------|--------------|
| `test_state.py` | `load_state` with missing/corrupt/valid state.json; `advance_track` cycles correctly; `override_track` validates input |
| `test_sources.py` | Each fetcher with mocked HTTP responses (use `httpx` mocking or `respx`); XML parsing for arXiv; HTML parsing for GitHub; JSON parsing for HN; Brave API response parsing |
| `test_synthesise.py` | `deduplicate` removes URL dupes; `rank_items` sorts correctly; `build_report` produces valid markdown with all sections; `build_teaser` fits 3-line format; edge case: all sources empty |
| `test_run.py` | Integration: mock all fetchers, verify file writes (latest + archive), state advancement, exit codes |

### 6.2 Mock Data

Create `scripts/fixtures/` with:
- `arxiv_response.xml` — 3 sample arXiv Atom entries
- `github_trending.html` — 5 sample `<article class="Box-row">` blocks
- `hn_topstories.json` — 10 story IDs
- `hn_item_*.json` — 3 sample story items
- `brave_search.json` — sample Brave API response

### 6.3 Integration Test

```bash
# Dry run — fetches real data, prints report, no file writes
uv run --with httpx python scripts/run.py --track ai --dry-run --verbose
```

Verify:
- Exit code 0
- stdout contains teaser (3 lines, starts with 🔬)
- stderr contains INFO logs for each source
- No files written

### 6.4 Manual Smoke Test

```bash
# Full run with ai track
uv run --with httpx python scripts/run.py --track ai

# Verify outputs
cat ~/.openclaw/workspace/memory/autoresearch-latest.md | head -20
tail -5 ~/.openclaw/workspace/memory/autoresearch-archive.md
cat skills/autoresearch/state.json
```

### 6.5 Regression Checks

- Run with `BRAVE_API_KEY` unset → web section gracefully omitted
- Corrupt `state.json` → resets and continues
- Delete `state.json` → creates fresh on first run
- Network offline → all sources return `[]` → exit 1, no file write, no state advance

---

## 7. Constraints and Assumptions

### Constraints

| Constraint | Detail |
|-----------|--------|
| **No LLM calls** | v1 uses structured merging only. Zero cost per run. LLM synthesis is a future enhancement. |
| **No new dependencies beyond httpx** | Uses `httpx` (already available via `uv run --with httpx`), `xml.etree.ElementTree` (stdlib), `json` (stdlib), `re` (stdlib), `asyncio` (stdlib), `argparse` (stdlib), `pathlib` (stdlib). |
| **Runtime < 60 seconds** | All HTTP calls have 15s timeout. HN has 30s total budget. Worst case: 4 × 15s sequential = 60s. Typical: <15s (concurrent). |
| **No auth required for core sources** | arXiv (public API), GitHub trending (public page), HN (public Firebase API). Only web_search needs `BRAVE_API_KEY` (optional). |
| **Python 3.10+** | Uses `X | Y` union syntax, `match` statement not used (compatibility). Dataclasses with `field()`. |
| **Atomic file writes** | Write to `{path}.tmp` then `os.rename()` to prevent partial writes on crash. |
| **Archive growth** | ~5KB per run × 365 nights = ~1.8MB/year. No rotation needed for years. |

### Assumptions

| Assumption | Detail |
|-----------|--------|
| **Cron runs as the OpenClaw agent** | The cron job is configured in OpenClaw's cron system, runs as the agent user, has access to the workspace. |
| **Telegram notification handled externally** | `run.py` prints the teaser to stdout. The cron wrapper (or agent) captures stdout and sends via `message` tool. This keeps the script decoupled from messaging infrastructure. |
| **GitHub trending HTML structure stays stable** | The `<article class="Box-row">` pattern with `<h2>` containing repo link has been stable for years. A structural canary logs a warning if it changes. |
| **arXiv API availability** | arXiv API has known rate limits (3 req/s burst, but we make 1-4 requests). Occasional 503s are expected and handled. |
| **Book draft integration reads `autoresearch-latest.md`** | Other cron jobs or agents can simply `cat` or read this file. No API needed. |
| **`~` expansion** | Config paths with `~` are expanded via `Path.expanduser()`. |
| **Track rotation persists across restarts** | `state.json` is the single source of truth. No in-memory state survives between runs. |

### Future Enhancements (out of scope for v1)

1. **LLM synthesis pass** — Use a cheap model (Gemini Flash / local Qwen) to write a narrative summary paragraph per section.
2. **RSS/Atom for additional blogs** — Integrate with `blogwatcher` skill for curated blog feeds.
3. **Dedup across runs** — Track seen URLs in state.json to avoid reporting the same trending repo two nights in a row.
4. **Relevance scoring with embeddings** — Replace keyword matching with semantic similarity.
5. **Configurable notification targets** — Support Discord, email in addition to Telegram.

---

## 8. Cron Integration

### Cron entry (OpenClaw cron system)

```
# Nightly autoresearch — 1 AM Sydney (14:00 UTC previous day)
0 14 * * * cd ~/.openclaw/workspace/skills/autoresearch && uv run --with httpx python scripts/run.py 2>>~/.openclaw/workspace/memory/autoresearch-errors.log
```

### Agent wrapper pattern

The OpenClaw agent's cron handler should:
1. Run the command
2. Capture stdout (the teaser)
3. If exit code 0 and stdout non-empty: send teaser notification via Telegram
4. If exit code 1: send failure notification via Telegram
5. stderr is appended to error log file

---

## 9. SKILL.md Outline

```yaml
---
name: autoresearch
description: >
  Nightly research pipeline that rotates through AI/agents, crypto/DeFi, and developer tools tracks.
  Pulls from arXiv, GitHub trending, Hacker News, and web search. Produces structured markdown reports.
---
```

Key sections:
- **Quick start**: `uv run --with httpx python scripts/run.py --dry-run`
- **Configuration**: Edit `config.json` to customise queries per track
- **Output**: `memory/autoresearch-latest.md` (latest), `memory/autoresearch-archive.md` (all)
- **Cron**: 1 AM Sydney nightly
- **CLI flags**: `--track`, `--dry-run`, `--verbose`
- **Dependencies**: `httpx` (via `uv run --with httpx`), optional `BRAVE_API_KEY` for web search
- **Integration**: Book draft cron reads `autoresearch-latest.md`

---

_Plan authored by: Alex Chen (Planner)_
_Date: 2026-03-15_
_Ready for Builder phase._
