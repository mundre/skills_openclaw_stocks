---
name: culturetour-search
description: >-
  指导智能体检索文旅素材并走通「搜索 → 列表 → 预览(HLS/MP4) → 选择资源 → 确认锁定」；搜索请求默认只取 5 条（page_size=5），列表须用 Markdown 表格展示，勿向用户直接粘贴工具/API 的原始 JSON。
  预览须用站内 HTML 播放页 preview_url（由 id 与 preview_play_path 拼接），勿把 fragment_url/m3u8 当可点击预览链（易触发下载）。调试阶段可不接交易 API。交易基址见 config.json 的 trade_api_base 或 TRADE_API_BASE。
---

# 文旅素材搜索（MCP / API）

## 目标

让智能体用**自然语言**检索文旅素材平台上的资源。每条结果必须**结构化保留**下游交易要用的字段，尤其是 **`metadata.fragment_url`（视频预览流）**。

- **推荐路径**：客户端已配置 MCP Server `wenlv-search`（或等价包名）时，调用工具 **`search_resources`**。
- **兜底路径**：无 MCP 时，用 **解析后的 API 基址** 直接 `POST` 请求，并按本文「输出映射」组装与工具一致的 JSON。

## 流程总览：先调试「预览 → 选择 → 确认」

**当前阶段（交易 API 未定时）**：智能体优先走通 **搜索 → 列表 → 预览 → 选择资源 → 确认锁定**。不在此阶段调用交易接口；确认成功后输出 **结构化「选中资源」**（见下），便于联调与后续接下单。

**交易入口**：保留在文档中，待 `TRADE_API_BASE` / `trade_api_base` 配置并约定接口后再启用（见「交易 API（预留）」）。

智能体按顺序引导；上一步未就绪时不要进入下一步。用户可随时要求「重新搜索」。

### 主路径（调试优先）

| 步骤 | 行为要点 |
|------|----------|
| **1. 搜索** | 调用 `search_resources` 或等价 POST；**`page_size` 固定为 `5`**（只取最相关的 5 条；若接口返回多于 5 条，展示时仍只渲染前 5 条）。保留 P0/P1 字段。 |
| **2. 列出结果** | **必须用 Markdown 表格展示**，**禁止**把工具/API 返回的整段 JSON 当作对用户的主回复（见下「搜索结果展示」与「展示与 JSON」）：列 **选择｜标题｜缩略图｜预览**；「预览」列链接为 **`preview_url`**（见「预览页地址」）。结构化字段在表格中已够用；确需可复制时再在表后附精简说明，勿默认贴大块 JSON。 |
| **3. 预览** | 引导用户打开 **`preview_url`**（站内播放页，统一处理 HLS/MP4）；可同时说明 **`stream_type`** 与原始 **`video_url`** 供技术核对。**预览仅用于选片，不等于已购原片**。 |
| **4. 选择资源** | 用户用序号或 `id` 指定**一条**；智能体**复述**该项的 `id`、`title`、`preview_url`、`stream_type`（必要时含 `resolution`、`duration_seconds`），防止误选。 |
| **5. 确认锁定** | 用户需**明确确认**本条（如「确认选这条」「就这条」）。未确认则**不进入交易**、也不输出最终「已锁定」结构化块。 |

### 搜索结果展示（表格，必选）

向用户展示检索结果时，**优先且默认**使用 **Markdown 表格**，固定四列（顺序与表头用词一致）：

| 列名 | 内容要求 |
|------|----------|
| **选择** | 该行序号（与后续「选第几条」对应），如 `1`、`2`；可附该条 **`id`**（小号或同格换行），便于复制。 |
| **标题** | `title`；过长可省略号，但勿改义。 |
| **缩略图** | 有 **`cover_url`** 时：`![](cover_url)`，或 `[封面](cover_url)`（部分 IM 表格内不渲染图片时用链接代替）。无封面时写「—」或「无」。 |
| **预览** | 使用 **`preview_url`**（`{api_origin}{preview_play_path}/{id}`）作为可点击链接，例如：`[预览](preview_url)`；可在同格附 **`stream_type`**（`HLS` / `MP4`）作标注。**勿**用原始 `video_url` 作为表格主链接（播放以站内预览页为准）。 |

