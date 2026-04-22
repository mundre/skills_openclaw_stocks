#!/usr/bin/env python3
"""
Fetch current and forecast Amber Electric prices.
Outputs JSON: {current_buy, current_feedin, forecast_next4h, descriptor, negspot}
Falls back to time-of-day estimates if API key not configured.
"""
import json
import os
import sys
from datetime import datetime, timezone
import urllib.request
import urllib.error

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SKILL_DIR, "config.json")


def load_config():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except Exception:
        return {}


def fetch_amber_prices(api_key: str, site_id: str) -> dict:
    """Fetch live prices from Amber API v1."""
    base = "https://api.amber.com.au/v1"
    headers = {"Authorization": f"Bearer {api_key}", "accept": "application/json"}

    def get(url):
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())

    # Get current prices
    current = get(f"{base}/sites/{site_id}/prices/current?next=4&previous=0&resolution=30")

    buy_now = None
    feedin_now = None
    forecast_buys = []
    forecast_feedins = []

    for interval in current:
        channel = interval.get("channelType", "")
        price = interval.get("perKwh", 0)
        itype = interval.get("type", "")

        if itype == "CurrentInterval":
            if channel == "general":
                buy_now = price
            elif channel == "feedIn":
                feedin_now = price
        elif itype == "ForecastInterval":
            if channel == "general":
                forecast_buys.append(price)
            elif channel == "feedIn":
                forecast_feedins.append(price)

    # Amber API sign convention:
    #   general: positive = you pay (cost)
    #   feedIn: negative = you earn (income), positive = rare, you pay to export
    # Normalize: feedin_earned = abs(feedin) so higher = better earnings
    feedin_earned = abs(feedin_now or 0)
    forecast_feedin_earned = [abs(p) for p in forecast_feedins[:8]]

    return {
        "current_buy": round(buy_now or 0, 2),
        "current_feedin": round(feedin_earned, 2),
        "forecast_buy_next4h": [round(p, 2) for p in forecast_buys[:8]],
        "forecast_feedin_next4h": [round(p, 2) for p in forecast_feedin_earned],
        "negspot": (buy_now or 0) < 0,
        "high_feedin": feedin_earned > 15,
        "source": "amber_api",
    }


def time_of_day_estimate() -> dict:
    """Fallback: estimate prices based on Sydney time-of-day patterns."""
    now = datetime.now()
    hour = now.hour

    # Sydney Amber rough patterns (c/kWh):
    # Peak: 7-9am, 5-9pm (~25-45c buy, 3-8c feedin)
    # Solar: 10am-3pm (~18-25c buy, 5-12c feedin, sometimes higher)
    # Off-peak: rest (~18-22c buy, 3-6c feedin)

    if 7 <= hour < 9:
        buy = 35.0
        feedin = 5.0
        descriptor = "morning_peak"
    elif 10 <= hour < 15:
        buy = 22.0
        feedin = 8.0
        descriptor = "solar_shoulder"
    elif 15 <= hour < 17:
        buy = 25.0
        feedin = 6.0
        descriptor = "late_afternoon"
    elif 17 <= hour < 21:
        buy = 38.0
        feedin = 4.0
        descriptor = "evening_peak"
    else:
        buy = 20.0
        feedin = 3.0
        descriptor = "off_peak"

    return {
        "current_buy": buy,
        "current_feedin": feedin,
        "forecast_buy_next4h": [buy] * 8,
        "forecast_feedin_next4h": [feedin] * 8,
        "negspot": False,
        "high_feedin": feedin > 15,
        "descriptor": descriptor,
        "source": "time_estimate_no_api_key",
    }


def main():
    config = load_config()
    amber_cfg = config.get("amber", {})
    api_key = amber_cfg.get("api_key", "") or os.environ.get("AMBER_API_KEY", "")
    site_id = amber_cfg.get("site_id", "") or os.environ.get("AMBER_SITE_ID", "")

    if api_key and site_id:
        try:
            result = fetch_amber_prices(api_key, site_id)
        except Exception as e:
            result = time_of_day_estimate()
            result["error"] = str(e)
    else:
        result = time_of_day_estimate()

    print(json.dumps(result))


if __name__ == "__main__":
    main()
