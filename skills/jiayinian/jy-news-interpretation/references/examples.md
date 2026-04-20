# 使用示例合集

本文件包含 jy-news-interpretation 技能的完整使用示例。

---

## 示例 1:24 小时财经热点速报

**用户查询**：今天有什么重要财经新闻？

**工具调用**：
```bash
# 使用 FinQuery 查询近期财经新闻
mcporter call jy-financedata-tool.FinQuery query="过去 24 小时财经热点新闻" --output json
```

**输出示例**：
```markdown
## 📅 财经日报 | 2026 年 3 月 31 日

### 🔥 热点速览
1. 中东局势升级，油价恐飙破 200 美元
2. 820 亿美元出逃！多国狂抛美债
3. 鲍威尔今晚亮相，降息预期生变
4. 国行版苹果 AI 上线后被撤回
5. 谷歌 TurboQuant 引爆内存股恐慌
...

### 📰 国内要闻
**三大指数集体收跌，创业板指跌 2.7% 领跌**
A 股今日全线回调，市场交投偏淡。上证指数收报 3891.86 点，跌 0.80%...

**关联标的**
| 名称 | 代码 | 现价 | 涨跌幅 | 影响 |
|------|------|------|--------|------|
| 上证指数 | 000001.SH | 3891.86 | -0.80% | 中性 |
```

---

## 示例 2：单条新闻深度解读

**用户查询**：帮我解读一下美联储加息的新闻

**工具调用**：
```bash
# 使用 FinancialResearchReport 获取研报观点
mcporter call jy-financedata-tool.FinancialResearchReport query="美联储加息 影响分析" --output json
# 使用 MacroIndustryData 查询宏观经济数据
mcporter call jy-financedata-tool.MacroIndustryData query="美联储加息 宏观经济" --output json
```

**输出示例**：
```markdown
## 📰 新闻解读：美联储加息

### 1️⃣ 热点速览
- **核心事件**：美联储宣布加息 25 个基点
- **时间**：2026 年 3 月 30 日
- **来源**：美联储官网

### 2️⃣ 深度解读
美联储在本次 FOMC 会议后宣布将联邦基金利率目标区间上调 25 个基点至 4.50%-4.75%...

### 4️⃣ 影响路径分析
> 美联储加息→美元走强→人民币贬值压力→外资流出 A 股→成长股估值承压→消费/科技板块回调

### 5️⃣ 关联标的
| 名称 | 代码 | 现价 | 涨跌幅 | 影响类型 |
|------|------|------|--------|----------|
| 贵州茅台 | 600519.SH | 1680.00 | -1.2% | 利空 |
| 宁德时代 | 300750.SZ | 185.50 | -2.5% | 利空 |
```

---

## 示例 3：行业新闻影响分析

**用户查询**：新能源行业最新政策新闻对市场的影响

**工具调用**：
```bash
# 使用 MacroIndustryData 查询行业经济数据
mcporter call jy-financedata-tool.MacroIndustryData query="新能源行业 政策 经济数据" --output json
# 使用 StockBelongIndustry 查询行业归属
mcporter call jy-financedata-api.StockBelongIndustry query="新能源汽车 上市公司" --output json
```

**输出示例**：
```markdown
## 🏭 行业分析：新能源汽车

### 最新动态
**新能源汽车购置税减免政策延续至 2027 年**
财政部等四部门联合发布公告，明确新能源汽车购置税减免政策延续...

### 行业数据
| 指标 | 数值 | 同比 | 环比 |
|------|------|------|------|
| 行业指数 | 2850.32 | +5.2% | +1.8% |
| 平均 PE | 28.5 | -12% | -3% |

### 关联标的
| 名称 | 代码 | 现价 | 涨跌幅 | 影响 |
|------|------|------|--------|------|
| 宁德时代 | 300750.SZ | 185.50 | +3.2% | 利好 |
| 比亚迪 | 002594.SZ | 225.80 | +2.8% | 利好 |
```

---

## 示例 4：个股公告解读

**用户查询**：贵州茅台最新公告深度解读

