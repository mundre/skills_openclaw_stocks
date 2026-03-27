---
name: tripgenie
description: Use for any travel question — hotels, flights, trains, attractions, destinations, and travel tips worldwide.
homepage: https://www.trip.com/tripgenie
metadata:
  openclaw:
    emoji: ✈️
    requires:
      env:
        - TRIPGENIE_API_KEY
      bins:
        - curl
        - jq
---

# TripGenie Actions

## Overview

Use `tripgenie` for travel-related queries. The agent calls TripGenie HTTP APIs with a **`token`** in the JSON body; how to obtain it is defined only in **Setup**.

## Security & privacy (read first)

1. **API keys** — Must be set by the user via env var or provided in-chat (see **Setup**). The skill must never write, read, or suggest writing to `~/.openclaw/.env` or any config file. Do not log or echo tokens.
2. **Trust the endpoint** — Confirm you intend to use **`https://tripgenie-openclaw-prod.trip.com`** and that TripGenie / Trip.com is an acceptable data processor for your use case before enabling this skill.
3. **External responses** — API output is **third-party content**. It may include links, promotional text, or structured data. **Do not assume it is safe to relay verbatim** in every context; summarize or filter when policy, safety, or privacy requires it. Avoid echoing raw responses into places that retain full history if they are unnecessary.
4. **Operational** — Review the key’s **scope, billing, and rate limits** with Trip.com. If you limit **autonomous skill invocation**, configure that in your agent/platform settings so travel queries are not sent to TripGenie more often than you want.

## Inputs to collect

- `query`: User's travel query text (required for all requests)
- `locale`: Language/region code (optional, use `LANG` when available)
- For flight searches: `departure`, `arrival`, `date`, `flight_type`

## Setup

1. **Obtain API key** — From [www.trip.com/tripgenie/openclaw](https://www.trip.com/tripgenie/openclaw) (or your Trip.com-provided channel), per provider terms. Do not share full keys in screenshots or public channels.
2. **Provide the token (pick one)**
   - **Environment variable `TRIPGENIE_API_KEY` (recommended)**: configured by the user or platform in the skill's runtime environment; the skill reads it directly and does not touch any config files.
   - **In conversation**: the user provides the API key in the current thread; the skill uses it only for this call — no persistence, no file writes, no echoing the full key. **If the env var is set, it takes priority.**
3. **Smoke test** — After configuration, run a minimal query; do not log bodies that expose the token.

## Endpoints

**Before running any command, resolve the token (in priority order):**

1. If `TRIPGENIE_API_KEY` is set in the environment, use it as `token`.
2. Otherwise, use the key the user provided in this conversation as `token` (single-use only, no persistence).

### General Query (`/openclaw/query`)

| Parameter | Required | Description |
|-----------|----------|-------------|
| `token` | Yes | API token (see **Setup** and token resolution above) |
| `query` | Yes | User's query text |
| `locale` | No | Language/region code |

```bash
jq -n --arg token "$TOKEN" --arg query "$USER_QUERY" --arg locale "$LANG" '{token: $token, query: $query, locale: $locale}' | curl -s -X POST https://tripgenie-openclaw-prod.trip.com/openclaw/query -H "Content-Type: application/json" -d @- > /tmp/tripgenie-result.md
cat /tmp/tripgenie-result.md
```

### Flight Search (`/openclaw/airline`)

| Parameter | Required | Format | Description |
|-----------|----------|--------|-------------|
| `token` | Yes | — | API token (see token resolution above) |
| `query` | Yes | — | User's query text |
| `departure` | Yes | City code | 3-letter city code (e.g., SHA, BJS) |
| `arrival` | Yes | City code | 3-letter city code (e.g., HKG, TYO) |
| `date` | Yes | YYYY-MM-DD | Departure date |
| `flight_type` | Yes | 0 or 1 | 1 = domestic China, 0 = international |
| `locale` | No | — | Language/region code |

**Domestic flight example:**

```bash
jq -n --arg token "$TOKEN" --arg query "$USER_QUERY" --arg departure "BJS" --arg arrival "SHA" --arg date "2026-03-15" --arg flight_type "1" '{token: $token, query: $query, departure: $departure, arrival: $arrival, date: $date, flight_type: $flight_type}' | curl -s -X POST https://tripgenie-openclaw-prod.trip.com/openclaw/airline -H "Content-Type: application/json" -d @- > /tmp/tripgenie-flight.md
cat /tmp/tripgenie-flight.md
```

**International flight example:**

```bash
jq -n --arg token "$TOKEN" --arg query "$USER_QUERY" --arg departure "FRA" --arg arrival "HKG" --arg date "2026-03-17" --arg flight_type "0" '{token: $token, query: $query, departure: $departure, arrival: $arrival, date: $date, flight_type: $flight_type}' | curl -s -X POST https://tripgenie-openclaw-prod.trip.com/openclaw/airline -H "Content-Type: application/json" -d @- > /tmp/tripgenie-flight.md
cat /tmp/tripgenie-flight.md
```

## Presenting results to the user

Return the API response directly to the user as-is.
