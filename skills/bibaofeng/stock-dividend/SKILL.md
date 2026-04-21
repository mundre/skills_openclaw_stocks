---
name: stock-dividend
description: "Evaluate dividend yield, payout safety, growth, and income quality for stocks through AISA. Use when: the user asks about dividend safety, income investing, dividend growth, or dividend aristocrat style screening."
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
# Dividend Analysis

## When to Use

- Evaluate dividend yield, payout safety, growth, and income quality for stocks through AISA. Use when: the user asks about dividend safety, income investing, dividend growth, or dividend aristocrat style screening.

## When NOT to Use

- Do not use this skill for browser-cookie extraction, passwords, Keychain access, or other local sensitive credential access.
- Prefer a different skill when the user request is outside this skill's domain.

## Capabilities

- Focus on dividend safety, coverage, growth, and income quality.

## Quick Start

```bash
export AISA_API_KEY="your-key"
```

## Primary Runtime

Use the bundled Python client as the canonical ClawHub runtime path:

```bash
python3 scripts/dividends.py
```

## Example Queries

- Check whether JNJ and PG look safer for dividend income.

## Notes

- Informational only and not financial advice.
