#!/usr/bin/env python3
"""
Simmer Brief — Fetch current portfolio state + ranked opportunities.
Outputs a single JSON envelope for use in Lobster pipelines.

Usage:
    uv run python skills/simmer/scripts/brief.py
    uv run python skills/simmer/scripts/brief.py --since 8h
    uv run python skills/simmer/scripts/brief.py --min-score 5
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

CREDS_FILE = Path.home() / ".config" / "simmer" / "credentials.json"
BASE_URL = "https://api.simmer.markets/api/sdk"


def get_api_key() -> str:
    with open(CREDS_FILE) as f:
        return json.load(f)["api_key"]


def api_get(endpoint: str, params: dict | None = None) -> dict | list:
    key = get_api_key()
    url = f"{BASE_URL}/{endpoint}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{qs}"
    req = Request(url, headers={"Authorization": f"Bearer {key}"})
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        print(f"[brief] HTTP error {e.code}: {e.reason}", file=sys.stderr)
        return {}
    except URLError as e:
        print(f"[brief] Network error: {e.reason}", file=sys.stderr)
        return {}


def parse_since(since_str: str) -> str:
    """Convert '4h', '8h', '1d' to ISO 8601 UTC timestamp."""
    now = time.time()
    match = re.match(r"(\d+)([hmds])", since_str)
    if not match:
        secs = 4 * 3600
    else:
        val, unit = int(match.group(1)), match.group(2)
        secs = val * {"s": 1, "m": 60, "h": 3600, "d": 86400}.get(unit, 3600)
    ts = datetime.fromtimestamp(now - secs, tz=timezone.utc)
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def calc_hours_to_resolution(resolves_at: str | None) -> float | None:
    """Calculate hours until resolution from ISO timestamp string."""
    if not resolves_at:
        return None
    try:
        # Handle both 'Z' and '+00:00' suffixes
        ts = resolves_at.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        now = datetime.now(tz=timezone.utc)
        delta = dt - now
        return round(delta.total_seconds() / 3600, 2)
    except Exception:
        return None


def fetch_opportunities(min_score: int = 0, limit: int = 100) -> list:
    """Fetch markets from multiple sorts, deduped, with computed hours_to_resolution."""
    seen_ids: set[str] = set()
    all_markets: list[dict] = []

    # Pass 1: sorted by opportunity_score (catches Simmer's own scoring)
    for sort_key in ("opportunity_score", "volume"):
        data = api_get("markets", {
            "sort": sort_key,
            "limit": limit,
            "status": "active",
        })
        markets = data.get("markets", []) if isinstance(data, dict) else data
        for m in markets:
            mid = m.get("id", "")
            if mid and mid not in seen_ids:
                seen_ids.add(mid)
                all_markets.append(m)

    if min_score > 0:
        all_markets = [m for m in all_markets if m.get("opportunity_score", 0) >= min_score]

    # Compute hours_to_resolution for each market (API doesn't always include it)
    for m in all_markets:
        if m.get("hours_to_resolution") is None:
            m["hours_to_resolution"] = calc_hours_to_resolution(m.get("resolves_at"))

    # Sort by opportunity_score descending so best picks appear first
    all_markets.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)

    return all_markets


def main():
    parser = argparse.ArgumentParser(description="Simmer Brief — fetch portfolio state")
    parser.add_argument("--since", default="4h", help="Briefing lookback window (e.g. 4h, 1d)")
    parser.add_argument("--min-score", type=int, default=0, help="Min opportunity_score filter")
    parser.add_argument("--limit", type=int, default=30, help="Max opportunities to fetch")
    args = parser.parse_args()

    since_iso = parse_since(args.since)

    # Fetch briefing
    briefing = api_get(f"briefing?since={since_iso}")
    if not briefing:
        print(json.dumps({"ok": False, "error": "Failed to fetch briefing"}))
        sys.exit(1)

    # Fetch top opportunities separately (briefing has limited list)
    opportunities = fetch_opportunities(min_score=args.min_score, limit=args.limit)

    portfolio = briefing.get("portfolio", {})
    positions = briefing.get("positions", {})
    performance = briefing.get("performance", {})
    risk_alerts = briefing.get("risk_alerts", [])

    # Summarise active positions
    active = positions.get("active", [])
    expiring = positions.get("expiring_soon", [])
    significant_moves = positions.get("significant_moves", [])

    output = {
        "ok": True,
        "fetched_at": datetime.now(tz=timezone.utc).isoformat(),
        "since": since_iso,
        "portfolio": {
            "sim_balance": portfolio.get("sim_balance", 0),
            "usdc_balance": portfolio.get("balance_usdc", 0),
            "positions_count": portfolio.get("positions_count", 0),
        },
        "performance": {
            "total_pnl_sim": performance.get("total_pnl", 0),
            "pnl_percent": performance.get("pnl_percent", 0),
            "win_rate": performance.get("win_rate", 0),
            "rank": performance.get("rank"),
            "total_agents": performance.get("total_agents"),
        },
        "risk_alerts": risk_alerts,
        "positions": {
            "active": [
                {
                    "market_id": p["market_id"],
                    "question": p["question"],
                    "side": p["side"],
                    "current_price": p.get("current_price"),
                    "avg_entry": p.get("avg_entry"),
                    "pnl": p.get("pnl"),
                    "resolves_at": p.get("resolves_at"),
                    "source": p.get("source"),
                }
                for p in active
            ],
            "expiring_soon": [
                {
                    "market_id": p["market_id"],
                    "question": p["question"],
                    "side": p["side"],
                    "pnl": p.get("pnl"),
                    "resolves_at": p.get("resolves_at"),
                }
                for p in expiring
            ],
            "significant_moves": [
                {
                    "market_id": p["market_id"],
                    "question": p["question"],
                    "side": p["side"],
                    "avg_entry": p.get("avg_entry"),
                    "current_price": p.get("current_price"),
                    "pnl": p.get("pnl"),
                }
                for p in significant_moves
            ],
        },
        "opportunities": [
            {
                "market_id": m["id"],
                "question": m["question"],
                "current_price": m.get("current_price"),
                "external_price_yes": m.get("external_price_yes"),
                "divergence": m.get("divergence"),
                "opportunity_score": m.get("opportunity_score", 0),
                "resolves_at": m.get("resolves_at"),
                "hours_to_resolution": m.get("hours_to_resolution"),
                "tags": m.get("tags", "[]"),
                "import_source": m.get("import_source"),
                "url": m.get("url"),
            }
            for m in opportunities
        ],
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
