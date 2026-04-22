---
metadata.openclaw:
  always: true
  reason: "Auto-classified as always-load (no specific rule for 'smartshift-advisor')"
---

# SmartShift Advisor Skill

Battery discharge/charge strategy advisor using Amber Electric prices + solar forecast + inverter state.

## Scripts

- `scripts/amber_prices.py` — Fetch current + forecast Amber prices (JSON output)
- `scripts/solar_forecast.py` — Fetch solar generation forecast via Open-Meteo (JSON output)  
- `scripts/inverter_state.py` — Read inverter/battery state from HA or local API (JSON output)
- `scripts/write_advice.py` — Receive JSON recommendation via stdin, write to HA input helper

## Config

Edit `config.json` in this directory to set API keys and site IDs.

## Strategy Logic

| Condition | Strategy |
|-----------|----------|
| Feed-in > 15c AND battery > 70% | aggressive_export |
| Feed-in > 8c AND battery > 50% | moderate_export |
| Feed-in < 5c AND battery < 30% | conservative_hold |
| Buy price < 5c (negspot) | grid_charge |
| Battery < 10% | emergency_hold |
