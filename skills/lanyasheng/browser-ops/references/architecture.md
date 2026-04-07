# 浏览器操作分层架构

## 为什么要分层？

同一个任务，不同方式的成本差 1000 倍：

| 任务 | 最便宜方式 | 最贵方式 | 差距 |
|------|-----------|---------|------|
| 读一篇内部文章 | curl/Jina ($0, 0 token) | Stagehand ($0.001, ~500 token) | ∞ |
| 刷知乎热榜 | opencli ($0, 0 token) | agent-browser (0$, ~2k token 上下文) | 上下文 2k |
| 填一个表单 | Playwright MCP ($0, ~1k token) | Stagehand ($0.001, ~2k token) | LLM 成本 ∞ |
| 抓 Cloudflare 站 | Zendriver ($0, 0 token) | Zyte ($0.02/页) | ∞ |

**两种 token 成本要区分**:
- **LLM token**: Stagehand 每次 act/extract 调 LLM，产生真金白银的 API 费用
- **上下文 token**: agent-browser/Playwright 的 snapshot 输出占用 agent 上下文窗口，不产生额外费用但影响上下文利用率

**分层的核心原则：永远用最便宜、最快的方式完成任务。只有当前层搞不定时才升级。**

## 3 个决策维度

所有路由决策本质上只回答 3 个问题：

```
维度 1: 需不需要浏览器？
  ├─ 不需要 → API / Jina / curl（最快最省）
  └─ 需要 → 进入维度 2

维度 2: 需不需要 AI 理解页面？
  ├─ 不需要（有适配器 / 已知 DOM）→ opencli 或 agent-browser ($0)
  └─ 需要（未知 DOM / 动态页面）→ Stagehand（花 LLM token）

维度 3: 能不能正常访问？
  ├─ 能 → 用上面选的工具
  └─ 被反爬拦了 → Zendriver / Camoufox 绕过
```

## 分层总览

| 层 | 名称 | 回答的问题 | 代表工具 | LLM token | 上下文 token | 速度 |
|----|------|-----------|---------|-----------|-------------|------|
| L1 | API | 有现成接口吗？ | requests/feedparser | $0 | ~0 | <0.5s |
| L2 | 轻量抓取 | 只要文本？ | Jina/curl/web_fetch | $0 | ~0 | <1s |
| **桥接** | **opencli** | **有适配器？** | **opencli (73 站点)** | **$0** | **极少 (JSON)** | **1-3s** |
| 批量 API | 批量数据？ | AKShare/新浪/平台API | $0 | ~0 | <1s/批 |
| L3a | Playwright MCP | 需要浏览器？ | Playwright/Puppeteer MCP | $0 | 中 (~1-3k) | 2-5s |
| L3b | agent-browser | 需要 CLI 操作？ | agent-browser + Lightpanda | $0 | 中 (~1-3k) | 2-5s |
| L4 | AI 增强浏览器 | DOM 未知？ | Stagehand v3 | **~$0.001** | 高 (~2-5k) | 5-15s |
| L5 | 云浏览器 | 大规模并发？ | Zyte/Browserless | $0 | 低 | 3-8s |
| L6 | 反检测 | 被拦了？ | Zendriver/Camoufox | $0 | 低 | 3-8s |

### Token 成本对比

| | LLM token (真金白银) | 上下文 token (占窗口) |
|---|---|---|
| **L1 API / L2 Jina / opencli** | $0 | 极少 (~100-500) |
| **L3a Playwright MCP** | $0 | 中 (snapshot ~1-3k) |
| **L3b agent-browser + Chrome** | $0 | 中 (snapshot ~1-3k) |
| **L3b agent-browser + Lightpanda** | $0 | **低 (semantic_tree ~500)** |
| **L4 Stagehand** | **~$0.001/动作** | 高 (~2-5k) |
| **L5 云浏览器** | $0 | 低 |

**关键认知**:
- L1-L3 + opencli 覆盖 90% 场景，零 LLM token 成本
- L3b 用 Lightpanda 替代 Chrome 可将上下文 token 减少 60-80%（semantic_tree 比 accessibility tree 精简）
- L4 Stagehand 只在"陌生网站 + 未知 DOM"时才值得花 LLM token

### 批量 vs 单次：路由判断

- **单次查看/操作** → opencli（像人一样用）
- **批量拉取（>10次/分钟）** → 直接调 API（像机器一样用）

