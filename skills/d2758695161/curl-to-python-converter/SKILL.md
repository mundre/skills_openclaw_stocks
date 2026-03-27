# curl-to-code

Convert cURL commands to Python, JavaScript, Go, or Node.js code. Paste a cURL command, get clean, runnable code.

## Usage

```
Convert this curl to Python: [paste curl]
Turn this curl into JavaScript fetch
Convert to Go http package
Make this curl into Node.js axios call
```

## What it does

Parses any cURL command and converts it to equivalent code in:
- **Python** — requests or httpx
- **JavaScript** — fetch, axios, or node https
- **Go** — net/http
- **PHP** — Guzzle
- **Ruby** — Net::HTTP
- **Rust** — reqwest

## Features

- Preserves: headers, cookies, auth, body data, query params
- Handles multipart/form-data file uploads
- Handles JSON bodies
- Handles authentication (Basic, Bearer, API keys)
- Handles redirects and timeouts

## Examples

- "Convert to Python: `curl -X POST https://api.example.com -H 'Authorization: Bearer token' -d '{"key":"value"}'`"
- "Turn this into axios: `curl https://example.com/api` with following redirects"
- "Convert to Node.js fetch with timeout"

## Notes

- Output is ready to run — just add your API key
- Includes proper error handling
- Handles both JSON and form-encoded bodies
