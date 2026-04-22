---
name: cross-border-finance
description: 跨境金融助手，专注于跨境资金转移的费用计算和最优路径推荐。使用场景：(1) 人民币出境——CNY换成境外法币（USD/EUR等），询问"怎么把人民币转到境外"、"出金最低费用路径"；(2) 境外法币入境——海外收入/工资换成CNY，询问"美元怎么转回国内"、"怎么把海外收入汇到国内"；(3) 法币与加密货币互换——USDT买卖、P2P出入金，询问"USDT怎么换人民币"、"人民币买USDT"；(4) 综合费用计算——计算手续费、汇率损耗、中间行费用，对比多平台路径。覆盖平台：Wise、N26、iFAST、中信国际银行、国内银行SWIFT、OKX、Bybit、Kraken、银联卡。
---

# 跨境金融助手

## 工作流

### 第一步：明确需求
收集以下信息（若用户未提供则追问）：
- **金额与货币**：发送多少、源货币是什么
- **目标货币**：希望到账什么货币
- **约束条件**：是否必须走合规路径？是否在中国大陆境内操作？是否有香港账户？
- **优先级**：最低费用 / 最快速度 / 最高安全性

### 第二步：运行费用计算脚本
自动尝试实时汇率（frankfurter.app），失败则使用备用静态汇率。

```bash
python3 scripts/calculate_costs.py --amount <金额> --from <源货币> --to <目标货币>
# 示例
python3 scripts/calculate_costs.py --amount 70000 --from CNY --to USD
python3 scripts/calculate_costs.py --amount 5000  --from USD --to CNY
python3 scripts/calculate_costs.py --amount 10000 --from USDT --to CNY
# 按优先级排序
python3 scripts/calculate_costs.py --amount 10000 --from CNY --to USD --priority speed
```

**支持货币对**：CNY→USD, CNY→EUR, USD→CNY, EUR→CNY, CNY→USDT, USDT→CNY, USD→USDT, EUR→USDT

### 第三步：展示对比表 + 推荐路径
脚本输出已包含对比表和分类推荐，在此基础上：
1. 结合用户约束（是否有香港账户、是否可接受合规风险等）调整推荐
2. 为推荐路径补充具体执行步骤
3. 标注关键风险

---

## 参考资料（按需加载）

- **银行类平台详情**（Wise, N26, iFAST, 中信国际, 国内银行SWIFT, 银联）  
  → [references/platforms-banking.md](references/platforms-banking.md)  
  _用于：具体费率数字、开户要求、监管限制、执行步骤_

- **加密平台详情**（OKX P2P, Bybit P2P, Kraken, USDT链上转账, 虚拟货币线下消费）  
  → [references/platforms-crypto.md](references/platforms-crypto.md)  
  _用于：P2P 操作细节、安全实践、链上费用、风险说明_

- **路径策略与场景分析**（出境/入境/加密互换对比、监管框架、特殊场景）  
  → [references/flow-strategies.md](references/flow-strategies.md)  
  _用于：场景化路径选择（留学生汇款/自由职业入境/大额回流等）_

---

## 输出标准格式

### 费用对比表
| 路径 | 预计到账 | 综合损耗% | 速度 | 安全性 | 合规状态 |
|------|---------|---------|------|--------|---------|

### 推荐路径
- **合规最优**：路径名 → 步骤 → 注意事项
- **灰色区域（如适用）**：路径名 → 合规风险等级 → 让用户自行决策

---

## 每次对话必须告知的合规提醒

1. 中国大陆个人年度购汇/汇款额度：**$50,000 USD 等值**
2. P2P 加密货币在中国大陆属**监管灰色地带**，存在银行卡冻结风险
3. 本技能提供信息参考，**不构成法律/投资建议**
4. 脚本汇率为参考值，实际到账以当时市场价为准
