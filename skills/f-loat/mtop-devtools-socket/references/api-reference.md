# API 参数参考

## set_mock 参数说明

用于动态设置 API 接口的 Mock 数据，支持两种方式：
- **方式一（mockData）**：直接传入完整的 Mock 响应数据，完全替换真实接口返回
- **方式二（fields）**：基于真实响应修改指定字段，适合微调场景

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `apiName` | string | ✅ | API 名称或正则表达式。例如 `"mtop.cart.query"` 精确匹配，`".*\\.cart\\..*"` 匹配所有购物车接口 |
| `mockData` | object | — | **【方式一】** 完整的 Mock 响应数据（JSON 对象）。传入后该接口将完全返回此数据，不再请求真实服务端。与 `fields` 二选一，同时提供时优先使用 `fields` |
| `fields` | array | — | **【方式二】** 基于真实响应修改指定字段。数组元素包含 `path`（字段路径）和 `value`（新值）。会先获取原始响应，然后只修改指定字段 |
| `enabled` | boolean | — | 是否启用 Mock。`true`（默认）：启用 Mock；`false`：禁用 Mock 恢复真实数据 |
| `delay` | number | — | 模拟响应延迟（毫秒），用于测试加载状态、超时等场景 |

### fields 数组元素结构

| 属性 | 类型 | 说明 |
|------|------|------|
| `path` | string | 字段路径，支持点号和数组索引。例如 `"data.result.list"`、`"data.items[0].name"` |
| `value` | any | 要设置的值，可以是任意类型（字符串、数字、布尔、对象、数组等） |

### 使用示例

