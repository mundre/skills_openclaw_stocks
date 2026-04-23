# 数据爬取方法论

> 通用爬取策略：根据网站渲染类型选择对应爬取手段
> 整理时间：2026-04-23

## 核心决策树

```
目标 URL
    │
    ├─► 是否需要 JS 执行？
    │       │
    │       ├─► 静态 HTML（直接返回内容）
    │       │       └─► 方案 A：HTTP 请求 + HTML 解析
    │       │
    │       └─► 需要 JS 渲染（内容由 JS 生成）
    │               └─► 方案 B：无头浏览器爬取
    │
    └─► 如何判断？
            browser_navigate(url) → browser_snapshot() 
            如果 snapshot 有内容 → 静态，直接请求
            如果 snapshot 空/极少 → 动态，需要无头浏览器
```

---

## 方案 A：静态网站爬取

### 适用条件

- 服务器端渲染（SSR）
- HTML 响应中直接包含完整内容
- 无头浏览器 snapshot 有内容

### 工具选择

| 工具 | 适用场景 | 优点 |
|------|----------|------|
| `requests` + `BeautifulSoup` | 简单页面 | 轻量、快速 |
| `playwright` (headless) | 需要等待 | 支持等待条件 |
| `scrapy` | 大规模爬取 | 异步、性能好 |

### requests + BeautifulSoup 模式

```python
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime

def crawl_static_page(url: str, output_dir: Path, selector: str = "article") -> dict:
    """
    静态页面爬取
    - url: 目标页面
    - output_dir: 保存目录
    - selector: 内容区域 CSS 选择器
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; SkillDistiller/1.0)"
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 提取标题
    title = soup.select_one("h1")
    title_text = title.get_text(strip=True) if title else url.split("/")[-1]
    
    # 提取主要内容
    content_elem = soup.select_one(selector)
    if content_elem is None:
        content_elem = soup.body  # fallback
    
    content_text = content_elem.get_text(separator="\n", strip=True)
    
    # 保存
    slug = url.split("/")[-1].replace(".html", "")
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / f"{slug}.md"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {title_text}\n\n")
        f.write(f"> 来源：{url}\n")
        f.write(f"> 抓取时间：{datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write(content_text)
    
    return {"success": True, "filepath": str(filepath), "chars": len(content_text)}
```

### 常见选择器

| 站点类型 | 推荐选择器 |
|----------|-----------|
| 博客文章 | `article`, `.post-content`, `.entry-content` |
| 文档站 | `article`, `.doc-content`, `.content` |
| 论坛 | `.post-content`, `.message-content` |
| 新闻 | `article`, `.article-body` |
| 通用 | `main`, `.content`, `.main` |

### 编码处理

```python
# 自动检测编码
response = requests.get(url)
response.encoding = response.apparent_encoding

# 强制 UTF-8
html = response.content.decode("utf-8", errors="replace")
```

### 反爬应对

```python
# 1. 添加延迟
import time
time.sleep(1)  # 请求间隔 1 秒

# 2. 设置完整 UA
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 3. 设置 Referer
headers["Referer"] = "https://www.google.com/"

# 4. 使用 Session 保持 Cookie
session = requests.Session()
session.headers.update(headers)
```

---

## 方案 B：无头浏览器爬取

### 适用条件

- 客户端渲染（SPA）
- 内容由 JavaScript 动态生成
- 直接请求无法获取内容

### 工具选择

| 工具 | 适用场景 | 优点 |
|------|----------|------|
| `playwright` | 通用场景 | API 简洁、支持等待 |
| `puppeteer` | Node.js 环境 | Chrome 原生、性能好 |
| `selenium` | 兼容性要求高 | 支持多浏览器 |
| `mcp_browser_*` | Hermes 集成 | 可直接调用 |

### playwright 模式

```python
from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime

def crawl_dynamic_page(url: str, output_dir: Path, wait_for: str = None) -> dict:
    """
    动态页面爬取（无头浏览器）
    - url: 目标页面
    - output_dir: 保存目录
    - wait_for: 等待条件选择器（如 "article"）
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 设置视口
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        # 访问页面
        page.goto(url, wait_until="networkidle")
        
        # 等待内容加载（如需要）
        if wait_for:
            page.wait_for_selector(wait_for, timeout=10000)
        
        # 提取内容
        content = page.content()
        title = page.title()
        
        # 提取纯文本
        text = page.inner_text("body")
        
        browser.close()
    
    # 保存
    slug = url.split("/")[-1].replace(".html", "")
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / f"{slug}.md"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"> 来源：{url}\n")
        f.write(f"> 抓取时间：{datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write(text)
    
    return {"success": True, "filepath": str(filepath), "chars": len(text)}
```

