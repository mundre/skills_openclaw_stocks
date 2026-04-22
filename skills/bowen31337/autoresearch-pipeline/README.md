# AutoResearch

Zero-cost nightly research aggregator that rotates through topic tracks, pulls from independent sources, and synthesises structured markdown reports.

## Features

- Rotates through configurable topic tracks
- Pulls from multiple independent research sources
- Synthesises structured markdown reports
- Outputs Telegram-compatible teasers

## Quick Start

```bash
# Dry run — fetches data, prints teaser, no file writes
uv run --with httpx python skills/autoresearch/scripts/run.py --dry-run

# Full run — writes reports and advances state
uv run --with httpx python skills/autoresearch/scripts/run.py

# Force a specific track
uv run --with httpx python skills/autoresearch/scripts/run.py --track crypto
```

## Requirements

- Chromium-based browser installed
- Python with httpx

## Installation

```bash
clawhub install autoresearch
```

## License

MIT
