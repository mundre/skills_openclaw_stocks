---
name: socialecho-social-media-management-agent
description: SocialEcho social media management API skill for querying team, accounts, articles, reports, upload URL, Reddit communities, Pinterest boards, and publishing posts using team API key. Use for integration checks and data pulls.
---

# SocialEcho Social Media Management Agent

Use this skill to call SocialEcho external APIs with a team API key.

## Prerequisites

1. Sign up / sign in at `https://app.socialecho.net/`.
2. Create a team.
3. In Team Management, create an API key.
4. Use explicit CLI options for auth/runtime (do not auto-read env vars):
   - `--api-key` (required)
   - `--base-url` (optional, default `https://api.socialecho.net`)
   - `--team-id` (optional; maps to `X-Team-Id` when set)
   - `--lang` (optional, default `zh_CN`)

## Setup

```bash
cd socialecho-skills
npm ci
```

Runtime requirement: Node.js `>=18`

## Commands

查询与报表（OpenAPI 约定为 **GET + JSON body**，脚本用 Node 原生 `http(s)` 发送）：

```bash
./team.js --api-key YOUR_KEY
./account.js --api-key YOUR_KEY --page 1 --type 1
./article.js --api-key YOUR_KEY --page 1 --account-ids 41,42
./report.js --api-key YOUR_KEY --start-date 2026-01-01 --end-date 2026-03-24 --time-type 1 --group day --account-ids 41,42
```

上传与发布相关：

```bash
./upload-url.js --api-key YOUR_KEY
./reddit-communities.js --api-key YOUR_KEY --account-id 163751
./pinterest-boards.js --api-key YOUR_KEY --account-id 163751
./publish-article.js --api-key YOUR_KEY --payload ./publish-payload.example.json
```

`publish-article` 的请求体字段以仓库内 `openapi.json` / `openapi.yaml` 中 `POST /v1/publish/article` 为准；请准备完整 JSON 文件并通过 `--payload` 传入。

## Notes

- 成功判定：HTTP `200` 且响应 JSON 的 `code` 为 `200` 或 `0`（与当前对外接口约定一致）。
- 外部 API 限流：单 Key 建议不超过 **120 次/分钟**；循环调用请加节流与退避。
- 规范文件：仓库根目录同步的 `默认模块.openapi.json` 与 skill 内 `openapi.json` / `openapi.yaml` 内容一致（便于 Clawhub / GitHub 与 Agent 阅读）。
