# First-Time Setup Guide

## Step 1: Explain what's needed

> To use this skill, you need a Pangolinfo API account. Pangolin provides Google search and AI Overview data through its APIs.
>
> 使用本技能需要 Pangolinfo API 账号。Pangolinfo 提供 Google 搜索和 AI 概览数据的 API 服务。

## Step 2: Guide registration

> 1. Go to [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_serp) and create an account
> 2. After login, find your API Key in the dashboard
>
> 1. 访问 [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_serp) 注册账号
> 2. 登录后在控制台找到你的 API Key

## Step 3: Collect credentials and authenticate

**If user provides an API key (recommended):**
```bash
export PANGOLINFO_API_KEY="<api_key>"
python3 scripts/pangolinfo.py --auth-only
```

**If user provides email + password:**
```bash
export PANGOLINFO_EMAIL="user@example.com"
export PANGOLINFO_PASSWORD="their-password"
python3 scripts/pangolinfo.py --auth-only
```

**Optional caching (only if the user explicitly asks for it):**
```bash
python3 scripts/pangolinfo.py --auth-only --cache-key
```
This persists the API key to `~/.pangolinfo_api_key`. Revoke by deleting that file.

## Step 4: Confirm and proceed

After auth returns `"success": true`:
1. Tell the user: "Authentication successful!"
2. Remind them env vars must remain set for future calls (unless cached).
3. Immediately retry their original request.

## Credit System

- **AI Mode:** 2 credits per request
- **SERP:** 2 credits per request
- **SERP Plus:** 1 credit per request
- Credits are only consumed on success (API code 0)
- Auth checks do not consume credits
- API key is permanent and does not expire unless account is deactivated
