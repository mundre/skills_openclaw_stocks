---
name: q-wms
version: 1.0.52
description: 千易 WMS 智能查询技能。覆盖库存、仓库、货主、库存日志、订单池、订单、任务、库内绩效、进销存（新）、主管晨报、异常雷达、积压分析、异常跟进；所有查询必须通过 q-claw。
user-invocable: true
---

# q-wms

## Scope

使用本 Skill 的场景：
- 查库存、库存数量、库存明细
- 查仓库、选择仓库、仓库列表
- 查货主、选择货主、货主列表
- 查库存变动日志
- 查订单池、订单池配置、波次开关配置
- 查订单完成情况、出库订单进展、订单异常排查
- 查任务完成情况、任务异常排查
- 查库内绩效、拣货绩效、绩效报表
- 查进销存（新）、IOS(New) 报表
- 查仓库主管晨报、主管晨间简报、今日仓内总览
- 查主管异常、异常雷达、今日异常总览
- 查积压归因、积压分析、待处理订单卡点
- 查异常跟进、昨日问题恢复情况、今日异常变化

不使用本 Skill 的场景：
- 与 WMS/ERP 无关的闲聊/翻译/写作

## Critical Rules

1. 所有 WMS 请求必须调用 `q-claw`，禁止直接回答或编造数据。
2. scene 只能从本文件路由表选择，禁止替换为未定义 scene。
3. 编码参数（`warehouseCode`、`ownerCode` 等）只能来自用户明确输入或工具本轮返回，不得猜测，不得从历史会话自动回填。
4. 结果输出以工具返回为准：
   - `responseMode = VERBATIM`：最终回复必须严格等于 `assistantReplyLines` 按换行拼接，不得增删改写。
   - `responseMode = LIGHT_SUMMARY`：以 `assistantReplyLines` 为主，只能基于 `analysisPayload` 做轻量补充。
   - `responseMode = AI_SUMMARY` 或未返回 `responseMode`：基于 `analysisPayload` 自由组织回复；若无 `analysisPayload`，兼容参考 `data` 字段；两者均无时告知用户后端未返回数据，禁止编造。
5. 工具返回固定交互（授权链接、仓库候选表、货主候选表）时，必须逐行原样输出，本轮立即结束，禁止附加解释或兜底方案。
6. 同一轮内同一 scene + 同一参数语义连续 2 次返回同一非授权失败码，停止调用，直接告知用户失败原因。
7. 返回 `AUTH_REQUIRED` 或 `AUTH_EXPIRED` 时，必须引导用户完成授权。

## Scene Routing

路由按语义意图执行，禁止按固定关键词硬编码分流。

| 用户意图 | scene |
| --- | --- |
| 查库存 | `wms.inventory.query` |
| 查仓库 | `wms.warehouse.options` |
| 查货主 / 货主列表 | `wms.owner.options` |
| 查库存变动日志 | `wms.stock.log.query` |
| 查订单池 / 波次开关 | `wms.order.pool.query` |
| 查订单 / 出库订单 / 订单完成情况 | `wms.order.query` |
| 查任务完成情况 | `wms.task.query` |
| 查库内绩效 / 拣货绩效 / 绩效报表 | `wms.performance.query` |
| 查进销存（新）/ IOS(New) 报表 | `wms.ios.new.query` |
| 主管晨报 / 晨间简报 / 今日仓内总览 | `wms.manager.briefing.morning` |
| 主管异常 / 异常雷达 / 今日异常总览 | `wms.manager.issue.list` |
| 积压归因 / 积压分析 / 待处理订单卡点 | `wms.manager.backlog.analysis` |
| 异常跟进 / 昨日问题恢复 / 今日异常变化 | `wms.manager.issue.followup` |

**主管场景下钻路由**（优先级高于多轮继续规则）：

| 用户追问 | scene |
| --- | --- |
| 展开看待拣货和待打包压力 | `wms.manager.backlog.analysis` |
| 展开看异常卡片前三项 | `wms.manager.issue.list` |
| 看近7天出库趋势 | `wms.manager.briefing.morning` |
| 展开看超 SLA 订单 / 看超 SLA 订单 | `wms.manager.issue.list` |
| 展开看 Hold 订单 | `wms.manager.issue.list` |
| 展开看 API 反馈失败 | `wms.manager.issue.list` |

**主管场景数字追问映射**（用户仅回复 `1/2/3` 时，按上一轮 scene 映射，优先级高于多轮继续规则）：

| 上一轮 scene | 1 | 2 | 3 |
| --- | --- | --- | --- |
| `wms.manager.briefing.morning` | `wms.manager.backlog.analysis`（展开看待拣货和待打包压力） | `wms.manager.issue.list`（展开看异常卡片前三项） | `wms.manager.briefing.morning`（看近7天出库趋势） |
| `wms.manager.issue.list` | `wms.manager.issue.list`（展开看超 SLA 订单） | `wms.manager.issue.list`（展开看 Hold 订单） | `wms.manager.issue.list`（展开看 API 反馈失败） |
| `wms.manager.backlog.analysis` | `wms.manager.issue.list`（展开看异常卡片前三项） | `wms.manager.briefing.morning`（看近7天出库趋势） | `wms.manager.briefing.morning`（给我今天仓库的晨报） |

