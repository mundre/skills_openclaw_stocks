---
name: yingmi-skill
description: 当用户需要查询基金、策略、公告、财经资讯，做资产配置、组合诊断、风险回测、现金流分析，或生成图表、PDF 时，优先使用本 Skill 获取真实数据与可执行能力。
license: MIT
version: 0.1.3
---


# yingmi-skill

本 Skill 通过 `yingmi-skill-cli` npm 包连接且慢 MCP 服务，提供基金查询、策略分析、资产配置等金融数据与分析能力。

## 前置条件

首次安装本 Skill 后，Agent 必须先执行一轮完整的 [CLI前置检查工作流](references/CLI前置检查.md)，确认 `yingmi-skill-cli` 已安装、已更新且环境已初始化；

执行任何 MCP 调用前，AI 必须先完成以下三个前置检查，禁止跳过。在前置检查完成前，不得直接进入后续 MCP 调用。

1. 环境检查：确认 `node -v` 和 `git --version` 可正常执行；若缺少 `node` 或 `git`，先引导用户安装对应环境，再继续后续检查。
2. [CLI前置检查工作流](references/CLI前置检查.md)
3. Skill 更新检查：执行 `scripts/check-upgrade.sh`

## 技能概览

### 第一类：MCP 原子能力

适用时机：当用户要查询基金、策略、公告、财经资讯，做资产配置、组合诊断、风险回测、现金流分析，或生成图表、PDF 时，优先直接调用 `mcp` 工具，不进入场景 skill。

标准用法：

1. 先执行 `yingmi-skill-cli mcp list` 查看全部工具摘要。
2. 选中目标工具后，必须先执行 `yingmi-skill-cli mcp schema <toolName>` 确认参数 Schema。
3. 确认入参后，再执行 `yingmi-skill-cli mcp call <toolName> --input '<json>'` 发起调用。
4. 如果要串联多个工具，优先按“先检索标的，再查详情，再做分析 / 渲染”的顺序执行。

调用示例：

```bash
# 先看工具列表
yingmi-skill-cli mcp list

# 无参数工具
yingmi-skill-cli mcp schema GetCurrentTime
yingmi-skill-cli mcp call GetCurrentTime --input '{}'

# 有参数工具
yingmi-skill-cli mcp schema SearchFunds
yingmi-skill-cli mcp call SearchFunds --input '{"keyword":"易方达蓝筹","size":3}'

# 一次查看多个工具的 Schema
yingmi-skill-cli mcp schema BatchGetFundsDetail GetFundDiagnosis GetFundsBackTest
```

能力分组：完整工具列表以 `yingmi-skill-cli mcp list` 的实时输出为准。

| 能力分组 | 什么时候使用 | 常用工具 |
| --- | --- | --- |
| 基础时间能力 | 需要确认当前时间、交易日范围等基础上下文时使用 | `GetCurrentTime`、`GetTxnDayRange` |
| 基金检索与基础资料 | 用户只知道基金名称、要确认基金代码，或需要基金详情、公告、交易规则时使用 | `SearchFunds`、`GuessFundCode`、`BatchGetFundsDetail`、`GetPopularFund`、`GetFundAnnouncements`、`GetAnnouncementContent`、`BatchGetFundTradeLimit`、`BatchGetFundTradeRules` |
| 单只基金深度分析 | 用户已明确某只基金，想看业绩、风险、持仓、归因、行业、债基异动或风格指标时使用 | `GetFundDiagnosis`、`AnalyzeFundRisk`、`GetBatchFundPerformance`、`BatchGetFundNavHistory`、`BatchGetFundsHolding`、`GetFundAssetClassAnalysis`、`getFundBenchmarkInfo`、`getFundBrinsonIndicator`、`getFundCampisiIndicator`、`getFundIndustryAllocation`、`getFundIndustryConcentration`、`getFundIndustryPreference`、`getFundIndustryReturns`、`getFundTurnoverRate`、`fund-equity-position`、`fund-recovery-ability`、`fund-sector-preference`、`getMarketTimingIndicator`、`getStockAllocationAndMetricsByFundCode`、`getQdFundAreaAllocation`、`getBondAllocationByFundCode`、`getBondFundCreditRatingLevel`、`getBondIndicator`、`getBondFundWithAlertRecord`、`getFundDiveCount` |
| 组合与策略分析 | 用户提供多只基金或策略，想做相关性分析、回测、风险评估、穿透配置、组合诊断时使用 | `GetFundsCorrelation`、`GetFundsBackTest`、`DiagnoseFundPortfolio`、`AnalyzePortfolioRisk`、`GetAssetAllocation`、`MonteCarloSimulate`、`GetPortfolioNavHistory`、`GetFundRelatedStrategies`、`StrategySearchByKeyword`、`GetStrategyDetails`、`GetStrategyRiskInfo`、`BatchGetStrategyRiskInfo`、`BatchGetStrategiesComposition`、`BatchGetPoTradeComposition`、`GetStrategyAssetClassAnalysis`、`GetStrategyBenchmark` |
| 财富规划与资产配置 | 用户已提供家庭成员、收支、资产负债、风险偏好或目标，希望直接做单项测算或配置方案时使用 | `AnalyzeFamilyMembers`、`AnalyzeIncomeExpense`、`AnalyzeAssetLiability`、`AnalyzeCashFlow`、`AnalyzeFinancialIndicators`、`GetAssetAllocationPlan`、`GetCompositeModel`、`AnalyzeInvestmentPerformance` |
| 基金筛选与排雷 | 用户不知道选什么基金，或想按券种、信用评级、换手率等条件筛选时使用 | `filterBondFundByBondType`、`filterBondFundByCreditRating`、`filterStockFundByStockTurnover` |
| 市场资讯与内容素材 | 用户要市场行情、财经资讯、热点、基金经理观点或投顾内容素材时使用 | `GetLatestQuotations`、`SearchFinancialNews`、`SearchHotTopic`、`SearchManagerViewpoint`、`searchInvestAdvisorContent`、`searchRealtimeAiAnalysis` |
| 图表与报告输出 | 用户已经有结构化数据，需要渲染图表、输出图片或导出 PDF 时使用 | `RenderEchart`、`RenderHtmlToPdf` |

