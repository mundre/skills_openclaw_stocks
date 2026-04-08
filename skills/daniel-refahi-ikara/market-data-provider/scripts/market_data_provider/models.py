from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class ProviderHealth:
    ok: bool
    provider: str
    message: str
    checked_at: datetime
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Instrument:
    symbol: str
    name: str | None = None
    exchange: str | None = None
    country: str | None = None
    currency: str | None = None
    provider: str = "unknown"
    raw: dict[str, Any] | None = None


@dataclass(slots=True)
class Quote:
    symbol: str
    price: float
    timestamp: datetime | None = None
    currency: str | None = None
    exchange: str | None = None
    provider: str = "unknown"
    raw: dict[str, Any] | None = None


@dataclass(slots=True)
class PriceBar:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float | None = None
    volume: int | None = None
    exchange: str | None = None
    currency: str | None = None
    provider: str = "unknown"
    raw: dict[str, Any] | None = None
