# 文旅素材搜索 API 参考

## 基址来源（可配置）

1. **环境变量** `WENLV_API_ORIGIN`：仅站点根（**不含** `/api/v1`）。若设置，优先使用。
2. 否则使用与本 Skill 同目录的 [config.json](../config.json) 中的 `api_origin`。
3. **`api_base`** = `api_origin`（去尾 `/`）+ `api_version_path`（默认 `/api/v1`）。

搜索：`POST {api_base}/resources/search`，`Content-Type: application/json`，**无需鉴权**。

## 预览页（用户点击「预览」）

统一播放页地址（与搜索同源站点）：

```
GET {api_origin}{preview_play_path}/{id}
```

默认 `preview_play_path` 为 **`/api/v1/play`**，即 `{api_origin}/api/v1/play/:id`。

**与 `fragment_url` 的区别**：`metadata.fragment_url` 是 **媒体流**（常为 m3u8/mp4 直链），在 Markdown 里作为主链接易导致 **下载 m3u8** 或无法播放；**表格/卡片中的可点击「预览」** 必须使用上式的 **HTML 播放页** URL，**不要**使用 `fragment_url`。若 `/api/v1/play/:id` 实际返回的是 playlist 而非 HTML，应调整 `preview_play_path` 或后端路由。`fragment_url` 仍保留在结构化结果中供交易与调试。

## 请求体

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | 是 | 搜索关键词，支持中文 |
| `category_id` | string (UUID) | 否 | 限定分类 |
| `use_llm` | boolean | 否 | 默认 true；**MCP/智能体侧建议固定 `false`** |
| `page` | number | 否 | 默认 1 |
| `page_size` | number | 否 | 默认 20，最大 100 |

## 响应顶层

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 0,
    "items": [],
    "page": 1,
    "page_size": 20
  }
}
```

## `data.items[]` 单条素材（原始）

典型字段（实际以接口为准）：

| 字段 | 说明 |
|------|------|
| `id` | 素材 UUID |
| `name` | 标题 |
| `description` | 描述 |
| `content` | 正文（可能为空） |
| `file_url` | 封面等资源路径（常为相对路径） |
| `file_type` | MIME |
| `file_size` | 字节 |
| `status` | 如 `active` |
| `category` | `{ id, name }` |
| `tags` | `[{ id, name, color }, ...]` |
| `metadata` | 见下表 |
| `created_at` / `updated_at` | ISO 时间 |

### `metadata` 重点

| 字段 | 说明 |
|------|------|
| `fragment_url` | **预览流**（HLS 或 MP4），**P0** |
| `product_name` | 原始文件名 |
| `product_code` | 产品编码 |
| `source` / `source_id` | 数据来源 |
| `pixel_dimensions` | 分辨率，如 `3840 X 2160` |
| `size` | 人类可读大小，如 `705.1M` |
| `format` | 如 `mp4` |
| `time_len` | 时长（秒，字符串或数字） |

## `fragment_url` 类型判定

| 类型 | 条件 | 播放 |
|------|------|------|
| HLS | URL 含 `/hls/` | 需 HLS 播放器 |
| MP4 | URL 以 `.mp4` 结尾 | 浏览器 `<video>` 可直接播 |

## 封面 `cover_url` 拼接

```
cover_url = 当前 api_origin（解析规则见上文）+ file_url
```

例：`api_origin` 为 `https://host`，`file_url` 为 `/files/shield-mind-index/x.jpg`  
→ `https://host/files/shield-mind-index/x.jpg`

## 调用示例

将 `API_BASE` 按上文从 `WENLV_API_ORIGIN` 或 [config.json](../config.json) 解析后替换：

```bash
curl "${API_BASE}/resources/search" \
  -H 'Content-Type: application/json' \
  -d '{"query":"a","use_llm":false,"page":1,"page_size":5,"category_id":"23e6ea38-1fe1-4779-8c51-28290abbb0e9"}'
```
