---
name: pharmacy-price-monitor
description: 药品电商价格监控与版本识别系统。监控京东、淘宝、拼多多等电商平台药品售价，识别低于标准价的违规商家及非授权版本（海外版、港版等），自动生成 Markdown 分析报告与多期趋势对比。使用 OpenClaw Browser 工具进行数据抓取，绕过反爬机制。适用于：价格体系维护、渠道风险监控、市场调研、代理商合规检查等场景。触发词：监控价格/查价格/价格监控/药品价格/电商比价/渠道监控。
---

# 药品电商价格监控 Skill

## 核心能力

- **价格合规性监控**：识别低于标准价的违规店铺
- **非授权版本识别**：检测海外版、港版、代购等非官方渠道商品
- **多平台监控**：支持京东、淘宝、拼多多
- **趋势分析**：多期数据对比，追踪违规变化
- **报告生成**：自动生成 Markdown 结构化报告
- **数据库存储**：SQLite 本地持久化，支持历史查询和趋势分析

## 适用场景

- 监控指定药品的电商平台售价是否低于公司 MAP 价
- 识别非授权销售渠道（海外版、港版等）
- 定期价格巡检，生成合规报告
- 分析各平台价格分布和违规趋势

---

## 工作流程

### 第一步：收集需求参数

必需参数：
- **药品名称**：完整药品名称（如："阿莫西林胶囊"）
- **标准价格**：公司规定的统一零售价（如：33 元）

可选参数：
- **规格**：药品规格（如："0.25g*24粒"）
- **监控平台**：京东、淘宝、拼多多（默认全部）

示例：
```
监控"黛力新 0.5mg:10mg 20片/盒"的价格，标准价50元，查京东和淘宝
```

---

### 第二步：数据抓取（Browser 工具）

**推荐方法：使用 Browser 工具直接抓取**
- 不依赖 Cookie导出
- 不受登录态过期影响
- 翻页更可靠

#### 2.1 京东抓取流程（✅已验证 2026-04-17）

**分页机制（2024年京东改版后）：**
- 底部显示 `"1/10 共10页 上一页 1 2 3 4 5 6 7 下一页"`
- URL **不变**，内容通过 AJAX 无刷新加载
- ❌ 点击"下一页"文字链接 → 无效（分页器不更新）
- ✅ 点击数字按钮（如"2"）→ 触发 AJAX 加载

**数据提取选择器（2024年京东新结构）：**
```
商品卡片：document.querySelectorAll('[data-sku]')
标题：item.querySelector('[class*="title"]').innerText
价格：item.querySelector('[class*="price"]').innerText（需清洗换行）
店铺：item.querySelector('[class*="name"]').innerText
```

**完整操作流程：**

```
1. 打开搜索页
   browser action:open url:"https://search.jd.com/Search?keyword=<关键词>"

2. 等待8秒让JS渲染
   browser action:act kind:wait timeMs:8000

3. 提取第1页数据（JS evaluate）
   browser action:act kind:evaluate fn:<提取JS>
   → 返回 'clicked page X' 表示成功
   → 返回 'no more pages' 表示已到最后一页，停止

4. 执行翻页JS（京东用"下一页"按钮，淘宝用数字按钮）
   browser action:act kind:evaluate fn:<翻页JS>

5. 等待6秒
   browser action:act kind:wait timeMs:6000

6. 提取当前页数据
   → 重复步骤4-6直到返回 'no more pages'

7. 合并所有页数据，去重
```

**⚠️ 重要：必须翻到"no more pages"才停止！**
- 京东有10-20页，必须逐页翻完
- 中途停止会丢失后面页面的数据

**停止条件：**
- 翻页JS返回 `'no more pages'` → 已到最后一页
- 翻页后商品数量不变 → 可能已卡在最后一页，停止

**提取数据 JS（每页执行）：**
```javascript
() => {
  const results = [];
  const items = document.querySelectorAll('[data-sku]');
  
  for (const item of items) {
    const titleEl = item.querySelector('[class*="title"]');
    const priceEl = item.querySelector('[class*="price"]');
    const shopEl = item.querySelector('[class*="name"]');
    
    const title = titleEl ? titleEl.innerText.trim() : '';
    let price = priceEl ? priceEl.innerText.trim().replace(/\s/g, '') : '';
    const shop = shopEl ? shopEl.innerText.trim() : '';
    
    if (title && price) {
      results.push({ title, price, shop, platform: '京东' });
    }
  }
  return JSON.stringify(results);
}
```

