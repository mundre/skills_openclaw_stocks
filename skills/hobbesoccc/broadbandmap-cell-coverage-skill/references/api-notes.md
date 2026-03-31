# API Notes

This skill ships with a configurable API caller because BroadbandMap API shapes can vary.

## Defaults

- Base URL: `https://broadbandmap.com`
- Endpoint: `/api/v1/location/cell`
- Query params: `lat`, `lng`

Also available:

- Internet providers endpoint: `/api/v1/location/internet?lat={lat}&lng={lng}`

If your target API differs, pass `--base-url`, `--endpoint`, and `--param-lat/--param-lon`.

## Authentication

If required, set `BROADBANDMAP_API_KEY` and pass `--api-key` or rely on env default.
The script adds bearer auth (`Authorization: Bearer ...`) and `x-api-key` header for compatibility.

## Normalization behavior

The script attempts to detect provider and technology data from common keys:

- providers/carriers/operators/networkProviders
- technologies/bands/networkTypes/radio

If unknown, raw JSON is still returned in `response`.
