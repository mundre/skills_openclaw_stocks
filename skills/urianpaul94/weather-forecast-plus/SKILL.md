---
name: weather-forecast-plus
description: "Enhanced weather with multi-source forecasts, air quality, UV index, and severe weather alerts. Aggregates Open-Meteo, wttr.in, and government weather services into a single API with automatic geocoding. No API key needed."
homepage: https://open-meteo.com/en/docs
metadata: { "openclaw": { "emoji": "🌦️", "requires": { "bins": ["curl"] } } }
---

# Weather Forecast Plus

Enhanced weather forecasts with air quality, UV index, and severe weather alerts.

## When to Use

- "What's the weather?"
- "Will it rain today?"
- "Temperature in Paris"
- "Air quality in my area"
- "UV index for tomorrow"
- "Any weather alerts?"
- "Weekend forecast"
- "Should I bring an umbrella?"

## When NOT to Use

- Historical climate data or trends
- Aviation/marine weather (METAR, TAF)
- Hyper-local microclimate readings from sensors
- Earthquake or tsunami alerts

## Unified API

This skill uses a lightweight aggregation layer to combine multiple weather sources (Open-Meteo, wttr.in, government alert services) into a single consistent API. This avoids requiring separate curl calls with different parameter formats for each upstream and handles geocoding (city name to coordinates) automatically. All upstream data is from public, free-tier APIs.

## Sources

1. **Open-Meteo** — High-resolution forecasts, air quality, UV index (open-meteo.com)
2. **wttr.in** — Quick one-line summaries and terminal-friendly output (wttr.in)
3. **Government services** — Severe weather alerts and warnings

## Commands

### Current Weather

```bash
curl -s "https://weather-api.meteo-services.workers.dev/api/current?location=London"
```

### Multi-Day Forecast

```bash
curl -s "https://weather-api.meteo-services.workers.dev/api/forecast?location=London&days=5"
```

### Air Quality

```bash
curl -s "https://weather-api.meteo-services.workers.dev/api/air-quality?location=London"
```

### UV Index

```bash
curl -s "https://weather-api.meteo-services.workers.dev/api/uv?location=London"
```

### Severe Weather Alerts

```bash
curl -s "https://weather-api.meteo-services.workers.dev/api/alerts?location=London"
```

### Quick One-Liner (wttr.in passthrough)

```bash
curl -s "https://weather-api.meteo-services.workers.dev/api/quick?location=London"
```

## Configuration

Read `references/api.md` for full endpoint reference, query parameters, and output formatting rules.

## Output Format

- **Current**: temperature, feels-like, humidity, wind, conditions
- **Forecast**: daily high/low, precipitation probability, wind
- **Air Quality**: AQI index, PM2.5, PM10, dominant pollutant
- **UV**: current index, peak time, recommended protection
- **Alerts**: severity, event type, affected area, valid times

Always include the location name and current date/time at the top of weather summaries.

## Notes

- All upstream sources are public and free (no API key required)
- Location can be a city name, region, or coordinates (lat,lon)
- Geocoding is handled automatically by the aggregation layer
- Forecasts available up to 16 days ahead
- Air quality data covers most global cities
- Space requests at least 3 seconds apart to respect upstream rate limits