### 等待策略

```python
# 等待网络空闲
page.goto(url, wait_until="networkidle")

# 等待选择器出现
page.wait_for_selector("article", timeout=10000)

# 等待函数返回 true
page.wait_for_function("document.querySelector('article')?.innerText.length > 100")

# 等待指定时间（兜底）
page.wait_for_timeout(3000)
```

### 常见问题处理

```python
# 无限滚动加载
for _ in range(5):
    page.keyboard.press("End")
    page.wait_for_timeout(1000)

# 点击加载更多
while page.query_selector("button.load-more"):
    page.click("button.load-more")
    page.wait_for_timeout(1000)

# Shadow DOM
shadow_content = page.evaluate(
    "document.querySelector('my-element').shadowRoot.innerText"
)
```

---

## 判断流程（通用）

### Step 1：试探请求

```python
import requests

def can_crawl_static(url: str) -> bool:
    """判断是否可以直接用请求获取内容"""
    try:
        resp = requests.get(url, timeout=10)
        html = resp.text
        
        # 检查内容密度
        text_ratio = len(BeautifulSoup(html, 'html.parser').get_text()) / len(html)
        
        # 静态页面文本比例通常 > 5%
        return text_ratio > 0.05
    except:
        return False
```

### Step 2：无头浏览器验证

```python
from playwright.sync_api import sync_playwright

def needs_browser(url: str) -> bool:
    """判断是否需要无头浏览器"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        
        # 检查渲染后内容
        body_text = page.inner_text("body")
        
        browser.close()
        
        # 如果内容过少，可能是动态加载
        return len(body_text) < 500
```

### Step 3：自动选择

```python
def auto_crawl(url: str, output_dir: Path) -> dict:
    """根据页面特性自动选择爬取方案"""
    
    # 先尝试静态
    if can_crawl_static(url):
        result = crawl_static_page(url, output_dir)
        if result["chars"] > 1000:
            return {"method": "static", **result}
    
    # 静态内容不足，使用无头浏览器
    return crawl_dynamic_page(url, output_dir)
```

---

## 批量爬取

### 章节清单格式

```json
// crawl_list.json
[
  {"slug": "introduction", "title": "介绍", "url": "https://example.com/docs/intro"},
  {"slug": "installation", "title": "安装", "url": "https://example.com/docs/install"},
  {"slug": "usage", "title": "使用", "url": "https://example.com/docs/usage"}
]
```

### 批量爬取脚本

```python
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def batch_crawl(list_file: Path, output_dir: Path, max_workers: int = 3):
    """批量爬取多个页面"""
    with open(list_file) as f:
        items = json.load(f)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    def crawl_item(item):
        url = item["url"]
        slug = item["slug"]
        
        try:
            # 自动选择方案
            result = auto_crawl(url, output_dir / slug)
            return {**item, **result}
        except Exception as e:
            return {**item, "error": str(e)}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(crawl_item, item): item for item in items}
        
        for future in as_completed(futures):
            result = future.result()
            status = "✓" if result.get("success") else "✗"
            print(f"{status} {result.get('slug', 'unknown')}")
```

---

## 内容验证

### 质量检查

```python
def validate_content(content: str) -> dict:
    """验证爬取内容质量"""
    checks = {
        "has_content": len(content) > 500,
        "has_headings": bool(__import__("re").search(r"^#{1,3}\s+", content, __import__("re").MULTILINE)),
        "has_code": "```" in content,
        "has_tables": "|" in content and content.count("|") >= 4,
    }
    
    score = sum(checks.values()) / len(checks)
    return {"passed": score >= 0.6, "score": score, "checks": checks}
```

### 常见问题

| 症状 | 原因 | 解决 |
|------|------|------|
| 内容为空 | JS 未执行 | 改用无头浏览器 |
| 只有导航 | 选择器错误 | 检查页面结构 |
| 内容截断 | 滚动加载未触发 | 添加滚动/等待 |
| 编码乱码 | 编码判断错误 | 指定 UTF-8 |
| 403/429 | 反爬触发 | 添加延迟/更换 UA |

---

## 源

> requests + BeautifulSoup 爬虫实践
> playwright 无头浏览器爬取经验
> 爬取策略判断流程
