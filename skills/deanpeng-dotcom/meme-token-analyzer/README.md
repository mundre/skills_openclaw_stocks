[🇺🇸 English](#english) · [🇨🇳 中文](#chinese)

---

<a name="english"></a>

# Meme Token Analyzer 🚀

> **The Ultimate Meme Token "Wealth Gene" Detection System**

A powerful LangGraph workflow that analyzes Meme tokens with humor and expertise, generating comprehensive wealth gene detection reports using real-time web sentiment, AI-generated prediction images, and multimodal AI analysis.

## 🚀 Installation

```bash
openclaw skill install https://github.com/AntalphaAI/Meme-Token-Analyzer
```

---

## 🎯 What Makes This Special?

**Edge Case Mastery**: Our analyzer doesn't just look at market caps—it scans the deep web for sentiment even on random strings. Whether it's a legendary meme like `$PEPE`, a major coin like `$BTC`, or a keyboard smash like `qwertyuiop`, it delivers intelligent analysis with real data!

---

## ✨ Features

### Core Capabilities
- **🔍 Real-Time Web Search**: Fetches latest news, social media sentiment, and market trends with **1-month time filter** for fresh data
- **🎨 AI Image Generation**: Creates "Moonshot" prediction images with cyberpunk aesthetic
- **🧹 Smart Data Cleaning**: Condenses search results into LLM-friendly summaries with **date freshness validation**
- **🤖 Multimodal AI Analysis**: Combines text sentiment + visual analysis using vision-language models
- **💎 Wealth Gene Rating**: Four-tier rating system with Degen-style humor

### Intelligent Features
- **🧠 Smart Detection**: Automatically identifies major coins (BTC/ETH/SOL), handles missing data, and filters irrelevant results
- **📅 Data Freshness Check**: Validates search result dates and warns if data is outdated
- **🎯 Edge Case Handling**: Gracefully processes random strings, unknown tokens, and obscure names

---

## 🏆 Wealth Gene Rating System

| Rating | Meaning | Potential |
|--------|---------|-----------|
| 🌟 **Diamond Hand** | Next 10000x coin | Legendary potential |
| 🌙 **Moonshot** | 100x expected | High growth potential |
| 🗑️ **Paper Hand** | Likely a rug | High risk |
| 💩 **Shitcoin** | Stay far away | Avoid |

---

## 📊 Case Studies

### Case 1: Classic Meme Token - $PEPE ✅

**Input**: `PEPE`

**Result**: 🌙 **Moonshot**

**Highlights**:
- Found real community discussions with recent dates
- Analyzed narrative magic (iconic meme + celebrity triggers)
- Detected viral visual gene potential
- Recommended for degens with risk tolerance

**Key Insight**: *"PEPE has the wealth gene pumping through its digital veins!"*

---

### Case 2: Major Cryptocurrency - $BTC ⚠️

**Input**: `BTC`

**Result**: 🌟 **Diamond Hand** (with special warning)

**Highlights**:
- **Triggered**: Smart detection for non-meme major coin
- **Warning**: "⚠️ Detected non-typical Meme, now performing cross-border scan with [Top Value Coin] perspective"
- Analyzed as value coin rather than meme token
- Still provided comprehensive analysis

**Key Insight**: *"BTC is not just a currency, it's a legend!"*

---

### Case 3: Edge Case - `qwertyuiop` 🎹

**Input**: `qwertyuiop` (keyboard smash)

**Result**: 🌙 **Moonshot**

**Highlights**:
- ✅ **Found real data**: 126 unique individuals discussing
- ✅ **Real sentiment**: 47.37% bullish sentiment detected
- ✅ **Activity ranking**: 446th in mentions
- ✅ **Intelligent analysis**: "Unique but underdeveloped narrative"
- ✅ **Actionable advice**: "If they lean into keyboard meme + cyberpunk anime, could 100x"

**Key Insight**: *"Even a keyboard smash has a story if you know where to look!"*

**This demonstrates our Edge Case Mastery**:
- No fabricated data or hallucinated prices
- Real web scraping capabilities
- Intelligent handling of unknown tokens
- Constructive analysis even for obscure inputs

---

## 🎨 Output Format

### Analysis Report Structure

```markdown
# $TOKEN Meme Token "Wealth Gene" Detection Report

## 🎯 Narrative Magic Analysis
[Memorability, concept uniqueness, sentiment]

## 📢 Community Hype Ability Prediction
[Community activity, shilling intensity]

## 🎨 Visual Gene Detection
[Visual appeal, viral potential]

## 🏆 Final Verdict: Wealth Gene Rating
[Rating: 🌟/🌙/🗑️/💩]

[Special warnings if applicable]
```

### Features
- ✅ Proper Markdown heading hierarchy
- ✅ Rich emoji annotations
- ✅ Mobile-friendly formatting
- ✅ Auto-embedded image URLs
- ✅ Clear visual hierarchy

---

## 🏗️ Architecture

### Workflow Structure

```
START
  ├── search (Web Search, 1m filter) ──> clean_data (Freshness Check) ──┐
  └── image_gen (2K Cyberpunk Image) ────────────────────────────────────┤
                                                                          ├─> analysis (Multimodal LLM) ──> END
```

### Tech Stack

- **Framework**: LangGraph (DAG-based workflow)
- **LLM**: doubao-seed-1-6-vision-250815 (Multimodal)
- **Skills**:
  - web-search (Real-time data)
  - image-generation (AI art)
  - llm (Vision-language model)

---

## 📁 Project Structure

```
src/
├── graphs/
│   ├── state.py              # State definitions
│   ├── graph.py               # Main graph orchestration
│   └── nodes/
│       ├── search_node.py     # Web search (time_range="1m")
│       ├── image_gen_node.py  # Image generation (2K)
│       ├── clean_data_node.py # Data cleaning + freshness check
│       └── analysis_node.py   # Multimodal analysis
config/
└── analysis_llm_cfg.json      # LLM prompts & config
```

---

## 🧪 Testing

### Test Cases

| Token | Type | Expected Behavior | Status |
|-------|------|-------------------|--------|
| `PEPE` | Classic meme | Normal analysis | ✅ PASS |
| `DOGE` | Major meme | Diamond Hand rating | ✅ PASS |
| `BTC` | Major coin | Special warning + analysis | ✅ PASS |
| `ETH` | Major coin | Special warning + analysis | ✅ PASS |
| `qwertyuiop` | Edge case | Real data + Moonshot | ✅ PASS |
| `XYZABC123` | Unknown | Freshness warning + analysis | ✅ PASS |

### Performance Metrics
- **Search**: ~3-5 seconds
- **Image Gen**: ~5-8 seconds
- **Analysis**: ~8-12 seconds
- **Total**: ~15-25 seconds

---

## 🛡️ Error Handling

The workflow gracefully handles:

✅ **Unknown tokens** with minimal data
✅ **Major cryptocurrencies** (BTC/ETH/SOL) with warnings
✅ **Random strings** and keyboard smashes
✅ **Outdated information** with freshness warnings
✅ **Empty search results** without hallucination
✅ **Missing publication dates** with appropriate notes

---

## 🎓 Pro Tips

1. **Compare multiple tokens** to understand rating differences
2. **Check date warnings** for data freshness validation
3. **Trust major coin warnings** - they're analyzed differently
4. **Read between the lines** - humor often masks real insights
5. **Use ratings wisely** - Diamond Hand > Moonshot > Paper Hand > Shitcoin

---

## 🤖 Bot Configuration

See `BOT_CONFIG.md` for:
- Opening greeting messages
- Suggested commands
- Bot avatar recommendations
- User onboarding tips

**Suggested Commands:**
1. `$PEPE` (Classic meme analysis)
2. `$BTC as a meme？` (Major coin detection)
3. `random stuff: qwertyuiop` (Edge case demonstration)

---

## 📝 Documentation

- `AGENTS.md` - Technical documentation for developers
- `BOT_CONFIG.md` - Bot setup guide
- `README.md` - This file (user-facing documentation)

---

## ⚠️ Disclaimer

This tool is for **entertainment and educational purposes only**. Not financial advice. Always DYOR (Do Your Own Research) before investing in any cryptocurrency. Meme tokens are highly volatile and risky investments.

**Remember**: Even Diamond Hands need risk management! 💎

---

## 📄 License

MIT License

**Maintainer**: AntalphaAI
**From keyboard smashes to moonshots - we analyze them all! 🚀**

---

<a name="chinese"></a>

# Meme Token 分析器 🚀

> **终极 Meme 代币"财富基因"检测系统**

一个强大的 LangGraph 工作流，以幽默而专业的方式分析 Meme 代币，结合实时网络情绪、AI 生成预测图像和多模态 AI 分析，生成全面的财富基因检测报告。

## 🚀 安装

```bash
openclaw skill install https://github.com/AntalphaAI/Meme-Token-Analyzer
```

---

## 🎯 核心优势

**边缘案例掌控力**：我们的分析器不仅仅看市值——它能在深网中爬取任意字符串的情绪数据。无论是传奇 Meme 如 `$PEPE`、主流币如 `$BTC`，还是随手乱打的 `qwertyuiop`，都能给出有真实数据支撑的智能分析！

---

## ✨ 功能特性

### 核心能力
- **🔍 实时网络搜索**：抓取最新新闻、社交媒体情绪和市场趋势，内置 **1个月时间过滤器** 保证数据新鲜
- **🎨 AI 图像生成**：以赛博朋克美学创作"登月"预测图像
- **🧹 智能数据清洗**：将搜索结果压缩为 LLM 友好摘要，并进行 **日期新鲜度验证**
- **🤖 多模态 AI 分析**：结合文本情绪 + 视觉分析，使用视觉语言模型
- **💎 财富基因评级**：四级评级系统，配有 Degen 风格幽默点评

### 智能特性
- **🧠 智能检测**：自动识别主流币（BTC/ETH/SOL），处理缺失数据，过滤无关结果
- **📅 数据新鲜度检查**：验证搜索结果日期，数据过期时自动预警
- **🎯 边缘案例处理**：优雅处理随机字符串、未知代币和冷门名称

---

## 🏆 财富基因评级系统

| 评级 | 含义 | 潜力 |
|------|------|------|
| 🌟 **钻石手** | 下一个 10000x | 传奇潜力 |
| 🌙 **登月** | 预期 100x | 高成长潜力 |
| 🗑️ **纸手** | 大概率归零 | 高风险 |
| 💩 **屎币** | 远离 | 避免 |

---

## 📊 案例演示

### 案例一：经典 Meme 代币 - $PEPE ✅

**输入**：`PEPE`

**结果**：🌙 **登月**

**亮点**：
- 找到近期真实社区讨论数据
- 分析了叙事魔力（标志性 Meme + 名人触发器）
- 检测到病毒式视觉基因潜力
- 推荐给有风险承受能力的 Degen

**核心洞察**：*"PEPE 的财富基因在数字血管中沸腾！"*

---

### 案例二：主流加密货币 - $BTC ⚠️

**输入**：`BTC`

**结果**：🌟 **钻石手**（含特别警告）

**亮点**：
- **触发**：非 Meme 主流币智能检测
- **警告**："⚠️ 检测到非典型 Meme，正以【顶级价值币】视角进行跨界扫描"
- 以价值币而非 Meme 代币角度进行分析
- 仍提供了全面的综合分析

**核心洞察**：*"BTC 不只是货币，它是传奇！"*

---

### 案例三：边缘案例 - `qwertyuiop` 🎹

**输入**：`qwertyuiop`（键盘乱打）

**结果**：🌙 **登月**

**亮点**：
- ✅ **找到真实数据**：126 名独立用户在讨论
- ✅ **真实情绪**：检测到 47.37% 看涨情绪
- ✅ **活跃度排名**：提及量第 446 名
- ✅ **智能分析**："叙事独特但尚未开发"
- ✅ **可执行建议**："如果结合键盘 Meme + 赛博朋克动漫方向，有望 100x"

**核心洞察**：*"即便是键盘乱打，只要知道往哪里找，都有故事！"*

**这展示了我们的边缘案例掌控力**：
- 无虚构数据或幻觉价格
- 真实网络爬取能力
- 对未知代币的智能处理
- 即使对冷门输入也能给出建设性分析

---

## 🎨 输出格式

### 分析报告结构

```markdown
# $TOKEN Meme 代币"财富基因"检测报告

## 🎯 叙事魔力分析
[记忆度、概念独特性、情绪]

## 📢 社区炒作能力预测
[社区活跃度、传播强度]

## 🎨 视觉基因检测
[视觉吸引力、病毒式传播潜力]

## 🏆 最终裁决：财富基因评级
[评级：🌟/🌙/🗑️/💩]

[如适用，包含特别警告]
```

### 格式特点
- ✅ 规范的 Markdown 标题层级
- ✅ 丰富的 Emoji 标注
- ✅ 移动端友好格式
- ✅ 自动嵌入图片 URL
- ✅ 清晰的视觉层次

---

## 🏗️ 架构

### 工作流结构

```
START
  ├── search（网络搜索，1个月过滤）──> clean_data（新鲜度检查）──┐
  └── image_gen（2K 赛博朋克图像）──────────────────────────────────┤
                                                                      ├─> analysis（多模态 LLM）──> END
```

### 技术栈

- **框架**：LangGraph（DAG 工作流）
- **LLM**：doubao-seed-1-6-vision-250815（多模态）
- **技能**：
  - web-search（实时数据）
  - image-generation（AI 绘图）
  - llm（视觉语言模型）

---

## 📁 项目结构

```
src/
├── graphs/
│   ├── state.py              # 状态定义
│   ├── graph.py               # 主图编排
│   └── nodes/
│       ├── search_node.py     # 网络搜索（time_range="1m"）
│       ├── image_gen_node.py  # 图像生成（2K）
│       ├── clean_data_node.py # 数据清洗 + 新鲜度检查
│       └── analysis_node.py   # 多模态分析
config/
└── analysis_llm_cfg.json      # LLM 提示词 & 配置
```

---

## 🧪 测试

### 测试用例

| 代币 | 类型 | 预期行为 | 状态 |
|------|------|----------|------|
| `PEPE` | 经典 Meme | 正常分析 | ✅ PASS |
| `DOGE` | 主流 Meme | 钻石手评级 | ✅ PASS |
| `BTC` | 主流币 | 特别警告 + 分析 | ✅ PASS |
| `ETH` | 主流币 | 特别警告 + 分析 | ✅ PASS |
| `qwertyuiop` | 边缘案例 | 真实数据 + 登月 | ✅ PASS |
| `XYZABC123` | 未知 | 新鲜度警告 + 分析 | ✅ PASS |

### 性能指标
- **搜索**：约 3-5 秒
- **图像生成**：约 5-8 秒
- **分析**：约 8-12 秒
- **总计**：约 15-25 秒

---

## 🛡️ 错误处理

工作流可优雅处理：

✅ 数据极少的**未知代币**
✅ **主流加密货币**（BTC/ETH/SOL）附带警告
✅ **随机字符串**和键盘乱打
✅ **过期信息**附带新鲜度警告
✅ **空搜索结果**不产生幻觉
✅ **缺失发布日期**附带适当说明

---

## 🎓 使用技巧

1. **对比多个代币**，理解评级差异
2. **关注日期警告**，验证数据新鲜度
3. **信任主流币警告**——它们的分析逻辑不同
4. **读懂言外之意**——幽默背后往往是真实洞察
5. **善用评级**：钻石手 > 登月 > 纸手 > 屎币

---

## 🤖 Bot 配置

详见 `BOT_CONFIG.md`：
- 开场问候语
- 推荐命令
- Bot 头像建议
- 用户引导提示

**推荐命令：**
1. `$PEPE`（经典 Meme 分析）
2. `$BTC as a meme？`（主流币检测）
3. `random stuff: qwertyuiop`（边缘案例演示）

---

## 📝 文档说明

- `AGENTS.md` - 开发者技术文档
- `BOT_CONFIG.md` - Bot 配置指南
- `README.md` - 本文件（用户端文档）

---

## ⚠️ 免责声明

本工具仅供**娱乐和教育目的**。不构成投资建议。在投资任何加密货币之前，请务必 DYOR（自行研究）。Meme 代币具有高度波动性和投资风险。

**记住**：即使是钻石手也需要风险管理！💎

---

## 📄 许可证

MIT License

**维护方**：AntalphaAI
**从键盘乱打到登月——我们分析一切！🚀**
