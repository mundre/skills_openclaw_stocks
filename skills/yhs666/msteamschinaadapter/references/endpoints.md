# Microsoft Teams China (世纪互联) Endpoints

## AAD Authority

| 环境 | Authority URL |
|------|---------------|
| **中国（世纪互联）** | `https://login.chinacloudapi.cn` 或 `https://login.partner.microsoftonline.cn` |
| **全球** | `https://login.microsoftonline.com` |

## Bot Framework API

| 环境 | Resource URI |
|------|-------------|
| **中国** | `https://api.botframework.azure.cn` |
| **全球** | `https://api.botframework.com` |

## Graph API

| 环境 | Root URL |
|------|---------|
| **中国** | `https://microsoftgraph.chinacloudapi.cn` |
| **全球** | `https://graph.microsoft.com` |

## JWKS (JWT Verification Keys)

| 环境 | JWKS URI |
|------|---------|
| **中国** | `https://login.botframework.azure.cn/v1/.well-known/keys` |
| **全球** | `https://login.botframework.com/v1/.well-known/keys` |

## AAD Token Issuers (for JWT `iss` claim)

| 环境 | Issuers |
|------|---------|
| **中国** | `https://api.botframework.azure.cn`, `https://sts.chinacloudapi.cn/{tenantId}/` |
| **全球** | `https://api.botframework.com`, `https://sts.windows.net/{tenantId}/` |

## Media / Auth Allow Hosts

Add to `DEFAULT_MEDIA_AUTH_HOST_ALLOWLIST`:
- `api.botframework.azure.cn`
- `botframework.azure.cn`
- `microsoftgraph.chinacloudapi.cn`
- `graph.microsoft.cn`

## How to Determine China vs Global

Check the `authority` field in msteams config:
- Contains `chinacloudapi.cn` or `partner.microsoftonline.cn` → **China**
- Otherwise → **Global** (default)

Also check `MSTEAMS_AUTHORITY` environment variable.

## Error Reference

| Error Code | Meaning | Fix |
|-----------|---------|-----|
| `AADSTS500011` | Resource principal not found in tenant | Using global Bot Framework resource in China AAD — need China endpoints |
| `AADSTS500011` (resource: `https://api.botframework.com`) | Same as above | The scope being requested is global, not China |
| `Audience mismatch` | JWT `aud` claim doesn't match any configured `clientId` | `config.connections` Map lost due to spread operator — must preserve Map |
| `401` at `POST /api/messages` | JWT verification failed | Check logs for specific reason (audience mismatch, expired, bad signature) |