表格**下方**建议再附一句操作说明：「回复序号或 id 选择一条进行预览/确认」。

### 展示与 JSON（必读）

- **对用户**：搜索列表的**唯一默认形态**是上文四列表格；**不要**用 JSON 代码块或裸 JSON 数组替代表格作为首屏结果。
- **对程序/联调**：若用户明确说「给我原始 JSON」「导出结构」或已进入「确认锁定」阶段，再按「标准结果 JSON 形状」或「确认成功后输出」给出 JSON。
- **条数**：请求体 **`page_size` 一律传 `5`**；若工具未支持传参则取返回列表的前 5 条再映射为表格。

**示例（结构示意，URL 替换为真实值）：**

```markdown
| 选择 | 标题 | 缩略图 | 预览 |
|------|------|--------|------|
| 1<br/>`uuid-…` | 雁荡山飞拉达攀岩 | ![封面](https://example.com/files/xxx.jpg) | [预览 · HLS](https://example.com/api/v1/play/uuid-…) |
| 2<br/>`uuid-…` | 另一素材标题 | [封面](https://example.com/files/yyy.jpg) | [预览 · MP4](https://example.com/api/v1/play/uuid-…) |
```

若客户端对表格内图片支持差，将「缩略图」列改为纯链接 `[查看封面](cover_url)` 即可。

### Markdown 内嵌画面（可选）

标准 Markdown **没有**可靠的「视频」语法；`![](url)` 仅用于**图片缩略图**（`cover_url`），**不要**用 `![](video_url)` 指望预览视频。

- **推荐**：表格「预览」列使用 **`[播放预览](preview_url)`**（或「在浏览器中打开」类文案），指向 **HTML 播放页**。
- **仅当 `stream_type` 为 `MP4`**：若对话客户端**允许未过滤的 HTML**（多数飞书/IM 会去掉），可在表格外**额外**附一行内嵌（**不能**替代 `preview_url` 链接；**HLS 不可用**此方式）：
  ```html
  <video controls width="100%" src="（与 video_url 相同的 MP4 HTTPS 直链）"></video>
  ```
  若 HTML 被过滤，用户仍依赖表格中的 **`preview_url`**。
- **HLS（m3u8）**：**不要**使用 `<video src="…m3u8">`**（浏览器普遍无法直接播）；**必须**用 **`preview_url`** 打开站内播放页。

### 预览与本地播放（能力边界）

**SKILL 无法在对话气泡内嵌入可执行的 HLS 播放器**（多数客户端会拦截脚本、iframe，且 OpenClaw / 飞书等需产品侧组件才能内嵌播放）。本 Skill 通过下列方式支持用户**在本机观看预览**：

1. **浏览器打开 `preview_url`（推荐）**  
   - 站内播放页已统一处理 HLS/MP4，用户直接点击表格中的「预览」链接即可。  
   - 若需在系统播放器中打开**原始流**，再使用 `video_url` + `stream_type`（见下文）。

2. **仅当无可用 HTML 播放页、且必须直接拉流时：再考虑 `video_url`**  
   - **`stream_type` 为 `MP4`**：多数浏览器可直接打开直链。  
   - **`stream_type` 为 `HLS`**：裸 m3u8 在 Chrome 常下载或无法播放；**Safari** 相对友好。  
   - 智能体应**优先推 `preview_url`**，避免向非技术用户丢裸 m3u8 链。

3. **本仓库脚本（本地用浏览器打开某 URL）**  
   - 路径：[scripts/open_preview.sh](scripts/open_preview.sh)（相对本 Skill 根目录）。  
   - 用法：优先 `bash scripts/open_preview.sh "<preview_url>" MP4`（播放页为 HTML 时按 HTTP 打开即可）；若需直接拉流，再传入 `video_url` 与 `HLS`/`MP4`。  
   - 适用于 Cursor / 终端；**飞书/OpenClaw** 仍以点击 **`preview_url`** 为主。

4. **可选：本机播放器（原始流）**  
   - **VLC** / **ffplay** 可粘贴 **`video_url`**；日常选片以 **`preview_url`** 为主。

飞书 / OpenClaw：**卡片按钮 URL** 与表格一致，指向 **`preview_url`**（即 `{api_origin}/api/v1/play/{id}`）；若产品另有独立 H5 域名，以产品为准，但须能播同一条 `id`。

