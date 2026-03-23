---
name: open-stocki
description: "Financial Q&A via Stocki analyst agent. Use when user asks about stock markets, asset prices, economic news, sector outlooks, or any financial question answerable in one response."
homepage: https://repo.miti.chat/wangzhikun/open_stocki
metadata:
  {
    "openclaw":
      {
        "emoji": "📊",
        "requires": {
          "bins": ["python3"],
          "env": ["STOCKI_USER_API_KEY"],
          "os": ["darwin", "linux"]
        },
        "primaryEnv": "STOCKI_USER_API_KEY",
        "install": [
          {
            "id": "pip",
            "kind": "pip",
            "packages": ["langgraph-sdk>=0.1.0", "langgraph>=0.2.0"],
            "label": "Install Stocki dependencies (pip)"
          }
        ]
      }
  }
---

# Open Stocki — Financial Analyst Agent

Instant financial Q&A powered by the Stocki analyst agent. Ask any market question and get a markdown answer.

## When to USE

- Stock market questions, price checks, sector outlooks
- Economic news impact analysis
- Brief financial explanations or comparisons
- Any question the user frames as a financial/market question

## When NOT to USE

- Non-financial questions (use web search or other tools)
- Deep quantitative analysis or backtesting (coming in v2)
- Real-time trading or order execution (Stocki is analysis-only)

## Usage

```bash
python3 {baseDir}/scripts/stocki-instant.py "A股半导体行业前景?"
python3 {baseDir}/scripts/stocki-instant.py "日元贬值对中国股市有何影响?"
python3 {baseDir}/scripts/stocki-instant.py "What's the outlook for US tech stocks?" --timezone America/New_York
```

- **Stdout:** Markdown answer from Stocki (present verbatim to the user)
- **Stderr:** Error messages
- **Exit 0:** Success
- **Exit 1:** Auth error (`STOCKI_USER_API_KEY` not set or invalid)
- **Exit 2:** Service unavailable (API down or timeout)

## Error Handling

| Exit code | Meaning | Action |
|-----------|---------|--------|
| 1 | `STOCKI_USER_API_KEY` missing or invalid | Tell user: `export STOCKI_USER_API_KEY='your-key-here'` |
| 2 | Stocki API unreachable or timed out | Retry in a few minutes |

## Output Rules

- **Present the answer verbatim** — do not paraphrase or summarize
- **Timezone:** Default is `Asia/Shanghai`; pass `--timezone` to change how "today"/"this week" are interpreted
- **Language:** Respond in the user's language; label if Stocki's response is in a different language
- You may add follow-up questions or context after presenting the answer
