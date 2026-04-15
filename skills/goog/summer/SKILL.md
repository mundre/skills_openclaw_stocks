---
name: summer
description: "Display a beautiful time dashboard showing a live summer countdown to Jun 21, 2026 at 1:24:30 am (the summer solstice), today's sunrise/sunset times in China (Beijing), and current time info. Use this skill whenever the user asks about summer countdown, days until summer, summer solstice 2026, sunrise or sunset in China, Beijing sunrise, time until summer, or wants a time/seasonal clock widget. Also trigger when the user asks how long until summer, when does summer start, what time is sunrise in China, or any combination of summer + time + China topics."
---

# Summer Time Skill — Summer Countdown + China Sunrise

This skill renders a live interactive time dashboard with three main panels:

1. **Summer Countdown** — live ticking countdown to June 21, 2026 at 01:24:30 (the summer solstice, sourced from timeanddate.com)
2. **China Sunrise/Sunset** — today's sunrise and sunset times for Beijing, China (fetched via open-meteo / sunrise-sunset API)
3. **Current Time** — today's date and a live clock

## How to build this widget

Create an `.html` file and present it. The file must:

### Summer Countdown Target
- Target datetime: **June 21, 2026 at 01:24:30 local time**
- Source: Summer Countdown – Countdown to Jun 21, 2026 1:24:30 am (timeanddate.com)
- Display: days, hours, minutes, seconds — all ticking live with `setInterval`

### Beijing Sunrise Data
Fetch from the sunrise-sunset API at runtime using the Beijing coordinates:
- Latitude: 39.9075
- Longitude: 116.3972
- API endpoint: `https://api.sunrise-sunset.org/json?lat=39.9075&lng=116.3972&formatted=0&date=today`
- Note: the API returns UTC times, convert to CST (UTC+8)
- Display: sunrise time, sunset time, solar noon, day length

### Widget Layout
Three cards side by side (or stacked on narrow screens):

```
[ Summer Countdown ]  [ Beijing Sunrise ]  [ Current Time ]
  XX days               Sunrise: HH:MM       Today's date
  XX hours              Sunset: HH:MM        Live clock HH:MM:SS
  XX minutes            Day length: H:MM
  XX seconds
```

### Visual style
- Clean, flat cards using CSS variables
- Sun/summer color accents (amber/orange tones) for the countdown card
- Teal/blue tones for sunrise card  
- Gray/neutral for current time
- Live ticking every second via `setInterval(update, 1000)`
- Responsive grid: `repeat(auto-fit, minmax(200px, 1fr))`

### Code structure
```html
<!-- Fetch sunrise on load, then tick every second -->
<script>
const SUMMER = new Date('2026-06-21T01:24:30'); // local time interpretation

async function fetchSunrise() {
  const r = await fetch('https://api.sunrise-sunset.org/json?lat=39.9042&lng=116.4074&formatted=0');
  const d = await r.json();
  // results.sunrise and results.sunset are ISO strings in UTC
  // Add 8 hours for CST
}

function tick() {
  // Update countdown, clock every second
}
setInterval(tick, 1000);
</script>
```

## Important notes
- The summer solstice countdown target is **fixed**: June 21, 2026 01:24:30 — do not make this user-configurable unless asked
- Sunrise data is **fetched live** from the API each page load
- All times display in **24h format** with leading zeros
- Day length = sunset minus sunrise in hours and minutes
- If the API call fails, show a friendly fallback: "Sunrise: ~5:44 · Sunset: ~18:47" (Beijing April averages)
