# Interface

## Protocol

`MarketDataProvider` exposes a stable interface for report engines and strategy layers.

### Required methods
- `healthcheck() -> ProviderHealth`
- `get_instrument(symbol: str, exchange: str | None = None) -> Instrument | None`
- `search_instruments(query: str, limit: int = 10) -> list[Instrument]`
- `get_latest_quote(symbol: str) -> Quote`
- `get_eod_bars(symbol: str, start: date | None = None, end: date | None = None, limit: int | None = None) -> list[PriceBar]`

## Current provider support
- `eodhd` — live market data backend
- `mock` — offline/testing backend

## Developer example
```python
from market_data_provider.factory import create_market_data_provider

provider = create_market_data_provider()
quote = provider.get_latest_quote("AAPL.US")
print(quote.price)
```

## Design constraints
- Return normalized models only.
- Raise typed provider errors.
- Keep raw API shape hidden inside provider adapters.
- Keep provider selection in the factory.
- Support at least one offline/testing backend so downstream code can be exercised without a live vendor.

## Error types
- `DataSourceError`
- `AuthenticationError`
- `RateLimitError`
- `SymbolNotFoundError`
- `TemporaryProviderError`
- `SchemaMappingError`

## Normalized models

### Instrument
- `symbol`
- `name`
- `exchange`
- `country`
- `currency`
- `provider`
- `raw` (optional debug payload)

### Quote
- `symbol`
- `price`
- `timestamp`
- `currency`
- `exchange`
- `provider`
- `raw` (optional debug payload)

### PriceBar
- `symbol`
- `timestamp`
- `open`
- `high`
- `low`
- `close`
- `adjusted_close`
- `volume`
- `provider`
- `exchange`
- `currency`
- `raw` (optional debug payload)
