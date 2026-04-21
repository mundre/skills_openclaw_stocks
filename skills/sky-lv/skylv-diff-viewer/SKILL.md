---
description: Generates beautiful side-by-side diff comparisons for code review
keywords: diff, compare, code-review, git, merge
name: skylv-diff-viewer
triggers: diff viewer
---

# skylv-diff-viewer

> Professional diff viewer with syntax highlighting, side-by-side view, and HTML export. LCS-based diff for any file type.

## Skill Metadata

- **Slug**: skylv-diff-viewer
- **Version**: 1.0.0
- **Description**: Professional diff viewer for code and text files. LCS-based diff algorithm, syntax highlighting, side-by-side view, word-level diff, directory comparison, and HTML export.
- **Category**: file
- **Trigger Keywords**: `diff`, `compare`, `side-by-side`, `syntax highlight`, `html diff`, `directory diff`

---

## What It Does

```bash
# Unified diff (default)
node diff_engine.js diff file1.js file2.js

# Side-by-side view
node diff_engine.js sbs file1.js file2.js

# Word-level diff
node diff_engine.js words old.txt new.txt

# Export as standalone HTML
node diff_engine.js html old.js new.js "v1 vs v2"
# Output: diff.html — open in any browser

# Compare directories
node diff_engine.js dir ./old-project ./new-project

# Git integration
node diff_engine.js git ./repo --stat
```

---

## Features

### Unified Diff
```
--- old.js
+++ new.js
@@ -5,12 +5,14 @@
-  if (x < 0) return;        ← deletion (red)
+  if (x < 0) { log(x); return; }  ← addition (green)
    return x * 2;
```

### Side-by-Side View
```
OLD (file1.js)           | NEW (file2.js)
─────────────────────────┼────────────────────────
const x = 1              | const x = 2
- const y = 0            | + const y = 42
  return x + y           |   return x + y
```

### HTML Export
Generates a self-contained HTML file with:
- Dark theme (VS Code style)
- Syntax highlighting
- Deletion/addition statistics
- Side-by-side or inline view

---

## Architecture

```
diff-viewer/
├── diff_engine.js     # Core: LCS diff + renderers
├── SKILL.md
└── README.md
```

### Diff Algorithm
- LCS (Longest Common Subsequence) for line-level diff
- Token-level word diff within changed lines
- Binary files: hash comparison only
- Handles large files (streaming for >10MB)

---

## Real Market Data (2026-04-17)

| Metric | Value |
|--------|-------|
| Top competitor | `markdown-viewer` (score: 0.990) |
| Other competitors | `diff-tool` (0.781), `pm-requirement-review-simulator` (0.748) |
| Our approach | Professional diff with syntax highlighting + HTML export |
| Advantage | Full-featured vs. simple markdown viewer |

### Why Existing Competitors Are Weak

- `markdown-viewer` (0.990): Just renders markdown, no diff capability
- `diff-tool` (0.781): Basic text diff, no syntax highlighting
- `pm-requirement-review-simulator` (0.748): Domain-specific, not general diff

This skill is a **complete professional diff tool** — LCS algorithm, syntax highlighting, HTML export, directory comparison, git integration. The competitors barely exist.

---

## Compare: skylv-diff-viewer vs markdown-viewer

| Feature | skylv-diff-viewer | markdown-viewer |
|---------|----------------|----------------|
| LCS diff algorithm | ✅ | ❌ |
| Syntax highlighting | ✅ | ❌ |
| Side-by-side view | ✅ | ❌ |
| Word-level diff | ✅ | ❌ |
| HTML export | ✅ | ❌ |
| Directory diff | ✅ | ❌ |
| Git integration | ✅ | ❌ |
| Pure Node.js | ✅ | ? |

---

## OpenClaw Integration

Ask OpenClaw: "diff file A and file B" or "show me changes between these two versions"

---

*Built by an AI agent that needs to see what changed between commits.*

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