原因：opencli 是单线程串行走 Chrome 扩展，批量场景需要并发+直连 API。金融行情用新浪 API / AKShare 一次批量请求，社交媒体用平台官方 API 或 Zendriver+代理并发，通用网页用 asyncio+aiohttp 并发抓取。

### Lightpanda vs Chrome (agent-browser 内核选择)

| 维度 | Chrome for Testing | Lightpanda |
|------|-------------------|------------|
| 启动速度 | 2-3s | <0.5s |
| 内存占用 | ~150MB+ | ~15MB |
| 上下文 token | ~1-3k (accessibility tree) | **~500 (semantic_tree)** |
| JS 支持 | 完整 | V8 但部分 Web API |
| 截图 | ✅ | ❌ (无渲染引擎) |
| Cookie 持久化 | ✅ (--profile) | ❌ (内存中) |
| 反检测 | 需 Zendriver | 天然无指纹 |

**推荐**: 不需要截图和完整 JS 时用 Lightpanda（省 token + 快 5x）。需要截图或复杂 JS 时用 Chrome。

## 各层详解

### L1: API 优先

**原则**: 有官方 API 绝不用爬虫。

- `requests` / `urllib` — HTTP 请求
- `feedparser` — RSS/Atom 解析

**适用**: 官方 API 可用、RSS Feed、Webhook。

### L2: 轻量抓取

**原则**: 只要正文，不开浏览器。

- **Jina AI Reader** — `curl "https://r.jina.ai/{url}"`
- `web_fetch` — Claude Code 内置
- `curl` — 直接 HTTP 抓取

**适用**: 文章/博客/文档正文提取。
**限制**: 无登录态、不执行 JS、不适合动态内容。
**失败信号**: 403 / 内容空 → 升级到 opencli 或 L3。

详见 `jina-usage.md`

### 桥接层: opencli

**原则**: 目标平台有适配器就用 opencli，零 LLM 成本。

核心优势:
- **零 token 成本** — 预建适配器，确定性执行
- **复用 Chrome 登录态** — 凭证不离开浏览器
- **内置反检测** — 隐藏 webdriver 指纹
- **453 个命令，73 个站点** — 开箱即用

**覆盖的站点分类（73 个站点，按认证方式）**:

| 类型 | public (无需登录) | cookie (需要 Chrome 登录态) | intercept (API 拦截) | ui (桌面应用) |
|------|-------------------|---------------------------|---------------------|--------------|
| 社交 | Bluesky | Twitter/X, Instagram, Facebook, TikTok, 微博, 即刻 | Twitter search/followers | — |
| 内容 | HackerNews, Wikipedia, arXiv, DEV.to, Lobsters, StackOverflow | Reddit, 知乎, 小红书, 豆瓣, Medium, Substack, V2EX, 贴吧, 微信公众号 | 36kr, ProductHunt, 小红书 feed | — |
| 视频 | 小宇宙 | B站, YouTube, 抖音, Pixiv | — | — |
| 财经 | 新浪财经 | 雪球, Yahoo Finance, Barchart | — | — |
| 购物 | — | Amazon, 京东, 什么值得买, Coupang | — | — |
| 新闻 | BBC, Google News, Bloomberg RSS | Bloomberg articles, Reuters | — | — |
| AI 工具 | — | Gemini, 豆包, NotebookLM, Grok | — | ChatGPT, Cursor, Codex, Antigravity, 豆包, ChatWise |
| 音乐 | Spotify(OAuth) | — | — | — |
| 项目管理 | — | ONES | — | Notion, Discord |
| AI 创作 | — | 即梦, Yollomi | — | — |
| 阅读 | — | 微信读书 | — | — |
| 社区 | V2EX (部分) | Linux.do, 知识星球 | — | — |
| 招聘 | — | BOSS直聘 | — | — |
| 外部 CLI | Docker, GitHub CLI, Vercel | — | — | 钉钉, 飞书, 企业微信, Obsidian |

**扩展方式**:
```bash
# AI 自动探索未知站点 → 生成适配器
opencli explore https://newsite.com --site newsite
opencli synthesize newsite

# 一键完成
opencli generate https://newsite.com --goal "提取商品价格"

# 手动编写 YAML 适配器（放到 clis/ 目录）
# 或 TypeScript 适配器（更复杂的场景）

# 安装社区适配器
opencli plugin install github:user/repo
```

详见 `opencli-usage.md`

### L3a: Playwright / Puppeteer MCP

**原则**: 已有 MCP 工具直接用，不需要额外安装。

