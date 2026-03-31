---
name: broadbandmap-cell-coverage
description: "PRELIMINARY/ITERATING SKILL (v0.x) - Query BroadbandMap-style public APIs for cellular coverage at a location, normalize results, and return a concise human summary plus raw JSON. Use when a user asks about cell coverage quality/availability for a specific address, city, or lat/lon and wants provider/technology details."
---

# BroadbandMap Cell Coverage

> **Status:** Preliminary skill (v0.x). This is an intentionally small first release and is expected to evolve quickly.

Use this skill to answer: “How good is cell coverage here?” for a specific location.

## Quick workflow

1. Resolve location to coordinates (lat/lon).
2. Run `scripts/cell_coverage_lookup.py` to call the coverage API.
3. Summarize key results:
   - top carriers
   - network tech (4G/5G)
   - confidence/quality fields if present
4. Include caveats when API fields are missing or endpoint behavior is unknown.

## Run the script

```bash
python3 scripts/cell_coverage_lookup.py --lat 39.7392 --lon -104.9903
```

Default endpoint used by this skill:

- `GET /api/v1/location/cell?lat={lat}&lng={lng}`
- Optional filters: `network` (`att|verizon|t-mobile|us-cellular|dish|gci|cellcom|c-spire`), `tech` (`4g|5g`)

Address mode (uses OpenStreetMap Nominatim geocoding first):

```bash
python3 scripts/cell_coverage_lookup.py --address "Denver, CO"
```

Optional overrides and filters:

```bash
python3 scripts/cell_coverage_lookup.py \
  --lat 39.7392 --lon -104.9903 \
  --network verizon \
  --tech 5g \
  --format report
```

Advanced endpoint overrides:

```bash
python3 scripts/cell_coverage_lookup.py \
  --lat 39.7392 --lon -104.9903 \
  --base-url "https://broadbandmap.com" \
  --endpoint "/api/v1/location/cell" \
  --param-lat lat --param-lon lng \
  --api-key "$BROADBANDMAP_API_KEY"
```

## Output contract

The script prints JSON by default with:

- `input`: address/lat/lon used
- `request`: final URL and query params
- `response`: parsed API JSON (or raw body)
- `summary`: best-effort normalized fields (`providers`, `technologies`, `notes`)
- `errors`: any recoverable errors

Use `--format report` for a concise human-readable output.

## Example commands

```bash
# Basic lookup by address
python3 scripts/cell_coverage_lookup.py --address "Austin, TX" --format report

# Filter to one network and 5G only
python3 scripts/cell_coverage_lookup.py --address "Seattle, WA" --network verizon --tech 5g --format report

# Raw JSON for automation/pipelines
python3 scripts/cell_coverage_lookup.py --lat 34.0522 --lon -118.2437 --format json
```

## Known limitations

- This skill is a preliminary v0.x release and will be iterated/enhanced.
- API is alpha and may change schema/limits without notice.
- Default public limit is low (~60 requests/hour/IP).
- Coverage maps are modeled estimates and may differ from real-world signal.

## Response style

When replying to users:

- Start with a one-paragraph answer.
- Then list providers/technologies in bullets.
- End with one caveat sentence: coverage maps are estimates and real-world signal may vary.

## references/

Read `references/api-notes.md` when endpoint details need adjustment.
