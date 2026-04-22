#!/usr/bin/env python3
"""
consumption_profile.py — Learn home consumption pattern from HA history.

Queries HA history API for last 14-30 days of `sensor.home_load_power`,
builds hourly kWh profile (weekday vs weekend), and writes to
~/.openclaw/workspace/ha-smartshift/.consumption_profile.json.

Usage:
    uv run python scripts/consumption_profile.py [--days 14] [--force]
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import defaultdict


HA_URL = os.environ.get("HA_URL", "http://localhost:8123")
HA_TOKEN_FILE = Path("~/.openclaw/workspace/ha-smartshift/.ha_token")
PROFILE_FILE = Path("~/.openclaw/workspace/ha-smartshift/.consumption_profile.json")
SKILL_DIR = Path(__file__).parent.parent
STALE_HOURS = 24 * 7  # recompute if older than 7 days


def load_token() -> str:
    if HA_TOKEN_FILE.exists():
        return HA_TOKEN_FILE.read_text().strip()
    token = os.environ.get("HA_TOKEN", "")
    if not token:
        raise RuntimeError(f"No HA token found at {HA_TOKEN_FILE} or HA_TOKEN env var")
    return token


def ha_get(path: str, token: str) -> dict | list:
    url = f"{HA_URL}{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        raise RuntimeError(f"HA API HTTP {e.code} for {path}: {body}")
    except Exception as e:
        raise RuntimeError(f"HA API error for {path}: {e}")


def is_stale(profile_file: Path) -> bool:
    if not profile_file.exists():
        return True
    mtime = datetime.fromtimestamp(profile_file.stat().st_mtime, tz=timezone.utc)
    age_hours = (datetime.now(timezone.utc) - mtime).total_seconds() / 3600
    return age_hours > STALE_HOURS


def fetch_history(token: str, days: int = 14) -> list:
    """Fetch home load power history from HA."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    start_str = start.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    
    entity = "sensor.home_load_power"
    path = f"/api/history/period/{start_str}?filter_entity_id={entity}&minimal_response=true&no_attributes=true"
    
    print(f"Fetching {days} days of history for {entity}...", file=sys.stderr)
    data = ha_get(path, token)
    
    if not data or not isinstance(data, list) or not data[0]:
        # Try alternative sensor names
        for alt in ["sensor.load_power", "sensor.house_load", "sensor.home_consumption_power"]:
            path2 = f"/api/history/period/{start_str}?filter_entity_id={alt}&minimal_response=true&no_attributes=true"
            try:
                data2 = ha_get(path2, token)
                if data2 and isinstance(data2, list) and data2[0]:
                    print(f"Using fallback sensor: {alt}", file=sys.stderr)
                    entity = alt
                    data = data2
                    break
            except Exception:
                pass
    
    if not data or not isinstance(data, list):
        raise RuntimeError(f"No history data returned for {entity}")
    
    states = data[0] if data else []
    print(f"Got {len(states)} state records", file=sys.stderr)
    return states, entity


