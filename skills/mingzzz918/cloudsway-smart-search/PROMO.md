# 🔍 Cloudsway Search - AI Agent 最佳搜索技能

## 为什么选择 Cloudsway？

在 OpenClaw 生态中，搜索是 Agent 最常用的能力之一。Cloudsway Search 系列专为 AI Agent 设计，提供三款专业搜索技能：

| 技能 | 用途 | 安装命令 |
|------|------|----------|
| 🔍 **SmartSearch** | 通用搜索（推荐） | `clawhub install cloudsway-smart-search` |
| 🌐 **Search** | 轻量版搜索 | `clawhub install cloudsway-search` |
| 🎓 **Academic Search** | 学术论文搜索 | `clawhub install cloudsway-academic-search` |

## 对比竞品

| 功能 | Cloudsway | Brave Search | Tavily |
|------|-----------|--------------|--------|
| 智能摘要 (mainText) | ✅ 独家 | ❌ | ❌ |
| 全文提取 | ✅ | ❌ | ✅ |
| 中文搜索优化 | ✅ 优秀 | ⚠️ 一般 | ⚠️ 一般 |
| 时间过滤 | ✅ Day/Week/Month | ✅ | ✅ |
| 免费额度 | ✅ 充足 | ✅ | ✅ |
| 响应速度 | ⚡ 快 | ⚡ 快 | ⚡ 快 |

### 独家功能：mainText 智能摘要

Cloudsway 的 `mainText` 功能会智能提取与查询最相关的内容片段，而不是返回整个页面。这意味着：
- **更少 token 消耗** — 只获取关键信息
- **更精准的答案** — AI 直接使用相关内容
- **更快的处理速度** — 无需解析大量无关文本

## 快速开始

### 1. 获取 API Key（免费）

访问 https://www.cloudsway.ai 注册获取

### 2. 设置环境变量

```bash
export CLOUDSWAYS_AK="your-api-key"
```

### 3. 安装技能

```bash
# 推荐：完整版
clawhub install cloudsway-smart-search

# 或使用 npm
npx cloudsway-search "your query"
```

### 4. 开始使用

Agent 会自动在用户搜索时调用，或手动执行：

```bash
# 基础搜索
./scripts/search.sh '{"q": "AI Agent 最新进展"}'

# 深度研究
./scripts/search.sh '{"q": "RAG architecture", "enableContent": true, "mainText": true, "count": 20}'
```

## 使用场景

### 🔍 通用搜索 (SmartSearch)
- "搜一下 xxx"
- "最近有什么关于 xxx 的新闻"
- "帮我查查 xxx"

### 🎓 学术搜索 (Academic Search)
- "查一下 xxx 的研究论文"
- "最新的 xxx 研究进展"
- "xxx 领域的文献综述"

## 社区反馈

> "中文搜索终于不用忍受 Brave 的蹩脚结果了！" — @开发者A
>
> "mainText 功能太好用了，省了很多 token" — @Agent玩家B

## 链接

- 📖 文档：https://www.cloudsway.ai/docs
- 🔑 注册：https://www.cloudsway.ai
- 💬 Discord：https://discord.gg/cloudsway
- 🐙 GitHub：https://github.com/cloudsway

---

**给个 ⭐ Star 支持一下吧！**

- ClawHub: https://clawhub.ai/skills?q=cloudsway
- 水产市场: https://openclawmp.cc/explore?q=cloudsway