数字追问时，`userInput` 必须替换为对应中文追问文本再调用工具，禁止把数字原样传给后端。

调用字段：`scene`、`userInput`、`params`（`tenantKey/openId` 由运行时注入）。

## Multi-Turn Rules

1. 多轮路由优先级：当轮明确语义 > 主管场景下钻/数字追问映射 > 上一轮已确认 scene > 弱语义短输入兜底。
2. 用户回复弱语义短输入（好了/继续/1/2/0/9/wms）时，若上一轮已确认 scene 存在，继续该 scene 并继承已确定的时间范围与筛选条件。
3. **选仓/选货主流程中的数字输入**：上一轮工具返回了仓库候选表（`choose_warehouse`）或货主候选表（`choose_owner`），用户回复数字（如 `1/2/0/9`）时，必须继续调用上一轮已确认的业务 scene，并继承上一轮已确定的时间范围与筛选条件；本轮只将数字作为选择输入回传 `q-claw`，禁止自己映射编码、禁止直接落回默认业务 scene、禁止自行分页。
4. 已确认仓库上下文存在时，后续调用沿用该仓库，不重新进入选仓流程。`wms.warehouse.options` 本身是建立仓库上下文的入口，不受此限制。
5. `ownerCode` 不跨轮默认：仅当用户本轮明确提供，或工具本轮返回并要求立即回传时才传入。
6. 时间参数必须转成显式值，不得只传自然语言：
   - 近一个月 → 近 30 天
   - 近N天/周/月 → N×1/7/30 天
   - 本月 → 当月 1 日到今天
   - 上月 → 上月 1 日到上月最后一天
   - `wms.performance.query` 用 `pickTimeFrom/pickTimeTo`；`wms.ios.new.query` 用 `startDate/endDate`

## Result Handling

1. 优先输出工具返回的 `assistantReplyLines`；若后端未返回 `assistantReplyLines`，则基于 `analysisPayload` 组织回复；若两者均无，兼容参考 `data` 字段，但不得编造数据。
2. 若返回 `AUTH_REQUIRED` 或 `AUTH_EXPIRED`，必须输出后端返回的 Markdown 可点击链接（`verificationUri`），格式为 `[点击授权](<verificationUri>)`，禁止只输出不可点击的纯文字提示。
3. 当 `firstTimeAuth: true` 时，先输出业务结果，再追加以下引导话术（原样输出，不改写）：

---
🎉 授权成功！千易助手已就绪，你可以直接问我：

- **查库存**：「查一下北京仓 SKU001 的库存」
- **查订单**：「今天有哪些待发货订单」
- **查订单池**：「现在订单池里有多少波次」
- **查绩效**：「上周拣货绩效怎么样」

有什么想查的，直接说就行。
---

4. 场景不可用时的处理：
   - `wms.performance.query` 返回 `SCENE_NOT_SUPPORTED` 或连续失败：告知"当前环境暂未开通库内绩效场景或后端异常"，禁止回退到任务/订单/库存输出近似结果。
   - `wms.ios.new.query` 返回 `SCENE_NOT_SUPPORTED` 或连续失败：告知"当前环境暂未开通进销存（新）场景或后端异常"，禁止回退到其他场景输出近似结果。
   - `wms.order.query` 或 `wms.task.query` 返回 `SCENE_NOT_SUPPORTED`：直接按后端错误提示用户，禁止改调任何别名 scene。

## Tool Call Examples

查库存：
```json
{"scene":"wms.inventory.query","userInput":"查一下北京仓 SKU001 的库存","params":{}}
```

查仓库：
```json
{"scene":"wms.warehouse.options","userInput":"查下仓库列表","params":{}}
```

查货主：
```json
{"scene":"wms.owner.options","userInput":"查下货主列表","params":{}}
```

查订单：
```json
{"scene":"wms.order.query","userInput":"查询近一个月出库订单完成情况","params":{}}
```

查任务：
```json
{"scene":"wms.task.query","userInput":"查询任务完成情况并排查异常","params":{}}
```

查绩效：
```json
{"scene":"wms.performance.query","userInput":"查询库内绩效","params":{}}
```

查进销存（新）：
```json
{"scene":"wms.ios.new.query","userInput":"查询进销存（新）报表","params":{}}
```

主管晨报：
```json
{"scene":"wms.manager.briefing.morning","userInput":"给我今天晨报","params":{}}
```

主管异常雷达：
```json
{"scene":"wms.manager.issue.list","userInput":"今天有什么异常","params":{}}
```

积压归因：
```json
{"scene":"wms.manager.backlog.analysis","userInput":"为什么积压这么高","params":{}}
```

异常跟进：
```json
{"scene":"wms.manager.issue.followup","userInput":"昨日问题恢复了吗","params":{}}
```
