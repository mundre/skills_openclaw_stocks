#!/usr/bin/env python3
"""
Polymarket Spread Sniper

Finds markets where the CLOB bid-ask spread is wide enough to profit by
buying the underpriced side and selling when the spread closes.

Strategy:
- Scan active Polymarket markets with high 24h volume
- Fetch live CLOB orderbook for each market
- If midpoint price diverges from market price by > threshold → buy the cheap side
- Exit when price returns to fair value (spread closes)

Usage:
    python spread_sniper.py              # Dry run
    python spread_sniper.py --live       # Real trades
    python spread_sniper.py --positions  # Show positions

Requires:
    SIMMER_API_KEY environment variable
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

sys.stdout.reconfigure(line_buffering=True)

from simmer_sdk.skill import load_config, update_config, get_config_path

SKILL_SLUG = "polymarket-spread-sniper"
TRADE_SOURCE = "sdk:spreadsniper"

CONFIG_SCHEMA = {
    "min_spread":         {"env": "SIMMER_SPREAD_MIN_SPREAD",      "default": 0.02,  "type": float},  # Min divergence AMM vs CLOB (2¢)
    "min_volume":         {"env": "SIMMER_SPREAD_MIN_VOLUME",       "default": 5000,  "type": float},  # Min 24h volume
    "max_position_usd":   {"env": "SIMMER_SPREAD_MAX_POSITION",     "default": 5.00,  "type": float},
    "max_trades_per_run": {"env": "SIMMER_SPREAD_MAX_TRADES",       "default": 3,     "type": int},
    "min_price":          {"env": "SIMMER_SPREAD_MIN_PRICE",        "default": 0.10,  "type": float},  # Never buy < 10¢
    "max_price":          {"env": "SIMMER_SPREAD_MAX_PRICE",        "default": 0.90,  "type": float},  # Never buy > 90¢
    "max_hours":          {"env": "SIMMER_SPREAD_MAX_HOURS",        "default": 720,   "type": int},    # Max hours to resolution
    "sizing_pct":         {"env": "SIMMER_SPREAD_SIZING_PCT",       "default": 0.05,  "type": float},
}

_config = load_config(CONFIG_SCHEMA, __file__, slug=SKILL_SLUG)

MIN_SPREAD         = _config["min_spread"]
MIN_VOLUME         = _config["min_volume"]
MAX_POSITION_USD   = _config["max_position_usd"]
MAX_TRADES_PER_RUN = _config["max_trades_per_run"]
MIN_PRICE          = _config["min_price"]
MAX_PRICE          = _config["max_price"]
MAX_HOURS          = _config["max_hours"]
SMART_SIZING_PCT   = _config["sizing_pct"]

MIN_SHARES_PER_ORDER = 5.0
MIN_TICK_SIZE        = 0.01
CLOB_API             = "https://clob.polymarket.com"

_client = None


def get_client(live=True):
    global _client
    if _client is None:
        try:
            from simmer_sdk import SimmerClient
        except ImportError:
            print("Error: simmer-sdk not installed. Run: pip install simmer-sdk")
            sys.exit(1)
        api_key = os.environ.get("SIMMER_API_KEY")
        if not api_key:
            print("Error: SIMMER_API_KEY not set")
            sys.exit(1)
        _client = SimmerClient(api_key=api_key, venue="polymarket", live=live)
    return _client


def clob_request(path):
    """Fetch from Polymarket CLOB public API."""
    try:
        url = f"{CLOB_API}{path}"
        req = Request(url, headers={"User-Agent": "spread-sniper/1.0"})
        with urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def get_clob_spread(token_id):
    """
    Returns (best_bid, best_ask, spread, mid) from live CLOB.
    Filters out extreme market-maker-only orders (< 0.02 or > 0.98).
    """
    data = clob_request(f"/book?token_id={token_id}")
    if not data:
        return None, None, None, None

    asks = [float(a["price"]) for a in data.get("asks", []) if 0.02 < float(a["price"]) < 0.98]
    bids = [float(b["price"]) for b in data.get("bids", []) if 0.02 < float(b["price"]) < 0.98]

    if not asks or not bids:
        return None, None, None, None

    best_ask = min(asks)
    best_bid = max(bids)
    spread = best_ask - best_bid
    mid = (best_ask + best_bid) / 2
    return best_bid, best_ask, spread, mid


def fetch_markets():
    """Fetch active Polymarket markets sorted by volume."""
    try:
        result = get_client()._request("GET", "/api/sdk/markets", params={
            "venue": "polymarket",
            "status": "active",
            "sort": "volume",
            "limit": 100,
        })
        return result.get("markets", [])
    except Exception as e:
        print(f"  Failed to fetch markets: {e}")
        return []


def get_portfolio():
    try:
        return get_client().get_portfolio()
    except Exception:
        return None


def execute_trade(market_id, side, amount, reasoning=""):
    try:
        result = get_client().trade(
            market_id=market_id, side=side, amount=amount,
            source=TRADE_SOURCE, reasoning=reasoning,
            skill_slug=SKILL_SLUG,
        )
        return {
            "success": result.success, "trade_id": result.trade_id,
            "shares_bought": result.shares_bought,
            "error": result.error, "simulated": result.simulated,
            "skip_reason": result.skip_reason,
        }
    except Exception as e:
        return {"error": str(e)}


def calculate_position_size(smart_sizing):
    if not smart_sizing:
        return MAX_POSITION_USD
    portfolio = get_portfolio()
    if not portfolio:
        return MAX_POSITION_USD
    balance = portfolio.get("balance_usdc", 0)
    smart = min(max(balance * SMART_SIZING_PCT, 1.0), MAX_POSITION_USD)
    return smart


def run_strategy(dry_run=True, positions_only=False, show_config=False,
                 smart_sizing=False, use_safeguards=True, quiet=False):

    def log(msg, force=False):
        if not quiet or force:
            print(msg)

    log("📊 Polymarket Spread Sniper")
    log("=" * 50)

    get_client(live=not dry_run)

    if dry_run:
        log("\n  [PAPER MODE] Use --live for real trades.")

    log(f"\n⚙️  Config:")
    log(f"  Min spread:     {MIN_SPREAD:.0%}")
    log(f"  Min volume:     ${MIN_VOLUME:,.0f}")
    log(f"  Max position:   ${MAX_POSITION_USD:.2f}")
    log(f"  Price range:    {MIN_PRICE:.0%} – {MAX_PRICE:.0%}")
    log(f"  Max hours:      {MAX_HOURS}h")

    if show_config:
        return

    if positions_only:
        from dataclasses import asdict
        positions = get_client().get_positions(venue="polymarket")
        tagged = [asdict(p) for p in positions if TRADE_SOURCE in str(getattr(p, "sources", ""))]
        log(f"\n📋 Open positions ({len(tagged)}):")
        for p in tagged:
            log(f"  {p.get('question','')[:55]} | pnl={p.get('pnl',0):+.2f}")
        return

    log("\n🔍 Scanning markets...")
    markets = fetch_markets()
    log(f"  {len(markets)} markets loaded")

    position_size = calculate_position_size(smart_sizing)
    trades_executed = 0
    trades_attempted = 0
    signals_found = 0
    skip_reasons = []
    execution_errors = []

    for market in markets:
        if trades_executed >= MAX_TRADES_PER_RUN:
            break

        market_id  = market.get("id")
        question   = market.get("question", "")[:60]
        vol        = market.get("volume_24h", 0) or 0
        market_p   = market.get("current_probability", 0.5) or 0.5
        token_id   = market.get("polymarket_token_id", "")
        resolves   = market.get("resolves_at", "")

        if vol < MIN_VOLUME:
            continue
        if not token_id:
            continue
        if not (MIN_PRICE <= market_p <= MAX_PRICE):
            continue

        # Check hours to resolution
        try:
            dt = datetime.fromisoformat(resolves.replace("Z", "+00:00"))
            hours = (dt - datetime.now(timezone.utc)).total_seconds() / 3600
            if hours < 0 or hours > MAX_HOURS:
                continue
        except Exception:
            continue

        # Fetch live CLOB spread
        best_bid, best_ask, spread, mid = get_clob_spread(token_id)
        if mid is None:
            continue

        # Divergence: AMM price vs CLOB mid
        # Compute net edge AFTER entry cost (paying ask/no-ask)
        if market_p < mid:
            # AMM underpriced → buy YES at CLOB ask
            side = "yes"
            entry_price = best_ask if best_ask else (mid + spread / 2)
            edge = mid - entry_price
        else:
            # AMM overpriced → buy NO at CLOB (pay 1 - best_bid)
            side = "no"
            entry_price = (1 - best_bid) if best_bid else (1 - (mid - spread / 2))
            edge = (1 - mid) - entry_price  # = best_bid - mid

        # Only trade when net edge exceeds MIN_SPREAD threshold
        if edge < MIN_SPREAD:
            continue

        signals_found += 1

        log(f"\n  {question}")
        log(f"     Mkt={market_p:.3f} Mid={mid:.3f} Spread={spread:.3f} Edge={edge:.3f}")
        log(f"     → BUY {side.upper()} @ {entry_price:.3f} | vol=${vol:.0f} | {hours:.0f}h")

        trades_attempted += 1
        result = execute_trade(
            market_id, side, position_size,
            reasoning=f"CLOB spread snipe: mid={mid:.3f}, market={market_p:.3f}, spread={spread:.3f}, edge={edge:.3f}"
        )

        if result.get("success"):
            trades_executed += 1
            shares = result.get("shares_bought", 0)
            sim = result.get("simulated", False)
            log(f"     {'[PAPER] ' if sim else ''}✅ Bought {shares:.1f} shares @ ${position_size:.2f}")
        elif result.get("skip_reason"):
            skip_reasons.append(result["skip_reason"])
            log(f"     ⏭️  Skipped: {result['skip_reason']}")
        else:
            err = result.get("error", "unknown")
            execution_errors.append(err)
            log(f"     ❌ Failed: {err}")

    log(f"\n{'=' * 50}")
    log(f"📊 Summary:")
    log(f"  Signals:  {signals_found}")
    log(f"  Executed: {trades_executed}/{trades_attempted}")

    if os.environ.get("AUTOMATON_MANAGED"):
        report = {
            "signals": signals_found,
            "trades_attempted": trades_attempted,
            "trades_executed": trades_executed,
        }
        if skip_reasons:
            report["skip_reason"] = ", ".join(dict.fromkeys(skip_reasons))
        if execution_errors:
            report["execution_errors"] = execution_errors
        print(json.dumps({"automaton": report}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Polymarket Spread Sniper")
    parser.add_argument("--live",          action="store_true")
    parser.add_argument("--dry-run",       action="store_true")
    parser.add_argument("--positions",     action="store_true")
    parser.add_argument("--config",        action="store_true")
    parser.add_argument("--set",           action="append", metavar="KEY=VALUE")
    parser.add_argument("--smart-sizing",  action="store_true")
    parser.add_argument("--no-safeguards", action="store_true")
    parser.add_argument("--quiet", "-q",   action="store_true")
    args = parser.parse_args()

    if args.set:
        updates = {}
        for item in args.set:
            if "=" in item:
                k, v = item.split("=", 1)
                if k in CONFIG_SCHEMA:
                    try:
                        v = CONFIG_SCHEMA[k]["type"](v)
                    except Exception:
                        pass
                updates[k] = v
        if updates:
            update_config(updates, __file__)
            print(f"Config updated: {updates}")
            _config = load_config(CONFIG_SCHEMA, __file__, slug=SKILL_SLUG)
            globals().update({
                "MIN_SPREAD": _config["min_spread"],
                "MIN_VOLUME": _config["min_volume"],
                "MAX_POSITION_USD": _config["max_position_usd"],
                "MAX_TRADES_PER_RUN": _config["max_trades_per_run"],
                "MIN_PRICE": _config["min_price"],
                "MAX_PRICE": _config["max_price"],
                "MAX_HOURS": _config["max_hours"],
            })

    run_strategy(
        dry_run=not args.live,
        positions_only=args.positions,
        show_config=args.config,
        smart_sizing=args.smart_sizing,
        use_safeguards=not args.no_safeguards,
        quiet=args.quiet,
    )

    if os.environ.get("AUTOMATON_MANAGED"):
        print(json.dumps({"automaton": {"signals": 0, "trades_attempted": 0, "trades_executed": 0, "skip_reason": "no_signal"}}))
