# Error Codes and Troubleshooting

## Pangolinfo API Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| 0 | Success | No action needed |
| 1001 | Parameter is empty | Check required fields |
| 1002 | Invalid parameter | Verify request format |
| 1004 | Invalid token | Auto-retried by script. If persistent, re-authenticate. |
| 1009 | Invalid parser name | Check `--mode` value |
| 2001 | Insufficient credits | Top up at [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_serp) |
| 2005 | No active plan | Subscribe at [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_serp) |
| 2007 | Account expired | Renew at [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_serp) |
| 2009 | Usage limit reached | Wait for next billing cycle or contact support |
| 2010 | Bill day not configured | Contact support |
| 4029 | Rate limited | Reduce request frequency |
| 10000 | Task execution failed | Retry. Check query format. |
| 10001 | Task execution failed | Retry. Likely a temporary server issue. |

## Authentication

### Token Lifecycle

- Tokens are **permanent** and do not expire
- A token becomes invalid only if the account is deactivated
- Error code `1004` triggers automatic token refresh

### Token Resolution Order

1. `PANGOLINFO_API_KEY` environment variable
2. Cached API key at `~/.pangolinfo_api_key` (if the file exists from a prior `--cache-key` run)
3. Fresh login using `PANGOLINFO_EMAIL` + `PANGOLINFO_PASSWORD`

### Auth Endpoint

```
POST https://scrapeapi.pangolinfo.com/api/v1/auth
Body: {"email": "<email>", "password": "<password>"}
Response: {"code": 0, "message": "ok", "data": "<token>"}
```

## Credit Costs

| Mode | Credits per request |
|------|---------------------|
| AI Mode (`googleAiSearch`) | 2 |
| SERP (`googleSearch`) | 2 |
| SERP Plus (`googleSearchPlus`) | 1 |

Credits are only consumed on successful requests (code 0).

## Common Issues

**"No authentication credentials" error**
Set environment variables: `export PANGOLINFO_API_KEY=...`

**Empty AI overview in response**
Not all queries trigger an AI overview. Try a more informational query.

**Timeout or network errors**
The script retries 3 times with exponential backoff. Check your network connection.

**Screenshot URL not returned**
Ensure `--screenshot` flag is passed.
