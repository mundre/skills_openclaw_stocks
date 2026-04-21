---
name: q-erp
version: 1.0.7
description: 千易 ERP 管理查询技能（一期）。覆盖今日经营动态、商品销售情况、增长潜力；所有查询必须通过 q-claw。
user-invocable: true
---

# q-erp Phase 1 Management Query Skill

## Scope

本 Skill 只处理 ERP 一期管理查询：
- 今日经营动态
- 商品销售情况
- 增长潜力

其中以下表达统一视为“商品销售情况”并路由到 `erp.product.sales.overview`：
- 热销商品排行
- 商品排行榜
- 热销 SPU
- 畅销商品
- 爆品排行
- 热销组合品

以下场景不在一期范围内：
- ERP 写入类动作（创建/修改单据、审批、回写）
- 与 ERP 管理查询无关的闲聊、翻译、写作

## Locale Policy

- 读取 `context.locale`。
- `zh_CN`：使用简体中文回复，并优先使用中文示例话术。
- `en_US`：使用英文回复，并优先使用英文示例话术。
- 其他 locale：统一回退到英文。
- 禁止翻译 `scene`、参数名、编码字段、状态码。

## Critical Rules

1. 所有 ERP 管理查询必须调用 `q-claw`，禁止直接编造业务数据。
2. scene 只能从本文件路由表选择，禁止替换为未定义 scene。
3. 对外介绍当前产品能力时，使用产品名“千易 ERP”，聚焦说明当前已接入的产品能力边界。
4. 结果以后端返回为准；缺失字段明确说明“后端未返回”。
5. 返回 `AUTH_REQUIRED` 或 `AUTH_EXPIRED` 时，必须输出后端返回的 Markdown 可点击链接（`verificationUri`），格式为 `[点击授权](<verificationUri>)`，禁止只输出不可点击的纯文字提示。

## Scene Routing

| 用户意图 | scene |
| --- | --- |
| 今日经营动态 | `erp.management.today.summary` |
| 商品销售情况 / 热销商品排行 / 商品排行榜 / 热销SPU / 畅销商品 / 爆品排行 / 热销组合品 | `erp.product.sales.overview` |
| 增长潜力 | `erp.product.growth.opportunity` |

调用字段固定为：`scene`、`userInput`、`params`（`tenantKey/openId` 由运行时注入）。

英文用户常用表达：
- `How is today's business performance`
- `Show me product sales overview`
- `Analyze growth opportunities`

## Multi-Turn Rules

1. 多轮路由优先级：当轮明确语义 > 上一轮已确认 ERP scene > 弱语义短输入兜底。
2. 用户回复弱语义短输入（好了/继续/ok/continue/0/9/erp）时，若上一轮已确认 ERP scene 存在，则继续该 scene；禁止无依据切换到其他 ERP scene。
3. 一期 ERP scene 默认不承诺稳定的结构化时间参数契约。用户问“昨天/上周/近7天/2026-04-13”这类时间范围时，必须保留在 `userInput` 中传给 `q-claw`，不得擅自构造未经文档声明的 `params` 字段。
4. 只有当后端 scene 文档或返回明确要求某个时间字段时，才允许传对应 `params`；且字段值必须来自用户本轮明确输入，禁止猜测或补全。
5. 若用户继续追问“昨天的呢”“上周的商品销售呢”这类省略句，必须改写成包含完整时间语义的 `userInput` 再继续调用对应 scene，禁止只传模糊短句。

## Time Handling

- `erp.management.today.summary`：今日/现在/当前经营快照，路由到 `erp.management.today.summary`。
- 用户问昨日、上周、近7天、指定日期的经营或销售情况时，仍按最接近的 ERP scene 路由，但最终结果必须以后端实际返回为准；若后端仍返回实时/当日数据，不得宣称自己查到了历史结果。
- 没有后端明确参数契约前，优先保持 `params = {}`，把时间语义放在 `userInput`，避免插件和 skill 自行发明字段。

## Tool Call Examples

今日经营动态：

```json
{"scene":"erp.management.today.summary","userInput":"看下今天经营动态","params":{}}
```

商品销售情况：

```json
{"scene":"erp.product.sales.overview","userInput":"看看商品销售情况","params":{}}
```

热销商品排行：

```json
{"scene":"erp.product.sales.overview","userInput":"热销商品排行，发我看下","params":{}}
```

增长潜力：

```json
{"scene":"erp.product.growth.opportunity","userInput":"分析增长潜力","params":{}}
```

## Result Handling

1. 优先输出工具返回的 `assistantReplyLines`。
2. 若返回 `AUTH_REQUIRED` 或 `AUTH_EXPIRED`，必须输出后端返回的 Markdown 可点击链接（`verificationUri`），格式为 `[点击授权](<verificationUri>)`，禁止只输出不可点击的纯文字提示。
3. 当 `firstTimeAuth: true` 时，业务结果后的引导话术由后端按 locale 追加；你只需正常输出后端返回的 `assistantReplyLines`，禁止自己再补一份首授权引导，禁止改写后端已追加的文案。