**工具调用**：
```bash
# 使用 CompanyBasicInfo 查询公司基本信息
mcporter call jy-financedata-api.CompanyBasicInfo query="贵州茅台 600519.SH" --output json
# 使用 PerformanceForecast 查询业绩预告
mcporter call jy-financedata-api.PerformanceForecast query="600519.SH 业绩预告" --output json
# 使用 FinancialAnalysis 查询财务分析指标
mcporter call jy-financedata-api.FinancialAnalysis query="600519.SH 财务指标" --output json
```

**输出示例**：
```markdown
### 📢 重要公告

**贵州茅台：2025 年年度报告**
公告编号：2026-015，发布时间：2026-03-30 18:00

公司 2025 年实现营收 1500 亿元，同比增长 15.2%；归母净利润 750 亿元，同比增长 18.5%...

**关联标的**
| 名称 | 代码 | 现价 | 涨跌幅 | 影响 |
|------|------|------|--------|------|
| 贵州茅台 | 600519.SH | 1680.00 | +1.5% | 利好 |
| 五粮液 | 000858.SZ | 165.20 | +0.8% | 利好 |
```

---

## 示例 5：关联标的分析

**用户查询**：分析中东局势对 A 股的影响及关联标的

**工具调用**：
```bash
# 使用 StockMultipleFactorFilter 筛选相关股票
mcporter call jy-financedata-tool.SmartStockSelection query="石油开采行业 上市公司" --output json
# 使用 StockBelongConcept 查询概念板块归属
mcporter call jy-financedata-api.StockBelongConcept query="原油概念 股票" --output json
# 使用 MarketPerformanceComparison 对比市场表现
mcporter call jy-financedata-api.MarketPerformanceComparison query="石油行业 市场表现" --output json
```

**输出示例**：
```markdown
### 关联标的分析

**直接受益标的（石油开采）**
| 名称 | 代码 | 逻辑说明 |
|------|------|----------|
| 中国海油 | 600938.SH | 纯上游开采，油价弹性最大 |
| 中国石油 | 601857.SH | 上游业务占比高，受益油价上涨 |

**直接受损标的（航空）**
| 名称 | 代码 | 逻辑说明 |
|------|------|----------|
| 南方航空 | 600029.SH | 燃油成本占总成本 30%+ |
| 中国国航 | 601111.SH | 国际航线占比高，燃油成本敏感 |
```

---

## 示例 6：定时任务配置

**每日 8:40 自动生成财经日报**

**Cron 配置**：
```json
{
  "name": "每日财经日报",
  "schedule": {
    "kind": "cron",
    "expr": "40 8 * * 1-5",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "请生成今日财经日报，包含过去 24 小时重要财经新闻、市场数据速览和关联标的分析"
  },
  "sessionTarget": "isolated",
  "enabled": true
}
```

---

## 示例 7：多格式输出

**Markdown 输出（默认）**
```bash
mcporter call jy-financedata-tool.FinQuery query="今日财经热点" --output json
```

**HTML 输出**
```bash
mcporter call jy-financedata-tool.FinQuery query="今日财经热点" --output html
```

**JSON 输出（程序化处理）**
```bash
mcporter call jy-financedata-tool.FinQuery query="今日财经热点" --output json --raw
```

---

## 错误处理示例

**场景 1：JY_API_KEY 未配置**
```
❌ 未检测到聚源数据 MCP 服务配置
请先配置 JY_API_KEY 并添加 MCP 服务（见环境检查与配置章节）

配置指引：
1. 发送邮件至 datamap@gildata.com 申请 API Key
2. 配置 MCP 服务：
   mcporter config add jy-financedata-tool --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-tool?token=你的 KEY"
   mcporter config add jy-financedata-api --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-api?token=你的 KEY"
3. 验证配置：mcporter list
```

**场景 2：服务调用失败**
```
⚠️ 聚源数据服务调用失败，正在重试 (1/3)...
⚠️ 聚源数据服务调用失败，正在重试 (2/3)...
⚠️ 聚源数据服务调用失败，正在重试 (3/3)...
❌ 服务调用失败，请稍后重试或联系管理员检查 API Key 状态
```

**场景 3：数据为空**
```
ℹ️ 过去 24 小时内未检测到重大财经新闻
建议：
- 扩大时间范围至近 3 天或近一周
- 指定具体行业或公司进行查询
- 检查新闻源是否正常更新
```
