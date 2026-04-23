---
name: how-much-token-did-this-chat-used
description: >-
  Track and display token usage for the current OpenClaw session and recent
  sessions, with cost estimation and remaining days projection. Auto-detects
  active model and matches billing rules dynamically. Shows: current session
  tokens, session cost, today's cumulative usage, last 10 session averages,
  Credit balance auto-calculated from cumulative sessions, and estimated
  remaining days. Use when the user asks about token consumption, cost, usage
  stats, "用了多少 token" / "token 用量" / "消耗了多少" / "最近十个chat" /
  "credit" / "余额" / "还能用几天" / "花费". Trigger on: token count, token
  usage, cost tracking, usage statistics, session stats, credit balance,
  daily usage summary, cost estimation, remaining days.
---

# How Much Token Did This Chat Used / Token 用量查询 v1.4

## 核心原则 / Core Principles

- **纯读取、无写入、声明清晰** — 所有数据查询时实时获取
- **动态识别模型** — 不写死模型列表，从 session_status 解析
- **Credit 自动计算** — 从 sessions_list 累计 totalTokens，不写死数字

## 数据源 / Data Sources

| 数据 | 工具 | 说明 |
|------|------|------|
| 当前会话 | `session_status` | tokens、model、context |
| 历史会话 | `sessions_list(limit=10)` | totalTokens、updatedAt |
| 成本计算 | `scripts/cost.py` | 动态匹配计费规则 |

## 工作流 / Workflow

### Step 1: 获取当前会话

Call `session_status` → parse model name, tokens in/out, cache, context.

### Step 2: 自动识别模型

从 session_status 的 Model 字段提取模型名（如 `xiaomicoding/mimo-v2-pro` → `mimo-v2-pro`）。
`scripts/cost.py` 内置 `detect_rate()` 自动匹配，找不到用默认费率。

### Step 3: 获取历史会话 + 自动算 Credit

Call `sessions_list(limit=10)`:
- `used_credit` = 所有会话 totalTokens 之和（自动累计）
- `today_credits` = 今日会话 totalTokens 之和
- `avg_daily` = 近 N 会话 totalTokens 平均值
- `total_credit` = 用户 Token Plan 总额度（从 `memory/mimo-credit.json` 读取，仅存总额度）

### Step 4: 运行成本计算

```bash
python3 <skill_dir>/scripts/cost.py <input> <output> <total> <used> <total_credit> <avg_daily> [model]
```

## 输出格式 / Output Format

```
📊 成本与额度报告
🧠 模型: mimo-v2-pro
━━━━━━━━━━━━━━━━━━━━━
🔹 当前会话
   📥 输入: X,XXX  📤 输出: X,XXX
   💾 缓存: XX%  📚 上下文: XXk/200k (XX%)
   💰 费用: ¥X.XXXX

📅 今日累计 (N 会话): ¥X.XX (≈ XXX Credit)
📊 近 10 会话平均: XX,XXX tokens/会话

💳 Credit (自动累计)
   已用: XX,XXX,XXX / XX,XXX,XXX (XX.X%)
   ⏳ 预计可用: XX.X 天
━━━━━━━━━━━━━━━━━━━━━
```

## 计费规则 / Billing Rates

内置 `scripts/cost.py`，用户可通过编辑 `MODEL_RATES` 字典扩展。
未知模型自动 fallback 到默认费率。

| 模型 | 输入/1k | 输出/1k |
|------|---------|---------|
| mimo-v2-pro | ¥0.002 | ¥0.004 |

## 注意事项 / Notes

- Credit 已用 = 所有会话累计 totalTokens（自动计算，无需手动更新）
- 总额度需从 `memory/mimo-credit.json` 读取（仅存储 totalCredits）
- Token 单价为参考值，实际以服务商计费为准
- 累计成本按 70% 输入 / 30% 输出比例估算
- 时区：Asia/Shanghai (UTC+8)

## 更新日志 / Changelog

### v1.4.0
- ✅ 新增模型成本自动换算，直接显示人民币花费 / Auto cost with CNY
- ✅ 新增 MiMo Credit 额度监控 + 剩余可用天数预估 / Credit + remaining days
- ✅ 新增上下文占比、缓存命中率统计 / Context & cache hit rate
- ✅ 多模型自动识别，适配不同计费标准 / Multi-model auto-detect
- 🧹 轻量重构：纯读取无写入 / Read-only, no writes

### v1.3.0
- 🤖 自动识别模型 / Auto model detection
- 📅 今日累计消耗 / Today's cumulative
- 📊 近 10 会话平均 / Last 10 avg

### v1.2.0
- 💳 MiMo V2 Credit 余额 / Credit balance

### v1.1.0
- 📚 最近 10 会话合计 / Last 10 sessions

### v1.0.0
- 📊 基础 Token 统计 / Basic token tracking
