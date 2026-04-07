---
name: browser-ops
description: "搜索+API+ 抓取 + 反爬统一入口。API 优先 (AKShare/新浪)/搜索引擎 API/网页抓取/爬虫/反爬。搜索 抓取 爬取 获取网页 打开网站 查股价 行情 热榜 热门 网站打不开 被拦截 截图 下载网页 批量查询。scrape crawl fetch browse screenshot cookie session anti-bot cloudflare bypass login。Twitter 微博 小红书 知乎 HackerNews Reddit B 站 GitHub trending 豆瓣 淘宝 京东。opencli agent-browser playwright zendriver camoufox jina stagehand。Use when: (1) 搜索 XXX, (2) 访问/抓取任何网站，(3) 查股价/行情/热榜，(4) 截图，(5) 反爬绕过，(6) 登录态复用。Also use when WebFetch/built-in tools fail (403/blocked/empty)."
---

# Browser Operations — 搜索+API+ 抓取 + 反爬统一入口

> **WHEN TO LOAD THIS SKILL** — match ANY of these patterns:
> - "搜索 XXX" / "search XXX"（没给 URL）
> - User mentions a URL or website name and wants data from it
> - 抓取/爬取/获取/打开/访问 any 网页/网站/页面
> - 查股价/行情/热榜/热门/trending/hot list from any platform
> - 截图/screenshot a webpage
> - 被拦截/403/Cloudflare/anti-bot/反爬/网站打不开
> - 批量查询/batch fetch (e.g. query 100 stocks)
> - 登录网站/login/cookie/session persistence
> - WebFetch returned 403/empty/blocked → escalate here
> - Twitter/微博/小红书/知乎/Reddit/HackerNews/B 站/GitHub/豆瓣
> - opencli/agent-browser/playwright/zendriver/camoufox/jina/stagehand

## 路由决策树（API 优先 → 搜索 → 抓取 → 浏览器 → 反爬）

```
收到任务
│
├─ 有官方 API / RSS？⭐ 最优先
│  └─ 是 → L0: API（$0，最稳定）
│     - 金融行情 → AKShare / 新浪 API
│     - 财报数据 → 官方 API
│     - RSS Feed → feedparser
│
├─ 要搜索 XXX（没给 URL）？
│  └─ L1: 搜索引擎 API（$0，多源聚合）
│     - "搜索 XXX" → Brave/Perplexity API
│     - 返回链接列表 + 摘要
│
├─ 有明确 URL / 站点？
│  ├─ 任意网页内容（含内部/SSO 站点）？
│  │  └─ L2a: opencli web read ($0, 复用 Chrome 登录态) ⭐⭐⭐
│  │     自动输出 Markdown，支持 SSO/内网/任意站点
│  │
│  ├─ 只需正文（文章/博客/文档）？
│  │  ├─ L2b: Jina ($0)
│  │  └─ 失败 (403/空) → opencli web read
│  │
│  ├─ 目标平台有 opencli 适配器？(73 站点)
│  │  └─ 是 → L2c: opencli <platform> <command> ($0) ⭐⭐
│  │     twitter/bilibili/xiaohongshu/reddit/zhihu/github...
│  │
│  └─ 批量数据拉取（>10 次/分钟）？
│     ├─ 金融行情 → AKShare/新浪 API（一次批量请求）
│     ├─ 社交媒体 → 平台官方 API 或 Zendriver+ 代理并发
│     └─ 通用网页 → asyncio+aiohttp 并发抓取
│
├─ 需要交互（点击/填表/滚动）？
│  ├─ 有 Playwright/Puppeteer MCP？→ L3a: 直接用 MCP 工具 ($0) ⭐
│  ├─ 固定流程/已知 DOM → L3b: agent-browser ($0)
│  └─ 动态网站/未知 DOM → L4: Stagehand (~$0.001/任务)
│
├─ 需要截图/渲染？
│  └─ Playwright MCP screenshot 或 agent-browser screenshot
│
├─ 大规模并发（>50 页）？
│  └─ L5: Zyte > Browserless > Hyperbrowser
│
└─ 被反爬拦截（403/Cloudflare 盾）？
   ├─ L6a: Zendriver (~90% bypass, Nodriver 继任者)
   └─ L6b: Camoufox (~80% bypass)
```

**核心原则**: 
- API 优先 > 搜索 API > 免浏览器抓取 > 浏览器 > 反爬
- 任意网页 → `opencli web read`（万能，复用 Chrome 登录态）
- 已知平台 → `opencli <platform>`（结构化数据）
- 交互 → Playwright MCP/agent-browser

## 升级/回退

