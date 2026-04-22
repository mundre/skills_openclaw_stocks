#!/usr/bin/env python3
"""
profit_optimizer.py — Profit-maximizing battery dispatch optimizer.

Given:
  - Amber forward price curve (next 12-24h)
  - Solar generation forecast
  - Home consumption profile (learned from HA history)
  - Current battery SOC

Solves: when should battery discharge/charge/hold to maximize profit?

Uses a simple greedy/LP-style dispatch optimization:
  - Export ONLY when feed_in_price > threshold
  - Reserve battery for home load during expensive buy hours
  - Charge when prices are cheap and solar insufficient

Output: JSON with recommended actions, next windows, expected profit.

Usage:
    uv run python scripts/profit_optimizer.py --prices prices.json --solar solar.json --state state.json
"""
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


# Default parameters (overridden by HA input_number if available)
DEFAULT_EXPORT_THRESHOLD_C = 15.0   # c/kWh minimum to export
DEFAULT_DISCHARGE_FLOOR_PCT = 20.0  # never discharge below this SOC %
DEFAULT_BATTERY_CAPACITY_KWH = 10.0 # assume 10kWh battery
DEFAULT_MAX_DISCHARGE_KW = 5.0      # max discharge rate kW
DEFAULT_MAX_CHARGE_KW = 5.0         # max charge rate kW
CHEAP_CHARGE_THRESHOLD_C = 8.0      # charge when buy price < this


