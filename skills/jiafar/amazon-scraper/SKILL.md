---
name: amazon-scraper
description: >
  High-performance containerized web scraper (Docker + Crawlee + Playwright).
  Use when user mentions any of these:
  爬虫, 爬取, 抓取, 采集, 数据采集, 爬数据, 抓数据, 获取数据,
  scrape, crawl, extract, fetch data, pull data,
  亚马逊, Amazon, ASIN, BSR, Best Sellers, 畅销榜, 热销榜, 新品榜, 飙升榜, 排行榜,
  选品, 竞品分析, 竞品调研, 市场调研, 品类分析, 类目分析, 产品调研,
  月销量, bought in past month, 销量, 评论数, 价格对比,
  YouTube, 视频字幕, 转录, transcript,
  网页内容, 网站数据, 页面抓取, 动态页面,
  TikTok, Twitter, X, 社交媒体数据, 帖子内容,
  关键词搜索, 搜索结果, search results,
  产品详情, 产品信息, listing数据, listing分析,
  top 100, top sellers, 热门产品, 爆款, 跑量款,
  价格带, 评分分布, review分析, 评论分析
---

# Amazon Scraper

Docker容器化爬虫，支持穿透反爬，三种模式自动识别（Amazon / YouTube / 通用网页）。

## 前置要求
- Docker 已安装并运行
- 首次使用前构建镜像（在 skill 目录下执行）:
  ```bash
  docker build -t clawd-crawlee /path/to/amazon-scraper/
  ```
- 创建输出目录: `mkdir -p ~/scrapes`

## 模式选择规则

### 1. Amazon模式 (`amazon_handler.js`)
**自动触发条件:** URL包含 `amazon.com`，或用户提到亚马逊/Amazon/ASIN/BSR/选品/竞品/畅销榜/类目分析等关键词

根据URL自动识别页面类型：

| URL特征 | 页面类型 | 可获取字段 |
|---|---|---|
| `/zgbs/` 或 `/bestsellers/` | 畅销榜 | rank, title, asin, price, rating, reviews, image, url |
| `/zg/new-releases/` | 新品榜 | 同上 |
| `/zg/movers-and-shakers/` | 飙升榜 | 同上 |
| `/s?k=` 或 `/s/` | 搜索结果 | title, asin, price, rating, reviews, image, url, **boughtPastMonth**, sponsored |
| `/dp/` 或 `/gp/product/` | 产品详情 | title, asin, price, rating, reviews, brand, bsr, **boughtPastMonth**, dateFirstAvailable, category, bullets, details, image |

**⚠️ 重要规则:**
- **Best Sellers页面没有月销量(boughtPastMonth)数据** — 亚马逊不在榜单页显示此信息
- **要获取月销量，必须用搜索页(`/s?k=关键词`)或产品详情页(`/dp/ASIN`)**
- 如果用户同时需要排名+月销量，建议：先爬Best Sellers拿排名，再用搜索页补月销

```bash
# 畅销榜（有排名，无月销）
docker run -t --rm clawd-crawlee node assets/amazon_handler.js "https://www.amazon.com/zgbs/electronics"

# 搜索结果（有月销，无排名）
docker run -t --rm clawd-crawlee node assets/amazon_handler.js "https://www.amazon.com/s?k=feather+duster"

# 产品详情（最全字段：BSR、品牌、卖点、月销）
docker run -t --rm clawd-crawlee node assets/amazon_handler.js "https://www.amazon.com/dp/B001TQ6IHS"

# 多页爬取
docker run -t --rm clawd-crawlee node assets/amazon_handler.js "URL" --pages 2
```

**输出格式:** JSON
```json
{
  "status": "SUCCESS",
  "type": "bestsellers|search|product-detail",
  "category": "品类名",
  "totalProducts": 30,
  "scrapedAt": "ISO时间",
  "products": [
    {
      "rank": 1,
      "title": "产品名",
      "asin": "B001TQ6IHS",
      "price": 9.94,
      "priceStr": "$9.94",
      "rating": 4.6,
      "reviews": 20547,
      "boughtPastMonth": "1K+",
      "image": "https://...",
      "url": "https://..."
    }
  ]
}
```

### 2. YouTube模式 (`main_handler.js`)
**自动触发条件:** URL包含 `youtube.com`，或用户提到YouTube/视频字幕/转录/transcript

- 拦截网络请求捕获字幕API (timedtext)
- 模拟点击"展开描述"和"转录稿"按钮
- 输出: `{status, type:"TRANSCRIPT"|"DESCRIPTION", videoId, data}`

```bash
docker run -t --rm clawd-crawlee node assets/main_handler.js "https://youtube.com/watch?v=xxx"
```

### 3. 通用模式 (`main_handler.js`)
**触发条件:** 非Amazon、非YouTube的URL，或用户提到爬取/抓取任意网页/社交媒体

- Playwright打开页面，等待JS加载完成
- 提取 `document.body.innerText`（纯文本，去广告噪音）
- 输出上限10000字符
- 输出: `{status:"SUCCESS", type:"GENERIC", title, data}`

