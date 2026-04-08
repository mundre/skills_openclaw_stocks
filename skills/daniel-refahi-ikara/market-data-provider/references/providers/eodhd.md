# EODHD provider notes

## Credentials
- Prefer `EODHD_API_TOKEN`
- Fallback to `EODHD_API_KEY`

## Initial endpoints used
- `exchanges-list` for health check
- `search` for instrument lookup
- `real-time` for latest quote
- `eod` for historical daily bars

## Symbol convention
Prefer fully qualified EODHD symbols such as `AAPL.US`.

## Notes
- Keep endpoint and response mapping isolated in `providers/eodhd.py`.
- Do not leak EODHD field names outside the adapter.
- If another provider is added later, the caller contract must remain unchanged.