Claude Code 环境中通常已配置 Playwright MCP 或 Puppeteer MCP：

```
browser_navigate / browser_click / browser_snapshot / browser_type
browser_take_screenshot / browser_fill_form / browser_evaluate
```

**优势**: 与 AI agent 原生集成，工具调用即浏览器操作。
**适用**: 需要浏览器交互，且当前环境已有 MCP 配置。

### L3b: agent-browser

**原则**: CLI 操作，可选 Chrome 或 Lightpanda 内核。

- **agent-browser** — Rust CLI
  - 默认内核: Chrome for Testing（完整渲染 + 截图）
  - **推荐内核: Lightpanda**（省 token + 快 5x + 省内存 10x）
  - 支持 `--profile` 持久化 Cookie
  - 支持统一 Cookie 存储 `state load`

**Lightpanda 作为 agent-browser 后端**:
```bash
# 启动 Lightpanda CDP 服务
./lightpanda serve --host 127.0.0.1 --port 9222

# agent-browser 连接到 Lightpanda（替代 Chrome）
agent-browser connect 9222
agent-browser open https://example.com
agent-browser snapshot     # 输出更精简，省上下文 token
```

**适用**: CLI 脚本、批量操作、不需要截图时优先用 Lightpanda。
**限制**: Lightpanda 不支持截图和部分 Web API。需要截图时回退到 Chrome。

### L4: AI 增强浏览器

**原则**: 只有"陌生网站 + 未知 DOM"才值得花 token。

- **Stagehand v3** — BrowserBase 出品
  - v3 API: `stagehand.act()`, `stagehand.extract()`, `stagehand.observe()`
  - LOCAL 模式使用本地 Chrome，需自备 LLM API key (Anthropic/OpenAI/Gemini)

**Token 成本明细**:
- `act("点击登录按钮")`: ~200-500 token (页面 snapshot + LLM 决策)
- `extract("提取价格", schema)`: ~300-800 token (页面内容 + 结构化提取)
- `observe("找到所有按钮")`: ~200-400 token
- 一个 5 步任务: ~2000-3000 token ≈ $0.003-0.005

**什么时候用 L4 而不是 L3**:
| 信号 | 选择 |
|------|------|
| 知道要点击哪个 CSS selector | L3 agent-browser |
| 不知道页面结构，要 AI "看" | L4 Stagehand |
| 页面结构频繁变化 | L4 Stagehand (自愈能力) |
| 需要从页面提取结构化数据 | L4 Stagehand `extract()` |

### L5: 云浏览器

**原则**: >50 页并发 或 需要全球 IP 池。

- **Zyte** (首选) — 智能代理 + 浏览器
- **Browserless** (次选) — Docker 化浏览器
- **Hyperbrowser** (第三)

**成本**: $0.01-0.02/页, $10-30/月订阅

### L6: 反检测

**原则**: 被拦了才用，不是默认选择。

- **Zendriver** (首选) — Chrome 内核, ~90% bypass, Nodriver 同作者继任（async-first 重写 + 内置 session/cookie 持久化）
- **Camoufox** (备选) — Firefox 内核, ~80% bypass

**零 token 成本**，但启动慢 (3-8s)。

详见 `anti-detection.md`

## 升级/回退规则

| 当前层 | 失败信号 | 升级到 | 原因 |
|--------|---------|--------|------|
| 任意 | 内部站点/SSO/任意网页 | **`opencli web read`** | 万能回退，复用 Chrome 登录态，输出 Markdown |
| L2 | 403 / 内容空 | `opencli web read` | Jina/WebFetch 失败时的通用回退 |
| opencli | exit 77 (需登录) | Chrome 手动登录后重试 | Cookie 过期 |
| opencli | 无适配器 | `opencli web read` 或 agent-browser | 未覆盖的站点用 web read 抓内容 |
| L3 | selector 频繁失效 | L4 Stagehand | DOM 不稳定，需要 AI |
| L3/L4 | 反爬拦截 (403/CF盾) | L6 Zendriver | 需要指纹伪装 |
| L4 | 任务简单/流程固定 | ← L3 | 省 token |
| L3+ | 只需正文 | ← L2 | 不需要浏览器 |

## 观察项（暂不纳入）

- Browser Use — 成本高 (~$0.01/任务), 观望
- Skyvern — 场景有限
- BrowserOS — 定位重叠, 成熟度不足

> See also: `routing.md` (路由决策树), `setup.md` (工具安装), `opencli-usage.md` (opencli 详解)
