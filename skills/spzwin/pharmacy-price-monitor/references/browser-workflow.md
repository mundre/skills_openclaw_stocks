# OpenClaw Browser 工具使用指南

## 工具概览

OpenClaw `browser` 工具提供真实 Chromium 浏览器控制能力，支持：
- 页面导航与加载
- 快照与页面结构提取
- 元素交互（点击、输入、滚动）
- 处理动态 JavaScript 内容
- 登录与 session 保留

---

## 基础操作

### 1. 启动浏览器

```bash
# 默认配置启动
browser action:start

# 指定 profile（user 为用户浏览器，需浏览器已运行）
browser action:start profile:user
```

### 2. 打开页面

```bash
# 打开 URL
browser action:open url:"https://search.jd.com/Search?keyword=阿莫西林"
```

### 3. 获取页面快照

```bash
# 使用 role 标签（默认）
browser action:snapshot

# 使用 ARIA 标签（推荐，更稳定）
browser action:snapshot refs:aria
```

**快照返回内容：**
- 页面标题
- URL
- 页面元素列表（带 role、name、selector 等）
- 可交互元素

### 4. 元素交互

```bash
# 点击元素
browser action:act ref:<element_ref> kind:click

# 输入文本
browser action:act ref:<element_ref> kind:type text:"阿莫西林胶囊"

# 滚动页面
browser action:act kind:press key:PageDown
```

---

## 京东商品抓取流程

### 步骤 1：打开搜索页面

```bash
browser action:open url:"https://search.jd.com/Search?keyword=阿莫西林胶囊 0.25g*24粒"
```

### 步骤 2：等待页面加载

```bash
# 等待几秒确保 JavaScript 执行完成
# 或使用 action:act kind:wait timeMs:3000

browser action:snapshot refs:aria
```

### 步骤 3：定位商品列表

从 snapshot 中查找：
- `role="list"` 或 `role="listitem"` 元素
- 包含商品卡片的容器

**典型 ARIA 结构：**
```json
{
  "role": "listitem",
  "name": "阿莫西林胶囊 0.25g*24粒",
  "elements": [
    {
      "role": "text",
      "name": "¥28.50"
    },
    {
      "role": "link",
      "name": "某某大药房旗舰店",
      "selector": ".shop-name"
    },
    {
      "role": "link",
      "name": "查看详情",
      "url": "https://item.jd.com/12345678.html"
    }
  ]
}
```

### 步骤 4：提取商品数据

**提取字段：**
- 商品标题：`name` 属性
- 店铺名称：店铺链接的 `name` 属性
- 价格：价格文本元素（去掉 "¥" 符号）
- 商品链接：`url` 属性

**代码示例（Python 解析）：**
```python
import json

# 假设 snapshot_data 是 browser action:snapshot 返回的 JSON
data = json.loads(snapshot_data)

# 遍历商品列表
for item in data['elements']:
    if item.get('role') == 'listitem':
        # 提取商品信息
        title = item.get('name', '')

        # 提取价格
        price = None
        for elem in item.get('elements', []):
            if '¥' in elem.get('name', ''):
                price = float(elem['name'].replace('¥', ''))
                break

        # 提取店铺
        shop = None
        for elem in item.get('elements', []):
            if elem.get('role') == 'link' and '店' in elem.get('name', ''):
                shop = elem['name']
                break

        # 提取链接
        url = None
        for elem in item.get('elements', []):
            if elem.get('role') == 'link' and 'item.jd.com' in elem.get('url', ''):
                url = elem['url']
                break

        if title and price:
            products.append({
                'title': title,
                'price': price,
                'shop': shop,
                'url': url,
                'platform': '京东'
            })
```

### 步骤 5：翻页（必须执行，确保数据完整）

京东翻页机制：底部有 "上一页 | 1 2 3 4 5 ... 下一页 | 输入框+跳转"

```bash
# 循环翻页，抓取全部数据
while True:
    # 抓取当前页数据
    browser action:snapshot refs:aria
    extract_products()
    
    # 检查是否最后一页
    total_pages = extract_total_pages()  # 从"共100页"中提取
    if current_page >= total_pages:
        break
    
    # 点击"下一页"（使用selector，最稳定）
    browser action:act selector:".pn-next a" kind:click
    browser action:act kind:wait timeMs:3000
    current_page += 1
```

