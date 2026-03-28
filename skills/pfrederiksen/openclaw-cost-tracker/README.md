# OpenClaw Cost Tracker

[![ClawHub](https://img.shields.io/badge/ClawHub-openclaw--cost--tracker-blue)](https://clawhub.ai/pfrederiksen/openclaw-cost-tracker)
[![Version](https://img.shields.io/badge/version-1.1.1-green)]()

An [OpenClaw](https://openclaw.ai) skill that parses session JSONL files to compute per-model token usage, costs, and daily spend trends. No API keys needed — reads directly from local session files.

## Features

- 💰 **Per-model breakdown** — cost, tokens, and request count by model
- 📊 **Daily spend chart** — text bar chart or JSON array for dashboards
- 🔍 **Token split** — input, output, cache read/write breakdown
- 📅 **Date filtering** — `--days N` or `--since YYYY-MM-DD`
- 📄 **JSON output** — `--format json` for integrations
- 🗂️ **`--agents-dir`** — point at any directory; no system-wide access required

## Installation

```bash
clawhub install openclaw-cost-tracker
```

## Usage

```bash
# All-time summary
python3 scripts/cost_tracker.py

# Last 7 days
python3 scripts/cost_tracker.py --days 7

# JSON output
python3 scripts/cost_tracker.py --format json

# Point at a specific agents directory (safe for non-root review)
python3 scripts/cost_tracker.py --agents-dir ~/sample-agents-copy
```

## Security

**No network calls.** The complete import list is: `json`, `os`, `sys`, `argparse`, `datetime`, `timedelta`, `typing`, `pathlib`, `re` — all Python stdlib. You can verify this yourself:

```bash
grep -n "^import\|^from" scripts/cost_tracker.py
```

**No writes.** The script only reads JSONL files and prints to stdout. No files are created or modified.

**No subprocess / shell execution.** No `subprocess`, `os.system`, `eval`, or `exec` anywhere in the source.

**Minimal directory access.** Only reads `*.jsonl` files under the agents directory. Use `--agents-dir` to point at a sample copy before running against your live data.

**Run as non-root.** The script needs no elevated permissions. Run it as a normal user.

You can audit the full 296-line source at [scripts/cost_tracker.py](scripts/cost_tracker.py) before installing.

## Requirements

- OpenClaw installed with session data in `~/.openclaw/agents/`
- Python 3.8+

## License

MIT

## Links

- [ClawHub](https://clawhub.ai/pfrederiksen/openclaw-cost-tracker)
- [OpenClaw](https://openclaw.ai)
- [Full source](scripts/cost_tracker.py)
