from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import UTC, date, datetime
from typing import Any

from ..errors import AuthenticationError, SchemaMappingError, SymbolNotFoundError, TemporaryProviderError
from ..models import Instrument, PriceBar, ProviderHealth, Quote


class EODHDMarketDataProvider:
    provider_name = "eodhd"
    base_url = "https://eodhd.com/api"

    def __init__(self, api_token: str | None, timeout_seconds: float = 20.0):
        if not api_token:
            raise AuthenticationError("Missing EODHD API token")
        self.api_token = api_token
        self.timeout_seconds = timeout_seconds

    def healthcheck(self) -> ProviderHealth:
        data = self._get_json("/exchanges-list/", {"fmt": "json"})
        count = len(data) if isinstance(data, list) else None
        return ProviderHealth(
            ok=True,
            provider=self.provider_name,
            message="EODHD reachable",
            checked_at=datetime.now(UTC),
            details={"records": count},
        )

    def get_instrument(self, symbol: str, exchange: str | None = None) -> Instrument | None:
        query = symbol if exchange is None else f"{symbol} {exchange}"
        results = self.search_instruments(query=query, limit=10)
        symbol_upper = symbol.upper()
        for item in results:
            base = item.symbol.split(".")[0].upper()
            if item.symbol.upper() == symbol_upper or base == symbol_upper:
                return item
        return results[0] if results else None

    def search_instruments(self, query: str, limit: int = 10) -> list[Instrument]:
        data = self._get_json("/search/", {"s": query, "limit": limit})
        if not isinstance(data, list):
            raise SchemaMappingError("Expected list from EODHD search endpoint")
        return [
            Instrument(
                symbol=str(item.get("Code") or item.get("code") or ""),
                name=item.get("Name") or item.get("name"),
                exchange=item.get("Exchange") or item.get("exchange"),
                country=item.get("Country") or item.get("country"),
                currency=item.get("Currency") or item.get("currency"),
                provider=self.provider_name,
                raw=item,
            )
            for item in data
            if item.get("Code") or item.get("code")
        ]

    def get_latest_quote(self, symbol: str) -> Quote:
        path = f"/real-time/{symbol}"
        data = self._get_json(path, {"fmt": "json"})
        if not isinstance(data, dict):
            raise SchemaMappingError("Expected object from EODHD real-time endpoint")
        if data.get("code") in (404, "404"):
            raise SymbolNotFoundError(symbol)
        price = data.get("close") or data.get("previousClose") or data.get("open")
        if price is None:
            raise SchemaMappingError(f"Missing price in EODHD quote for {symbol}")
        ts = self._parse_epoch(data.get("timestamp"))
        return Quote(
            symbol=symbol,
            price=float(price),
            timestamp=ts,
            currency=data.get("currency"),
            exchange=data.get("exchange") or data.get("gmtoffset"),
            provider=self.provider_name,
            raw=data,
        )

    def get_eod_bars(
        self,
        symbol: str,
        start: date | None = None,
        end: date | None = None,
        limit: int | None = None,
    ) -> list[PriceBar]:
        params: dict[str, Any] = {"fmt": "json"}
        if start:
            params["from"] = start.isoformat()
        if end:
            params["to"] = end.isoformat()
        if limit:
            params["period"] = "d"
        path = f"/eod/{symbol}"
        data = self._get_json(path, params)
        if not isinstance(data, list):
            raise SchemaMappingError("Expected list from EODHD eod endpoint")
        bars = [self._map_bar(symbol, item) for item in data]
        if limit is not None:
            return bars[-limit:]
        return bars

    def _map_bar(self, symbol: str, item: dict[str, Any]) -> PriceBar:
        try:
            ts = datetime.fromisoformat(str(item["date"]) + "T00:00:00+00:00")
            return PriceBar(
                symbol=symbol,
                timestamp=ts,
                open=float(item["open"]),
                high=float(item["high"]),
                low=float(item["low"]),
                close=float(item["close"]),
                adjusted_close=float(item["adjusted_close"]) if item.get("adjusted_close") is not None else None,
                volume=int(item["volume"]) if item.get("volume") is not None else None,
                provider=self.provider_name,
                raw=item,
            )
        except KeyError as exc:
            raise SchemaMappingError(f"Malformed EOD bar payload: missing {exc}") from exc

    def _get_json(self, path: str, params: dict[str, Any]) -> Any:
        query = dict(params)
        query["api_token"] = self.api_token
        url = f"{self.base_url}{path}?{urllib.parse.urlencode(query)}"
        request = urllib.request.Request(url, headers={"User-Agent": "market-data-provider/0.1"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8", "replace")
        except Exception as exc:
            raise TemporaryProviderError(str(exc)) from exc
        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise SchemaMappingError("Provider returned non-JSON response") from exc
        if isinstance(data, dict) and str(data.get("status", "")).lower() == "error":
            raise TemporaryProviderError(str(data))
        return data

    @staticmethod
    def _parse_epoch(value: Any) -> datetime | None:
        if value in (None, ""):
            return None
        try:
            return datetime.fromtimestamp(int(value), tz=UTC)
        except Exception:
            return None
