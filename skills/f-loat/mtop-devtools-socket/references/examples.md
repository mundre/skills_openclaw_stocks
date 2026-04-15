# 使用示例

## API 调试

```bash
# 获取最近请求（默认返回 panel 当前模式的数据）
mtop-devtools get_requests --payload '{"count": 5}'

# 强制指定获取 mtop 请求
mtop-devtools get_requests --payload '{"count": 5, "source": "mtop"}'

# 强制指定获取普通 HTTP 请求（xhr/fetch，非 mtop）
mtop-devtools get_requests --payload '{"count": 10, "source": "requests"}'

# 获取 error 日志
mtop-devtools get_logs --payload '{"level": "error", "limit": 50}'

# 获取最近 20 条 RUM/aplus 埋点事件
mtop-devtools get_events --payload '{"limit": 20}'

# 只看 aplus 埋点事件
mtop-devtools get_events --payload '{"source": "aplus", "limit": 20}'

# 按事件类型过滤（正则）
mtop-devtools get_events --payload '{"event_type": "CLK", "source": "aplus"}'

# 过滤特定 name/url（正则）
mtop-devtools get_events --payload '{"filter": "cart|order", "limit": 10}'

# 获取 API schema
mtop-devtools get_api_schema --payload '{"api": "mtop.fliggy.flyrs.render", "version": "1.0"}'

# 只获取 HSF 接口信息（服务名、方法、版本）
mtop-devtools get_api_schema --payload '{"api": "mtop.fliggy.flyrs.render", "fields": ["hsf"]}'

# 只获取请求参数 JSON Schema
mtop-devtools get_api_schema --payload '{"api": "mtop.fliggy.flyrs.render", "fields": ["schema"]}'
```

## Mock & 请求规则

```bash
# 按字段修改 API 响应（mock）
mtop-devtools set_mock --payload '{"apiName": "mtop.cart.query", "fields": [{"path": "data.total", "value": 150}], "enabled": true}'

# 查看所有 mock 配置
mtop-devtools get_mocks --payload '{}'

# 添加请求重定向规则（将 h5api.m.taobao.com 请求重定向到本地服务）
mtop-devtools add_rule --payload '{"actionType": "redirect", "filter": "^https://h5api\\.m\\.taobao\\.com/.*", "redirectUrl": "http://localhost:3000/$&", "description": "Redirect to local dev server"}'

# 添加请求头修改规则（给所有 mtop 请求添加自定义头）
mtop-devtools add_rule --payload '{"actionType": "modifyHeaders", "filter": "^https://h5api\\..*\\.taobao\\.com/", "requestHeaders": [{"header": "x-custom-token", "operation": "set", "value": "test-token-123"}]}'

# 添加请求拦截规则（阻止特定域名的请求）
mtop-devtools add_rule --payload '{"actionType": "block", "filter": "^https://ads\\.example\\.com/.*", "description": "Block ads"}'
```

## 网络请求代理

```bash
# 代理 GET 请求，自动携带 Cookie
mtop-devtools proxy_request --payload '{"url": "https://api.example.com/data", "method": "GET"}'

# 代理 POST 请求，自动携带 Cookie，发送 JSON body
mtop-devtools proxy_request --payload '{"url": "https://api.example.com/submit", "method": "POST", "body": {"key": "value"}, "withCookies": true}'

# 代理请求，指定自定义请求头
mtop-devtools proxy_request --payload '{"url": "https://api.example.com/data", "headers": {"X-Custom-Token": "abc123"}, "params": {"page": "1", "size": "20"}}'

# 发起 mtop GET 请求（自动签名、自动携带 token）
mtop-devtools send_mtop_request --payload '{"api": "mtop.trade.order.detail", "data": {"orderId": "12345"}}'

# 发起 mtop POST 请求，指定版本号
mtop-devtools send_mtop_request --payload '{"api": "mtop.trade.order.create", "data": {"itemId": "67890", "quantity": 1}, "method": "POST", "version": "2.0"}'

# 发起 mopen 请求（api 以 mopen. 开头，自动使用 mopen 签名算法）
mtop-devtools send_mtop_request --payload '{"api": "mopen.trade.order.query", "data": {"status": "paid"}}'

# 发起预发环境的 mtop 请求（h5api.wapa.taobao.com）
mtop-devtools send_mtop_request --payload '{"api": "mtop.trade.order.detail", "data": {"orderId": "12345"}, "env": "pre"}'
```

## 浏览器操作

