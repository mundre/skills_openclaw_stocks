---
name: BuyWise
description: |
  BuyWise is your personal shopping advisor — it helps you decide whether to buy, where to buy, and when to buy, across all major global and Chinese platforms.

  Instead of manually checking Amazon, eBay, AliExpress, Temu, JD, Taobao, and Tmall one by one, BuyWise aggregates prices from all platforms into a single comparison table with clear best-pick recommendations. It goes beyond simple price lookup: BuyWise analyzes historical price trends to detect fake promotions (the inflate-then-discount trick common in Double 11 / 618 sales), distills thousands of user reviews into a concise strengths/complaints/red-flags summary, recommends better alternatives at lower prices, and tells you whether to buy now or wait for the next major sale event.

  Just tell BuyWise what you want to buy — it handles the rest.

keywords: 购物助手, 比价, 值不值得买, 买前必看, 识别假促销, 双11, 618, 京东, 淘宝, 天猫, 拼多多, 评价分析, 好物推荐, 省钱, 替代品, 购物时机, 历史价格, 最低价, 购物决策, 剁手前, 亚马逊, 速卖通, shopping assistant, price comparison, buy or wait, deal checker, Amazon, eBay, AliExpress, Temu, JD, Taobao, Tmall, price tracker, review summary, best price, shopping advisor, is it worth buying, fake discount, product review, alternatives, best deal
metadata:
  openclaw:
    runtime:
      node: ">=18"
    recommends:
      skills:
        - gstack
---

# BuyWise — 全球购物决策助手

> 比价 · 识别假促销 · 评价提炼 · 替代品推荐 · 买入时机判断

## 何时使用

- 用户问"这个值得买吗""这个怎么样"
- 用户说"帮我比价""最低价在哪""哪里买最便宜"
- 用户问"双11能便宜多少""618值得等吗""现在买合适吗"
- 用户说"帮我看看评价""这个评价怎么样""有没有问题"
- 用户说"有没有平替""有没有更便宜的""有没有更好的"
- 用户发来商品链接，询问是否值得购买

---

## 🌐 语言规则

- 默认中文；用户英文提问切英文
- 价格按用户所在市场显示（国内用 ¥，国际用 $）
- 平台名称保留原文（不翻译 Amazon / JD / Temu 等）

---

## 🛒 覆盖平台

| 市场 | 平台 |
|------|------|
| 中国国内 | 京东、淘宝、天猫、拼多多（百亿补贴）、闲鱼（二手） |
| 国际 | Amazon、eBay、AliExpress、Temu |

---

## 🔌 数据来源

BuyWise 通过 **browser 工具直接导航到真实数据页面**获取价格，不依赖 web_search 猜测：

| 数据类型 | 来源 | 覆盖平台 |
|---------|------|---------|
| 中国市场价格 | **什么值得买 smzdm.com** | 京东、淘宝、天猫、拼多多 |
| Amazon 历史价格 | **CamelCamelCamel** | Amazon 全球 |
| Amazon 当前价格 | amazon.com 搜索页 | Amazon |
| eBay 价格 | ebay.com 搜索页 | eBay |
| AliExpress 价格 | aliexpress.com 搜索页 | AliExpress |
| Temu / 闲鱼 | web_search 补充 | Temu、闲鱼 |
| 评价 | web_search + 小红书/知乎/Reddit | 多平台 |

> 需要 `gstack` skill 已安装以启用 browser 导航能力。未安装时降级为 web_search（精度下降）。

---

## 📋 功能说明

### 综合决策（主功能）
用户说"帮我看看 XX"时触发完整分析：
1. **多平台比价** — browser 导航 smzdm/Amazon/eBay/AliExpress 等获取真实价格，汇总对比表
2. **促销真实性** — browser 导航 CamelCamelCamel + smzdm 价格走势图，判断是否真实低价
3. **评价提炼** — 从京东/知乎/小红书/Reddit 等多源提炼 3 优点 / 3 槽点 / 适合人群 / 红旗警告
4. **替代品推荐** — 搜索同类更高性价比产品，推荐 2-3 个选项
5. **购买时机** — 结合历史低价、大促节点、当前价格给出 🟢立即买 / 🟡再等等 / 🔴不建议

### 独立比价
用户只问"XX 多少钱""哪里最便宜"时，仅输出比价表，不做完整分析。

### 促销核查
用户说"这个双11真的便宜吗""这个折扣是真的吗"时，专项分析价格历史，判断促销真实性。

### 评价深读
用户说"详细说说评价""口碑怎么样"时，深度搜索多平台评测、论坛讨论、投诉记录。

---

## 🔧 脚本说明

```bash
# 完整购物决策（主入口）
node scripts/advise.js <商品名> [--lang zh|en]
# 示例：
node scripts/advise.js "戴森吸尘器 V15"
node scripts/advise.js "Sony WH-1000XM5" --lang en

# 仅比价
node scripts/compare.js <商品名> [--lang zh|en]
node scripts/compare.js "AirPods Pro 2"

# 促销真实性核查
node scripts/deal-check.js <商品名> [--price 当前价] [--was 标称原价] [--lang zh|en]
node scripts/deal-check.js "iPhone 16" --price 5999 --was 7999

# 评价提炼
node scripts/review-scan.js <商品名> [--lang zh|en]
node scripts/review-scan.js "小米路由器 BE7000"
```

---

## ⚠️ 注意事项

1. 价格基于 WebSearch 实时搜索，可能存在轻微延迟，购买前以平台实际页面为准
2. 历史价格分析依赖公开信息，若平台不公示价格历史则以搜索结果为准
3. 评价摘要基于公开评测，不代表所有用户体验
4. 促销节点判断（双11/618等）以中国电商日历为基准；国际促销参考 Black Friday / Prime Day
5. 替代品推荐不含广告或赞助，仅基于性价比分析