def build_profile(states: list) -> dict:
    """Build hourly consumption profile from state records.
    
    Returns dict with:
      - hourly_kwh[0..23]: typical kWh draw per hour (all days average)
      - weekday_kwh[0..23]: weekday hourly average
      - weekend_kwh[0..23]: weekend hourly average
      - total_samples: number of valid readings
      - peak_hours: top 5 consumption hours
      - low_hours: bottom 5 consumption hours
    """
    # Accumulate watt readings per (hour, day_type)
    # day_type: 0=weekday, 1=weekend
    hour_buckets = defaultdict(list)  # (hour, day_type) -> [watts]
    
    prev_time = None
    prev_watts = None
    
    for record in states:
        try:
            # State can be "unavailable", "unknown", or numeric
            state_str = record.get("state", "")
            if state_str in ("unavailable", "unknown", ""):
                continue
            watts = float(state_str)
            if watts < 0 or watts > 50000:  # sanity check
                continue
            
            ts_str = record.get("last_changed") or record.get("last_updated", "")
            if not ts_str:
                continue
            
            # Parse ISO timestamp
            ts_str = ts_str.replace("Z", "+00:00")
            try:
                ts = datetime.fromisoformat(ts_str)
            except ValueError:
                # Try without timezone
                ts = datetime.fromisoformat(ts_str[:19]).replace(tzinfo=timezone.utc)
            
            # Convert to local Sydney time (UTC+10/11)
            # Simple offset: use UTC+10 (AEST) as baseline
            local_ts = ts.astimezone(timezone(timedelta(hours=10)))
            hour = local_ts.hour
            is_weekend = local_ts.weekday() >= 5  # 5=Sat, 6=Sun
            day_type = 1 if is_weekend else 0
            
            hour_buckets[(hour, day_type)].append(watts)
            
        except (ValueError, KeyError, TypeError):
            continue
    
    if not hour_buckets:
        raise RuntimeError("No valid power readings found in history data")
    
    # Compute averages and convert W → kWh per hour
    # Average watts × 1h = Wh, divide by 1000 = kWh
    hourly_kwh = {}
    weekday_kwh = {}
    weekend_kwh = {}
    
    for hour in range(24):
        wd_readings = hour_buckets.get((hour, 0), [])
        we_readings = hour_buckets.get((hour, 1), [])
        all_readings = wd_readings + we_readings
        
        hourly_kwh[hour] = round(sum(all_readings) / len(all_readings) / 1000, 3) if all_readings else 0.5
        weekday_kwh[hour] = round(sum(wd_readings) / len(wd_readings) / 1000, 3) if wd_readings else hourly_kwh[hour]
        weekend_kwh[hour] = round(sum(we_readings) / len(we_readings) / 1000, 3) if we_readings else hourly_kwh[hour]
    
    # Find peak and low consumption hours
    sorted_hours = sorted(range(24), key=lambda h: hourly_kwh[h], reverse=True)
    peak_hours = sorted_hours[:6]
    low_hours = sorted_hours[-6:]
    
    total_samples = sum(len(v) for v in hour_buckets.values())
    
    return {
        "hourly_kwh": hourly_kwh,
        "weekday_kwh": weekday_kwh,
        "weekend_kwh": weekend_kwh,
        "peak_hours": sorted(peak_hours),
        "low_hours": sorted(low_hours),
        "total_samples": total_samples,
        "avg_daily_kwh": round(sum(hourly_kwh.values()), 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Build home consumption profile from HA history")
    parser.add_argument("--days", type=int, default=14, help="Days of history to fetch (default: 14)")
    parser.add_argument("--force", action="store_true", help="Force recompute even if profile is fresh")
    parser.add_argument("--output", help="Output file path (default: ~/.ha_consumption_profile)")
    args = parser.parse_args()
    
    output_file = Path(args.output) if args.output else PROFILE_FILE
    
    if not args.force and not is_stale(output_file):
        print("Profile is fresh (< 7 days old). Use --force to recompute.", file=sys.stderr)
        if output_file.exists():
            print(output_file.read_text())
        return
    
    try:
        token = load_token()
    except RuntimeError as e:
        print(json.dumps({"error": str(e), "hourly_kwh": {str(h): 0.5 for h in range(24)}}))
        sys.exit(1)
    
    try:
        states, entity = fetch_history(token, args.days)
        profile = build_profile(states)
        profile["entity"] = entity
        profile["days_analyzed"] = args.days
        profile["generated_at"] = datetime.now(timezone.utc).isoformat()
        profile["version"] = 2
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(profile, indent=2))
        print(json.dumps(profile, indent=2))
        print(f"\nProfile written to {output_file}", file=sys.stderr)
        print(f"Total samples: {profile['total_samples']}", file=sys.stderr)
        print(f"Avg daily consumption: {profile['avg_daily_kwh']} kWh", file=sys.stderr)
        print(f"Peak consumption hours: {profile['peak_hours']}", file=sys.stderr)
        
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        # Return minimal default profile so advisor can still run
        default_profile = {
            "error": str(e),
            "hourly_kwh": {str(h): 0.3 if 0 <= h <= 6 else 0.8 if 17 <= h <= 21 else 0.5 for h in range(24)},
            "weekday_kwh": {str(h): 0.3 if 0 <= h <= 6 else 0.8 if 17 <= h <= 21 else 0.5 for h in range(24)},
            "weekend_kwh": {str(h): 0.4 if 0 <= h <= 7 else 0.9 if 10 <= h <= 14 else 0.6 for h in range(24)},
            "peak_hours": [17, 18, 19, 20, 21, 12],
            "low_hours": [2, 3, 4, 5, 1, 0],
            "total_samples": 0,
            "avg_daily_kwh": 14.0,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "version": 2,
            "is_default": True,
        }
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(default_profile, indent=2))
        print(json.dumps(default_profile, indent=2))
        sys.exit(0)  # Exit 0 so advisor can use the default


if __name__ == "__main__":
    main()
