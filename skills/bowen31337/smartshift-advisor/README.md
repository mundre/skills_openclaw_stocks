# SmartShift Advisor

Battery discharge/charge strategy advisor using Amber Electric prices + solar forecast + inverter state.

## Installation

```bash
cp -r . ~/.openclaw/workspace/skills/smartshift-advisor/
```

## Scripts

- `scripts/amber_prices.py` — Fetch current + forecast Amber prices (JSON output)
- `scripts/solar_forecast.py` — Fetch solar generation forecast via Open-Meteo (JSON output)
- `scripts/inverter_state.py` — Read inverter/battery state from HA or local API (JSON output)
- `scripts/write_advice.py` — Write recommendation to HA input helper

## Configuration

Edit `config.json` to set your Amber API key and site ID, or use environment variables:
- `AMBER_API_KEY` — Your Amber Electric API key
- `AMBER_SITE_ID` — Your Amber site identifier

## Strategy Logic

| Condition | Strategy |
|-----------|----------|
| Feed-in > 15c AND battery > 70% | aggressive_export |
| Feed-in > 8c AND battery > 50% | moderate_export |
| Feed-in < 5c AND battery < 30% | conservative_hold |
| Buy price < 5c (negspot) | grid_charge |
| Battery < 10% | emergency_hold |

## License

MIT — see [LICENSE](./LICENSE)
