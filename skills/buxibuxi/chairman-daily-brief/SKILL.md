---
name: chairman-daily-brief
description: >-
  上市公司董事长专属早晚报 skill。为高管提供战略决策视角的每日简报，
  涵盖公司股价异动、行业政策动态、竞争对手动向、资本市场情绪、
  监管公告提醒等关键信息。早班聚焦开盘前瞻与风险预警，
  晚报侧重收盘复盘与明日策略。数据源自 QVeris 多源聚合。
env:
  - QVERIS_API_KEY
requirements:
  env_vars:
    - QVERIS_API_KEY
credentials:
  required:
    - QVERIS_API_KEY
  primary: QVERIS_API_KEY
  scope: read-only
  endpoint: https://qveris.ai/api/v1
runtime:
  language: nodejs
  node: ">=18"
install:
  mechanism: local-skill-execution
  external_installer: false
  package_manager_required: false
persistence:
  writes_within_skill_dir:
    - config/companies.json
    - config/watchlist.json
    - .evolution/tool-evolution.json
  writes_outside_skill_dir: false
security:
  full_content_file_url:
    enabled: true
    allowed_hosts:
      - qveris.ai
    protocol: https
network:
  outbound_hosts:
    - qveris.ai
metadata:
  openclaw:
    requires:
      env: ["QVERIS_API_KEY"]
    primaryEnv: "QVERIS_API_KEY"
    homepage: https://qveris.ai
auto_invoke: true
source: https://qveris.ai
examples:
  - "生成早班报告：关注 600519.SS 茅台"
  - "董事长晚报：生成 0700.HK 腾讯的收盘简报"
  - "早班简报：比亚迪及新能源汽车行业"
  - "生成早班报告，关注竞争对手宁德时代"
  - "晚报：汇总我关注的三家上市公司今日动态"
---

# 董事长早晚报 (Chairman Daily Brief)

专为上市公司董事长设计的高管视角每日市场简报系统。

## 核心价值

区别于普通投资者看盘，本 skill 从**董事长决策视角**出发：

- **股价异动 → 影响解读**：不是看涨跌，而是分析对融资、并购、股东关系的影响
- **行业政策 → 战略机会**：第一时间捕捉监管变化带来的业务机会或风险
- **竞争对手 → 对标分析**：对手重大动作对本公司的影响评估
- **市场情绪 → 资本策略**：投资者情绪对公司资本运作的时机建议
- **公告提醒 → 合规预警**：监管公告、重大事项提醒

## 早晚报差异

### 早班 (Morning Brief) — 开盘前 7:00-9:00

**目标**：让董事长在开盘前掌握全局，做好应对准备

**内容模块**：
1. **隔夜全球市场**：美股、港股、A50 期指走势对今日开盘的影响
2. **宏观政策速递**： overnight 发布的行业政策、监管动态
3. **本公司前瞻**：盘前股价预期、今日关键价位、潜在波动因素
4. **行业雷达**：行业内其他公司重大事项、行业指数走势
5. **竞争情报**：主要竞争对手的最新动态与应对建议
6. **风险提示**：需要关注的潜在风险点
7. **今日重点关注**：会议、公告、投资者活动等日程提醒

### 晚报 (Evening Brief) — 收盘后 15:30-18:00

**目标**：复盘今日表现，规划明日策略

**内容模块**：
1. **收盘概览**：大盘走势、行业表现、本公司股价表现
2. **成交分析**：成交量、资金流向、龙虎榜（如有）
3. **今日公告**：本公司及竞争对手的重要公告汇总
4. **舆情监控**：媒体报道、分析师观点、社交媒体情绪
5. **机构动向**：研报评级变动、目标价调整、大宗交易
6. **政策解读**：当日发布的相关政策对公司的影响分析
7. **明日策略建议**：基于今日行情的明日应对策略

## 数据源

通过 QVeris 聚合多源数据：

- **行情数据**：THS iFinD、Alpha Vantage、Yahoo Finance
- **财经新闻**：Caidazi 新闻、同花顺财经、东方财富
- **研报数据**：Caidazi 研报、分析师评级
- **政策公告**：交易所公告、证监会发布、行业协会
- **社交媒体**：X/Twitter 情绪、雪球讨论热度
- **宏观数据**：经济数据、行业统计

## 使用方式

### 生成早班报告

