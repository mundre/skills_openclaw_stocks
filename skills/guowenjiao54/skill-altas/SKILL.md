---
name: skill-atlas
description: "技能图谱。核心技能提供基础框架，常驻技能基于习惯动态调整。按场景管理技能，同步 ClawHub 热门技能数据库。Keywords: 技能管理, skill atlas, 技能图谱, 核心技能, 常驻技能, 场景, ClawHub."
---

# 技能图谱 (Skill Atlas)

> 🐱 首次启用时，自动检查并安装核心技能。

双层技能架构：核心技能提供基础能力，常驻技能基于使用习惯动态进化。

## 🚀 首次启用流程（自动）

首次加载本技能时，自动执行以下步骤：

### 第一步：检查核心技能

使用 `clawhub list` 查看当前已安装的技能，对照以下 5 个核心技能：

| 核心技能 | 职责 |
|----------|------|
| **skill-atlas** | 技能类型/信息管理、ClawHub 数据库 |
| **proactive-agent** | 判断用户需要、自动学习使用习惯 |
| **find-skills** | 搜索/下载/安装新技能 |
| **skill-vetter** | 安全审查，安装前检查风险 |
| **self-improving-agent** | 持续更新优化自身 |

### 第二步：安装缺失的核心技能

对于每个未安装的核心技能，自动执行：

```bash
clawhub install <技能名>
```

> 如果 `clawhub` CLI 未安装，先执行 `npm i -g clawhub`

### 第三步：安装完成后询问用户

所有核心技能安装成功后，主动询问用户：

> **"核心技能已就绪！是否启用 skill-atlas 技能图谱？"**
>
> - 是 → 介绍双层架构，询问用户选择场景
> - 否 → 保持静默，随时可通过 "技能图谱" 唤醒

---

## 🏗️ 双层架构

```
┌─────────────────────────────────────┐
│           常驻技能层 (Residents)     │
│  • 用户自定义 + 使用习惯自动判断       │
│  • 动态增删，不影响核心               │
│  • proactive-agent 自动管理          │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│           核心技能层 (Core)          │
│  • skill-atlas  • proactive-agent  │
│  • find-skills  • skill-vetter     │
│  • self-improving-agent            │
│  • 不可禁用，始终保持                │
└─────────────────────────────────────┘
```

### 核心技能（5个，始终启用）

| 技能 | 职责 |
|------|------|
| **skill-atlas** | 技能类型/信息管理、ClawHub 数据库 |
| **proactive-agent** | 判断用户需要、自动学习使用习惯 |
| **find-skills** | 搜索/下载/安装新技能 |
| **skill-vetter** | 安全审查，安装前检查风险 |
| **self-improving-agent** | 持续更新优化自身 |

### 常驻技能（动态层）

- 由 `proactive-agent` 根据使用频率自动判断
- 用户可手动增删
- 达到使用阈值后自动提升为常驻
- 久未使用自动降级

---

## 📂 技能分类（ClawHub 10k+ 下载）

### 🔍 搜索资讯
Summarize, Multi Search Engine, Tavily, Brave Search, Baidu Search, News Summary

### 🛡️ 安全审查
Skill Vetter

### 🤖 AI 代理增强
self-improving-agent, Proactive Agent, Self-Improving + Proactive, Evolver

### 🧠 知识/记忆
ontology, Elite Longterm Memory, Memory Setup, ByteRover

### 📁 文件处理
Nano Pdf, Word/DOCX, Excel/XLSX, Markdown Converter, Pdf, Powerpoint/PPTX

### 🌐 浏览器自动化
Agent Browser, Browser Use, Browser Automation, Playwright MCP

### ⚡ 自动化
Automation Workflows, Desktop Control, Auto-Updater, n8n

### 🔌 API 集成
Github, Gog, Notion, API Gateway, Slack, Trello, Discord

### 💼 工作办公
Himalaya, imap-smtp-email, Gmail, Caldav Calendar, Obsidian

### 💰 投资交易
Polymarket, Stock Analysis, Stock Watcher, Stock Market Pro

### 🎨 创意设计
Nano Banana Pro, SuperDesign

### 🎬 多媒体
Openai Whisper, YouTube Watcher, Video Frames, YouTube

### 🌤️ 生活
Weather, Sonoscli

---

## 🔧 管理命令

### 查看状态
```
技能状态
当前场景
核心技能列表
常驻技能列表
```

### 切换场景
```
切换到 [场景名]
```
可用场景：default / trading / dev / content / growth / news / research / life / work / creative / market / automation / media / full

### 管理常驻技能
```
添加常驻 [技能名]
移除常驻 [技能名]
自动优化常驻
```

### 搜索/安装技能
```
搜索 [关键词]
从 ClawHub 安装 [技能名]
安装 [技能名]
```

### 技能安全审查
```
审查技能 [技能名]
安装前审查 [技能名]
```

---

## ⚙️ 配置

配置文件：`config/scenes.json`

| 字段 | 说明 |
|------|------|
| core_skills | 核心技能列表（不可禁用） |
| resident_skills | 当前常驻技能 |
| resident_auto_rules | 自动优化规则 |
| categories | 技能分类配置 |
| scenes | 场景模式配置 |

---

## 📊 ClawHub 数据

热门技能数据库：`config/clawhub_skills.md`

- 下载量 ≥ 10k 的技能按场景分类
- 定期更新（更新时间见文件头部）
- 用户可根据分类自行选择常驻技能

---

## 🌟 自动优化逻辑

proactive-agent 自动判断常驻技能：

1. 同一技能使用 ≥ N 次 → 建议提升为常驻
2. 常驻技能连续 7 天未使用 → 建议降级
3. 新安装技能使用后表现良好 → 纳入观察列表

用户可随时手动调整：`添加常驻` / `移除常驻`
