---
name: hermes-memory
description: >-
  给AI装一个「人脑级」记忆系统。它能记住你说过的一切重要信息，下次聊天自动想起来。
  不用云端、不用API Key、不花一分钱——全部数据存在你自己的电脑上。
  说「记住这个」它就记住，问「我上次说了什么」它就找到。自动整理、自动遗忘过时信息。
  适合：想让自己的AI助手拥有长期记忆的用户。
  触发词：记忆、记住、之前说过、上次聊到、搜索记忆、忘了什么。
---

# Hermes-Memory 本地向量记忆系统

**你的AI助手是不是每次聊天都像失忆了？** 这个skill就是解决这个问题的。

Hermes-Memory 给AI装上了长期记忆：记住你的偏好、持仓、策略、教训……下次聊天自动关联上下文，就像跟一个老朋友说话一样。

### 为什么用它？
- **完全本地，隐私零风险** —— 数据存在你电脑上的SQLite文件里，不传任何云端
- **零成本** —— 不需要API Key，不需要付费服务，本地embedding模型免费跑
- **中文优化** —— 专用中文向量模型，搜索准确率远超英文通用模型
- **开箱即用** —— 安装依赖后直接使用，不需要额外启动数据库服务（不像Qdrant/Milvus那样需要单独部署）
- **越用越聪明** —— 自动去重、自动衰减过时记忆、实体关系图谱越建越丰富
- **类型自由定制** —— 内置交易、策略、教训等类型，也可以随时自定义任何新类型

### 和其他方案对比
| | Hermes-Memory | 云端向量库(Qdrant/Milvus) | 纯文本记忆(MEMORY.md) |
|---|---|---|---|
| 部署难度 | pip install即可 | 需要启动独立服务 | 零部署 |
| 语义搜索 | ✅ 中文优化 | ✅ 但需额外配置 | ❌ 只能关键词匹配 |
| 隐私安全 | ✅ 完全本地 | ⚠️ 需自建服务 | ✅ 本地文件 |
| 成本 | 免费 | 看方案 | 免费 |
| 大规模性能 | 千条级优秀 | 百万级优秀 | 几百条就乱 |
| 记忆管理 | 自动衰减+去重 | 手动管理 | 手动维护 |

## 快速开始

所有命令必须用 Python 3.12+（支持OpenSSL 3.0+），macOS推荐 `/opt/homebrew/bin/python3.12`。

```bash
# 搜索记忆（语义搜索，支持中文）
python3 scripts/memdb.py search "止损策略" --limit 5

# 添加记忆
python3 scripts/memdb.py add "内容" --type portfolio --entity 某科技股

# 智能检测关键词并写入
python3 scripts/memory_tool.py check "用户说的内容"

# 建立实体关系
python3 scripts/memdb.py relate "某科技股" "属于" "医药板块"

# 查看实体关系（支持多跳）
python3 scripts/memdb.py relations "某科技股" --depth 2

# 统计
python3 scripts/memdb.py stats
```

## 记忆类型

类型完全开放，可自由扩展。以下是内置推荐类型：

### 通用类型
| type | 用途 | 示例 |
|------|------|------|
| preference | 用户偏好 | 数据源用东财、回复用中文 |
| user-profile | 用户画像 | 用户基本信息和背景 |
| fact | 事实/决策 | 用户的重要决定 |
| note | 笔记 | 其他 |
| lesson | 教训（带severity） | 缺乏风控导致亏损 |

### 交易/投资类型（内置，可按需使用）
| type | 用途 | 示例 |
|------|------|------|
| portfolio | 持仓变动 | 买入某科技股、清仓某消费股 |
| strategy | 策略规则 | 主线共振策略买点、情绪周期L4 |
| market-view | 大盘/板块判断 | 大盘缩量反弹，半导体主线 |
| trade-plan | 交易计划 | 某股跌破MA20则止损 |
| stock-note | 个股研究笔记 | 某股：行业龙头，产能扩张期 |
| watchlist | 关注标的 | 关注某股回调至20日线 |
| review | 复盘结论 | 本周操作：胜率40%，亏损来自追高 |

**自定义类型：** `--type` 参数接受任意字符串，无需预定义。根据你的使用场景自由创造类型：
```bash
# 程序员用户可能用
type=bugfix type=architecture type=deploy

# 创作者用户可能用
type=idea type=draft type=publish

# 学生用户可能用
type=course type=exam type=schedule
```

## 实时写入规则

每次回复用户后，检查是否有值得长期记住的信息：

**关键词触发（用 memory_tool.py check）：**
- 买了/卖了/加仓/减仓/清仓/建仓/止盈/止损 → portfolio
- 新策略/改策略/情绪周期/买点卖点 → strategy
- 纠正我/不对/错误/教训/踩坑 → lesson
- 以后用/记住/偏好/改用 → preference

**LLM判断（直接用 memdb.py add）：**
- 隐含信息（用户随口提到的新方向、生活变化）→ fact
- 重要决策 → fact
- **根据对话领域自适应选择类型**，不限于上表
- **遇到新模式可创造新类型**，`--type` 无白名单限制

**判断标准：** 这条信息1周后还有用吗？是→写入，否→跳过。

## 实体关系图谱

写入记忆时，主动建立实体间关联：

```bash
# 股票→板块
python3 scripts/memdb.py relate "某科技股" "属于" "医药板块"
# 策略→组件
python3 scripts/memdb.py relate "主线共振策略" "包含" "买点规则"
# 教训→应用
python3 scripts/memdb.py relate "某股亏损" "教训应用于" "止损规则"
```

## 自动维护

- **衰减：** `memdb.py decay --days 30` 标记30天未更新的记忆为expired
- **归档：** `memdb.py archive` 将expired记忆移入archive表
- **导出：** `memdb.py export --dir ./entities` 同步Markdown可读备份
- **导入：** `memdb.py import --dir ./entities` 从Markdown导入

推荐Cron每晚23点执行：decay → export → stats。

## CLI完整参考

```bash
python3 scripts/memdb.py add "内容" --type <type> [--entity <实体>] [--severity high|medium|low] [--source manual|conversation|cron]
python3 scripts/memdb.py search "查询" [--type <type>] [--status active|expired] [--entity <实体>] [--limit N] [--format text|json]
python3 scripts/memdb.py list [--type <type>] [--status active] [--limit N]
python3 scripts/memdb.py relate "实体A" "关系" "实体B"
python3 scripts/memdb.py relations "实体" [--depth 1|2|3] [--direction from|to|both]
python3 scripts/memdb.py unrelate "实体A" "关系" "实体B"
python3 scripts/memdb.py decay [--days 30]
python3 scripts/memdb.py archive
python3 scripts/memdb.py export --dir <目录>
python3 scripts/memdb.py import --dir <目录>
python3 scripts/memdb.py stats
```

## 详细文档

- **安装指南：** 见 [references/install.md](references/install.md)
- **AGENTS.md集成：** 见 [references/integration.md](references/integration.md)

## 架构

```
用户对话 → LLM判断/关键词触发 → memdb.py add/relate → SQLite + 向量DB
                                                        ↓
                        Cron每晚 ← decay + export ← entities/ Markdown备份
```

**技术栈：**
- 存储层：SQLite（结构化数据）+ sqlite-vec（向量索引）+ FTS5（全文搜索）
- Embedding：text2vec-base-chinese（768维，本地运行，MPS加速）
- 关系层：relations表（实体关系图谱，支持多跳BFS查询）
- 去重：向量余弦相似度 >0.95 自动合并