### 确认成功后输出（调试 / 联调）

在未接交易 API 时，确认锁定后输出一段 **JSON**（或等价结构），便于下游与后续接入：

```json
{
  "stage": "selected_confirmed",
  "resource": {
    "id": "uuid",
    "title": "…",
    "preview_url": "https://{api_origin}/api/v1/play/{id}",
    "video_url": "…",
    "stream_type": "HLS | MP4"
  },
  "trade_next": "交易 API 就绪后可在此接入下单/原片；当前未调用。"
}
```

`resource` 中应包含当前 SKILL 已映射的 P1 字段（如 `description`、`cover_url`）若用户需要。

### 交易 API（预留，暂不调用）

以下仅在 **`TRADE_API_BASE` 或 `trade_api_base` 已配置** 且产品已约定路径/鉴权后执行；**当前默认不执行**。

1. **基址**：环境变量 **`TRADE_API_BASE`** 优先；否则 [config.json](config.json) 的 **`trade_api_base`** 非空字符串。
2. **调用**：用已锁定资源的 `id`（`resource_id`）按产品约定发起请求；鉴权勿泄露到对话。
3. **原片**：仅以接口**真实返回**的下载/任务字段为准，勿伪造链接。

若均未配置或接口未定：智能体在确认锁定后**仅**完成上文「确认成功后输出」，并可用一句话说明「交易与原片将在接口就绪后接入同一 `resource.id`」。

## API 基址配置（可更换）

**单一默认值**：与本 Skill 同目录的 [config.json](config.json)（`api_origin` + `api_version_path`）。

**解析规则**（智能体 / MCP 实现须一致）：

1. 若存在环境变量 **`WENLV_API_ORIGIN`**（仅站点根，**不要**含 `/api/v1`），则以其为 `api_origin`。
2. 否则使用 `config.json` 中的 `api_origin`。
3. `api_base` = `api_origin`（去掉末尾 `/`）+ `api_version_path`（须以 `/` 开头，默认 `/api/v1`）。

| 项目 | 说明 |
|------|------|
| 基址 | `{api_base}`，例如 `{api_origin}/api/v1` |
| 搜索 | `POST {api_base}/resources/search` |
| 鉴权 | 无（公开接口） |
| Content-Type | `application/json` |

换环境时：改 **config.json** 或部署侧设置 **`WENLV_API_ORIGIN`** 即可，无需改 Skill 正文中的长 URL。**交易**相关另设 **`TRADE_API_BASE`** 或 `config.json` 的 **`trade_api_base`**（非空时生效）。

### 预览页地址（用户点击「预览」）

统一使用站点上的播放页（与原始 `fragment_url` 区分）：

```
preview_url = {api_origin} + {preview_play_path} + "/" + {id}
```

- **`api_origin`**：与上文搜索 API 同源（`WENLV_API_ORIGIN` 或 `config.json` 的 `api_origin`，**无**末尾 `/`）。
- **`preview_play_path`**：默认 **`/api/v1/play`**（见 [config.json](config.json) 的 `preview_play_path`，一般无需改）。
- **`id`**：素材 UUID，与搜索结果中每条 `id` 一致。

示例：`https://d2128144f966ce17-yishield.cn01.apps.yishield.com/api/v1/play/6a6e1ff5-5e26-4d37-b676-53916e071e95`

**表格「预览」列**、飞书卡片按钮、OpenClaw 内链均应使用 **`preview_url`**，便于同一页面内处理 HLS/MP4。**`video_url`（fragment）仍须保留**在结构化结果中，供交易、调试与核对原始流。

### 播放页与裸流（必读：避免一点就下载 m3u8）

