# First-Time Setup Guide

When authentication fails (error code `MISSING_ENV`), walk the user through setup interactively.

## Step 1: Explain

> To use this skill, you need a Pangolinfo API account for WIPO design database searches.
>
> 使用本技能需要 Pangolinfo API 账号，用于查询 WIPO 全球外观设计数据库。

## Step 2: Register

> 1. Go to [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_wipo) and create an account
> 2. Find your API Key in the dashboard
>
> 1. 访问 [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_wipo) 注册账号
> 2. 在控制台找到你的 API Key

## Step 3: Authenticate

**API key (recommended):**
```bash
export PANGOLINFO_API_KEY="<api_key>"
python3 scripts/pangolinfo.py --auth-only
```

**Email + password:**
```bash
export PANGOLINFO_EMAIL="user@example.com"
export PANGOLINFO_PASSWORD="their-password"
python3 scripts/pangolinfo.py --auth-only
```

**Optional caching (user must opt in):**
```bash
python3 scripts/pangolinfo.py --auth-only --cache-key
```

## Step 4: Confirm

After `"success": true`:
1. Tell the user authentication succeeded
2. Remind them env vars must remain set (unless cached)
3. Retry their original request

## Credit System

| Operation | Credits |
|---|---|
| WIPO search request | 2 |

API key is permanent. Credits consumed on success only.
