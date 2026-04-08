from __future__ import annotations

from datetime import date
from typing import Protocol

from .models import Instrument, PriceBar, ProviderHealth, Quote


class MarketDataProvider(Protocol):
    provider_name: str

    def healthcheck(self) -> ProviderHealth: ...

    def get_instrument(self, symbol: str, exchange: str | None = None) -> Instrument | None: ...

    def search_instruments(self, query: str, limit: int = 10) -> list[Instrument]: ...

    def get_latest_quote(self, symbol: str) -> Quote: ...

    def get_eod_bars(
        self,
        symbol: str,
        start: date | None = None,
        end: date | None = None,
        limit: int | None = None,
    ) -> list[PriceBar]: ...
