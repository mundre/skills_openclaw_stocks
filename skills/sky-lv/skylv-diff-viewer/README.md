# diff-viewer

> Professional diff viewer with syntax highlighting, side-by-side view, and HTML export.

[![Node.js](https://img.shields.io/badge/Node.js-14+-green)](https://nodejs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Quick Start

```bash
node diff_engine.js diff file1.js file2.js
node diff_engine.js sbs old.json new.json
node diff_engine.js html old.txt new.txt "v1 vs v2"
node diff_engine.js dir ./old-project ./new-project
```

## Features

- LCS (Longest Common Subsequence) diff algorithm
- Syntax highlighting (20+ languages)
- Side-by-side view
- Word-level diff
- HTML export (standalone, dark theme)
- Directory comparison

## HTML Export

```bash
node diff_engine.js html old.js new.js "config changes"
# Opens: diff.html
```

## Architecture

Pure Node.js, no external dependencies.
