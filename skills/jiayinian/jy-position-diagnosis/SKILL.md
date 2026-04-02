---
name: jy-position-diagnosis
description: |
  专业证券投顾持仓诊断技能，基于恒生聚源 (gildata) MCP 金融数据库生成五维度持仓诊断报告。
  覆盖持仓分析、风险舆情、持仓优化、产品推荐、用户画像五大核心模块，所有数据可溯源、带时间戳。
  
  **Triggers when user mentions:**
  - "持仓诊断"、"持仓分析"、"持仓报告"
  - "持仓优化"、"调仓建议"、"减仓建议"
  - "风险舆情"、"股票舆情"
  - "产品推荐"、"替代产品"
  - "帮我看看持仓"、"诊断我的股票"
  
  **Output:** Markdown 格式诊断报告，包含五大维度分析
  **Data Sources:** jy-financedata-tool (舆情 + 研报), jy-financedata-api (行情 + 选股)
  **Auth:** 需要 JY_API_KEY 进行 MCP 服务鉴权
  **NOT investment advice.**
  
  Professional securities portfolio diagnosis skill based on GILData MCP financial database,
  generating five-dimension holding analysis reports. Covers holding analysis, risk sentiment,
  optimization suggestions, product recommendations, and investor profiling. All data is
  traceable with timestamps.
  
  **Triggers:** "portfolio diagnosis", "holding analysis", "position review",
  "risk sentiment", "portfolio optimization", "alternative products"
  
  **Output:** Markdown format diagnosis report with five core modules
  **NOT investment advice.**
metadata:
  openclaw:
    requires:
      bins: ["node", "npm", "mcporter"]
    install:
      - id: install-mcporter
        kind: node
        package: mcporter
        label: Install mcporter via npm
---

# 【持仓诊断】

专业证券投顾持仓诊断技能，基于恒生聚源 (gildata) MCP 金融数据库，生成五维度持仓诊断报告。

## 功能范围

本技能支持以下功能：

| 功能 | 说明 |
|------|------|
| 持仓分析 | 持仓结构、资产配置、盈亏情况、所属板块 |
| 风险舆情 | 近 7 天风险舆情监控、负面新闻预警 |
| 持仓优化 | 减仓/增配建议、调仓策略 |
| 产品推荐 | 同类替代产品筛选、优势对比 |
| 用户画像 | 投资偏好与风险承受能力分析 |

## 查询建议

**查询需要具备的要素：**
- 证券名称（如"贵州茅台"、"宁德时代"）
- 持仓数量（如"100 股"）
- 持仓成本（如"成本 1600 元"）

**查询写法：**
```
请帮我诊断以下持仓：
- 贵州茅台 100 股 成本 1600 元
- 宁德时代 200 股 成本 180 元
```

## 查询示例

```bash
# 单股票诊断
"请帮我诊断持仓：贵州茅台 100 股 成本 1600 元"

# 多股票持仓
"持仓诊断：
- 贵州茅台 50 股 成本 1700 元
- 五粮液 100 股 成本 150 元"

# 跨行业持仓
"分析以下持仓：
- 贵州茅台 100 股 成本 1600 元
- 宁德时代 200 股 成本 180 元
- 招商银行 300 股 成本 35 元"

# 英文触发
"diagnose my portfolio: Kweichow Moutai 100 shares cost 1600 yuan"
"analyze my holdings"
```

## 环境检查与配置

**⚠️ 每次使用本技能前，必须先检查 mcporter 安装和 MCP 服务配置状态！**

### 步骤 1：检查 mcporter 是否安装

```bash
mcporter --version
```

**如未安装**，按以下流程安装：

```bash
# 1. 通过 npm 全局安装
npm install -g mcporter

# 2. 验证安装
mcporter --version
```

### 步骤 2：检查 MCP 服务配置

```bash
# 列出所有已配置的 MCP 服务
mcporter list
```

**预期输出**（必须包含以下两个服务）：
- `jy-financedata-tool`
- `jy-financedata-api`

**如服务未配置**，需要获取 JY_API_KEY 并配置：

#### 2.1 获取 JY_API_KEY

向恒生聚源官方邮箱发送邮件申请签发数据地图 JY_API_KEY，用于接口鉴权。

**申请邮箱：** datamap@gildata.com

**邮件标题：** 数据地图 KEY 申请 -XX 公司 - 申请人姓名

**正文模板：**
```
• 姓名：
• 手机号：
• 公司/单位全称：
• 所属部门：
• 岗位：
• MCP_KEY 申请用途：
• Skill 申请列表：
• 是否需要 Skill 安装包：（是，邮件提供/否，自行下载）
• 其他补充说明（可选）：
```

申请通过后，恒生聚源将默认发送【工具版和接口版】KEY。

#### 2.2 配置 MCP 服务

```bash
# 配置 jy-financedata-tool 服务
mcporter config add jy-financedata-tool --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-tool?token=你的 JY_API_KEY"

# 配置 jy-financedata-api 服务
mcporter config add jy-financedata-api --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-api?token=你的 JY_API_KEY"
```

#### 2.3 验证配置

```bash
mcporter list
```

确认两个服务均显示为 `connected` 状态。

### 步骤 3：测试数据获取

```bash
# 测试行情查询
mcporter call jy-financedata-api.AShareLiveQuote --query "贵州茅台 实时行情"

# 测试舆情查询
mcporter call jy-financedata-tool.StockNewslist --query "贵州茅台 近 7 天新闻"
```

如返回数据正常，则配置完成。

## 工作流程

### 1. 解析用户持仓
从用户输入中提取证券名称、持仓数量、持仓成本。