- **`video_url`（`metadata.fragment_url`）** 指向的是 **媒体流**（常见为 `.m3u8` 播放清单或 `.mp4` 直链），**不是**给用户点的「网页预览」。在 Markdown 里若写成 `[预览](video_url)`，浏览器对 **HLS** 往往会 **下载 m3u8** 或无法内联播放；Chrome 对裸 m3u8 也无法像 Safari 那样直接播。**禁止**将 `video_url` 作为表格「预览」列或卡片按钮的主链接。
- **`preview_url`** 必须对应 **返回 HTML 的站内播放页**（页内用 hls.js 等处理 HLS，或对 MP4 用 `<video>`），用户点击后在**浏览器页面里播放**，而不是下载清单文件。
- **MCP / 映射**：`preview_url` **一律只由** `{api_origin}{preview_play_path}/{id}` **按上文公式拼接**（见 [config.json](config.json)），**不得**把 `fragment_url` 填进 `preview_url`，也不得用 `video_url` 顶替。
- 若已按上式拼接仍出现「一点就下载 m3u8」：说明当前 `preview_play_path` 对应路由实际返回的是 **playlist** 或 **302 到 m3u8**（`Content-Type` 为 `application/vnd.apple.mpegurl` 等）。请把 **`preview_play_path`** 改成产品/后端提供的 **真实 HTML 播放器路径**（或联系后端改为对该路由返回 HTML 播放页）；**不要**通过改用 `video_url` 来「凑合」当预览。

### 请求体

```json
{
  "query": "雁荡山飞拉达",
  "category_id": "23e6ea38-1fe1-4779-8c51-28290abbb0e9",
  "use_llm": false,
  "page": 1,
  "page_size": 5
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `query` | 是 | 关键词，支持中文自然语言 |
| `category_id` | 否 | 分类 UUID，缩小范围 |
| `use_llm` | 否 | **智能体侧固定传 `false`**（关键词匹配，快且稳定） |
| `page` | 否 | 默认 1 |
| `page_size` | 否 | 接口默认 20、最大 100；**智能体侧固定传 `5`**（列表只展示 5 条） |

### 响应约定

- 业务成功：`code === 0`，列表在 `data.items`，总数 `data.total`，分页 `data.page` / `data.page_size`。
- HTTP 非 2xx 或 `code !== 0`：向用户说明错误，勿伪造结果。

更完整的原始字段说明见 [references/api_reference.md](references/api_reference.md)。

## MCP 工具：`search_resources`

在支持 MCP 的客户端（Claude Code、Claude Desktop、OpenClaw 等）中，应优先调用该工具，参数与上表一致（工具实现内部固定 `use_llm: false`）。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `query` | string | 是 | — | 搜索关键词 |
| `category_id` | string (UUID) | 否 | — | 分类 ID |
| `page` | integer | 否 | 1 | 页码 ≥ 1 |
| `page_size` | integer | 否 | **5** | 智能体调用时传 **5**（接口允许 1–100） |

工具返回 **一段可解析的 JSON 文本**（或等价结构）；智能体**解析后须先渲染 Markdown 表格**（见「搜索结果展示」），**不得**将原始 JSON 直接作为对用户的列表回复。

## 字段优先级（输出必须遵守）

### P0 — 核心（交易直连，缺一不可）

| 来源字段 | 输出键名（与 MCP 对齐） | 说明 |
|----------|-------------------------|------|
| `id` | `id` | 素材唯一 ID |
| `name` | `title` | 标题 |
| `metadata.fragment_url` | `video_url` | **原始预览流**（HLS m3u8 或 MP4 直链），交易/核对用，**表格「预览」列不用作主链** |

**派生（必选，用于展示与点击）**  

| 派生规则 | 输出键名 | 说明 |
|----------|----------|------|
| `{api_origin}{preview_play_path}/{id}` | `preview_url` | **表格「预览」列、卡片按钮**统一用此链接（须为 **HTML 播放页**，非 fragment）；`preview_play_path` 默认 `/api/v1/play`，见 [config.json](config.json) |

同时必须输出 **`stream_type`**（由 `video_url` / fragment 判定）：

- URL 含路径片段 **`/hls/`** → `"HLS"`（需 HLS 播放器，如 hls.js）
- URL **以 `.mp4` 结尾** → `"MP4"`（浏览器可直接播）
- 若 `fragment_url` 为空：不要编造 `video_url`；可省略 `stream_type` 或标为无法判定（勿写假链接）

### P1 — 重要（展示与交易辅助）

| 来源 | 输出键名 |
|------|----------|
| `description` | `description` |
| `metadata.product_name` | `original_filename` |
| `metadata.pixel_dimensions` | `resolution` |
| `metadata.time_len` | `duration_seconds`（建议保留一位小数，字符串或数字与工具一致即可） |
| `metadata.size` | `file_size` |
| `metadata.format` | `format` |
| `file_url`（相对路径） | `cover_url`：**当前 `api_origin`** + `file_url`（与 `api_base` 去掉 `api_version_path` 一致） |
| `category.name` | `category` |
| `tags[].name` | `tags`：逗号分隔或数组，与工具一致 |

### P2 — 辅助（可选）

`metadata.source_id`、`metadata.product_code`、`file_type`、`file_size`（字节）等，在用户需要排查或对接数据源时再输出。

## 标准结果 JSON 形状（解析/转发用）

智能体整理输出时，每条结果建议符合（与 MCP 一致）：

```json
{
  "total": 15,
  "page": 1,
  "page_size": 5,
  "results": [
    {
      "#": "1",
      "id": "uuid",
      "title": "雁荡山飞拉达攀岩",
      "preview_url": "https://{api_origin}/api/v1/play/uuid",
      "video_url": "https://...",
      "stream_type": "HLS",
      "description": "…",
      "original_filename": "….mp4",
      "resolution": "3840 X 2160",
      "duration_seconds": "47.4",
      "file_size": "705.1M",
      "format": "mp4",
      "cover_url": "{api_origin}/files/...",
      "category": "wenlv",
      "tags": "雁荡山, 航拍"
    }
  ]
}
```

## 无 MCP 时的 curl 示例

将 `API_BASE` 设为解析后的完整基址（`api_origin` + `api_version_path`）。**默认站点根须与 [config.json](config.json) 中 `api_origin` 保持一致**（换域名时改 config 并同步下面默认值，或只用 `export`）。

```bash
# 环境变量优先；未设置时使用默认值（应与 config.json 的 api_origin 相同）
ORIGIN="${WENLV_API_ORIGIN:-https://d2128144f966ce17-yishield.cn01.apps.yishield.com}"
API_BASE="${ORIGIN%/}/api/v1"
curl -sS "${API_BASE}/resources/search" \
  -H 'Content-Type: application/json' \
  -d '{"query":"雁荡山","use_llm":false,"page":1,"page_size":5}'
