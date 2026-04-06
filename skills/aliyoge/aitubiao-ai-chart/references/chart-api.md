# Chart API Reference

> **重要**：所有非流式响应都包裹在 `{ "code": 0, "msg": "ok", "data": { ... } }` 结构中。
> 下面的响应示例展示的是 `data` 字段内的业务数据。
> **即使 HTTP 状态码为 200，也必须检查 `code` 字段是否为 0。非 0 表示业务错误（如 AI贝不足、项目数已满）。**

## 1. Create Chart Project (一站式)

**Endpoint**: `POST {BASE_URL}/api/v1/agent/chart/create-project`

一次调用完成：AI 图表生成 → 项目创建 → 截图生成

**Headers**:
```
Authorization: Bearer {API_KEY}
Content-Type: application/json
```

**Request Body**:
```json
{
  "markdownTable": "| Month | Revenue |\n|-------|---------|\n| Jan | 1000 |",
  "projectName": "Sales Analysis",
  "requirement": "use blue color theme, prefer bar charts"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| markdownTable | string | Yes | Markdown format table data |
| projectName | string | No | Project name, default "AI图表" |
| requirement | string | No | User-specific requirements for chart generation (e.g., color preferences, chart type preferences, focus areas) |

**Response** (data 字段内容):
```json
{
  "success": true,
  "project": {
    "id": "cuid_string",
    "title": "Sales Analysis",
    "status": "generated",
    "width": 960,
    "height": 540,
    "projectUrl": "https://app.aitubiao.com/workspace/cuid_string"
  },
  "charts": [
    {
      "index": 1,
      "type": "basic-bar",
      "title": "Revenue Trend",
      "description": "Monthly revenue analysis showing upward trend.",
      "screenshotSuccess": true,
      "screenshotUrl": "https://oss.xxx/ai-snapshot/..."
    }
  ],
  "quota": {
    "shellCoinCost": 10,
    "shellBalance": 90,
    "projectsUsed": 6,
    "projectsLimit": 50,
    "projectsRemaining": 44,
    "canCreateProject": true
  },
  "totalCharts": 1,
  "processingTime": "25000ms"
}
```

**注意**:
- AI 生成 + 项目创建 + 截图可能需要 30-60 秒，请设置足够的超时时间 (建议 120s)。
- 截图失败不影响项目创建，`screenshotSuccess` 为 `false` 时查看 `error` 字段。
- `quota` 字段可能为 `null`（配额查询失败时），不影响项目创建结果。

**业务错误响应** (code ≠ 0):
```json
{
  "code": 90001,
  "msg": "exp.shell.SHELL_NOT_ENOUGH",
  "quota": {
    "shellCoinCost": 10,
    "shellBalance": 3,
    "projectsUsed": 5,
    "projectsLimit": 50,
    "projectsRemaining": 45,
    "canCreateProject": false
  }
}
```

| 错误码 | 含义 | 处理方式 |
|--------|------|---------|
| 90001 | AI贝不足 | 展示 quota 中的余额和消耗信息，建议充值或升级会员 |
| 40007 | 项目数已满 | 展示 quota 中的已用/上限，建议删除旧项目或升级会员 |

## 2. Get User Quota (通用配额查询)

**Endpoint**: `GET {BASE_URL}/api/v1/agent/quota`

查询用户当前 AI贝余额、项目配额和所有 AI 功能的 AI贝消耗量。建议在创建项目前调用此接口预检。

**Headers**:
```
Authorization: Bearer {API_KEY}
```

**Response** (data 字段内容):
```json
{
  "shellBalance": 100,
  "shellLeft": 80,
  "shellNum": 20,
  "projectsUsed": 5,
  "projectsLimit": 50,
  "projectsRemaining": 45,
  "pptGeneratePageLimit": 32,
  "features": {
    "chartProject": { "key": "chartProject", "cost": 10, "unit": "次", "label": "图表项目创建", "billingModel": "per-request" }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| shellBalance | number | 当前 AI贝总余额 (shellLeft + shellNum) |
| shellLeft | number | 每月可重置的 AI贝 |
| shellNum | number | 永久 AI贝 |
| projectsUsed | number | 已创建项目数 |
| projectsLimit | number | 项目数上限（由会员等级决定） |
| projectsRemaining | number | 剩余可创建项目数 |
| pptGeneratePageLimit | number | 单次 PPT 生成的最大页数（由会员等级决定） |
| features | Record | 各 AI 功能的 AI贝消耗（cost 为 0 表示免费或未配置，billingModel 表示计费模型：per-request=按次/per-quantity=按数量/per-page=按页） |

## Supported Chart Types (40 types)

基础: basic-bar, basic-column, basic-line, basic-pie, basic-radar, bar-progress, donut-progress
分组: grouped-bar, grouped-column
堆叠: stacked-bar, stacked-column, stacked-area, percent-bar, percent-column, percent-stacked-bar, percent-stacked-column
混合: mixed-line-grouped-column, mixed-line-stacked-column
特殊: funnel, cascaded-area, river-area, butterfly, dynamic-bar, dynamic-ranking, jade-jue
高级: sankey, chord, voronoi, descartes-heatmap, single-layer-treemap, word-cloud, rose-pie, symbol-bar, symbol-column, symbol-pie, difference-arrow-bar, difference-arrow-column, liquid, compose-waterfall, check-in-bubble