**方式一：完整 Mock 数据**
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
  }
}
```

**方式二：基于真实响应修改字段**
```json
{
  "apiName": "mtop.cart.query",
  "fields": [
    {"path": "data.result.total", "value": 150},
    {"path": "data.result.items[0].name", "value": "测试商品"}
  ]
}
```

**禁用 Mock**
```json
{
  "apiName": "mtop.cart.query",
  "enabled": false
}
```

### 注意事项

1. **mockData 和 fields 二选一**：如果同时提供，`fields` 优先级更高
2. **大 JSON 支持**：当 `mockData` 很大时，建议使用 `--payload-file` 参数从文件读取
3. **Chrome Native Messaging 限制**：单条消息最大 1MB，超过会失败

---

## send_mtop_request 参数说明

在当前浏览器页面上下文中发起 mtop API 请求，自动处理签名计算、token 提取等。需要当前页面已登录（有对应的 Cookie）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `api` | string | ✅ | mtop API 名称，例如 `"mtop.trade.order.detail"`。以 `"mopen."` 开头的会使用 mopen 签名算法 |
| `data` | object | — | 请求数据（JSON 对象），即 mtop 请求中的 data 参数。例如 `{"itemId": "12345"}` |
| `version` | string | — | API 版本号，默认 `"1.0"` |
| `method` | string | — | HTTP 方法，`"GET"`（默认）或 `"POST"`。POST 时 data 参数放在请求体中 |
| `appKey` | string | — | appKey，默认 `"12574478"` |
| `env` | string | — | 请求环境：`"online"`（默认，线上）/ `"pre"`（预发）。不同环境对应不同的 mtop 网关域名 |
| `timeout` | number | — | 请求超时时间（毫秒），默认 10000 |

### 环境与域名映射

| `env` 值 | 网关域名 |
|---|---|
| `online`（默认） | `h5api.m.taobao.com` |
| `pre` | `h5api.wapa.taobao.com` |

### 签名算法

- **mtop 接口**：`md5(token & timestamp & appKey & data)`，token 从 `_m_h5_tk` Cookie 中提取
- **mopen 接口**（api 以 `mopen.` 开头）：`md5(api & v & timestamp & appKey & token & md5(data))`，token 从 `m_tk` 或 `_tb_token_` Cookie 中提取

### 使用示例

```json
{
  "api": "mtop.trade.order.detail",
  "data": {"orderId": "12345"},
  "version": "1.0",
  "method": "GET"
}
```

**响应结构**：
```json
{
  "success": true,
  "response": {
    "api": "mtop.trade.order.detail",
    "data": { "...": "..." },
    "ret": ["SUCCESS::调用成功"],
    "v": "1.0"
  },
  "requestData": {"orderId": "12345"}
}
```

### 注意事项

1. **需要登录态**：浏览器中需要有对应域名的 Cookie，包含 `_m_h5_tk`（mtop）或 `m_tk`/`_tb_token_`（mopen）
2. **DNR 方式执行**：与 `proxy_request` 一样，通过 Chrome DNR 规则注入 Cookie 后在 background 中直接 fetch，不依赖页面上下文
3. **与 proxy_request 的区别**：`proxy_request` 是通用 HTTP 代理；`send_mtop_request` 专门用于 mtop 协议，自动处理签名

---

## proxy_request 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | string | ✅ | 完整的目标 URL（含 http/https） |
| `method` | string | — | HTTP 方法，默认 `GET`，支持 GET/POST/PUT/DELETE/PATCH/HEAD |
| `headers` | object | — | 自定义请求头（键值对） |
| `params` | object | — | URL 查询参数，自动拼接到 URL |
| `body` | any | — | 请求体。传对象时自动 JSON 序列化并设置 Content-Type: application/json |
| `withCookies` | boolean | — | 是否自动附加浏览器 Cookie，默认 `true` |
| `cookieDomain` | string | — | 指定读取 Cookie 的域名，不填时自动从 url 中提取 |
| `responseType` | string | — | 响应格式：`auto`（默认，自动检测）/`json`/`text`。`auto` 时若 Content-Type 为图片/音视频/PDF/压缩包等二进制类型，body 以 base64 字符串返回，`bodyType` 为 `"base64"` |
| `timeout` | number | — | 超时毫秒数，默认 30000 |

**响应结构**：
```json
{
  "status": 200,
  "statusText": "OK",
  "headers": { "content-type": "application/json" },
  "body": { "data": "..." },
  "bodyType": "json",
  "attachedCookieCount": 12
}
```

- `bodyType`：`"json"` | `"text"` | `"base64"`
- **二进制响应（图片/PDF/压缩包等）**：`bodyType` 为 `"base64"`，`body` 为 base64 编码字符串。如需保存文件，可将其 decode 后写入磁盘。

---

## get_requests `source` 参数说明

| `source` 值 | 说明 |
|---|---|
| 不传 | 使用 panel 当前模式（推荐默认用法） |
| `"mtop"` | 强制只返回 mtop 接口 |
| `"requests"` | 强制只返回普通 xhr/fetch 请求（非 mtop） |

---

## get_events 参数说明

用于查询面板"埋点验证"（RUM/aplus）模块缓存的上报事件。**需要先在 DevTools 中切换到埋点验证视图以启用采集。**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `source` | string | — | 数据来源：`"rum"`（阿里云 RUM）/ `"aplus"`（aplus 埋点）/ `"all"`（默认） |
| `event_type` | string | — | 按事件类型过滤，支持正则，如 `"CLK"` `"PV"` `"resource"` |
| `filter` | string | — | 按 `name` 或 `url` 字段过滤，支持正则 |
| `since` | number | — | 只返回最近 N 秒内的事件 |
| `limit` | number | — | 返回条数，默认 20 |

**响应结构**：
```json
{
  "meta": { "count": 5, "totalMatched": 12, "totalInBuffer": 80, "source": "all" },
  "events": [
    {
      "id": "aplus-1-1700000000000",
      "source": "aplus",
      "event_type": "CLK",
      "name": "181.xxx.c.d",
      "url": "https://...",
      "timestamp": 1700000000000,
      "batchTimestampMs": 1700000000000,
      "validation": { "level": "success", "issues": [], "checks": ["..."] },
      "_raw": { "gmkey": "CLK", "gokey_params": {} },
      "_context": { "view": { "spm-url": "..." } }
    }
  ]
}
```

---

## get_selected_element 参数说明

用于读取 DevTools Elements 面板当前选中元素的信息，可选返回节点截图。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `includeOuterHTML` | boolean | — | 是否返回 `outerHTML`（最多 3000 字符），默认 `true` |
| `includeScreenshot` | boolean | — | 是否附带选中元素截图，默认 `false`。开启后会自动滚动到元素并按元素范围裁剪 |

**响应结构（不带截图）**：
```json
{
  "tagName": "div",
  "selector": "body > div.app > main.content",
  "xpath": "/html/body/div/main",
  "rect": { "x": 120, "y": 240, "width": 320, "height": 80 },
  "computedStyle": { "display": "block", "position": "relative" },
  "attributes": { "class": "content" }
}
```

**响应结构（带截图）**：
```json
{
  "tagName": "div",
  "selector": "body > div.app > main.content",
  "rect": { "x": 120, "y": 240, "width": 320, "height": 80 },
  "screenshot": {
    "meta": {
      "format": "png",
      "width": 336,
      "height": 96,
      "size": 18244,
      "url": "https://example.com/page",
      "title": "Example"
    },
    "data": "iVBORw0KGgoAAAANSUhEUgAA..."
  }
}
```

## page_snapshot 参数说明

用于获取当前页面的无障碍树快照，感知页面结构以决定下一步操作。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tabId` | number | — | 目标标签页 ID，不填时使用当前激活标签页 |
| `depth` | number | — | 树深度，默认 15，复杂页面可调大 |