**翻页选择器参考：**
- 下一页：`.pn-next a`
- 上一页：`.pn-prev`
- 页码数字：`.pn-num a`
- 输入框：`.p-skip input`
- 跳转按钮：`.p-skip button`

---

## 淘宝商品抓取流程

### 步骤 1：打开搜索页面

```bash
browser action:open url:"https://s.taobao.com/search?q=阿莫西林胶囊 0.25g*24粒"
```

### 步骤 2：处理登录（如需要）

淘宝可能需要登录，遇到登录提示时：
- 用户手动登录
- 重新 snapshot 获取登录后的页面

```bash
# 登录后重新快照
browser action:snapshot refs:aria
```

### 步骤 3：提取商品数据

淘宝的 ARIA 结构与京东类似，提取字段相同：
- 商品标题
- 店铺名称
- 价格
- 商品链接

### 步骤 4：翻页（必须执行，确保数据完整）

淘宝翻页机制：底部有 "上一页 | 下一页 | 1/100" 格式

```bash
# 循环翻页，抓取全部数据
while True:
    # 抓取当前页数据
    browser action:snapshot refs:aria
    extract_products()
    
    # 检查"下一页"按钮是否禁用（最后一页时禁用）
    browser action:snapshot refs:aria
    if is_next_button_disabled(snapshot):
        break
    
    # 点击"下一页"（使用selector）
    browser action:act selector:".next" kind:click
    browser action:act kind:wait timeMs:3000
    current_page += 1
```

**翻页选择器参考：**
- 下一页：`.next`
- 上一页：`.prev`
- 页码显示：`.page-num`（格式：1/100）

**检测最后一页：**
- 方法1：检查 `.next` 元素是否包含 `disabled` 类
- 方法2：从页码显示提取当前页和总页数，判断是否到达最后一页

---

## 拼多多商品抓取流程

### 步骤 1：打开搜索页面

```bash
browser action:open url:"https://mobile.yangkeduo.com/search_result.html?search_key=阿莫西林胶囊"
```

### 步骤 2：提取商品数据

拼多多的 ARIA结构可能不同，需要通过 snapshot 实际分析后调整提取逻辑。

---

## 常见问题处理

### 1. 验证码处理

遇到滑块验证码时：
- 用户手动完成验证
- 重新 snapshot 获取验证后的页面

```bash
browser action:snapshot refs:aria
```

### 2. 页面加载慢

```bash
# 使用 wait 等待特定元素出现
browser action:act kind:wait textGone:"加载中"
```

### 3. 动态加载内容

```bash
# 滚动到底部触发加载
browser action:act kind:press key:End

# 等待内容加载
browser action:act kind:wait timeMs:2000
browser action:snapshot refs:aria
```

### 4. 封控处理

如遇到封控：
- 等待 5-10 分钟后重试
- 切换 IP（如有条件）
- 使用账号登录后再抓取

---

## 最佳实践

1. **使用 ARIA 标签**：`refs:aria` 更稳定，推荐使用
2. **等待页面加载**：重要页面加载完成后再 snapshot
3. **错误重试**：网络问题或加载失败时重试 1-2 次
4. **避免高频请求**：每个平台间隔 30-60 秒，防止封控
5. **保存 session**：如需登录，使用 `profile:user` 保留 cookies

---

## 完整工作流示例

```bash
# 1. 启动浏览器
browser action:start

# 2. 打开京东搜索页
browser action:open url:"https://search.jd.com/Search?keyword=阿莫西林"

# 3. 等待加载
browser action:snapshot refs:aria

# 4. 提取数据（解析 snapshot 返回的 JSON）
# [Python 脚本处理]

# 5. 翻页（如需要）
browser action:act ref:<下一页> kind:click
browser action:snapshot refs:aria

# 6. 切换平台，重复步骤 2-5
browser action:open url:"https://s.taobao.com/search?q=阿莫西林"
browser action:snapshot refs:aria

# 7. 关闭浏览器
browser action:stop
```
