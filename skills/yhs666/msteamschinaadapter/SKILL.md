---
name: msteams-china-patch
description: "Patch OpenClaw to support Microsoft Teams China (世纪互联/21Vianet). Use when: (1) user reports msteams webhook 401 errors or AADSTS500011 with api.botframework.com, (2) connecting to Teams China/世纪互联, (3) msteams webhook failed errors appear in logs. This skill runs the msteams-china patch script and provides manual fallback steps for any patches that cannot be auto-applied."
---

# MSTeams China Patch

Patches OpenClaw's compiled msteams extension to use Microsoft Teams China (世纪互联/21Vianet) endpoints.

**哈希无关设计：** 脚本通过内容 marker（函数名、字符串字面量）定位文件，不依赖 `src-CfmuZgBM.js` 这类哈希文件名，OpenClaw 更新后哈希变化也能正常运行。

## Step 1 — Run the Patch Script

```bash
node /home/yang/.openclaw/workspace/skills/msteams-china-patch/scripts/apply_patch.js
```

Expected output:
```
Indexing dist files...
  1448 files indexed

Applying patches...

[OK]   buildMSTeamsAuthConfig - MSAL 中国区认证
[OK]   GRAPH_ROOT - Graph API 中国区
[OK]   getAccessToken Graph scope - 中国区
...
=== Result: 8 applied, 8 already, 0 missing, 0 not found ===

Restart gateway: systemctl --user restart openclaw-gateway
```

## Step 2 — Restart Gateway

```bash
systemctl --user restart openclaw-gateway
# or
openclaw gateway restart
```

## Step 3 — Verify

Send a test message to the bot from Teams. Check logs:
```bash
openclaw gateway logs --tail 50
```

## What the Script Does

脚本通过内容 marker 定位目标文件（哈希文件名自动兼容）：

| # | Patch | Marker 定位 |
|---|-------|------------|
| 1 | `buildMSTeamsAuthConfig` — adds `authority`, `issuers`, `scope` for China | `buildMSTeamsAuthConfig` + `getAuthConfigWithDefaults` |
| 2 | `GRAPH_ROOT` → `microsoftgraph.chinacloudapi.cn` | `GRAPH_ROOT` + `microsoftgraph` |
| 3 | `getAccessToken("https://graph.microsoft.com")` → China | `MsalTokenProvider` + `GRAPH_ROOT` |
| 4 | `DEFAULT_MEDIA_HOST_ALLOWLIST` adds China Graph CDN | `DEFAULT_MEDIA_HOST_ALLOWLIST` + `microsoftgraph` |
| 5 | `DEFAULT_MEDIA_AUTH_HOST_ALLOWLIST` adds China endpoints | `DEFAULT_MEDIA_AUTH_HOST_ALLOWLIST` + `microsoftgraph` |
| 6 | `getDefaultIssuers` adds China issuer | `getDefaultIssuers` + `api.botframework.com` |
| 7 | `MsalConnectionManager.applyConnectionDefaults` issuers adds China | `MsalConnectionManager` + `applyConnectionDefaults` |
| 8 | `jwksUri` adds China JWKS endpoint | `payload.iss` + `login.botframework.com` |
| 9 | `verifyOptions` audience adds China | `verifyOptions` + `api.botframework.com` |
| 10 | `getTokenServiceEndpoint` default → China | `getTokenServiceEndpoint` + `TOKEN_SERVICE_ENDPOINT` |
| 11 | `createConnectorClientWithIdentity` scope default → China | `createConnectorClientWithIdentity` |
| 12 | `createUserTokenClient` scope/audience defaults → China | `createUserTokenClient` |
| 13 | `getAccessToken` botframework scope → China | `MsalTokenProvider` + `loadAuthConfigFromEnv` |
| 14 | `scopeCandidatesForUrl` adds China Graph domain | `scopeCandidatesForUrl` + `graph.microsoft.com` |

## Manual Fallback (if script reports `missing` or `not found`)

If any patch shows `missing` (pattern not found in located file) or `not found` (no file matches markers):

1. **Read the endpoints reference:**
   ```
   references/endpoints.md
   ```

2. **Locate the file manually** — search for the function name or string literal in dist:
   ```bash
   grep -r "functionName" ~/.nvm/versions/node/v24.14.1/lib/node_modules/openclaw/dist/*.js
   ```

3. **Read the actual content** and use `edit` tool with the real `oldText → newText`.

## Key Bug: `Audience Mismatch`

The most critical bug the script fixes is in `buildMSTeamsAuthConfig`. The original code returns:
```javascript
return sdk.getAuthConfigWithDefaults({ clientId, clientSecret, tenantId });
```

This causes MSAL to fall back to **global** endpoints because no China configuration is passed. The script fixes this by adding:
```javascript
return sdk.getAuthConfigWithDefaults({
    clientId: creds.appId,
    clientSecret: creds.appPassword,
    tenantId: creds.tenantId,
    authority: "https://login.chinacloudapi.cn",
    issuers: ["https://api.botframework.azure.cn", "https://sts.chinacloudapi.cn/"],
    scope: "https://api.botframework.azure.cn"
});
```

## Configuration (After Patching)

Configure the msteams channel with the `authority` field:

```json
{
  "channels": {
    "msteams": {
      "enabled": true,
      "appId": "<APP_ID>",
      "appPassword": "<APP_PASSWORD>",
      "tenantId": "<TENANT_ID>",
      "authority": "https://login.partner.microsoftonline.cn"
    }
  }
}
```

Or via environment variables:
```bash
MSTEAMS_AUTHORITY=https://login.partner.microsoftonline.cn
MSTEAMS_APP_ID=<APP_ID>
MSTEAMS_APP_PASSWORD=<APP_PASSWORD>
MSTEAMS_TENANT_ID=<TENANT_ID>
```

## Endpoints Reference

See `references/endpoints.md` for the complete China vs Global endpoint table (AAD authority, Bot Framework API, Graph API, JWKS URIs, AAD token issuers).
