# Micro Memory 🧠

**智能记忆系统 | Intelligent Memory System**

> 不是简单的笔记存储，而是会思考、会遗忘、会提醒的第二大脑。
> Not just note storage, but a thinking, forgetting, reminding second brain.

---

## 为什么你需要它？| Why You Need It?

| 传统笔记 | Micro Memory |
|---------|-------------|
| 写下来就遗忘 | 智能强度衰减，主动提醒复习 |
| 孤立无关联 | 知识图谱，自动关联相关记忆 |
| 手动整理归档 | 自动归档，健康报告一目了然 |
| 静态存储 | 动态记忆，越用越聪明 |

| Traditional Notes | Micro Memory |
|------------------|--------------|
| Write and forget | Smart decay, active review reminders |
| Isolated entries | Knowledge graph, auto-linking related memories |
| Manual organization | Auto-archive, health dashboard |
| Static storage | Dynamic memory, gets smarter with use |

---

## 核心特性 | Core Features

### 🧠 智能记忆强度 | Intelligent Memory Strength
- 记忆会随时间自然衰减（符合艾宾浩斯遗忘曲线）
- 主动提醒需要复习的内容
- 强化机制让重要记忆更持久

- Memories naturally decay over time (Ebbinghaus forgetting curve)
- Proactive reminders for review
- Reinforcement makes important memories last longer

### 🔗 知识图谱 | Knowledge Graph
- 记忆之间自由建立关联
- 自动发现知识连接
- 可视化关联网络

- Free linking between memories
- Auto-discover knowledge connections
- Visualize relationship networks

### 📊 健康仪表盘 | Health Dashboard
- 记忆库整体健康度评分
- 弱记忆和临界记忆预警
- 归档和备份管理

- Overall memory health score
- Weak & critical memory alerts
- Archive and backup management

### 🤖 原生集成 | Native Integration
- Clawdbot 自动触发，无需手动命令
- 智能识别"记住"、"搜索"等意图
- 对话中自然交互

- Clawdbot auto-triggers, no manual commands
- Intent recognition: "remember", "search", etc.
- Natural conversation interaction

---

## 快速开始 | Quick Start

### 安装 | Install

```bash
clawdhub install micro-memory
```

### 添加记忆 | Add Memory

```bash
# 基础添加 | Basic add
node dist/index.js add "学习内容"

# 带标签和重要性 | With tags & importance
node dist/index.js add "重要知识点" --tag=study --type=longterm --importance=5

# 带关联 | With links
node dist/index.js add "相关概念" --tag=study --link=1,2
```

### 自然语言触发 | Natural Language Triggers

| 你说 | You Say | 自动执行 |
|------|---------|---------|
| 记住... / 记录... | Remember... / Note... | 自动添加记忆 |
| 搜索记忆... | Search memory... | 自动搜索 |
| 列出记忆 | List my memories | 自动列出 |
| 记忆健康 | Memory health | 健康报告 |
| 复习记忆 | Review memories | 今日复习 |

---

## 命令参考 | Command Reference

### 记忆管理 | Memory Management

```bash
# 列出记忆 | List memories
node dist/index.js list
node dist/index.js list --tag=study
node dist/index.js list --type=longterm --show_strength

# 搜索记忆 | Search memories
node dist/index.js search "关键词"
node dist/index.js search "关键词" --tag=study --limit=5

# 强化记忆 | Reinforce memory
node dist/index.js reinforce --id=1
node dist/index.js reinforce --id=1 --boost=2
```

### 复习系统 | Review System

```bash
# 今日复习 | Today's review
node dist/index.js review
node dist/index.js review --today
```

### 健康报告 | Health Report

```bash
# 记忆库健康 | Memory health
node dist/index.js health
```

### 关联网络 | Link Network

```bash
# 建立关联 | Create links
node dist/index.js link --from=1 --to=2,3

# 查看图谱 | View graph
node dist/index.js graph
node dist/index.js graph --id=1
```

### 归档导出 | Archive & Export

```bash
# 归档旧记忆 | Archive old memories
node dist/index.js archive --older_than=30

# 导出数据 | Export data
node dist/index.js export --format=json
node dist/index.js export --format=csv
```

---

## 记忆强度系统 | Memory Strength System

| 强度 | Strength | 状态 | Status | 说明 | Description |
|------|----------|------|--------|------|-------------|
| 💎 80-100 | Permanent | 永久 | Permanent | 永远不会遗忘 | Never forgets |
| 💪 60-79 | Strong | 强 | Strong | 长期保持 | Long-term retention |
| 📊 40-59 | Stable | 稳定 | Stable | 中期记忆 | Medium-term |
| ⚠️ 20-39 | Weak | 弱 | Weak | 需要复习 | Needs review |
| 🔴 0-19 | Critical | 临界 | Critical | 即将遗忘 | About to forget |

---

## 间隔重复算法 | Spaced Repetition

基于 SM-2 算法简化实现：

| 等级 | Level | 间隔 | Interval |
|------|-------|------|----------|
| 0 | Level 0 | 1天 | 1 day |
| 1 | Level 1 | 3天 | 3 days |
| 2 | Level 2 | 7天 | 7 days |
| 3 | Level 3 | 14天 | 14 days |
| 4 | Level 4 | 30天 | 30 days |
| 5 | Level 5 | 60天 | 60 days |
| 6+ | Level 6+ | 90天 | 90 days |

---

## 数据存储 | Data Storage

```
store/
├── index.json      # 记忆主索引 | Memory index
├── links.json      # 关联网络 | Link network
├── reviews.json    # 复习计划 | Review schedule
├── store.md        # Markdown 备份 | Markdown backup
└── archive/        # 归档文件 | Archived files
```

---

## 技术栈 | Tech Stack

- **语言 | Language:** TypeScript (Native Clawdbot Skill)
- **版本 | Version:** 3.1.2
- **架构 | Architecture:** 零依赖原生实现 | Zero-dependency native implementation

---

## 适合谁？| Who Is It For?

- 🎓 **学习者** - 管理学习笔记，构建知识体系
- 💼 **工作者** - 记录项目信息，追踪重要决策
- 🧑‍💻 **开发者** - 保存技术方案，积累代码片段
- 📝 **写作者** - 收集素材灵感，管理创作内容

- 🎓 **Learners** - Manage study notes, build knowledge systems
- 💼 **Professionals** - Record project info, track decisions
- 🧑‍💻 **Developers** - Save technical solutions, code snippets
- 📝 **Writers** - Collect ideas, manage creative content

---

## 立即开始 | Get Started Now

```bash
clawdhub install micro-memory
```

然后对 Clawdbot 说：
> "记住：我今天学习了间隔重复算法"

Then tell Clawdbot:
> "Remember: I learned about spaced repetition algorithms today"

---

*让记忆不再沉睡，让知识真正属于你。*
*Don't let memories sleep, make knowledge truly yours.*