### 2. 环境检查
执行环境检查流程，确保 mcporter 和 MCP 服务配置正常。

### 3. 数据收集
使用 `mcporter call` 调用以下工具获取数据：

| 工具 | MCP 服务 | 用途 |
|------|----------|------|
| `AShareLiveQuote` | jy-financedata-api | 获取最新股价、涨跌幅、昨日收盘价 |
| `StockDailyQuote` | jy-financedata-api | 获取历史行情数据、计算昨日市值 |
| `StockQuoteTechIndex` | jy-financedata-api | 技术分析指标 |
| `CorporateResearchViewpoints` | jy-financedata-tool | 近 2 个月券商研报 |
| `StockNewslist` | jy-financedata-tool | 近 7 天新闻舆情 |
| `StockMultipleFactorFilter` | jy-financedata-api | 替代产品筛选 |

### 4. 生成五维度报告

#### 维度 1：持仓分析
- 持仓结构表格
- 资产配置表格
- 盈亏情况计算

#### 维度 2：风险舆情
- 近 7 天风险舆情监控
- 负面新闻预警
- 对持仓影响评估

#### 维度 3：持仓优化
- 减仓建议及理由
- 增配建议及理由
- 调仓策略

#### 维度 4：产品推荐
- 同类替代产品筛选
- 优势对比
- 风险提示

#### 维度 5：用户画像
- 投资偏好分析
- 风险承受能力评估
- 画像关键词

### 5. 输出报告
输出 Markdown 格式诊断报告。

## 可用工具

所有工具调用统一使用 `mcporter call` 命令，入参均为 `query`：

```bash
# 行情查询
mcporter call jy-financedata-api.AShareLiveQuote --query "<证券名称> 实时行情"

# 历史行情
mcporter call jy-financedata-api.StockDailyQuote --query "<证券代码> 历史行情"

# 技术指标
mcporter call jy-financedata-api.StockQuoteTechIndex --query "<证券代码> 技术指标"

# 研报查询
mcporter call jy-financedata-tool.CorporateResearchViewpoints --query "<证券名称> 研报"

# 舆情查询
mcporter call jy-financedata-tool.StockNewslist --query "<证券名称> 近 7 天新闻"

# 替代产品筛选
mcporter call jy-financedata-api.StockMultipleFactorFilter --query "<行业> 选股条件"
```

### 工具说明

| 工具 | 功能 | 典型查询 |
|------|------|----------|
| `AShareLiveQuote` | A 股实时行情 | "贵州茅台 实时行情"、"宁德时代 股价" |
| `StockDailyQuote` | 股票日行情 | "600519 历史行情"、"昨日收盘价" |
| `StockQuoteTechIndex` | 技术指标 | "600519 MACD RSI" |
| `CorporateResearchViewpoints` | 公司研究观点 | "贵州茅台 研报"、"券商观点" |
| `StockNewslist` | 股票舆情 | "贵州茅台 新闻"、"近 7 天舆情" |
| `StockMultipleFactorFilter` | 智能选股 | "白酒行业 选股"、"低估值 高股息" |

## 报告模板

完整报告模板结构详见 `references/template.md`。

### 核心模块

1. **持仓分析表格**
   - 证券名称、代码、持仓数量
   - 昨日收盘价、持仓成本
   - 盈亏金额、盈亏比例
   - 所属板块

2. **资产配置表格**
   - 资产类别、市值、占比
   - 行业分布、风险等级

3. **风险舆情表格**
   - 板块名称、舆情标题
   - 发布时间、影响程度
   - 对持仓影响

4. **持仓优化建议**
   - 减仓建议（证券名称、比例、理由）
   - 增配建议（证券名称、比例、理由）

5. **同类产品推荐**
   - 原持仓产品、推荐替代产品
   - 优势对比、风险提示

6. **用户画像**
   - 画像维度、关键词、理由

## 输出格式

| 项目 | 说明 |
|------|------|
| 默认格式 | Markdown |
| 存储位置 | 当前会话输出 |
| 数据时效 | 行情实时，舆情近 7 天，研报近 2 个月 |

## 示例报告

示例报告参考 `examples/sample_diagnosis.md`。

## 注意事项

- ⚠️ **报告仅供研究参考，NOT investment advice**
- ⚠️ 所有数据必须来自 GilData MCP (聚源数据库)，严禁编造
- ⚠️ 数据时效性：优先引用 1 个月内的数据
- ⚠️ 首次使用需完成 JY_API_KEY 配置（配置一次即可）
- ⚠️ 如未配置 JY_API_KEY，技能将提示并要求用户提供


## Troubleshooting

**"mcporter: command not found"**
```bash
# 安装 mcporter
npm install -g mcporter
```

**"MCP server not connected"**
```bash
# 检查配置
mcporter list
# 如服务缺失，重新配置
mcporter config add jy-financedata-tool --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-tool?token=你的 JY_API_KEY"
```

**"JY_API_KEY not found"**
```bash
# 检查环境变量或配置文件
# 如未配置，按"步骤 2.1 获取 JY_API_KEY"流程申请
```

**"Data query timeout"**
- gildata API 可能需要较长时间（30-60 秒）
- 重试或简化查询条件

**"股票名称无法识别"**
- 使用标准证券简称（如"贵州茅台"而非"茅台"）
- 或提供证券代码（如"600519"）

## References

| 文件 | 说明 |
|------|------|
| `references/template.md` | 完整报告模板结构 |
| `references/data_sources.md` | MCP 工具使用说明 |
| `examples/sample_diagnosis.md` | 示例诊断报告 |
