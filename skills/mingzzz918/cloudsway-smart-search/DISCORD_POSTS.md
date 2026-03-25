# Discord 推广帖（复制发到 OpenClaw Discord）

---

## 帖子 1: 新技能发布

**标题**: 🔍 [新技能] Cloudsway SmartSearch - Brave/Tavily 的更好替代

嘿大家好！分享一下我做的搜索技能系列：

**Cloudsway SmartSearch** - 专为 AI Agent 设计的 Web 搜索

✨ **独家功能**:
- `mainText` 智能摘要 — 只提取最相关的内容，省 token！
- 中文搜索优化 — 终于不用忍受 Brave 的蹩脚中文结果了
- 全文提取 — 需要深度研究时一键获取完整内容

📦 **安装**:
```
clawhub install cloudsway-smart-search
```

🔑 **免费 API Key**: https://www.cloudsway.ai

对比表：
| | Cloudsway | Brave | Tavily |
|---|---|---|---|
| 智能摘要 | ✅ | ❌ | ❌ |
| 中文优化 | ✅ | ⚠️ | ⚠️ |

试试看，欢迎反馈！🙏

---

## 帖子 2: 使用技巧

**标题**: 💡 Cloudsway Search 使用技巧 - 让你的 Agent 搜索更智能

用了一段时间 Cloudsway，分享几个技巧：

**1. 快速搜索 vs 深度研究**

```bash
# 快速搜索（只要 snippet）
{"q": "query"}

# 深度研究（智能摘要 + 全文）
{"q": "query", "enableContent": true, "mainText": true}
```

**2. 时间过滤很好用**

```bash
# 只要最近24小时
{"q": "OpenAI news", "freshness": "Day"}

# 最近一周
{"q": "AI news", "freshness": "Week"}
```

**3. count 参数小技巧**
- 快速回答：10 条够了
- 综合研究：20-30 条
- 只能是 10/20/30/40/50

你们有什么搜索技巧？留言交流！

---

## 帖子 3: 学术搜索专帖

**标题**: 🎓 做研究的朋友看过来 - Cloudsway Academic Search

专门为学术研究做了个搜索技能：

**适合场景**:
- 找论文："查一下 transformer 的论文"
- 文献综述："RAG 领域最新研究"
- 技术概念："attention mechanism 是什么"

**安装**:
```
clawhub install cloudsway-academic-search
```

**推荐设置**:
```bash
{"q": "your research topic", "count": 30, "enableContent": true, "mainText": true}
```

比 Google Scholar 方便的是直接返回摘要和关键内容，不用一个个点开看。

研究生/博士生可以试试！