**翻页 JS（京东 - 推荐方案）：**
```javascript
// 京东翻页 - 直接点击"下一页"按钮
// 适用于京东搜索页（2024年改版后验证）
() => {
  const nextBtns = document.querySelectorAll('[class*="next"]');
  for (const btn of nextBtns) {
    const txt = btn.innerText ? btn.innerText.trim() : '';
    if (txt === '下一页') {
      btn.click();
      return 'clicked next page';
    }
  }
  return 'no more pages';
}
```

**翻页 JS（备选方案 - 动态找数字按钮）：**
```javascript
// 如果"下一页"按钮失效，使用数字按钮翻页
() => {
  const allElements = document.querySelectorAll('*');
  let maxPage = 0;
  let nextBtn = null;
  
  for (const el of allElements) {
    try {
      const txt = el.innerText ? el.innerText.trim() : '';
      if (txt.isdigit() && el.childNodes.length === 1) {
        const num = parseInt(txt);
        const parent = el.parentElement;
        if (parent && parent.innerText && parent.innerText.includes('下一页')) {
          if (num > maxPage) {
            maxPage = num;
            nextBtn = el;
          }
        }
      }
    } catch(e) {}
  }
  
  if (nextBtn) {
    nextBtn.click();
    return 'clicked page ' + maxPage;
  }
  return 'no more pages';
}
```

**⚠️ 注意事项：**
- 翻页后必须等待 6 秒（AJAX 加载需要时间）
- 用 `networkidle` 判断加载完成会永远超时（京东有持续追踪请求）
- 翻页失败特征：点击后商品数量不变 → 停止翻页

---

#### 2.2 淘宝抓取流程（✅已验证 2026-04-17）

**已知限制：**
- URL 的 page 参数会被服务器强制重定向回 page=1
- ❌ 直接访问 `&page=2` 的 URL → 回到第1页
- ✅ 必须用点击数字按钮翻页

**分页机制：**
- 显示"上一页 当前第1页 /5 下一页"
- 点击数字按钮"2"可以正常翻页（不是URL参数）

**提取数据 JS：**
```javascript
() => {
  const results = [];
  const seen = new Set();
  const links = document.querySelectorAll('a[href*="detail.tmall.com"], a[href*="item.htm"]');
  
  for (const link of links) {
    const text = link.innerText || '';
    if (text.includes('黛力新') && text.includes('¥') && text.includes('片')) {
      const priceMatch = text.match(/¥\s*([\d.]+)/);
      const dealsMatch = text.match(/(\d+[\d万]*)\s*人付款/);
      const price = priceMatch ? priceMatch[1] : '';
      const deals = dealsMatch ? dealsMatch[1] : '';
      let title = '商品标题';
      
      // 提取店铺名
      const lines = text.split('\n').filter(l => l.trim());
      let shop = '';
      for (let j = lines.length - 1; j >= 0; j--) {
        const l = lines[j].trim();
        if (l.includes('旗舰店') || l.includes('大药房') || l.includes('医药专营')) {
          shop = l;
          break;
        }
      }
      
      if (price && !seen.has(price)) {
        seen.add(price);
        results.push({ title, price, shop, deals, platform: '淘宝' });
      }
    }
  }
  return JSON.stringify(results);
}
```

**翻页 JS（淘宝通用 - 动态版本）：**
```javascript
// 淘宝翻页 - 自动点击下一个数字按钮
() => {
  const allElements = document.querySelectorAll('*');
  let maxPage = 0;
  let nextBtn = null;
  
  for (const el of allElements) {
    try {
      const txt = el.innerText ? el.innerText.trim() : '';
      if (txt.isdigit() && el.childNodes.length === 1) {
        const num = parseInt(txt);
        const parent = el.parentElement;
        if (parent && parent.innerText && parent.innerText.includes('下一页')) {
          if (num > maxPage) {
            maxPage = num;
            nextBtn = el;
          }
        }
      }
    } catch(e) {}
  }
  
  if (nextBtn) {
    nextBtn.click();
    return 'clicked page ' + maxPage;
  }
  return 'no more pages';
}
```

