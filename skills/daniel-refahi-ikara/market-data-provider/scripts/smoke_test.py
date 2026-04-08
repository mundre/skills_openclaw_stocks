#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from market_data_provider.factory import create_market_data_provider  # noqa: E402


def main() -> int:
    provider = create_market_data_provider()
    health = provider.healthcheck()
    quote = provider.get_latest_quote(os.getenv("MARKET_DATA_SMOKE_SYMBOL", "AAPL.US"))
    payload = {
        "provider": provider.provider_name,
        "health": {
            "ok": health.ok,
            "message": health.message,
            "details": health.details,
        },
        "quote": {
            "symbol": quote.symbol,
            "price": quote.price,
            "timestamp": quote.timestamp.isoformat() if quote.timestamp else None,
            "currency": quote.currency,
        },
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
