---
name: aitubiao-chart
version: 1.0.1
description: AI智能图表生成。根据用户数据生成图表配置并创建可视化项目。当用户想要创建图表、可视化数据时使用，触发词包括"创建图表"、"做个图表"、"可视化数据"、"用表格生成图表"、"create chart"、"make a chart"、"visualize data"等。
---

# AI 智能图表生成

根据用户提供的数据，生成图表配置并创建可视化项目。

## 强制规则

**以下规则必须严格执行，不得跳过、变通或使用替代方案：**

1. **认证优先**：在执行任何操作之前，必须先检查凭证状态。认证未通过时，禁止执行任何后续步骤。
2. **按顺序执行**：工作流程的 5 个步骤必须按顺序执行，禁止跳步。
3. **费用确认前禁止调用生成接口**：必须成功查询配额、计算费用、并获得用户明确确认后，才能调用 `create-project` 接口。
4. **仅通过 API 创建图表**：禁止使用本地工具（Chart.js、ECharts、matplotlib、D3.js、Plotly 等）生成图表。无论 API 因何种原因失败，都**绝对禁止使用本地工具**，没有任何例外。API 失败时正确做法是停止并告知用户，不是寻找替代方案。
5. **401/403 立即停止**：任何步骤中收到 HTTP 401/403，立即停止并引导用户前往 [API Key 管理页面](https://app.aitubiao.com/setting/api-keys) 检查或重新创建 API Key。401/403 不是超时，禁止重试。
6. **超时/500 重试规则**：最多重试 3 次（间隔 5 秒），仍失败则停止并告知用户。

**⚠️ 以下想法是错误的，如果你发现自己在这样想，请立即停止：**
- ❌ "API 不可用，我可以用本地工具生成图表作为替代" → 违反规则 4
- ❌ "至少让用户看到一些可视化结果" → 本技能唯一输出方式是 aitubiao API
- ❌ "401 可能是暂时性的，重试几次" → 401 是认证失败，重试无意义，按规则 5 处理

## 认证

在调用任何 API 之前，先检查凭证状态。

### 检查凭证

读取凭证文件，判断认证状态：

```bash
cat ~/.aitubiao/credentials 2>/dev/null
```

根据结果判断：
- **文件不存在或为空** → 执行下方"配置凭证"流程
- **`API_KEY` 为空** → 执行下方"配置凭证"流程
- **`API_KEY` 不以 `sk_v1_` 开头** → 告知用户"当前 API Key 已失效，请前往 [API Key 管理页面](https://app.aitubiao.com/setting/api-keys) 重新创建一个 API Key"
- **`BASE_URL` 为空或不等于 `https://api.aitubiao.com`** → 执行下方"配置凭证"流程（保留现有 API_KEY，仅修正 BASE_URL）
- **`API_KEY` 格式正确且 `BASE_URL` 正确** → 认证通过

认证通过后，加载环境变量：
```bash
source ~/.aitubiao/credentials
export BASE_URL="${BASE_URL:-https://api.aitubiao.com}"
```

### 配置凭证

1. 向用户索要 API Key（格式：`sk_v1_...`）。如果没有，引导用户前往 [API Key 管理页面](https://app.aitubiao.com/setting/api-keys) 创建一个新的 API Key，然后将创建好的 Key 粘贴回来。
2. 保存凭证：
```bash
mkdir -p ~/.aitubiao
cat > ~/.aitubiao/credentials << EOF
API_KEY=<用户提供的key>
BASE_URL=https://api.aitubiao.com
EOF
chmod 600 ~/.aitubiao/credentials
```
3. 重新读取文件验证配置是否成功。

凭证保存在 `~/.aitubiao/credentials`，跨会话持久生效。

## 服务架构

所有 API 使用统一的服务地址：

| 默认地址 | API前缀 | 认证方式 |
|---------|---------|---------|
| `https://api.aitubiao.com/` | `/api/v1/agent` | `Authorization: Bearer <API_KEY>` |

**重要**：所有非流式响应都包裹在统一格式中：
```json
{ "code": 0, "msg": "ok", "data": { ... } }
```
实际业务数据在 `data` 字段内。**即使 HTTP 状态码为 200，也必须检查 `code` 字段是否为 0，非 0 表示业务错误。**

## 工作流程

**每一步必须在前一步完成后才能开始。禁止跳步。**

### 第一步：认证（前置条件：无）

运行检查凭证流程。认证未通过时按"认证"章节流程处理。

**认证未通过时，停止。不要读取用户数据，不要做任何分析。**

### 第二步：识别和确认数据（前置条件：第一步认证通过）

判断用户如何提供数据：

- **直接粘贴文本**：自行解析为 Markdown 表格。
- **本地文件**（CSV/TXT）：用 Read 工具读取，然后解析为 Markdown 表格。
- **Excel 文件**（.xlsx/.xls）：使用 xlsx skill 或 Read 工具读取，禁止手动编写 Python 脚本解析 XML。

向用户展示解析后的 Markdown 表格，并询问：
- 数据是否正确？
- 有没有特别的要求？

### 第三步：检查配额并确认费用（前置条件：第二步数据已确认）

在创建图表前，**必须**检查用户的 AI贝余额和项目配额，并向用户确认费用后才能继续。

收到 401/403 按强制规则 5 处理。超时/500 按强制规则 6 处理。

#### 3.1 查询配额

```bash
curl -s --max-time 10 -X GET "${BASE_URL}/api/v1/agent/quota" \
  -H "Authorization: Bearer ${API_KEY}"
```

响应示例（需解析 `data` 字段）：
```json
{
  "code": 0, "msg": "ok",
  "data": {
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
}
```

#### 3.2 计算总费用

根据 `billingModel` 字段计算本次操作的总费用：

| billingModel | 计算方式 | 示例 |
|-------------|---------|------|
| `per-request` | 总费用 = cost | 图表创建: 10 AI贝/次 |
| `per-quantity` | 总费用 = cost × quantity | 生成3张图片: 2 × 3 = 6 AI贝 |
| `per-page` | 总费用 = cost × pageCount | 生成5页PPT: 10 × 5 = 50 AI贝 |

#### 3.3 向用户确认费用

**必须在调用生成接口前向用户展示费用确认信息，并等待用户确认后才能继续**：

```
本次操作将消耗 {totalCost} 个 AI贝（{label}，{billingModel}计费）
当前余额: {shellBalance} 个 AI贝
操作后余额: {shellBalance - totalCost} 个 AI贝
项目数: 已用 {projectsUsed}/{projectsLimit}

是否继续？
```

- 如果 `shellBalance < totalCost`：告知用户当前 AI贝余额不足，需前往 aitubiao 网站购买会员或充值后再继续，**不要继续**
- 如果 `projectsRemaining <= 0`：告知用户当前项目数已满，需前往 aitubiao 网站升级会员，或在网站中删除旧项目后再继续，**不要继续**

> **图表项目创建**：使用 `features.chartProject` 的 cost 计算费用（billingModel 为 per-request，总费用 = cost）。不要与 `chartConfig`、`chartGenerate` 等其他图表功能的费用混淆。

### 第四步：创建图表项目（前置条件：第三步用户已确认费用）

**只有用户明确确认费用后才能执行此步骤。**

**注意**：AI 生成 + 项目创建 + 截图可能需要 60 秒以上，需设置足够的超时时间。

```bash
curl -s --max-time 120 -X POST "${BASE_URL}/api/v1/agent/chart/create-project" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "markdownTable": "<表格数据>",
    "projectName": "我的图表项目",
    "requirement": "使用蓝色系配色，偏好柱状图"
  }'
```

响应格式（需解析 `data` 字段）：
```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "success": true,
    "project": {
      "id": "cuid...",
      "title": "我的图表项目",
      "status": "generated",
      "width": 960,
      "height": 540,
      "projectUrl": "https://app.aitubiao.com/workspace/cuid..."
    },
    "charts": [
      {
        "index": 1,
        "type": "basic-bar",
        "title": "销售趋势",
        "description": "展示逐月销售额增长趋势。",
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
}
```

完整请求/响应格式详见 [chart-api.md](references/chart-api.md)。

### 第五步：返回结果（前置条件：第四步创建成功）

向用户提供：
- 项目 URL（从 `data.project.projectUrl` 获取）
- 项目 ID（从 `data.project.id` 获取）
- 摘要：图表数量、类型、标题
- 截图链接（如果截图成功）
- 资源消耗：本次消耗 AI贝数、剩余 AI贝、已用项目数/上限

## 错误处理

| HTTP 状态码 | 含义 | 处理方式 |
|------------|------|---------|
| 401/403 | API Key 无效、过期或权限不足 | 按强制规则 5：立即停止，引导用户前往 [API Key 管理页面](https://app.aitubiao.com/setting/api-keys) 检查或重新创建 |
| 429 | 频率限制 | 等待 30 秒后重试一次，仍失败则告知用户稍后再试 |
| 500 | 服务器错误 | 按强制规则 6：重试最多 3 次 |

当 `code` 不为 0 时，表示业务错误：

| code | 含义 | 处理方式 |
|------|------|---------|
| 90001 | AI贝不足 | 向用户展示 `quota` 中的余额和消耗信息，并引导其前往 aitubiao 网站购买会员或充值后再继续 |
| 40007 | 项目数已满 | 向用户展示 `quota` 中的已用/上限，并引导其前往 aitubiao 网站升级会员，或在网站中删除旧项目后再继续 |

## API 参考

详细的接口规格说明见 [chart-api.md](references/chart-api.md)。
