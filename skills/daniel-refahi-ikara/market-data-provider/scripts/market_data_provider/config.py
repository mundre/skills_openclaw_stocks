from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class ProviderConfig:
    provider: str = "eodhd"
    timeout_seconds: float = 20.0
    eodhd_api_token: str | None = None


def load_config() -> ProviderConfig:
    provider = os.getenv("MARKET_DATA_PROVIDER", "eodhd").strip().lower()
    timeout = float(os.getenv("MARKET_DATA_TIMEOUT_SECONDS", "20"))
    token = os.getenv("EODHD_API_TOKEN") or os.getenv("EODHD_API_KEY")
    return ProviderConfig(
        provider=provider,
        timeout_seconds=timeout,
        eodhd_api_token=token,
    )