---

#### 2.3 拼多多抓取流程（✅已验证 2026-04-20）

**关键技术发现（⚠️ 重要修正 2026-04-20）：**
- `window.rawData.stores.store.data.ssrListData.list` 只在**首屏 SSR 时注入一次**
- 滚动后 AJAX 加载的新商品**不在** `window.rawData` 中，翻页后它仍然是 20 条
- ✅ 正确方法：**滚动完成后，从 DOM 提取所有商品文本**，再解析结构
- 商品文本特征：同时包含 `黛力新` + `¥` + `片` + 长度 30~800 字符的 DOM 元素
- 价格字段在 DOM 中被拆成多行（如 `¥\n42\n.6`），需要清洗合并
- 翻页机制：**瀑布流无限滚动**，`scrollHeight` 会随加载不断扩大
- 停止条件：连续 3 次滚动后 DOM 中 drug items 数量不变（建议上限 20 次滚动）

**操作流程：**
```
1. browser action:open url:"https://mobile.yangkeduo.com/search_result.html?search_key=<关键词>"
2. 等待8秒（SSR渲染完成）
3. 循环（最多20次）：
   a. 执行滚动 JS：window.scrollBy(0, 800)
   b. 等待3秒（让 AJAX 加载）
   c. 检查 drug items 数量
   d. 若数量不变次数 >= 3，停止滚动
4. 执行 DOM 提取 JS（见下方）
5. Python 解析价格/标题/销量，生成报告
```

**滚动 JS（拼多多）：**
```javascript
() => {
  window.scrollBy(0, 800);
  return 'scrolled, scrollH=' + document.body.scrollHeight;
}
```

**DOM 提取 JS（滚动完成后执行，全量提取）：**
```javascript
// 从 DOM 提取所有商品（用于滚动完成后一次性提取）
() => {
  var all = document.querySelectorAll('*');
  var rawItems = [];
  for (var i = 0; i < all.length; i++) {
    var txt = all[i].innerText || '';
    if (txt.indexOf('黛力新') === -1) continue;
    if (txt.indexOf('片') === -1) continue;
    if (txt.indexOf('¥') === -1) continue;
    if (txt.length < 30 || txt.length > 800) continue;
    rawItems.push(txt);
  }
  // 按前50字符去重
  var seen = {};
  var unique = [];
  for (var j = 0; j < rawItems.length; j++) {
    var key = rawItems[j].substring(0, 50);
    if (!seen[key]) { seen[key] = true; unique.push(rawItems[j]); }
  }
  return 'unique:' + unique.length + ' samples:' + JSON.stringify(unique.slice(0,2)).substring(0, 300);
}
```

**Python 解析脚本（处理 DOM 原始文本）：**
```python
import re

def parse_pinduoduo_items(raw_texts):
    """解析拼多多 DOM 原始文本，提取结构化商品数据"""
    results = []
    for txt in raw_texts:
        lines = txt.split('\n')
        title = ''
        price = ''
        sales = ''
        for li, line in enumerate(lines):
            l = line.strip()
            # 取第一个含药品名的行作为标题
            if not title and ('黛力新' in l or '氟哌噻吨' in l or '加乐舒' in l):
                title = l
            # ¥ 符号后面跟着数字/小数点是价格
            if l == '¥' and li + 1 < len(lines):
                p1 = lines[li+1].strip()
                p2 = lines[li+2].strip() if li+2 < len(lines) else ''
                # 处理 ¥
42
.6 格式（价格被拆成多行）
                if p2 and re.match(r'^\.[0-9]$', p2):
                    price = p1 + p2
                else:
                    price = p1
            # 销量
            if '本店已拼' in l or '全店总售' in l:
                sales = l
                break
        if title and price:
            results.append({'title': title[:80], 'price': price, 'sales': sales, 'platform': '拼多多'})
    return results
```

**⚠️ 注意事项：**
- ❌ 不要依赖 `window.rawData` 取滚动后的数据（它不更新！）
- ✅ 必须从 DOM 提取：`querySelectorAll` + 关键词过滤
- 等待时间：首次加载 8 秒，每次滚动后等待 3 秒
- 价格清洗：`¥\n42\n.6` → `42.6`
- 拼多多无限滚动：热门药品搜索可达数百条，建议设滚动上限（如 20 次）