**响应结构**：
```json
{
  "url": "https://example.com",
  "title": "Example Page",
  "snapshot": "@e1 [WebArea \"Example Page\"]\n  @e2 [navigation]\n    @e3 [link \"Home\"]\n    @e4 [link \"About\"]\n  @e5 [heading \"Welcome\"] (level=1)\n  @e6 [textbox \"Search\"] (focused)\n  @e7 [button \"Submit\"]",
  "elementCount": 7
}
```

**@ref 机制**：snapshot 输出中每个元素会带有 `@ref`（如 `@e1`、`@e2`），可以直接用于 `page_click` 和 `page_type` 的 `selector` 参数。

---

## page_click 参数说明

用于点击页面元素，支持 JS 点击和 CDP 真实鼠标点击。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tabId` | number | — | 目标标签页 ID，不填时使用当前激活标签页 |
| `selector` | string | ✅ | 元素选择器，支持 CSS 选择器或 `@ref` 格式（从 page_snapshot 获取） |
| `clickType` | string | — | 点击方式：`js`（默认，快速）/`cdp`（真实鼠标点击，可触发文件对话框等需要用户手势的操作） |

---

## page_type 参数说明

用于向输入框填写文本。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tabId` | number | — | 目标标签页 ID，不填时使用当前激活标签页 |
| `selector` | string | ✅ | 元素选择器，支持 CSS 选择器或 `@ref` 格式（从 page_snapshot 获取） |
| `text` | string | ✅ | 要填写的文本 |
| `clearFirst` | boolean | — | 是否先清空原有内容，默认 `true`。设为 `false` 时追加文本 |

---

## page_press 参数说明

用于在页面中按下键盘按键。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tabId` | number | — | 目标标签页 ID，不填时使用当前激活标签页 |
| `key` | string | ✅ | 按键名称，支持 Enter/Tab/Escape/Backspace/Delete/ArrowUp/ArrowDown/ArrowLeft/ArrowRight/Home/End/PageUp/PageDown/Space |
| `modifiers` | string[] | — | 修饰键数组，支持 ctrl/alt/shift/meta/cmd |

---

## page_wait 参数说明

用于等待指定时间或等待某个元素出现。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tabId` | number | — | 目标标签页 ID，不填时使用当前激活标签页 |
| `time` | number | — | 等待毫秒数，与 `selector` 二选一 |
| `selector` | string | — | CSS 选择器，等待元素出现，与 `time` 二选一 |
| `timeout` | number | — | 等待超时时间（毫秒），默认 10000 |

---

## page_navigate 参数说明

用于在当前标签页内导航到新 URL。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tabId` | number | — | 目标标签页 ID，不填时使用当前激活标签页 |
| `url` | string | ✅ | 要导航到的 URL |

---

## page_upload 参数说明

用于向页面上的 `<input type="file">` 元素上传文件。通过 CDP `DOM.setFileInputFiles` 实现。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tabId` | number | — | 目标标签页 ID，不填时使用当前激活标签页 |
| `selector` | string | ✅ | 元素选择器，支持 CSS 选择器或 `@ref` 格式（从 page_snapshot 获取），必须指向 `<input type="file">` 元素 |
| `filePaths` | string[] | ✅ | 本地文件路径数组，如 `["/Users/me/photo.jpg"]`。支持多文件上传 |