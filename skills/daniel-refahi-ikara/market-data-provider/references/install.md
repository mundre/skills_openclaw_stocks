# Installation

## Storefront / quick install
Use these commands after the skill is installed under `~/.openclaw/workspace/skills/market-data-provider`.

### Live EODHD setup
```bash
cd ~/.openclaw/workspace
export MARKET_DATA_PROVIDER=eodhd
export EODHD_API_TOKEN="YOUR_EODHD_TOKEN"
export MARKET_DATA_TIMEOUT_SECONDS=20
export MARKET_DATA_SMOKE_SYMBOL=AAPL.US
python3 ~/.openclaw/workspace/skills/market-data-provider/scripts/smoke_test.py
```

### Offline mock setup
```bash
cd ~/.openclaw/workspace
export MARKET_DATA_PROVIDER=mock
python3 ~/.openclaw/workspace/skills/market-data-provider/scripts/smoke_test.py
```

## Expected result
The smoke test prints JSON with:
- `provider`
- `health.ok: true`
- a sample `quote`

## Developer quick start
Set `PYTHONPATH` so Python can import the installed package directly.

```bash
export PYTHONPATH="$HOME/.openclaw/workspace/skills/market-data-provider/scripts:$PYTHONPATH"
export MARKET_DATA_PROVIDER=eodhd
export EODHD_API_TOKEN="YOUR_EODHD_TOKEN"
```

Then use it in Python:

```python
from market_data_provider.factory import create_market_data_provider

provider = create_market_data_provider()
health = provider.healthcheck()
quote = provider.get_latest_quote("AAPL.US")
bars = provider.get_eod_bars("AAPL.US", limit=5)

print(health)
print(quote)
print(bars)
```

## Configuration
Required for live EODHD:
- `MARKET_DATA_PROVIDER=eodhd`
- `EODHD_API_TOKEN=<token>` or `EODHD_API_KEY=<token>`

Optional:
- `MARKET_DATA_TIMEOUT_SECONDS=20`
- `MARKET_DATA_SMOKE_SYMBOL=AAPL.US`

Offline/testing:
- `MARKET_DATA_PROVIDER=mock`

## Notes
- The package import root lives at `~/.openclaw/workspace/skills/market-data-provider/scripts`.
- Downstream code should import `create_market_data_provider()` from `market_data_provider.factory`.
- Report engines should not import provider-specific modules directly.