---

### 第三步：数据库存储

#### 3.1 数据库初始化

数据库路径：`~/.openclaw/skills/pharmacy-price-monitor/price_monitor.db`

**数据库架构：**

```sql
-- 药品表（按药品名称去重）
CREATE TABLE IF NOT EXISTS drugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    spec TEXT,
    standard_price REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 抓取记录表（每次抓取一条记录）
CREATE TABLE IF NOT EXISTS crawl_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drug_id INTEGER NOT NULL,
    platform TEXT NOT NULL,
    total_items INTEGER,
    min_price REAL,
    max_price REAL,
    avg_price REAL,
    crawl_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (drug_id) REFERENCES drugs(id)
);

-- 商品详情表
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crawl_record_id INTEGER NOT NULL,
    drug_id INTEGER NOT NULL,
    platform TEXT NOT NULL,
    title TEXT,
    price REAL NOT NULL,
    shop TEXT,
    deals TEXT,
    url TEXT,
    is_low_price BOOLEAN DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (crawl_record_id) REFERENCES crawl_records(id),
    FOREIGN KEY (drug_id) REFERENCES drugs(id)
);
```

#### 3.2 数据存储脚本

每次抓取完成后，将数据存入数据库：

```python
import sqlite3, json
from datetime import datetime

DB_PATH = "~/.openclaw/skills/pharmacy-price-monitor/price_monitor.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS drugs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        spec TEXT,
        standard_price REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS crawl_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        drug_id INTEGER NOT NULL,
        platform TEXT NOT NULL,
        total_items INTEGER,
        min_price REAL,
        max_price REAL,
        avg_price REAL,
        crawl_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (drug_id) REFERENCES drugs(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crawl_record_id INTEGER NOT NULL,
        drug_id INTEGER NOT NULL,
        platform TEXT NOT NULL,
        title TEXT,
        price REAL NOT NULL,
        shop TEXT,
        deals TEXT,
        url TEXT,
        is_low_price BOOLEAN DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (crawl_record_id) REFERENCES crawl_records(id),
        FOREIGN KEY (drug_id) REFERENCES drugs(id))''')
    conn.commit()
    return conn

def save_crawl(drug_name, spec, standard_price, platform, products):
    conn = init_db()
    c = conn.cursor()
    
    # 插入或获取药品ID
    c.execute('''INSERT OR IGNORE INTO drugs (name, spec, standard_price) 
                 VALUES (?, ?, ?)''', (drug_name, spec, standard_price))
    c.execute('SELECT id FROM drugs WHERE name = ?', (drug_name,))
    drug_id = c.fetchone()[0]
    
    # 计算价格统计
    prices = [float(p['price'].replace('¥','').replace(',','')) for p in products]
    min_p, max_p, avg_p = min(prices), max(prices), sum(prices)/len(prices)
    
    # 插入抓取记录
    c.execute('''INSERT INTO crawl_records 
                 (drug_id, platform, total_items, min_price, max_price, avg_price)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (drug_id, platform, len(products), min_p, max_p, avg_p))
    crawl_record_id = c.lastrowid
    
    # 插入商品
    for p in products:
        price_val = float(p['price'].replace('¥','').replace(',',''))
        is_low = 1 if standard_price and price_val < standard_price else 0
        c.execute('''INSERT INTO products 
                     (crawl_record_id, drug_id, platform, title, price, shop, deals, is_low_price)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (crawl_record_id, drug_id, platform, p.get('title',''), 
                   price_val, p.get('shop',''), p.get('deals',''), is_low))
    
    conn.commit()
    conn.close()
    print(f"已存储 {len(products)} 条商品数据到数据库")

# 使用示例：
# save_crawl("黛力新", "0.5mg:10mg 20片/盒", 50.0, "京东", jd_products)
# save_crawl("黛力新", "0.5mg:10mg 20片/盒", 50.0, "淘宝", taobao_products)
```

#### 3.3 历史查询