| 信号 | 动作 |
|------|------|
| L0/L1 无结果 | → L2 抓取 |
| L2 返回 403/内容空 | → `opencli web read`（万能回退）|
| 内部站点/SSO 站点 | → `opencli web read`（复用 Chrome 登录态）|
| opencli exit 77 (需要登录) | → 在 Chrome 中手动登录，再重试 |
| L3 selector 频繁失效 | → L4 Stagehand (AI 理解 DOM) |
| L3/L4 被反爬拦截 | → L6 Zendriver/Camoufox |
| 任务只要正文但用了 L3+ | ← 降回 L2 |

## 工具速查

### L0: API 优先（最优先）

```bash
# 金融行情
python3 -c "import akshare as ak; print(ak.stock_zh_a_spot().head())"
curl "https://hq.sinajs.cn/list=sh600036,sz000001"

# RSS
python3 -c "import feedparser; print(feedparser.parse('https://example.com/feed.xml'))"
```

### L1: 搜索引擎 API

```bash
# 搜索 XXX（没给 URL 时）
opencli search "GitHub trending Python"  # 返回链接列表 + 摘要
```

### L2a: opencli web read（万能抓取）

```bash
# 任意网页转 Markdown（含内部/SSO 站点）⭐⭐⭐
opencli web read --url "https://any-site.com/page"        # 输出 Markdown
opencli web read --url "https://internal.company.com/doc" # SSO 站点也能用
```

### L2c: opencli 平台适配器（73 站点）

```bash
opencli twitter trending                     # Twitter 热门
opencli xiaohongshu search "旅行"            # 小红书搜索
opencli zhihu hot                            # 知乎热榜
opencli github trending                      # GitHub trending
```

### L2b: Jina（正文提取）

```bash
curl -s "https://r.jina.ai/https://example.com/article" > article.md
```

### L3a: Playwright MCP

`browser_navigate` / `browser_click` / `browser_snapshot` / `browser_type` / `browser_take_screenshot`

### L3b: agent-browser

```bash
agent-browser open <url> / snapshot -i / click @e1 / fill @e2 "text" / screenshot
```

### L4: Stagehand v3（AI 增强）

```typescript
const stagehand = new Stagehand({ env: "LOCAL", model: "anthropic/claude-sonnet-4-5" });
await stagehand.init();
await stagehand.act("点击登录按钮");
```

### L6: 反爬

```bash
python3 -c "import zendriver; ..."  # ~90% bypass
python3 -c "import camoufox; ..."   # ~80% bypass
```

## Bootstrap（首次使用自动执行）

```bash
# 1. 检测已安装的工具
opencli doctor                                    # 桥接层：复用 Chrome 登录态
which agent-browser && agent-browser --version    # L3: 命令化浏览器
node -e "require('@browserbasehq/stagehand')"     # L4: AI 增强浏览器
python3 -c "import zendriver"                      # L6: 反爬

# 2. 缺失则安装（按优先级）
npm install -g @jackwener/opencli                  # 必装：桥接层
npm install -g agent-browser && agent-browser install  # 必装：命令化浏览器
pip install zendriver                               # 按需：遇到反爬时装

# 3. 初始化统一 Cookie 存储
mkdir -p ~/.browser-ops/cookie-store ~/.browser-ops/profiles/shared
```

详细安装和 Chrome 扩展配置见 `references/setup.md`

## 统一 Cookie 存储

**登录一次，所有工具复用。** Cookie 统一存储在 `~/.browser-ops/cookie-store/unified-state.json`。

```bash
# 首次登录（弹出浏览器窗口，手动登录后按 Enter）
bash scripts/sync-cookies.sh login https://your-company-sso.example.com

# 查看存储状态
bash scripts/sync-cookies.sh status

# agent-browser 自动加载统一 Cookie
bash scripts/sync-cookies.sh import
agent-browser open https://internal.example.com   # 直接访问内网
```

各工具复用方式见 `references/state-management.md`

## References

- `references/setup.md` — 工具安装与验证
- `references/opencli-usage.md` — opencli 桥接层详解
- `references/architecture.md` — 分层架构详解
- `references/routing.md` — 路由决策树
- `references/state-management.md` — Session/Cookie 持久化
- `references/jina-usage.md` — Jina 正文提取
- `references/anti-detection.md` — 反爬策略

## Operator Notes

- **必装**: opencli + agent-browser。opencli 需 Chrome 扩展，有适配器的平台优先用（零 LLM 成本）。
- **按需**: Stagehand 需 Anthropic/OpenAI/Gemini API key。Zendriver/Camoufox 需 Python 3.12+。
- **搜索需求**: 用 `opencli search` 或 Brave/Perplexity API
- **API 优先**: 能用 API 绝不用爬虫

## 版本历史

- **2.9.0**: 整合搜索层 + API 优先原则 | **2.8.0**: opencli web read 万能抓取 | **2.7.0**: 准确性修正 | **2.6.0**: 触发率 | **2.4.0**: 批量 API | **1.0**: 初版