```bash
# 单公司早班
node scripts/chairman_daily.mjs morning --symbol 600519.SS --company 贵州茅台

# 多公司早班（投资组合视角）
node scripts/chairman_daily.mjs morning --watchlist holdings

# 带行业关注
node scripts/chairman_daily.mjs morning --symbol 002594.SZ --industry 新能源汽车
```

### 生成晚报

```bash
# 单公司晚报
node scripts/chairman_daily.mjs evening --symbol 0700.HK --company 腾讯控股

# 完整复盘（含竞争对手分析）
node scripts/chairman_daily.mjs evening --symbol 000858.SZ --competitors 000568.SZ,000596.SZ

# 简洁模式（仅关键信息）
node scripts/chairman_daily.mjs evening --symbol AAPL --format summary
```

### 管理关注列表

```bash
# 添加关注公司
node scripts/chairman_daily.mjs watch --action add --symbol 600519.SS --company 贵州茅台 --role self

# 添加竞争对手
node scripts/chairman_daily.mjs watch --action add --symbol 002594.SZ --company 比亚迪 --role competitor --peer-group 新能源汽车

# 查看关注列表
node scripts/chairman_daily.mjs watch --action list

# 删除关注
node scripts/chairman_daily.mjs watch --action remove --symbol 600519.SS
```

### OpenClaw 定时任务设置

```bash
# 早班定时（工作日 8:00）
openclaw cron add \
  --name "董事长早班简报" \
  --cron "0 8 * * 1-5" \
  --tz Asia/Shanghai \
  --session isolated \
  --message "运行 chairman-daily-brief 生成早班报告：node scripts/chairman_daily.mjs morning --watchlist holdings" \
  --channel feishu \
  --to <chat-id>

# 晚报定时（工作日 15:35）
openclaw cron add \
  --name "董事长晚报简报" \
  --cron "35 15 * * 1-5" \
  --tz Asia/Shanghai \
  --session isolated \
  --message "运行 chairman-daily-brief 生成晚报：node scripts/chairman_daily.mjs evening --watchlist holdings" \
  --channel feishu \
  --to <chat-id>
```

## 输出格式

### 早班报告示例

```markdown
# 📊 董事长早班简报 — 贵州茅台 (600519.SH)
📅 2026年3月4日 星期二 08:00

---

## 🌍 隔夜全球市场
| 市场 | 收盘 | 涨跌 | 对A股影响 |
|------|------|------|-----------|
| 道琼斯 | 43,850 | +0.5% | 正面 |
| 纳斯达克 | 18,920 | +1.2% | 正面 |
| 恒生指数 | 23,450 | -0.3% | 轻微负面 |
| A50期指 | 13,280 | +0.4% | 正面开盘预期 |

**点评**：美股科技股强势反弹，对A股成长股情绪有提振作用。A50期指小幅上涨，预计今日茅台开盘平稳。

---

## 📰 宏观政策速递
🔔 **白酒行业监管新规** — 市场监管总局发布《白酒标签标识管理办法》征求意见稿，对高端白酒的营销宣传提出更严格要求。
- **影响评估**：中性偏负面，短期或影响营销投入
- **应对建议**：提前梳理广告合规性，准备投资者沟通话术

---

## 📈 本公司前瞻
| 指标 | 数值 | 预期 |
|------|------|------|
| 昨收 | 1,580元 | - |
| 盘前情绪 | 中性 | 小幅高开预期 |
| 关键阻力位 | 1,600元 | 突破需放量 |
| 关键支撑位 | 1,550元 | 强支撑 |

**今日关注点**：
- 是否有机构研报发布
- 北向资金流向
- 经销商渠道动销数据传闻

---

## 🏭 行业雷达
| 公司 | 动态 | 影响 |
|------|------|------|
| 五粮液 | 发布年报预告，净利润+12% | 行业景气度确认 |
| 泸州老窖 | 宣布提价5% | 行业定价权稳固 |

---

## 🎯 竞争情报
**五粮液 (000858.SZ)** — 年报超预期
- **要点**：四季度营收加速，高端产品占比提升
- **对茅台影响**：行业竞争加剧，需关注自身市场份额
- **建议**：加速直销渠道建设，提升消费者触达效率

---

## ⚠️ 风险提示
1. **政策风险**：白酒行业监管趋严，关注后续细则
2. **估值风险**：当前PE 28x，高于历史均值，需业绩持续增长支撑
3. **外资流出**：北向资金连续3日净卖出，需关注持续性

---

## 📅 今日重点关注
- 09:30 国家统计局公布2月CPI数据
- 10:00 公司投资者关系部季度沟通会
- 14:00 行业协会座谈会（董事长出席）

---
*数据来源：QVeris | THS iFinD、Caidazi、同花顺财经*
```

