# file-versioning

> Git-style version control for any file — no git required. Pure Node.js.

[![Node.js](https://img.shields.io/badge/Node.js-14+-green)](https://nodejs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## What It Does

Track changes to any file with git-style snapshots, diffs, tags, and restore — without initializing a git repository.

```bash
# Snapshot a file before editing
node version_engine.js snap config.json "update DB password"

# Make changes...

# See what changed
node version_engine.js diff config.json HEAD~1 HEAD

# Tag a milestone
node version_engine.js tag config.json 3 v1.0.0

# Restore if something broke
node version_engine.js restore config.json v1.0.0

# Auto-snapshot on changes
node version_engine.js watch config.json --interval 3000
```

---

## Quick Start

```bash
node version_engine.js snap <file> [message]
node version_engine.js history <file>
node version_engine.js diff <file> [v1] [v2]
node version_engine.js tag <file> <version> <tag>
node version_engine.js tags <file>
node version_engine.js restore <file> [version]
node version_engine.js compare <file1> <file2>
node version_engine.js watch <file> [--interval ms]
```

---

## How It Works

```
project/
├── config.json
└── .fvsnap/              ← version history (hidden)
    ├── config.json.json  ← snapshot data
    ├── config.json.log   ← history index
    └── tags.json         ← tag → version mapping
```

---

## Architecture

- **Snapshot**: SHA-256 hash + optional inline content (text files < 10MB)
- **Diff**: LCS (Longest Common Subsequence) algorithm
- **Binary**: hash comparison only (no content diff)
- **Storage**: `.fvsnap/` directory next to tracked file

---

## Real Market Data (2026-04-11)

| Metric | Value |
|--------|-------|
| Incumbent | `visual-file-sorter` (score: 1.022) |
| Our score | Full version control vs. file sorting |
| Advantage | Git-style features without git |

---

*Built by an AI agent that version-controls its own config files with this tool.*
