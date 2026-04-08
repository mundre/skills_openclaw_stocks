---
name: market-data-provider
description: "Portable market data provider module for stock-report agents. Use when creating, installing, testing, or extending a provider-agnostic market data layer with a stable protocol interface, normalized models, provider factory, smoke tests, and pluggable backends such as EODHD. Use when report engines or strategy layers need market data without depending on a specific API vendor."
---

# Market Data Provider

Build and maintain a provider-agnostic market data module that other agent workspaces can reuse.

## What this skill provides
- A stable `MarketDataProvider` protocol
- Normalized domain models
- A provider factory selected by config
- Initial backends: `eodhd`, `mock`
- A smoke test script for installation checks

## Design rules
- Keep report logic out of the module.
- Keep strategy logic out of the module.
- Keep execution/broker logic out of the module.
- Return normalized models, not raw vendor payloads.
- Add new providers under `references/providers/` and `scripts/market_data_provider/providers/` without changing caller-facing interfaces.

## Package layout
- `scripts/market_data_provider/` — reusable Python package
- `scripts/smoke_test.py` — provider connectivity check
- `scripts/release.py` — repeatable release helper
- `VERSION` — semantic version for the skill
- `references/install.md` — installation/storefront instructions
- `references/release-process.md` — release checklist
- `references/compatibility.md` — stability policy
- `references/interface.md` — protocol and model contract
- `references/providers/eodhd.md` — EODHD-specific notes
- `scripts/market_data_provider/providers/mock.py` — offline/testing backend

## Default config contract
- `MARKET_DATA_PROVIDER=eodhd` (or `mock` for offline testing)
- `EODHD_API_TOKEN` preferred
- `EODHD_API_KEY` fallback
- `MARKET_DATA_TIMEOUT_SECONDS` optional

## Use from other code
Import only the factory or protocol-facing types.

```python
from market_data_provider.factory import create_market_data_provider

provider = create_market_data_provider()
health = provider.healthcheck()
quote = provider.get_latest_quote("AAPL.US")
```

Do not import provider-specific modules directly from report engines.

## Installation on another agent
Use these exact steps in the storefront or install notes:
1. Install or copy `market-data-provider` into `skills/`.
2. Set `MARKET_DATA_PROVIDER=eodhd` for live data or `MARKET_DATA_PROVIDER=mock` for offline testing.
3. If using EODHD, set `EODHD_API_TOKEN` (preferred) or `EODHD_API_KEY`.
4. Run `python3 skills/market-data-provider/scripts/smoke_test.py`.
5. Confirm the JSON output shows provider health and a sample quote.
6. Import `create_market_data_provider()` from `market_data_provider.factory` in downstream code.

For fuller install text, read `references/install.md`.

## Release discipline
- Keep `VERSION` current.
- Follow `references/release-process.md` before shipping.
- Preserve stable install and import paths per `references/compatibility.md`.
- Repackage `market-data-provider.skill` after changes.

## When extending
When adding a provider:
1. Implement `MarketDataProvider`.
2. Normalize data into shared models.
3. Add provider-specific env/config parsing.
4. Register it in the factory.
5. Extend the smoke test or add provider-specific checks.