```bash
docker run -t --rm clawd-crawlee node assets/main_handler.js "https://任意网址"
```

## Agent调用决策树

```
用户给了URL?
├─ 包含 amazon.com → 用 amazon_handler.js
│   ├─ 需要月销量? → 建议用搜索URL(/s?k=) 或详情页(/dp/)
│   └─ 需要排名? → 用畅销榜URL(/zgbs/)
├─ 包含 youtube.com → 用 main_handler.js (自动YouTube模式)
└─ 其他网站 → 用 main_handler.js (通用模式)

用户没给URL，只说了需求?
├─ "爬亚马逊XX品类Top" / "XX类目排行" / "XX畅销榜" → 构造 https://www.amazon.com/zgbs/品类
├─ "搜亚马逊XX" / "XX关键词搜索" / "找XX产品" → 构造 https://www.amazon.com/s?k=关键词
├─ "分析某个ASIN" / "看看这个产品" / "XX的详情" → 构造 https://www.amazon.com/dp/ASIN
├─ "XX的月销量" / "XX卖了多少" / "XX销量怎么样" → 用搜索页或详情页（有boughtPastMonth）
├─ "竞品分析" / "竞品调研" / "对手在卖什么" → 先搜索再逐个爬详情
├─ "选品" / "什么好卖" / "品类机会" / "市场调研" → Best Sellers + 搜索结合
└─ 其他 → 先web_search找到URL，再用对应模式爬
```

## 常见用户意图 → 操作映射

| 用户说 | 操作 |
|---|---|
| "帮我看看亚马逊XX品类" | 爬 /zgbs/品类 畅销榜 |
| "XX在亚马逊卖得怎么样" | 搜索 /s?k=XX 看月销 |
| "分析一下这个ASIN: BXXXXXXXXX" | 爬 /dp/ASIN 详情页 |
| "XX品类有什么机会" | 畅销榜 + 搜索 综合分析 |
| "帮我爬这个链接" | 判断URL类型，选对应handler |
| "这个YouTube视频讲了什么" | YouTube模式抓字幕 |
| "帮我抓XX网站的内容" | 通用模式 |
| "搜一下XX的竞品" | 搜索页爬取 + 分析 |
| "XX月销多少" / "XX一个月卖多少" | 搜索页或详情页 |
| "帮我看看top 100" / "热门产品" | Best Sellers畅销榜 |
| "新品有哪些" / "最近上了什么新品" | /zg/new-releases/ |
| "什么产品涨得快" / "飙升榜" | /zg/movers-and-shakers/ |

## 反爬能力
- 每次清除Cookie，模拟全新用户
- Docker沙箱隔离，无指纹追踪
- Playwright模拟真实浏览器行为
- 自动滚动加载懒加载内容
- 支持重试（maxRetries: 2）

## 数据输出模式（重要）

### 模式一：stdout 直接输出（适合单次抓取）
```bash
# 单URL抓取，结果打印到终端
docker run --rm clawd-crawlee node assets/amazon_handler.js "https://www.amazon.com/dp/ASIN"
```
⚠️ 并行执行多个容器时，stdout 会交织混乱，导致数据丢失或解析错误。

### 模式二：文件输出（适合批量抓取）⭐ 推荐
```bash
# 方式A：单次抓取写入文件
OUTDIR=~/scrapes && mkdir -p $OUTDIR
docker run --rm clawd-crawlee node assets/amazon_handler.js "URL" > $OUTDIR/$(date +%s).json 2>&1

# 方式B：批量抓取（使用 scripts/batch-scrape.sh）
# 设置输出目录（可自定义）
export SCRAPE_DIR=~/scrapes
# 执行批量抓取（从 stdin 读 ASIN 列表）
cat asin-list.txt | bash /path/to/amazon-scraper/scripts/batch-scrape.sh
# 结果文件存于 $SCRAPE_DIR/{timestamp}.json
```
✅ 结果直接写文件，不走 stdout，完全避免输出混乱问题。

### 批量分析工作流
```
1. 爬取数据  -> 存文件到 ~/scrapes/
2. 本地分析  -> Python 读文件做统计分析
3. 结果进LLM -> 只把分析结论发给 AI，避免大量原始数据浪费 token
```

## 浏览器直采模式（Browser Extraction）⭐ 搜索页首选

当 Crawlee 容器不可用或 CSS 选择器失效时，可直接用浏览器工具提取 Amazon 搜索结果。**此方式更可靠**，因为能实时调试 DOM 选择器。

### 步骤
1. `browser_navigate` 打开搜索 URL: `https://www.amazon.com/s?k=关键词`
2. 用 `browser_console` 执行 JS 提取数据（选择器见下方）
3. 结果直接为 JSON 数组，可用 Python 做后续分析

### 关键 DOM 选择器（2026-04 验证）

