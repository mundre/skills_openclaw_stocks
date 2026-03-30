#!/usr/bin/env python3
"""Risk asset collection for iran-war-tracker."""

from __future__ import annotations

import csv
import io

import requests

from config import COINGECKO_BTC_URL, DEFAULT_TIMEOUT, RISK_ASSETS
from normalize import normalize_text
from schemas import AssetSnapshot


def collect_assets(session: requests.Session) -> dict[str, AssetSnapshot]:
    assets: dict[str, AssetSnapshot] = {}
    for name, symbol in RISK_ASSETS.items():
        assets[name] = fetch_stooq_asset(session, name, symbol)
    if not assets["BTC"].price:
        assets["BTC"] = fetch_btc_fallback(session)
    return assets


def fetch_stooq_asset(session: requests.Session, name: str, symbol: str) -> AssetSnapshot:
    url = f"https://stooq.com/q/l/?s={symbol}&i=d"
    try:
        response = session.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        rows = list(csv.DictReader(io.StringIO(response.text)))
        if not rows:
            return AssetSnapshot(name=name, symbol=symbol, source="stooq", error="empty response")
        row = rows[0]
        return AssetSnapshot(
            name=name,
            symbol=symbol,
            price=normalize_text(row.get("Close", "")),
            change_pct=normalize_text(row.get("Change", "")),
            source="stooq",
        )
    except Exception as exc:
        return AssetSnapshot(name=name, symbol=symbol, source="stooq", error=normalize_text(exc))


def fetch_btc_fallback(session: requests.Session) -> AssetSnapshot:
    try:
        response = session.get(COINGECKO_BTC_URL, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        data = response.json()["bitcoin"]
        price = data.get("usd", "")
        change = data.get("usd_24h_change", "")
        return AssetSnapshot(
            name="BTC",
            symbol="btcusd",
            price=str(price),
            change_pct=f"{float(change):.2f}" if change != "" else "",
            source="coingecko",
        )
    except Exception as exc:
        return AssetSnapshot(name="BTC", symbol="btcusd", source="coingecko", error=normalize_text(exc))