```

将返回的 `data.items` 按上文映射为 `results` 数组，并带上 `total`、`page`、`page_size`。

## 智能体行为要点

1. **须同时保留 `preview_url`（表格/点击）与 `video_url`（原始流）**；**列表「预览」列只链向 `preview_url`**；**列表展示须用「选择｜标题｜缩略图｜预览」表格**（见「搜索结果展示」）。
2. **`use_llm` 固定 false**，除非产品方明确要求开启语义搜索。
3. **面向用户的列表**：以 **Markdown 表格** 为主；结构化字段在表格与列链接中体现。**不要**用整段 JSON 代替表格。仅在用户索要导出、或确认锁定后的约定 JSON 块中再输出 JSON。
4. 分页：默认只拉第 1 页且 **`page_size`=5**；用户要「更多」时递增 `page`（仍建议每次 `page_size`=5），注意 `total` 边界。
5. **预览与成单分离**：用户点击的预览必须是 **`preview_url`（HTML 播放页）**，**不要**把 **`video_url`（m3u8/mp4 流）** 做成主链接以免下载或无法播放。预览仅用于选片；**原片/授权**在交易 API 接入后**仅**以接口成功响应为准；调试阶段无交易接口时不得伪造原片链接。
6. **交易安全**（启用交易 API 后）：不在对话中输出完整密钥；失败时返回接口错误摘要，不猜测成功。

## 客户端接入（备忘）

- **Claude Code**：`.mcp.json` 中 `command` + `args` 指向 stdio MCP 包；若需换站点根，增加 `env`：
  ```json
  "env": { "WENLV_API_ORIGIN": "https://你的新域名" }
  ```
- **Claude Desktop / OpenClaw**：同上，在 MCP 配置里为进程设置 `WENLV_API_ORIGIN`。
- 未配置 `env` 时，MCP 实现应回退读取其内置或同仓库的 **config.json** 默认值。

具体包名与发布流程以实际 npm 包为准；本 Skill 约束 **行为、配置解析顺序、API 路径与输出字段**。
