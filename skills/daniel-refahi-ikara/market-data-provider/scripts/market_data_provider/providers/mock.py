from __future__ import annotations

from datetime import UTC, date, datetime

from ..models import Instrument, PriceBar, ProviderHealth, Quote


class MockMarketDataProvider:
    provider_name = "mock"

    def healthcheck(self) -> ProviderHealth:
        return ProviderHealth(
            ok=True,
            provider=self.provider_name,
            message="Mock provider reachable",
            checked_at=datetime.now(UTC),
            details={"mode": "mock"},
        )

    def get_instrument(self, symbol: str, exchange: str | None = None) -> Instrument | None:
        return Instrument(symbol=symbol, name=f"Mock {symbol}", exchange=exchange, provider=self.provider_name)

    def search_instruments(self, query: str, limit: int = 10) -> list[Instrument]:
        return [Instrument(symbol="MOCK.US", name=f"Mock result for {query}", exchange="US", provider=self.provider_name)][:limit]

    def get_latest_quote(self, symbol: str) -> Quote:
        return Quote(
            symbol=symbol,
            price=100.0,
            timestamp=datetime.now(UTC),
            currency="USD",
            exchange="MOCK",
            provider=self.provider_name,
        )

    def get_eod_bars(
        self,
        symbol: str,
        start: date | None = None,
        end: date | None = None,
        limit: int | None = None,
    ) -> list[PriceBar]:
        bars = [
            PriceBar(
                symbol=symbol,
                timestamp=datetime.now(UTC),
                open=99.0,
                high=101.0,
                low=98.5,
                close=100.0,
                adjusted_close=100.0,
                volume=100000,
                exchange="MOCK",
                currency="USD",
                provider=self.provider_name,
            )
        ]
        return bars[-limit:] if limit is not None else bars
