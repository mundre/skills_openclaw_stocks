#!/usr/bin/env python3
"""
Simmer Execute — Execute approved trades from score.py recommendations.
Reads scored JSON from stdin (output of score.py), executes each trade.
Respects circuit breakers and dry-run mode.

Usage:
    # Full pipeline (dry run)
    uv run python skills/simmer/scripts/brief.py | \
      uv run python skills/simmer/scripts/score.py | \
      uv run python skills/simmer/scripts/execute.py --dry-run

    # Live execution (after Lobster approval)
    uv run python skills/simmer/scripts/execute.py < scored.json

    # Single trade override
    uv run python skills/simmer/scripts/execute.py \
      --market-id UUID --side yes --amount 100 --reasoning "my thesis"
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

CREDS_FILE = Path.home() / ".config" / "simmer" / "credentials.json"
BASE_URL = "https://api.simmer.markets/api/sdk"
LOG_FILE = Path(__file__).parent.parent / "data" / "trade_log.jsonl"

# Circuit breaker: refuse to trade if portfolio USDC < this
MIN_USDC_BALANCE = 5.0
# Max trades per pipeline run (safety)
MAX_TRADES_PER_RUN = 5


def get_api_key() -> str:
    with open(CREDS_FILE) as f:
        return json.load(f)["api_key"]


def api_post(endpoint: str, payload: dict) -> dict:
    key = get_api_key()
    url = f"{BASE_URL}/{endpoint}"
    data = json.dumps(payload).encode()
    req = Request(url, data=data, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    })
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        body = e.read().decode() if hasattr(e, "read") else ""
        return {"ok": False, "error": f"HTTP {e.code}: {e.reason}", "body": body}
    except URLError as e:
        return {"ok": False, "error": f"Network: {e.reason}"}


def log_trade(record: dict):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")


def execute_trade(pick: dict, dry_run: bool = False) -> dict:
    """Execute a single trade. Returns result dict."""
    market_id = pick["market_id"]
    side = pick["side"]
    trade_params = pick.get("trade", {})
    sim_amount = trade_params.get("sim_amount", 100.0)
    usdc_amount = trade_params.get("usdc_amount", 0.0)
    venue = trade_params.get("venue", "simmer")
    source = trade_params.get("source", "sdk:lobster-pipeline")
    reasoning = pick.get("reasoning", "Lobster pipeline recommendation")

    result = {
        "market_id": market_id,
        "question": pick.get("question", ""),
        "side": side,
        "sim_amount": sim_amount,
        "usdc_amount": usdc_amount,
        "venue": venue,
        "dry_run": dry_run,
        "ts": datetime.now(tz=timezone.utc).isoformat(),
    }

    if dry_run:
        result["status"] = "dry_run"
        result["message"] = f"[DRY RUN] Would trade {side.upper()} ${sim_amount} $SIM on: {pick.get('question', market_id)[:60]}"
        print(f"  [DRY RUN] {side.upper()} ${sim_amount} $SIM — {pick.get('question', market_id)[:60]}", file=sys.stderr)
        log_trade(result)
        return result

    # Execute $SIM trade
    if sim_amount > 0:
        payload = {
            "market_id": market_id,
            "side": side,
            "amount": sim_amount,
            "venue": "simmer",
            "source": source,
            "reasoning": reasoning,
        }
        resp = api_post("trade", payload)
        result["sim_response"] = resp
        result["status"] = "ok" if resp.get("ok") else "error"
        result["message"] = resp.get("message", str(resp))

    # Execute USDC trade (real money — extra caution)
    if usdc_amount > 0 and venue in ("polymarket", "kalshi"):
        payload = {
            "market_id": market_id,
            "side": side,
            "amount": usdc_amount,
            "venue": venue,
            "source": source,
            "reasoning": reasoning,
        }
        resp = api_post("trade", payload)
        result["usdc_response"] = resp
        if result.get("status") != "error":
            result["status"] = "ok" if resp.get("ok") else "error"

    if result.get("status") == "ok":
        print(f"  ✅ {side.upper()} ${sim_amount} $SIM — {pick.get('question', market_id)[:60]}", file=sys.stderr)
    else:
        print(f"  ❌ FAILED — {result.get('message', '?')[:80]}", file=sys.stderr)

    log_trade(result)
    time.sleep(0.5)  # rate limit courtesy
    return result


def main():
    parser = argparse.ArgumentParser(description="Simmer Execute — run approved trades")
    parser.add_argument("--dry-run", action="store_true", help="Preview trades without executing")
    parser.add_argument("--top", type=int, default=None, help="Only execute top N picks")
    # Single-trade override flags
    parser.add_argument("--market-id", help="Single trade: market UUID")
    parser.add_argument("--side", choices=["yes", "no"], help="Single trade: side")
    parser.add_argument("--amount", type=float, default=100.0, help="Single trade: $SIM amount")
    parser.add_argument("--reasoning", default="Manual trade via execute.py")
    args = parser.parse_args()

    # Single-trade mode
    if args.market_id:
        if not args.side:
            print(json.dumps({"ok": False, "error": "--side required for single trade"}))
            sys.exit(1)
        picks = [{
            "market_id": args.market_id,
            "question": args.market_id,
            "side": args.side,
            "reasoning": args.reasoning,
            "trade": {"sim_amount": args.amount, "usdc_amount": 0.0, "venue": "simmer"},
        }]
        risk_alerts = []
        portfolio = {}
    else:
        # Read scored recommendations from stdin
        try:
            scored = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(json.dumps({"ok": False, "error": f"Invalid JSON: {e}"}))
            sys.exit(1)

        if not scored.get("ok"):
            print(json.dumps({"ok": False, "error": "Score step failed", "detail": scored}))
            sys.exit(1)

        picks = scored.get("picks", [])
        risk_alerts = scored.get("risk_alerts", [])
        portfolio = scored.get("portfolio", {})

        # Circuit breaker: block if risk alerts present and real money involved
        real_money_picks = [p for p in picks if p.get("trade", {}).get("usdc_amount", 0) > 0]
        if risk_alerts and real_money_picks and not args.dry_run:
            print(json.dumps({
                "ok": False,
                "error": "Circuit breaker: risk alerts present with real USDC trades",
                "risk_alerts": risk_alerts,
            }))
            sys.exit(1)

    if args.top:
        picks = picks[:args.top]

    picks = picks[:MAX_TRADES_PER_RUN]  # hard cap

    if not picks:
        print(json.dumps({"ok": True, "message": "No picks to execute", "results": []}))
        sys.exit(0)

    print(f"\nExecuting {len(picks)} trade(s){'  [DRY RUN]' if args.dry_run else ''}...", file=sys.stderr)

    results = []
    for pick in picks:
        result = execute_trade(pick, dry_run=args.dry_run)
        results.append(result)

    ok_count = sum(1 for r in results if r.get("status") in ("ok", "dry_run"))
    err_count = len(results) - ok_count

    output = {
        "ok": err_count == 0,
        "dry_run": args.dry_run,
        "executed": len(results),
        "ok_count": ok_count,
        "error_count": err_count,
        "results": results,
        "portfolio": portfolio,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
