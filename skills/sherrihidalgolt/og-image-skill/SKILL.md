---
name: og-image-skill
description: Generate og image images using the Neta AI API. Returns a direct image URL.
tools: Bash
---

# OG Image Generator

Generate stunning og image generator ai images from a text description. Get back a direct image URL instantly.

## When to use
Use when someone asks to generate or create og image generator images.

## Quick start
```bash
node ogimage.js "your description here"
```

## Options
- `--size` — `portrait`, `landscape`, `square`, `tall` (default: `landscape`)


## Token

Requires a Neta API token via `NETA_TOKEN` env var or `--token` flag.
- Global: <https://www.neta.art/open/>
- China:  <https://app.nieta.art/security>

```bash
export NETA_TOKEN=your_token_here
```

## Install
```bash
npx skills add SherriHidalgolt/og-image-skill
```
