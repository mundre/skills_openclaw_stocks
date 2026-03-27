---
name: extract-formulas-from-pdf
description: "Extract Formulas from PDF - extract mathematical formulas from PDF documents using MinerU. Use when a PDF contains LaTeX or math formulas."
homepage: https://mineru.net
metadata: {"openclaw": {"emoji": "📄", "requires": {"bins": ["mineru-open-api"], "env": ["MINERU_TOKEN"]}, "primaryEnv": "MINERU_TOKEN", "install": [{"id": "npm", "kind": "node", "package": "mineru-open-api", "bins": ["mineru-open-api"], "label": "Install via npm"}, {"id": "go", "kind": "go", "package": "github.com/opendatalab/MinerU-Ecosystem/cli/mineru-open-api", "bins": ["mineru-open-api"], "label": "Install via go install", "os": ["darwin", "linux"]}]}}
---

# Extract Formulas From Pdf

Convert and extract content from .pdf using MinerU (`mineru-open-api`).

## Install

```bash
npm install -g mineru-open-api
# or via Go (macOS/Linux):
go install github.com/opendatalab/MinerU-Ecosystem/cli/mineru-open-api@latest
```

## Quick Start

```bash
# Extract formulas from PDF (requires token)
mineru-open-api extract paper.pdf -o ./out/

# With VLM for better formula accuracy
mineru-open-api extract paper.pdf --model vlm -o ./out/
```

## Authentication

Token required for `extract` and `crawl`:

```bash
mineru-open-api auth            # Interactive token setup
export MINERU_TOKEN="your-token" # Or via environment variable
```

Create token at: https://mineru.net/apiManage/token

## Capabilities

- Supports local files and URLs
- Requires token (`mineru-open-api auth` or `MINERU_TOKEN` env)
- Supported input: .pdf
- Language hint with `--language` (default: `ch`, use `en` for English)
- Page range with `--pages` (where applicable)

## Notes

- Formula recognition requires `extract` with token. Use `--formula` flag (enabled by default). Output is Markdown with LaTeX inline.
- Output goes to stdout by default; use `-o <dir>` to save to file
- Binary formats (docx) require `-o` flag (cannot stream to stdout)
- All progress/status messages go to stderr
- MinerU is an open-source project by OpenDataLab (Shanghai AI Lab): https://github.com/opendatalab/MinerU
