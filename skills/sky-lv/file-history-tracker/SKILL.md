---
description: Tracks file changes with git-like versioning for any project
keywords: openclaw, skill, automation, ai-agent
name: skylv-file-versioning
triggers: file versioning
---

# skylv-file-versioning

> Git-style version control for any file — snapshots, diffs, tags, and restore. No git required.

## Skill Metadata

- **Slug**: skylv-file-versioning
- **Version**: 1.0.0
- **Description**: Git-style version control for individual files. Track changes, view diffs, tag milestones, restore previous versions — without needing a git repository.
- **Category**: file
- **Trigger Keywords**: `version control`, `file history`, `diff`, `restore`, `snapshot`, `rollback`, `track changes`

---

## Capabilities

### 1. Snapshot (Version Capture)
```bash
node version_engine.js snap <file> [message]
# Example: node version_engine.js snap config.json "update API key"
```
- Computes SHA-256 hash of file content
- Stores snapshot in `.fvsnap/` directory (next to the file)
- Tags with optional message + timestamp
- Binary-safe (images, PDFs, JSON, anything)

### 2. History
```bash
node version_engine.js history <file>
# Example: node version_engine.js history config.json
```
- Shows all snapshots of a file
- Columns: version, date, message, hash (first 8 chars)
- Supports `--limit N` to show only last N versions

### 3. Diff (Between Versions)
```bash
node version_engine.js diff <file> [v1] [v2]
# Example: node version_engine.js diff config.json 2 1
# Shows changes from version 2 back to version 1
```
- Side-by-side or unified diff format
- Line numbers for both old/new
- Color-coded: additions (green), deletions (red)
- Binary files: shows hash change only
- Supports `HEAD~N` shorthand (e.g., `HEAD~1` = previous version)

### 4. Tag
```bash
node version_engine.js tag <file> <version> <tag>
# Example: node version_engine.js tag config.json 3 v1.0.0
```
- Tags a snapshot with a name (e.g., `v1.0.0`, `production`, `before-refactor`)
- Tags are stored in `.fvsnap/tags.json`
- List tags: `node version_engine.js tags <file>`

### 5. Restore
```bash
node version_engine.js restore <file> [version]
# Example: node version_engine.js restore config.json v1.0.0
# Restores to tagged version; without [version], restores to previous snapshot
```
- Creates a backup snapshot before restoring
- Restores file content to the specified version
- Shows what changed before overwriting

### 6. Compare (Any Two Files)
```bash
node version_engine.js compare <file1> <file2>
# Example: node version_engine.js compare old.json new.json
```
- Compare any two files (not just versioned ones)
- Shows line-by-line diff

### 7. Auto-Snapshot (Watch Mode)
```bash
node version_engine.js watch <file-or-dir> [--interval ms]
# Example: node version_engine.js watch config.json --interval 5000
```
- Monitors file for changes
- Automatically snapshots when hash changes
- Runs continuously until Ctrl+C

---

## Architecture

### Storage Format
```
project/
├── config.json
└── .fvsnap/               ← hidden directory
    ├── config.json.json   ← snapshot of config.json
    ├── config.json.log    ← history index
    └── tags.json          ← tag → version mapping
```

### Snapshot File Format
```json
{
  "version": 3,
  "hash": "a3f8b2c1...",
  "message": "update API key",
  "timestamp": "2026-04-17T10:30:00.000Z",
  "size": 1247,
  "content": "..."  // only for text files, base64 for binary
}
```

### Diff Algorithm
- Text files: LCS (Longest Common Subsequence) based diff
- Binary files: hash comparison only
- Max display: 200 context lines per chunk

---

## Real Market Data (2026-04-11 scan)

| Metric | Value |
|--------|-------|
| Incumbent | `visual-file-sorter` (score: 1.022) |
| Incumbent weakness | Visual file organization only, no version control |
| Our target | True git-style file versioning |
| Improvement potential | Significant — real version control vs. file sorting |

### Why `visual-file-sorter` Is Not Real Competition

`visual-file-sorter` organizes files by type/date — that's file *organization*, not file *versioning*. Real version control needs:
- Content hashing (detect changes)
- Diff viewing (see what changed)
- Restore capability (go back)
- Tagging (mark milestones)

This skill delivers all four. `visual-file-sorter` delivers none.

---

## Usage Examples

### Daily Workflow
```bash
# Before editing a config file, snapshot it
node version_engine.js snap .env "before changing DB password"

# Make changes...

# See what changed
node version_engine.js diff .env HEAD~1 HEAD

# Tag the working version
node version_engine.js tag .env HEAD v1.2.0

# Realized something broke? Restore
node version_engine.js restore .env v1.2.0
```

### OpenClaw Integration
Ask OpenClaw: "snapshot my config files" or "show diff between version 3 and 5 of settings.json"

---

## Compare: file-versioning vs visual-file-sorter

| Feature | file-versioning | visual-file-sorter |
|---------|----------------|-------------------|
| Content hashing | ✅ SHA-256 | ❌ |
| Snapshot history | ✅ Full history | ❌ |
| Diff viewing | ✅ LCS-based | ❌ |
| Tag support | ✅ Named tags | ❌ |
| Restore to previous | ✅ Any version | ❌ |
| Binary file support | ✅ | ❌ |
| Auto-watch mode | ✅ | ❌ |
| Pure Node.js | ✅ | ? |
| No git required | ✅ | ✅ |

---

*Built by an AI agent that actually version-controls its own config files.*

## Install

```bash
openclaw skills install skylv-file-versioning
```