### 晚报报告示例

```markdown
# 🌙 董事长晚报 — 腾讯控股 (0700.HK)
📅 2026年3月4日 星期二 18:00

---

## 📊 收盘概览
| 指标 | 数值 | 变动 |
|------|------|------|
| 收盘价 | 485.00 HKD | +2.5% |
| 成交量 | 1,250万股 | 放量15% |
| 成交额 | 60.6亿 HKD | - |
| 市值 | 4.62万亿 HKD | - |

**大盘对比**：恒指 +0.8%，腾讯跑赢大盘 1.7个百分点

---

## 💰 成交分析
- **资金流向**：北向资金净买入 8.5亿港元
- **主力资金**：大单净流入 5.2亿港元
- **龙虎榜**：未上榜

---

## 📢 今日公告
**本公司公告**：
- 无重大事项公告

**行业公告**：
- 网易发布Q4财报，游戏业务超预期
- 监管部门发布游戏版号新一批名单

---

## 📰 舆情监控
**媒体报道**：
- 彭博：腾讯AI业务布局加速，对标OpenAI
- 财新：微信视频号商业化提速，广告收入预期上调

**分析师观点**：
- 高盛：维持"买入"评级，目标价 520 HKD（+7%）
- 摩根士丹利：上调至"增持"，看好云业务扭亏

**社交媒体情绪**：正面（72% 正面，18% 中性，10% 负面）

---

## 🏦 机构动向
| 机构 | 评级变动 | 目标价 | 点评 |
|------|----------|--------|------|
| 高盛 | 维持买入 | 520 HKD | AI业务催化剂 |
| 大摩 | 上调至增持 | 510 HKD | 云业务扭亏 |
| 瑞银 | 维持中性 | 480 HKD | 估值合理 |

**大宗交易**：今日无大宗交易

---

## 📋 政策解读
**游戏版号常态化发放**
- **政策内容**：今日发放新一批游戏版号，腾讯获批2款
- **影响分析**：行业政策环境持续改善，利好游戏业务增长
- **战略意义**：为后续新品上线铺平道路

---

## 🎯 明日策略建议
**基于今日行情，建议明日关注**：

1. **投资者沟通**：利用今日股价上涨窗口，适时与机构投资者沟通
2. **回购节奏**：如股价回调至480以下，可考虑加快回购节奏
3. **并购时机**：市场情绪向好，可关注潜在并购标的
4. **风险对冲**：建议适度配置衍生品对冲短期波动

**关键价位监控**：
- 突破 490 → 打开上行空间至 520
- 跌破 475 → 触发技术性调整

---
*数据来源：QVeris | THS iFinD、Caidazi、X Sentiment*
```

## 工具链路由

本 skill 通过 `references/tool-chains.json` 定义数据获取的优先级路由：

```json
{
  "morning_brief": {
    "market_overview": ["ths_ifind.global_market", "alpha_vantage.market_status"],
    "policy_news": ["caidazi.news.query", "caidazi.report.query"],
    "company_quote": ["ths_ifind.real_time_quotation"],
    "industry_data": ["ths_ifind.industry_index", "caidazi.sector_analysis"],
    "sentiment": ["qveris_social.x_domain_hot_topics"]
  },
  "evening_brief": {
    "company_quote": ["ths_ifind.real_time_quotation", "ths_ifind.history_quotation"],
    "announcements": ["caidazi.news.query", "exchange_announcements"],
    "research": ["caidazi.report.query", "alpha_news_sentiment"],
    "fund_flow": ["ths_ifind.capital_flow", "ths_ifind.dragon_tiger"]
  }
}
```

## 安全与隐私

- 仅使用 `QVERIS_API_KEY`，不存储其他凭证
- 仅调用 `qveris.ai` API
- 本地持久化仅限于 skill 目录内的配置文件
- 研究报告仅供参考，不构成投资建议

## 更新日志

- v1.0.0：初始版本，支持早班/晚报基础功能
- v1.1.0：新增竞争对手分析模块
- v1.2.0：新增政策解读与风险提示模块
