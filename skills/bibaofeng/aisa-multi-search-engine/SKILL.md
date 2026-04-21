---
name: aisa-multi-search-engine
description: "Run web search, scholar search, Tavily search and extract, smart search, and Perplexity-style deep research through one AISA skill. Use when: the user needs broad web research, academic search, URL extraction, or multi-source evidence gathering."
author: aisa
version: "1.0.0"
license: Apache-2.0
user-invocable: true
primaryEnv: AISA_API_KEY
requires:
  env:
    - AISA_API_KEY
  bins:
    - python3
metadata:
  openclaw:
    primaryEnv: AISA_API_KEY
    requires:
      env:
        - AISA_API_KEY
      bins:
        - python3
---
# AISA Multi Search Engine

## When to Use

- Run web search, scholar search, Tavily search and extract, smart search, and Perplexity-style deep research through one AISA skill. Use when: the user needs broad web research, academic search, URL extraction, or multi-source evidence gathering.

## When NOT to Use

- Do not use this skill for browser-cookie extraction, passwords, Keychain access, or other local sensitive credential access.
- Prefer a different skill when the user request is outside this skill's domain.

## Capabilities

- Bundle seven search modes behind one AISA API key and one Python client.
- Cover structured web search, academic search, smart hybrid search, Tavily search and extract, Perplexity deep research, and multi-source synthesis.
- Fit research, due diligence, market scanning, and evidence collection workflows.

## Quick Start

```bash
export AISA_API_KEY="your-key"
```

## Primary Runtime

Use the bundled Python client as the canonical ClawHub runtime path:

```bash
python3 scripts/search_client.py
```

## Example Queries

- Use multi-source research to compare agent frameworks released in 2026.
- Search academic papers about multimodal reasoning from 2024 onward.
- Extract the main content from a list of URLs and summarize the overlaps.

## Notes

- The shipped Python client is the primary runtime path for ClawHub.