| 数据 | 选择器 | 备注 |
|---|---|---|
| 商品卡片 | `[data-component-type="s-search-result"]` | 遍历所有结果 |
| ASIN | `card.getAttribute('data-asin')` | 卡片属性 |
| 完整标题 | `.a-text-normal` | ⚠️ `h2 a span` 只取到品牌名！ |
| 品牌 | `h2 span` (第一个) | 仅品牌名 |
| 价格 | `.a-price .a-offscreen` | parseFloat |
| 评分 | `[aria-label*="out of"]` → getAttribute('aria-label') | parseFloat |
| 评论数 | 正则 `\(([\d,.]+[KkMm]?)\)` 匹配卡片全文 | K=×1000, M=×1000000 |
| 月销量 | 遍历所有 span 找 "bought in past month" | 正则 `([\d,.]+[KkMm]?\+?)\s*bought` |

### 提取脚本模板
```javascript
const items = [];
document.querySelectorAll('[data-component-type="s-search-result"]').forEach(card => {
    const asin = card.getAttribute('data-asin');
    const title = card.querySelector('.a-text-normal')?.textContent.trim();
    const brand = card.querySelector('h2 span')?.textContent.trim();
    const price = parseFloat(card.querySelector('.a-price .a-offscreen')?.textContent.replace(/[^0-9.]/g, '') || 0);
    const rating = parseFloat(card.querySelector('[aria-label*="out of"]')?.getAttribute('aria-label') || 0);
    let reviews = null;
    const rm = card.textContent.match(/\(([\d,.]+[KkMm]?)\)/);
    if (rm) { let r = rm[1].replace(/,/g,''); if (r.includes('K')) r = parseFloat(r)*1000; reviews = parseInt(r); }
    let bpm = null;
    card.querySelectorAll('span').forEach(s => {
        const m = s.textContent.trim().match(/([\d,.]+[KkMm]?\+?)\s*bought/i);
        if (m) bpm = m[1];
    });
    if (title && asin) items.push({ asin, brand, title, price, rating, reviews, boughtPastMonth: bpm });
});
JSON.stringify(items);
```

## Amazon 市场容量分析（属性提取+统计）

对搜索结果进行属性提取和市场容量量化分析，是选品调研的核心能力。

### 属性提取维度（从标题解析）

| 维度 | 关键词模式 | 示例 |
|---|---|---|
| Material | cotton, polyester, wool, cashmere, fleece, knit, ribbed, cable knit, waffle knit, crochet, blend | "Cable Knit" → cable knit |
| Style | pullover, cardigan, hoodie(s), sweatshirt(s), tunic, tee/t-shirt, jumper, blouse, polo | ⚠️ 多标签可叠加 |
| Sleeve | long sleeve/long-sleeve, short sleeve, 3/4 sleeve, sleeveless | 两种写法都要匹配 |
| Neckline | crew neck/crewneck, v-neck/v neck, turtleneck, henley, stand neck, half/quarter zip, collared, lapel, round neck | 多标签可叠加 |
| Thickness | lightweight/light weight, midweight, heavyweight, fleece, cozy | lightweight 是绝对主流 |
| Occasion | casual, dressy, business, work, outdoor, travel, date night, workout | casual 占 70%+ |
| Audience | women, plus size, oversized, petite, loose fit, cropped fit | oversized 平均销量最高 |
| Season | fall, winter, spring, summer | fall 主流, spring 蓝海 |
| Pattern | cable knit, solid, striped, floral, color block, hollow out, novelty, ribbed | 大部分未标注 |
| Color | black, white, navy, red, green, beige, grey... | 大部分搜索页不显示 |

### 市场容量统计框架
```python
# 对每个属性维度统计: 销量合计, 商品数, 平均销量, 市场占比, Top3集中度
for dim in dimensions:
    attr_sales = defaultdict(int)
    attr_count = defaultdict(int)
    for product in active_products:
        for val in product['attributes'][dim]:
            attr_sales[val] += product['estimatedSales']
            attr_count[val] += 1
    # Top3集中度 = Top3属性销量之和 / 该维度总销量
```

### 月销量估算规则
- `boughtPastMonth` 字段直接解析: "400+" → 400, "1K+" → 1000, "2M+" → 2000000
- 无此字段的商品销量记为0，从分析中排除

## Crawlee 已知问题与修复

### 搜索页标题为 null 的 Bug ⚠️
**原因:** `amazon_handler.js` 中搜索页选择器 `h2 a span` 只匹配到品牌名 span（class: `a-size-base-plus a-color-base`），完整标题在 `.a-text-normal` 元素中。

**修复:** 在 `amazon_handler.js` 的 search 分支（约第174行）中修改：
```javascript
// 旧（只取品牌）:
const titleEl = card.querySelector('h2 a span');
// 新（取完整标题）:
const titleEl = card.querySelector('.a-text-normal');
```

### Crawlee 依赖缺失
Crawlee 安装后还需单独安装 playwright: `npm install playwright && npx playwright install chromium && npx playwright install-deps chromium`

## 局限
- 通用模式输出上限10000字符
- Amazon单页最多约30-50个产品
- 不支持需要登录的页面
- Docker容器启动有~10秒冷启动时间
- 畅销榜页面（/zgbs/）不显示月销量数字，需另爬详情页补全
- 搜索页颜色属性大多不显示在标题中（需爬详情页或图片识别）