### 第二类：场景 skill

适用时机：当用户的问题已经明确命中某个金融场景，需要完整的分析流程、脚本执行约束或固定输出模板时，优先进入对应 `remote-skill`，再按该 skill 的 `SKILL.md` 执行。

标准用法：

1. 执行 `yingmi-skill-cli remote-skill list` 查看当前可用的场景 skill。
2. 选中目标 skill 后，执行 `yingmi-skill-cli remote-skill enter <skillName>` 进入该 skill 上下文。
3. 进入后，优先执行 `yingmi-skill-cli remote-skill exec --script 'cat SKILL.md'` 阅读该 skill 的完整说明。
4. 后续所有脚本执行都通过 `yingmi-skill-cli remote-skill exec --script '<command>'` 或 `--script-file <path>` 完成。
5. 场景 skill 内部如果还要调用 MCP 工具，仍然必须遵循第一类能力的规则：先 `mcp schema`，再 `mcp call`。

调用示例：

```bash
# 查看场景 skill 列表
yingmi-skill-cli remote-skill list

# 进入某个 skill 上下文
yingmi-skill-cli remote-skill enter fund-analyst

# 先读取 skill 说明，再执行后续脚本
yingmi-skill-cli remote-skill exec --script 'cat SKILL.md'
```

场景 skill 清单：完整列表以 `yingmi-skill-cli remote-skill list` 的实时输出为准。

| 场景 skill | 什么时候使用 | 说明 |
| --- | --- | --- |
| `fund-analyst` | 用户已经明确基金代码或基金名称，想知道“这只基金怎么样”时使用 | 提供单只基金深度分析、多基金对比、持仓与交易规则解读 |
| `portfolio-doctor` | 用户提供基金持仓组合，想判断组合是否合理、是否要优化时使用 | 提供组合诊断、资产配置分析、相关性评估、回测和蒙特卡洛模拟 |
| `fund-screener` | 用户不知道买什么，想筛选基金、推荐基金或排查问题基金时使用 | 提供多维度选基、热门基金推荐、债基排雷、策略组合查找 |
| `market-morning-brief` | 用户要市场早报、行情速报、热点汇总、基金经理观点摘要时使用 | 聚合行情、资讯、热点和投顾内容，生成结构化市场简报 |
| `advisor-content-studio` | 用户要写市场解读、基金推荐文案、投教内容、热点评论或做内容排版时使用 | 负责选题发现、素材搜集、写作与 HTML / 长图排版 |
| `family-financial-planner` | 用户要做家庭财务规划、财务体检、收支梳理、退休目标或配置方案时使用 | 提供家庭财务规划与体检的完整流程 |
| `qieman-wealth-family-advisor` | 用户要执行且慢财富规划主流程时使用 | 聚合收支分析、资产负债评估、现金流预测与资产配置等环节 |
| `qieman-wealth-goalmatch` | 用户不知道该设什么财富目标，希望系统推荐优先目标时使用 | 根据家庭画像与财务数据推荐 2 到 4 个目标 |
| `qieman-wealth-goalcalc` | 用户要测算“每月投多少、几年后能有多少、目标能否达成”时使用 | 基于复利公式做目标终值与达成率测算 |
| `qieman-wealth-healthcheck` | 用户已经有结构化财务数据，想快速计算健康指标和评级时使用 | 计算 9 项财务健康指标与评级，并输出 HTML 报告 |
| `qieman-wealth-report` | 用户已经完成规划分析，接下来要生成完整书面报告时使用 | 汇总全量数据，输出 9 大模块的完整规划报告 |
| `data-visualization` | 用户要做图表、仪表板、交互式可视化或导出 HTML / PNG / SVG / PDF 时使用 | 提供通用数据可视化与多格式输出能力 |
