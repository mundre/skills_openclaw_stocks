# Error Codes and Troubleshooting

## Script Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| `MISSING_ENV` | No credentials | Set `PANGOLINFO_API_KEY`, or `PANGOLINFO_EMAIL` + `PANGOLINFO_PASSWORD` |
| `AUTH_FAILED` | Wrong credentials | Verify email and password |
| `RATE_LIMIT` | Too many requests | Wait and retry |
| `NETWORK` | Connection issue | Check internet / firewall |
| `SSL_CERT` | Certificate error | macOS: run Install Certificates.command |
| `API_ERROR` | Pangolinfo API error | Check parameters and `hint` field |
| `PARSE_ERROR` | Invalid API response | Retry; may be transient |

## Pangolinfo API Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| 0 | Success | No action needed |
| 1004 | Invalid token | Auto-retried by script |
| 2001 | Insufficient credits | Top up at [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_wipo) |
| 2005 | No active plan | Subscribe at [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_wipo) |
| 2007 | Account expired | Renew at [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_wipo) |
| 2009 | Usage limit reached | Wait for next billing cycle or contact support |
| 2010 | Bill day not configured | Contact support |
| 4029 | Rate limited | Reduce request frequency |

## Authentication

- Tokens are **permanent** (don't expire unless account deactivated)
- Error code `1004` triggers automatic token refresh
- Resolution order: `PANGOLINFO_API_KEY` env > `~/.pangolinfo_api_key` cache > fresh login

## Credit Costs

| Operation | Credits |
|---|---|
| WIPO search request | 2 |

Credits consumed on success (code 0) only.

## Common Issues

**"No authentication credentials" error** -- Set `PANGOLINFO_API_KEY` env var.

**Empty results** -- Check IRN, holder name spelling, or try broader search parameters.

**Timeout errors** -- Script retries 3x with exponential backoff. Check network.
