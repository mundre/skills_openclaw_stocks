---
name: api-event-query
description: "Closeli 设备事件查询接口。支持自然语言查询设备事件，并返回 AI 摘要与事件列表，包括事件类型、时间范围，以及图片或视频地址。Use when: 需要直接提问设备事件情况，例如“有没有人出现”“有没有车开过”“我的猫去哪里了”，快速获取事件分析结果与明细。⚠ 安全要求：必须设置 AI_GATEWAY_API_KEY 环境变量，使用最小权限凭证，环境变量请前往APP中AI设置页获取。"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
      env: ["AI_GATEWAY_API_KEY"]
      configPaths: ["~/.openclaw/.env"]
    primaryEnv: "AI_GATEWAY_API_KEY"
---

# 事件查询接口

`POST /api/event/query` 是 AI 驱动的事件查询接口，支持自然语言查询，返回 AI 摘要和事件列表。

## ⚠️ 展示规则（MUST 严格遵守）

脚本输出 JSON 格式的结构化数据，这是预期行为。以下展示规则是给 agent 的格式化指令：agent MUST 解析脚本输出的 JSON，按下述规则转换为用户友好的格式后再展示，MUST NOT 直接展示原始 JSON。

1. 当 `code == 0` 且 `data.events` 非空时：

📋 AI 摘要：{summary}

| 时间 | 事件标签 | 场景描述 |
|------|----------|----------|
| {time} | {ai_events 用逗号连接} | {ai_scene} |

在表格之后，逐条展示每个事件的缩略图链接：

📷 {time} - {ai_events}
[查看截图]({pic_url})

关键规则：
- device_id MUST 去掉 `xxxxS_` 前缀再展示
- pic_url MUST 用 `[查看截图](url)` Markdown 链接格式输出
- MUST NOT 使用 `![](url)` 图片语法（部分客户端不支持内联图片渲染）
- MUST NOT 输出裸 URL 文本
- 超过 10 条只展示前 10 条，提示总数

2. 当 `events` 为空数组时，回复："查询时间范围内没有匹配的事件。"
3. 当 `code != 0` 时，回复："接口调用失败，错误码 {code}，原因：{message}"

## 前置依赖

脚本依赖 httpx。如果未安装，脚本会提示 `python3 -m pip install httpx`。

## 配置声明

本 skill 依赖以下配置项，agent 和用户 MUST 在运行前确认已正确配置。

### 必需配置

| 配置项 | 传递方式 | 说明 |
|--------|----------|------|
| AI_GATEWAY_API_KEY | 环境变量（推荐）、`~/.openclaw/.env`（fallback）、命令行 `--api-key` | API 密钥，用于接口鉴权。脚本按此优先级自动获取 |

### 可选配置

| 配置项 | 传递方式 | 默认值 | 说明 |
|--------|----------|--------|------|
| AI_GATEWAY_HOST | 环境变量、`~/.openclaw/.env` | `https://ai-open-gateway.closeli.cn` | 网关地址 |
| AI_GATEWAY_VERIFY_SSL | 环境变量 | true | 设为 false 可禁用 TLS 证书验证（仅限开发环境） |
| AI_GATEWAY_NO_ENV_FILE | 环境变量 | false | 设为 true 可禁用 `~/.openclaw/.env` fallback 读取（生产环境推荐） |

### Fallback 配置路径

脚本默认会读取 `~/.openclaw/.env` 文件作为 fallback 配置源。该文件为所有 skill 共享，格式为 `KEY=VALUE`（每行一条）。生产环境 MUST 设置 `AI_GATEWAY_NO_ENV_FILE=true` 禁用此 fallback，改为通过环境变量直接传递所有配置。

## 安全注意事项

- 共享凭证文件 `~/.openclaw/.env` 可被同一用户下所有 skill 读取。生产环境 MUST 通过环境变量传递 API_KEY，MUST NOT 依赖共享凭证文件
- TLS 证书验证默认启用，MUST NOT 在生产环境禁用（禁用会导致中间人攻击风险，攻击者可截获 API_KEY 和设备数据）
- 使用前 MUST 确认 AI_GATEWAY_HOST 指向可信域名
- MUST 使用最小权限的 API_KEY，避免复用高权限凭证。本 skill 仅需事件查询权限

## 网络访问声明

本 skill 仅访问以下端点（均为 AI_GATEWAY_HOST 下的路径）：

| 端点 | 方法 | 用途 |
|------|------|------|
| /api/event/query | POST | 自然语言查询设备事件 |

脚本不访问任何其他网络资源。

## 快速开始

```bash
python3 query_events.py \
  --device-ids "xxxxS_aabbccddeeff" \
  --start-date "2026-03-16" \
  --end-date "2026-03-18" \
  --query "今天有没有人来过"
```

## 请求格式

### 请求体

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| device_ids | string[] | 是 | - | 设备 ID 列表，不能为空。格式: `xxxxS_<mac>` |
| start_date | string | 是 | - | 查询开始日期，格式 `yyyy-MM-dd` |
| end_date | string | 是 | - | 查询结束日期，格式 `yyyy-MM-dd` |
| query | string | 是 | - | 自然语言查询内容 |
| locale | string | 否 | `"zh_CN"` | 语言区域，影响 AI 摘要语言 |

## 响应格式

```json
{
  "code": 0,
  "message": "success",
  "request_id": "<32位请求追踪ID>",
  "data": {
    "summary": "今天共检测到3次有人出现的事件。",
    "events": [...],
    "_total_count": 15
  }
}
```

### data 字段

| 参数名 | 类型 | 说明 |
|--------|------|------|
| summary | string | AI 生成的事件摘要文本 |
| events | array | 事件列表（脚本已裁剪到前 3 条） |
| _total_count | integer | 事件总数（脚本附加字段） |

### events 数组元素

| 参数名 | 类型 | 说明 |
|--------|------|------|
| device_id | string | 设备 ID |
| event_id | string | 事件 ID |
| time | string | 格式化时间字符串 |
| ai_events | string[] | AI 识别的事件标签列表 |
| ai_scene | string | AI 描述的场景文字 |
| pic_url | string | 事件缩略图短链接（可能为空） |

## 错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|------------|------|
| 1001 | 401 | 未提供 api_key |
| 1002 | 401 | api_key 无效或已禁用 |
| 2001 | 400 | 缺少必要参数 |
| 3001 | 502 | 网关内部服务调用失败 |
| 5000 | 500 | 内部错误 |

## 注意事项

- device_ids 不能为空数组，否则返回错误码 2001
- start_date 和 end_date 格式为 `yyyy-MM-dd`
- query 支持自然语言
- 全局超时为 120 秒
