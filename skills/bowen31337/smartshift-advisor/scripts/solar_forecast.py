#!/usr/bin/env python3
"""Fetch solar/weather forecast for SmartShift advisor."""
import json
import os
import urllib.request

LATITUDE = float(os.environ.get("LATITUDE", "-33.7114"))
LONGITUDE = float(os.environ.get("LONGITUDE", "150.9457"))
SOLAR_CAPACITY_KW = float(os.environ.get("SOLAR_CAPACITY_KW", "20.0"))

def main():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LATITUDE}&longitude={LONGITUDE}"
        f"&hourly=shortwave_radiation,cloudcover,temperature_2m"
        f"&daily=sunrise,sunset,precipitation_sum"
        f"&timezone=Australia/Sydney&forecast_days=3"
    )
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())

    hourly = data["hourly"]
    daily = data.get("daily", {})
    result = {"days": []}

    for day_offset in range(3):
        start = day_offset * 24
        day_rad = []
        day_cloud = []
        day_temp = []

        for i in range(start, min(start + 24, len(hourly["time"]))):
            hour = int(hourly["time"][i][11:13])
            if 6 <= hour <= 18:
                day_rad.append(hourly["shortwave_radiation"][i] or 0)
                day_cloud.append(hourly["cloudcover"][i] or 0)
                day_temp.append(hourly["temperature_2m"][i] or 0)

        if not day_rad:
            continue

        est_kwh = sum(r / 1000.0 * SOLAR_CAPACITY_KW for r in day_rad)
        avg_cloud = sum(day_cloud) / len(day_cloud)
        peak_hours = sum(1 for r in day_rad if r > 400)

        if avg_cloud < 30:
            confidence = "sunny"
        elif avg_cloud < 60:
            confidence = "partly_cloudy"
        else:
            confidence = "cloudy"

        day_info = {
            "date": hourly["time"][start][:10],
            "est_kwh": round(est_kwh, 1),
            "avg_cloud_pct": round(avg_cloud, 1),
            "peak_hours": peak_hours,
            "confidence": confidence,
            "avg_temp_c": round(sum(day_temp) / len(day_temp), 1) if day_temp else None,
            "precipitation_mm": daily.get("precipitation_sum", [None, None, None])[day_offset],
            "sunrise": daily.get("sunrise", [None, None, None])[day_offset],
            "sunset": daily.get("sunset", [None, None, None])[day_offset],
        }
        result["days"].append(day_info)

    # Battery refill estimate for tomorrow
    if len(result["days"]) > 1:
        tomorrow = result["days"][1]
        hours_to_full = round(46.0 / SOLAR_CAPACITY_KW * (100 / max(100 - tomorrow["avg_cloud_pct"], 10)), 1)
        result["tomorrow_refill_hours"] = min(hours_to_full, 12)
        result["tomorrow_confidence"] = tomorrow["confidence"]

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
