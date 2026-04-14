---
name: api-device-live
description: "调用 ai-open-gateway 的设备直播接口 POST /api/device/live，获取指定设备的 H5 播放器直播链接。Use when: 需要远程查看设备实时画面、获取直播链接分享给他人。⚠️ 需设置 AI_GATEWAY_API_KEY。"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
      env: ["AI_GATEWAY_API_KEY"]
      configPaths: ["~/.openclaw/.env"]
    primaryEnv: "AI_GATEWAY_API_KEY"
---

# 设备直播链接接口

`POST /api/device/live` 用于获取指定设备的 H5 播放器直播链接。接口会校验设备归属，然后返回可直接在浏览器中打开的播放器 URL。

## ⚠️ 展示规则（MUST 严格遵守）

脚本输出 JSON 格式的结构化数据，这是预期行为。以下展示规则是给 agent 的格式化指令：agent MUST 解析脚本输出的 JSON，按下述规则转换为用户友好的格式后再展示，MUST NOT 直接展示原始 JSON。

脚本输出中包含 `_device_name` 字段（设备名称），用于展示。

1. 当 `code == 0` 且 `data` 包含 `live_url` 时，MUST 使用 Markdown 链接格式：

📺 「客厅摄像机」的直播：

[▶️ 点击打开直播播放器](https://example.com/h5player/pro/autoPlay_credentials.html?...)

关键规则：
- 从 `_device_name` 获取设备名称，用「设备名称」展示，而不是 MAC 地址
- 如果 `_device_name` 为空，则用去掉 `xxxxS_` 前缀的 MAC 地址作为备选
- live_url MUST 用 Markdown 链接语法 `[文字](url)` 输出，MUST NOT 输出裸 URL 文本
- 链接文字用 `▶️ 点击打开直播播放器`

2. 当 `code != 0` 时，回复："接口调用失败，错误码 {code}，原因：{message}"

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
- MUST 使用最小权限的 API_KEY，避免复用高权限凭证。本 skill 仅需设备直播链接获取权限

## 网络访问声明

本 skill 仅访问以下端点（均为 AI_GATEWAY_HOST 下的路径）：

| 端点 | 方法 | 用途 |
|------|------|------|
| /api/device/list | POST | 获取设备名称映射 |
| /api/device/live | POST | 获取设备直播链接 |

脚本不访问任何其他网络资源。

## 快速开始

```bash
python3 get_live_url.py --device-id "xxxxS_aabbccddeeff"
```

## 请求格式

### 请求体

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| device_id | string | 是 | 设备 ID，格式: `xxxxS_<mac>`，不能为空 |

## 响应格式

```json
{
  "code": 0,
  "message": "success",
  "request_id": "<32位请求追踪ID>",
  "data": {
    "live_url": "https://example.com/h5player/pro/autoPlay_credentials.html?t=k7qp2vx9nb4ml8wr3ty6sa"
  },
  "_device_name": "客厅摄像机"
}
```

### data 字段

| 参数名 | 类型 | 说明 |
|--------|------|------|
| live_url | string | H5 播放器直播链接，可直接在浏览器或 WebView 中打开 |

## 错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|------------|------|
| 1001 | 401 | 未提供 api_key（缺少 Authorization 头或格式不正确） |
| 1002 | 401 | api_key 无效或已禁用 |
| 2001 | 400 | 缺少必要参数（device_id 为空，或设备不属于当前用户） |
| 3001 | 502 | 网关内部服务调用失败 |
| 5000 | 500 | 内部错误 |

## 注意事项

- device_id 不能为空，否则返回错误码 2001
- 设备不属于当前用户时会直接报错
- 返回的 live_url 中只包含一个 22 字符短期 token（默认 120 秒过期），h5player 加载后会自动调用 `/api/player/exchange` 换取真实播放凭证。所有敏感信息（apiKey、productKey、流 token、deviceId）均不进入 URL
- 全局请求超时为 120 秒