```python
def query_history(drug_name, platform=None, limit=10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if platform:
        c.execute('''SELECT cr.crawl_time, cr.platform, cr.total_items, 
                            cr.min_price, cr.max_price, cr.avg_price
                     FROM crawl_records cr
                     JOIN drugs d ON cr.drug_id = d.id
                     WHERE d.name = ? AND cr.platform = ?
                     ORDER BY cr.crawl_time DESC LIMIT ?''',
                  (drug_name, platform, limit))
    else:
        c.execute('''SELECT cr.crawl_time, cr.platform, cr.total_items,
                            cr.min_price, cr.max_price, cr.avg_price
                     FROM crawl_records cr
                     JOIN drugs d ON cr.drug_id = d.id
                     WHERE d.name = ?
                     ORDER BY cr.crawl_time DESC LIMIT ?''',
                  (drug_name, limit))
    
    results = c.fetchall()
    conn.close()
    return results

# 查询示例：query_history("黛力新", platform="京东")
```

---

### 第四步：数据处理

#### 4.1 价格清洗

京东价格含换行符，需清洗：
```python
price = price.replace('¥', '').replace('\n', '').replace(' ', '')
# "¥\n50" → "50"
```

#### 4.2 去重

多页数据按 title+price 去重：
```python
seen = set()
unique = []
for p in results:
    key = p['title'][:30] + p['price']
    if key not in seen:
        seen.add(key)
        unique.append(p)
```

---

### 第五步：报告生成

生成 Markdown 报告，结构：

```markdown
# 药品电商价格监控报告

## 一、调研目标
- 药品：XXX
- 规格：XXX
- 标准价格：XXX 元
- 平台：京东、淘宝

## 二、数据概览
| 平台 | 商品数 | 价格区间 |
|------|--------|----------|
| 京东 | X | ¥X - ¥X |
| 淘宝 | X | ¥X - ¥X |

## 三、低价商品清单
| 平台 | 店铺 | 价格 | 备注 |
|------|------|------|------|

## 四、购买建议
| 场景 | 推荐 | 价格 |
|------|------|------|
```

---

## 快速开始

**抓取京东全部数据（动态翻页）：**
```
1. browser action:open url:"https://search.jd.com/Search?keyword=黛力新+0.5mg+10mg+20片"
2. 等待8秒
3. 执行提取JS → 保存第1页
4. 执行翻页JS → 返回 'clicked page X'
5. 等待6秒 → 执行提取JS → 保存第X页
6. 重复步骤4-5，直到返回 'no more pages'
7. 合并所有页数据，去重
```

**抓取淘宝数据：**
```
1. browser action:open url:"https://s.taobao.com/search?q=黛力新+0.5mg+10mg+20片"
2. 等待8秒
3. 执行提取JS → 保存
4. 执行翻页JS(2) → 等待6秒 → 执行提取JS
5. 重复直到翻页失败
6. 合并数据，去重
```

**抓取拼多多数据：**
```
1. browser action:open url:"https://mobile.yangkeduo.com/search_result.html?search_key=黛力新+0.5mg+10mg+20片"
2. 等待8秒
3. 执行提取JS → 保存数据
4. 执行滚动JS → 等待5秒
5. 检查 lastPage：
   - lastPage === false → 重复步骤3-5
   - lastPage === true → 停止
6. 合并所有数据，去重
```

---

## 重要注意事项

### 1. 翻页核心区别

| 平台 | 翻页方式 | URL变化 | 关键 |
|------|----------|---------|------|
| 京东 | 点击数字按钮 | 不变 | ❌ 不能用"下一页"文字链接 |
| 淘宝 | 点击数字按钮 | 可能被重定向 | ✅ 以页面文字为准 |
| 拼多多 | `window.scrollBy(0,800)` + DOM提取 | 不变 | ✅ 滚动完成后从 DOM 提取（`window.rawData` 不更新！） |

### 2. 等待时间
- 京东首次加载：8秒
- 京东翻页后：6秒
- 淘宝每次翻页：6秒
- 拼多多每次滚动后：3秒

### 3. 防封注意
- 每页间隔 1-2 秒随机延迟
- 避免短时间内大量请求
- 优先使用 Browser 工具（保持登录态）
- 拼多多：✅ 已验证可从 DOM 提取（`window.rawData` 在滚动后不更新，必须用 querySelectorAll + 关键词过滤）

### 4. 各平台验证时间
- 京东：✅ 已验证 2026-04-17
- 淘宝：✅ 已验证 2026-04-17
- 拼多多：✅ 已验证 2026-04-20
