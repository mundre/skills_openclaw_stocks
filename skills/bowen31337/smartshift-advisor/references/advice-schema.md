# Advice JSON Schema

## Fields

| Field | Type | Required | Bounds | Description |
|-------|------|----------|--------|-------------|
| `export_threshold` | float | ✅ | 3-30 c/kWh | Min earn/kWh to trigger grid export |
| `discharge_floor` | float | ✅ | 5-60 % | Min SoC to keep in battery |
| `strategy` | string | ✅ | enum | One of: aggressive_export, moderate_export, conservative_hold, grid_charge, emergency_hold |
| `reasoning` | string | ✅ | — | Plain English explanation of why |
| `hold_until` | string | | HH:MM | Don't discharge before this time (wait for peak) |
| `confidence` | float | | 0-1 | How confident the advisor is |
| `alerts` | array | | — | Any anomalies detected (price spikes, weather warnings) |
| `max_export_kwh` | float | | — | Suggested max kWh to export tonight |

## Strategy Definitions

- **aggressive_export**: Sunny tomorrow, high peaks tonight → drain hard
- **moderate_export**: Partly cloudy or moderate peaks → balanced
- **conservative_hold**: Cloudy tomorrow or low peaks → preserve battery
- **grid_charge**: Negative spot price → take free grid power
- **emergency_hold**: Extreme price spike or grid event → don't touch battery
