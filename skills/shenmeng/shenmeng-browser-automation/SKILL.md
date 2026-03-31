---
name: browser-automation
description: 浏览器自动化操作与网页交互技能。用于自动填写表单、抓取网页数据、执行网页测试、模拟用户操作、批量处理网页任务。支持Playwright、Selenium等主流自动化框架。当用户需要自动化浏览器操作、网页数据抓取、表单自动填写、网页测试时使用。
---

# Browser Automation 浏览器自动化

> 💰 **本 Skill 已接入 SkillPay 付费系统**
> - 每次调用费用：**0.01 USDT**
> - 支付方式：BNB Chain USDT
> - 请先确保账户有足够余额

使用Playwright和Selenium进行浏览器自动化操作，支持网页数据抓取、表单填写、自动化测试等功能。

## 核心能力

1. **网页数据抓取** - 自动提取网页内容、表格、图片
2. **表单自动填写** - 自动输入、选择、提交表单
3. **自动化测试** - 网页功能测试、回归测试
4. **批量任务处理** - 批量操作多个网页
5. **截图与PDF生成** - 网页截图、生成PDF报告

## 适用场景

| 场景 | 示例 |
|------|------|
| **数据采集** | 抓取商品价格、新闻内容、社交媒体数据 |
| **自动表单** | 自动填写调查问卷、注册表单、申请表格 |
| **网页测试** | 自动化功能测试、UI测试、性能测试 |
| **批量操作** | 批量下载文件、批量提交任务、批量查询 |
| **内容监控** | 监控网页变化、价格变动、内容更新 |

## 技术栈

### 主要工具
- **Playwright** - 微软开源，现代浏览器自动化（推荐）
- **Selenium** - 经典选择，社区支持广泛
- **BeautifulSoup** - HTML解析，配合requests使用
- **Scrapy** - 大规模数据抓取框架

### 浏览器支持
- Chromium/Chrome
- Firefox
- WebKit (Safari)
- Edge

## 工具清单

- `web_scraper.py` - 网页数据抓取器
- `form_filler.py` - 表单自动填写
- `batch_processor.py` - 批量网页处理器
- `page_monitor.py` - 网页内容监控
- `screenshot_tool.py` - 网页截图工具

## 参考资料

- **Playwright指南**：`references/playwright-guide.md`
- **反爬虫策略**：`references/anti-detection.md`
- **最佳实践**：`references/best-practices.md`
- **常见问题**：`references/troubleshooting.md`

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install
```

### 2. 抓取网页数据
```bash
python scripts/web_scraper.py --url https://example.com --selector ".product-title" --output data.json
```

### 3. 自动填写表单
```bash
python scripts/form_filler.py --url https://example.com/form --config form_config.json
```

### 4. 批量处理
```bash
python scripts/batch_processor.py --urls urls.txt --script custom_script.py
```

## 使用示例

### 示例1：抓取电商产品价格

**用户**："帮我抓取京东上iPhone的价格"

**执行**：
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://search.jd.com/Search?keyword=iPhone")
    
    # 等待页面加载
    page.wait_for_selector(".gl-item")
    
    # 提取数据
    products = page.query_selector_all(".gl-item")
    data = []
    for product in products[:10]:
        title = product.query_selector(".p-name a").inner_text()
        price = product.query_selector(".p-price strong").inner_text()
        data.append({"title": title, "price": price})
    
    browser.close()
```

### 示例2：自动填写表单

**用户**："帮我自动填写这个注册表单"

**配置** (`form_config.json`):
```json
{
  "url": "https://example.com/register",
  "fields": [
    {"selector": "#username", "value": "myusername"},
    {"selector": "#email", "value": "myemail@example.com"},
    {"selector": "#password", "value": "mypassword123"},
    {"selector": "#confirm", "value": "mypassword123"},
    {"selector": "#agree", "action": "check"}
  ],
  "submit": "#submit-btn"
}
```

### 示例3：监控网页变化

**用户**："监控这个商品页面，价格低于1000时通知我"

```python
python scripts/page_monitor.py --url https://example.com/product --selector ".price" --condition "<1000" --interval 3600
```

## 安全与合规

### ⚠️ 重要提醒

1. **遵守Robots协议**
   - 检查网站的robots.txt
   - 遵守爬取频率限制
   - 尊重网站的反爬虫规则

2. **法律合规**
   - 不要抓取个人隐私数据
   - 不要破解付费内容
   - 遵守当地数据保护法律

3. **道德准则**
   - 不要对目标网站造成过大负载
   - 设置合理的请求间隔
   - 不要用于恶意竞争

### 反检测策略

- 使用随机User-Agent
- 模拟真实鼠标移动
- 添加随机延迟
- 使用代理IP轮换
- 处理验证码（必要时人工介入）

## 常见问题

**Q: 被网站封IP怎么办？**
A: 使用代理池，降低请求频率，模拟更真实的行为

**Q: 遇到验证码怎么办？**
A: 使用验证码识别服务，或降低频率避免触发

**Q: 动态加载的内容抓不到？**
A: 使用Playwright等待元素加载，或使用API接口

**Q: 需要登录的页面怎么抓？**
A: 先模拟登录保存cookie，或使用已登录的session

---

*自动化工具应当用于提高效率，而非违反规则。请合法合规使用。*