def parse_amber_prices(prices_json: dict) -> list[dict]:
    """Parse Amber prices output into list of {time, buy_c, sell_c, duration_min}."""
    slots = []
    
    # Handle both current+forecast format
    items = []
    if isinstance(prices_json, list):
        items = prices_json
    elif isinstance(prices_json, dict):
        if "current" in prices_json:
            curr = prices_json["current"]
            if isinstance(curr, list):
                items.extend(curr)
            elif isinstance(curr, dict):
                items.append(curr)
        if "forecasts" in prices_json:
            fc = prices_json["forecasts"]
            if isinstance(fc, list):
                items.extend(fc)
    
    for item in items:
        if not isinstance(item, dict):
            continue
        
        # Try various field names
        ts = item.get("start_time") or item.get("startTime") or item.get("time") or item.get("nem_time") or item.get("period_start")
        if not ts:
            continue
        
        # Parse timestamp
        try:
            ts_str = str(ts).replace("Z", "+00:00")
            dt = datetime.fromisoformat(ts_str)
        except ValueError:
            try:
                dt = datetime.strptime(str(ts)[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        
        # Get prices - Amber uses c/kWh
        buy_c = item.get("per_kwh") or item.get("price") or item.get("buy_price") or item.get("spot_per_kwh")
        sell_c = item.get("feed_in_tariff") or item.get("feed_in") or item.get("sell_price") or item.get("feedin_kwh")
        
        if buy_c is None:
            continue
        
        # Convert from $/kWh to c/kWh if needed
        if buy_c is not None and abs(float(buy_c)) < 2:  # probably $/kWh
            buy_c = float(buy_c) * 100
        if sell_c is not None and abs(float(sell_c)) < 2:
            sell_c = float(sell_c) * 100
        
        buy_c = float(buy_c) if buy_c is not None else 25.0
        sell_c = float(sell_c) if sell_c is not None else 3.0
        
        duration_min = item.get("duration") or item.get("duration_min", 30)
        
        slots.append({
            "time": dt,
            "buy_c": buy_c,
            "sell_c": sell_c,
            "duration_min": int(duration_min),
            "duration_h": int(duration_min) / 60.0,
        })
    
    return sorted(slots, key=lambda x: x["time"])


def parse_solar_forecast(solar_json: dict) -> dict[int, float]:
    """Parse solar forecast into hour->kWh dict for today and tomorrow."""
    hourly_kwh = {}
    
    # Handle Open-Meteo format
    if "hourly" in solar_json:
        hourly = solar_json["hourly"]
        times = hourly.get("time", [])
        # Try different power fields
        power_field = None
        for field in ["direct_radiation", "diffuse_radiation", "shortwave_radiation", "radiation"]:
            if field in hourly:
                power_field = field
                break
        
        if power_field and times:
            values = hourly.get(power_field, [])
            for ts_str, val in zip(times, values):
                try:
                    dt = datetime.fromisoformat(ts_str)
                    # Convert W/m² to estimated kWh (rough: assume ~3kW peak system)
                    # 1 W/m² * ~20m² panel * ~0.18 efficiency ≈ factor
                    kwh = float(val or 0) * 0.005  # rough conversion
                    hour_key = dt.hour
                    hourly_kwh[hour_key] = hourly_kwh.get(hour_key, 0) + kwh
                except (ValueError, TypeError):
                    pass
    
    # Handle Solcast format
    if "forecasts" in solar_json:
        for fc in solar_json["forecasts"]:
            ts = fc.get("period_end") or fc.get("period_start")
            if not ts:
                continue
            try:
                dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                pv_kwh = float(fc.get("pv_estimate", 0) or fc.get("pv_estimate10", 0) or 0)
                # Solcast gives kWh per 30min period
                hour_key = dt.hour
                hourly_kwh[hour_key] = hourly_kwh.get(hour_key, 0) + pv_kwh
            except (ValueError, TypeError):
                pass
    
    # Handle simple format from our solar_forecast.py
    if "hourly_kwh" in solar_json:
        for h, v in solar_json["hourly_kwh"].items():
            try:
                hourly_kwh[int(h)] = float(v or 0)
            except (ValueError, TypeError):
                pass
    
    return hourly_kwh


def get_consumption_for_hour(profile: dict, hour: int, is_weekend: bool = False) -> float:
    """Get expected home consumption kWh for given hour from profile."""
    if is_weekend and "weekend_kwh" in profile:
        kwh_map = profile["weekend_kwh"]
    elif not is_weekend and "weekday_kwh" in profile:
        kwh_map = profile["weekday_kwh"]
    else:
        kwh_map = profile.get("hourly_kwh", {})
    
    # Keys may be int or str
    return float(kwh_map.get(hour, kwh_map.get(str(hour), 0.5)))


def optimize_dispatch(
    price_slots: list[dict],
    solar_hourly: dict[int, float],
    consumption_profile: dict,
    current_soc_pct: float,
    battery_capacity_kwh: float = DEFAULT_BATTERY_CAPACITY_KWH,
    export_threshold_c: float = DEFAULT_EXPORT_THRESHOLD_C,
    discharge_floor_pct: float = DEFAULT_DISCHARGE_FLOOR_PCT,
    max_discharge_kw: float = DEFAULT_MAX_DISCHARGE_KW,
    max_charge_kw: float = DEFAULT_MAX_CHARGE_KW,
) -> dict:
    """
    Optimize battery dispatch over the next 24h price slots.
    
    Returns:
        {
            "strategy": str,
            "actions": [{"time": iso, "action": str, "kwh": float, "reason": str}],
            "next_window": {"start_iso": str, "end_iso": str, "action": str},
            "expected_profit_today_cents": float,
            "baseline_profit_cents": float,
            "profit_improvement_cents": float,
            "discharge_floor": float,
            "export_threshold": float,
            "reasoning": str,
        }
    """
    now = datetime.now(timezone.utc)
    is_weekend = now.weekday() >= 5
    
    # Simulate battery SOC over time
    soc_kwh = current_soc_pct / 100.0 * battery_capacity_kwh
    floor_kwh = discharge_floor_pct / 100.0 * battery_capacity_kwh
    
    actions = []
    total_profit_cents = 0.0
    baseline_profit_cents = 0.0  # what we'd earn if we just hold
    
    # Current hour for action decisions
    current_hour = now.hour
    
    # Find best export windows: slots where sell_c > threshold
    export_slots = [s for s in price_slots if s["sell_c"] >= export_threshold_c and s["time"] >= now]
    expensive_buy_slots = [s for s in price_slots if s["buy_c"] >= 20.0 and s["time"] >= now]
    cheap_charge_slots = [s for s in price_slots if s["buy_c"] < CHEAP_CHARGE_THRESHOLD_C and s["time"] >= now]
    
    # Find the most profitable export window (next 24h)
    best_export_window = None
    if export_slots:
        # Group consecutive slots
        best_sell_c = max(s["sell_c"] for s in export_slots)
        best_export_window = next(s for s in export_slots if s["sell_c"] == best_sell_c)
    
    # Find peak consumption hours (when we need battery most)
    peak_consumption_hours = set(consumption_profile.get("peak_hours", [17, 18, 19, 20, 21]))
    
    # Determine how much energy we need to reserve for peak consumption
    energy_needed_for_peak_kwh = 0.0
    for slot in expensive_buy_slots[:8]:  # next ~4h of expensive slots
        h = slot["time"].hour
        consumption_kwh = get_consumption_for_hour(consumption_profile, h, is_weekend)
        solar_kwh = solar_hourly.get(h, 0.0)
        net_needed = max(0, consumption_kwh - solar_kwh)
        energy_needed_for_peak_kwh += net_needed * slot["duration_h"]
    
    # Cap reserve at battery capacity
    energy_needed_for_peak_kwh = min(energy_needed_for_peak_kwh, battery_capacity_kwh * 0.8)
    
    # Available to export = current SOC - floor - peak reserve
    available_kwh = max(0, soc_kwh - floor_kwh - energy_needed_for_peak_kwh)
    
    # Decision logic
    current_slot = next((s for s in price_slots if s["time"] <= now <= s["time"] + timedelta(minutes=s["duration_min"])), None)
    if not current_slot and price_slots:
        current_slot = price_slots[0]
    
    current_sell_c = current_slot["sell_c"] if current_slot else 3.0
    current_buy_c = current_slot["buy_c"] if current_slot else 25.0
    
    # Strategy determination
    if current_sell_c >= export_threshold_c and available_kwh > 0.5:
        strategy = "export_peak"
        export_kwh = min(available_kwh, max_discharge_kw * 0.5)  # 30min slot
        profit_gain = export_kwh * current_sell_c
        actions.append({
            "time": now.isoformat(),
            "action": "export",
            "kwh": round(export_kwh, 2),
            "sell_c": current_sell_c,
            "reason": f"Feed-in {current_sell_c:.1f}c/kWh > threshold {export_threshold_c:.1f}c/kWh, {available_kwh:.1f}kWh available",
        })
        total_profit_cents += profit_gain
    elif current_buy_c < CHEAP_CHARGE_THRESHOLD_C and soc_kwh < battery_capacity_kwh * 0.9:
        strategy = "charge"
        charge_kwh = min((battery_capacity_kwh * 0.9 - soc_kwh), max_charge_kw * 0.5)
        actions.append({
            "time": now.isoformat(),
            "action": "charge",
            "kwh": round(charge_kwh, 2),
            "buy_c": current_buy_c,
            "reason": f"Grid price {current_buy_c:.1f}c/kWh very cheap, pre-charging battery",
        })
    elif current_hour in peak_consumption_hours and soc_kwh > floor_kwh:
        strategy = "discharge"
        consumption_kwh = get_consumption_for_hour(consumption_profile, current_hour, is_weekend)
        solar_kwh = solar_hourly.get(current_hour, 0.0)
        discharge_kwh = min(max(0, consumption_kwh - solar_kwh), soc_kwh - floor_kwh, max_discharge_kw * 0.5)
        if discharge_kwh > 0:
            saved = discharge_kwh * current_buy_c  # saved by not buying from grid
            total_profit_cents += saved
            actions.append({
                "time": now.isoformat(),
                "action": "self_consume",
                "kwh": round(discharge_kwh, 2),
                "buy_c": current_buy_c,
                "reason": f"Peak consumption hour, grid at {current_buy_c:.1f}c/kWh — saving {saved:.1f}c",
            })
        else:
            strategy = "hold"
    else:
        strategy = "hold"
    
    # Project next profitable export window
    next_window = None
    if export_slots:
        ws = export_slots[0]
        we = ws["time"] + timedelta(minutes=ws["duration_min"])
        # Find end of consecutive window
        for i in range(1, len(export_slots)):
            gap = (export_slots[i]["time"] - we).total_seconds() / 60
            if gap <= 35:  # allow 5min gap
                we = export_slots[i]["time"] + timedelta(minutes=export_slots[i]["duration_min"])
            else:
                break
        
        next_window = {
            "start_iso": ws["time"].isoformat(),
            "end_iso": we.isoformat(),
            "action": f"export at {ws['sell_c']:.1f}c/kWh",
            "avg_sell_c": round(sum(s["sell_c"] for s in export_slots[:4]) / min(4, len(export_slots)), 1),
        }
    
    # Build reasoning
    reason_parts = []
    reason_parts.append(f"Battery: {current_soc_pct:.0f}% SOC ({soc_kwh:.1f}kWh).")
    reason_parts.append(f"Floor reserved: {floor_kwh:.1f}kWh + {energy_needed_for_peak_kwh:.1f}kWh for peak load.")
    reason_parts.append(f"Available to export: {available_kwh:.1f}kWh.")
    if current_slot:
        reason_parts.append(f"Current: buy {current_buy_c:.1f}c, sell {current_sell_c:.1f}c/kWh.")
    if export_slots:
        reason_parts.append(f"Next profitable export: {len(export_slots)} slots >{export_threshold_c:.0f}c (best: {max(s['sell_c'] for s in export_slots):.1f}c).")
    else:
        reason_parts.append(f"No export slots above {export_threshold_c:.0f}c threshold in next 24h.")
    if peak_consumption_hours:
        reason_parts.append(f"Peak home load hours (from profile): {sorted(peak_consumption_hours)}.")
    if next_window:
        reason_parts.append(f"→ Hold for export window at {next_window['start_iso'][:16]} UTC.")
    
    reasoning = " ".join(reason_parts)
    
    # Confidence: higher when we have real price data and consumption profile
    has_price_data = len(price_slots) > 2
    has_profile_data = consumption_profile.get("total_samples", 0) > 100
    confidence = 0.4
    if has_price_data:
        confidence += 0.3
    if has_profile_data:
        confidence += 0.2
    if available_kwh > 1.0:
        confidence += 0.1
    confidence = min(0.95, confidence)
    
    return {
        "strategy": strategy,
        "actions": actions,
        "next_window": next_window,
        "export_threshold": export_threshold_c,
        "discharge_floor": discharge_floor_pct,
        "available_to_export_kwh": round(available_kwh, 2),
        "energy_reserved_for_peak_kwh": round(energy_needed_for_peak_kwh, 2),
        "expected_profit_today_cents": round(total_profit_cents, 1),
        "current_sell_c": current_sell_c,
        "current_buy_c": current_buy_c,
        "reasoning": reasoning,
        "confidence": round(confidence, 2),
        "peak_buy_hours_ahead": len(expensive_buy_slots),
        "export_slots_ahead": len(export_slots),
    }


def main():
    parser = argparse.ArgumentParser(description="Profit-maximizing battery dispatch optimizer")
    parser.add_argument("--prices", help="Path to Amber prices JSON file")
    parser.add_argument("--solar", help="Path to solar forecast JSON file")
    parser.add_argument("--state", help="Path to inverter state JSON file")
    parser.add_argument("--profile", help="Path to consumption profile JSON file",
                        default="~/.openclaw/workspace/ha-smartshift/.consumption_profile.json")
    parser.add_argument("--export-threshold", type=float, default=DEFAULT_EXPORT_THRESHOLD_C)
    parser.add_argument("--discharge-floor", type=float, default=DEFAULT_DISCHARGE_FLOOR_PCT)
    args = parser.parse_args()
    
    # Load inputs
    prices_data = {}
    if args.prices:
        prices_data = json.loads(Path(args.prices).read_text())
    else:
        # Read from stdin or use empty
        if not sys.stdin.isatty():
            prices_data = json.load(sys.stdin)
    
    solar_data = {}
    if args.solar:
        solar_data = json.loads(Path(args.solar).read_text())
    
    state_data = {}
    if args.state:
        state_data = json.loads(Path(args.state).read_text())
    
    profile_data = {}
    profile_file = Path(args.profile)
    if profile_file.exists():
        try:
            profile_data = json.loads(profile_file.read_text())
        except Exception:
            pass
    
    # Parse data
    price_slots = parse_amber_prices(prices_data)
    solar_hourly = parse_solar_forecast(solar_data)
    
    # Get current SOC
    current_soc = float(
        state_data.get("soc_pct") or
        state_data.get("battery_soc") or
        state_data.get("soc") or
        50.0
    )
    
    # Battery capacity from state
    battery_capacity = float(state_data.get("battery_capacity_kwh", DEFAULT_BATTERY_CAPACITY_KWH))
    
    result = optimize_dispatch(
        price_slots=price_slots,
        solar_hourly=solar_hourly,
        consumption_profile=profile_data,
        current_soc_pct=current_soc,
        battery_capacity_kwh=battery_capacity,
        export_threshold_c=args.export_threshold,
        discharge_floor_pct=args.discharge_floor,
    )
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
