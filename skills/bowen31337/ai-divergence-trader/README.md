# Polymarket AI Divergence Trader

Find markets where AI consensus diverges from the real market price, then trade the edge.

## What It Does

1. Scans all active markets for AI vs market price divergence
2. Filters to markets with edge above threshold (default 2%) and zero fees
3. Checks safeguards (flip-flop detection, existing positions)
4. Sizes using Kelly criterion, capped conservatively
5. Executes trades on the mispriced side

## Quick Start

```bash
# Scan only (dry run)
python ai_divergence.py

# Scan + execute trades
python ai_divergence.py --live
```

## Configuration

This is a template skill. Customize edge thresholds, sizing strategies, and filters for your own trading logic.

## Installation

```bash
clawhub install polymarket-ai-divergence
```

## License

MIT