```bash
# 打开新标签页（后台打开，等待加载完成后返回 tabId）
mtop-devtools tab_open --payload '{"url": "https://example.com"}'

# 打开新标签页并激活（前台显示）
mtop-devtools tab_open --payload '{"url": "https://example.com", "active": true}'

# 列出当前窗口所有标签页
mtop-devtools tab_list --payload '{}'

# 关闭指定标签页
mtop-devtools tab_close --payload '{"tabId": 12345}'

# JS 点击元素（默认方式，快速）
mtop-devtools page_click --payload '{"selector": "button.submit"}'

# CDP 真实鼠标点击（可触发文件对话框等需要用户手势的操作）
mtop-devtools page_click --payload '{"selector": ".upload-btn", "clickType": "cdp"}'

# 在指定 Tab 上点击元素
mtop-devtools page_click --payload '{"tabId": 12345, "selector": "#login-btn"}'

# 向输入框填写文本（自动清空原有内容）
mtop-devtools page_type --payload '{"selector": "input[name=username]", "text": "test_user"}'

# 向输入框追加文本（不清空原有内容）
mtop-devtools page_type --payload '{"selector": "textarea.comment", "text": "追加内容", "clearFirst": false}'

# 滚动到页面底部
mtop-devtools page_scroll --payload '{"direction": "bottom"}'

# 向下滚动 800px
mtop-devtools page_scroll --payload '{"direction": "down", "distance": 800}'

# 滚动到页面顶部
mtop-devtools page_scroll --payload '{"direction": "top"}'

# 在页面上下文中执行 JavaScript
mtop-devtools page_eval --payload '{"expression": "document.title"}'

# 在指定 Tab 上执行 JavaScript
mtop-devtools page_eval --payload '{"tabId": 12345, "expression": "document.querySelectorAll(\"a\").length"}'

# 按 Enter 键
mtop-devtools page_press --payload '{"key": "Enter"}'

# 按 Ctrl+Space
mtop-devtools page_press --payload '{"key": "Space", "modifiers": ["ctrl"]}'

# 等待 2 秒
mtop-devtools page_wait --payload '{"time": 2000}'

# 等待元素出现
mtop-devtools page_wait --payload '{"selector": ".result-list", "timeout": 5000}'

# 在当前标签页导航
mtop-devtools page_navigate --payload '{"url": "https://example.com"}'

# 上传单个文件
mtop-devtools page_upload --payload '{"selector": "input[type=file]", "filePaths": ["/Users/me/photo.jpg"]}'

# 上传多个文件
mtop-devtools page_upload --payload '{"selector": "#file-input", "filePaths": ["/tmp/a.png", "/tmp/b.pdf"]}'

# 使用 @ref 引用上传（从 page_snapshot 获取）
mtop-devtools page_upload --payload '{"selector": "@e5", "filePaths": ["/Users/me/doc.pdf"]}'
```

## 页面感知

```bash
# 获取当前页面的无障碍树快照（感知页面结构，决定下一步操作）
mtop-devtools page_snapshot --payload '{}'

# 获取指定 Tab 的页面快照
mtop-devtools page_snapshot --payload '{"tabId": 12345}'

# 控制树深度（默认 15，复杂页面可调大）
mtop-devtools page_snapshot --payload '{"depth": 20}'

# 获取当前页面截图（PNG 格式）
mtop-devtools get_screenshot --payload '{"format": "png"}'

# 获取当前页面截图（JPEG 格式，质量 90）
mtop-devtools get_screenshot --payload '{"format": "jpeg", "quality": 90}'

# 保存截图到文件（推荐方式，无需手动处理 base64）
mtop-devtools get_screenshot --output ./screenshot.png

# 保存 JPEG 截图到文件
mtop-devtools get_screenshot --payload '{"format": "jpeg", "quality": 80}' --output ./screenshot.jpg

# 获取 Elements 面板当前选中元素的详细信息（含布局、样式、属性）
mtop-devtools get_selected_element --payload '{}'

# 不含 outerHTML（减少数据量，适合只看布局和样式）
mtop-devtools get_selected_element --payload '{"includeOuterHTML": false}'

# 获取选中元素信息 + 节点截图（自动滚动并按元素裁剪）
mtop-devtools get_selected_element --payload '{"includeScreenshot": true}'
```

## 从文件读取参数（--payload-file）

当 JSON 参数很大（如完整的 mock 响应数据），使用 `--payload-file` 从文件读取：

```bash
# 使用文件中的 JSON 作为参数
mtop-devtools set_mock --payload-file ./mock-data.json

# 大体积 mock 数据推荐用法
mtop-devtools set_mock --payload-file /path/to/large-mock.json
```

`mock-data.json` 示例：
```json
{
  "apiName": "mtop.cart.query",
  "mockData": {
    "data": {
      "result": {
        "total": 150,
        "items": [
          {"id": 1, "name": "商品1", "price": 50}
        ]
      }
    },
    "ret": ["SUCCESS::调用成功"]
  },
  "enabled": true
}
```
