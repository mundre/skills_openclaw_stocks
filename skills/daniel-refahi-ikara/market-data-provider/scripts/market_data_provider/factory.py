from __future__ import annotations

from .config import load_config
from .errors import DataSourceError
from .protocols import MarketDataProvider
from .providers.eodhd import EODHDMarketDataProvider
from .providers.mock import MockMarketDataProvider


def create_market_data_provider() -> MarketDataProvider:
    config = load_config()
    if config.provider == "eodhd":
        return EODHDMarketDataProvider(
            api_token=config.eodhd_api_token,
            timeout_seconds=config.timeout_seconds,
        )
    if config.provider == "mock":
        return MockMarketDataProvider()
    raise DataSourceError(f"Unsupported market data provider: {config.provider}")
