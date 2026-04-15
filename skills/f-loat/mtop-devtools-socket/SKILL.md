---
name: mtop-devtools-socket
description: '通过本地 socket 调用 Mtop DevTools 浏览器插件能力（获取请求/日志/埋点、设置 mock、获取 API schema、代理 HTTP 请求、浏览器操作与页面感知）'
argument-hint: '<action> [--payload <json> | --payload-file <path>]'
---

# Mtop DevTools Socket 技能

## 📦 前置条件

使用本技能前，需要先安装 [Mtop DevTools 浏览器插件](https://mtop-devtools.io.alibaba-inc.com/)。安装完成后，打开 Chrome DevTools 应能看到 `Mtop Viewer` 标签页。

> 如果连接失败，CLI 会自动提示插件安装地址，无需记忆。

## 🚀 快速开始

### 第 1 步：安装依赖（仅首次）

首次使用前，安装 Native Messaging Host 和 CLI 工具：

```bash
npm install -g @mtop-devtools/native-host @mtop-devtools/client
```

> 安装 `@mtop-devtools/native-host` 时会自动完成 Native Messaging 初始化。如需手动初始化或指定自定义扩展 ID，运行 `mtop-devtools-native-host initialize [--extension-id <id>]`。

### 第 2 步：连接并使用

安装完成后即可直接调用。如果连接失败，可打开 DevTools 切换到 Mtop Viewer 面板手动触发建联：

```bash
mtop-devtools get_requests --payload '{"count": 5}'
mtop-devtools get_logs --payload '{"limit": 10}'
```

## 🎯 意图识别与支持的操作

根据用户的描述，选择对应的操作和参数：

### API 调试

| 用户说的话（示例） | 操作 | 说明 |
|---|---|---|
| 获取最近的请求、看下刚才发了什么 | `get_requests` | 获取请求，默认返回 panel 当前模式（mtop 或普通请求） |
| 获取 mtop 接口请求 | `get_requests` + `source: "mtop"` | 强制获取 mtop 接口 |
| 获取普通 HTTP 请求（xhr/fetch） | `get_requests` + `source: "requests"` | 强制获取非 mtop 请求 |
| 看下控制台日志、报了什么错 | `get_logs` | 获取浏览器控制台日志 |
| 看下埋点数据、RUM 事件、aplus 上报了什么 | `get_events` | 获取 RUM/aplus 埋点事件 |
| 获取接口 schema、接口出入参是什么 | `get_api_schema` | 获取 API 接口 schema，可选择返回 schema、hsf 或全部 |

### Mock & 请求规则

| 用户说的话（示例） | 操作 | 说明 |
|---|---|---|
| mock 掉某个接口、让接口返回 xxx | `set_mock` | 设置 API mock 数据 |
| 查看当前有哪些 mock | `get_mocks` | 查看当前生效的 mock |
| 添加请求规则、重定向请求、修改请求头、拦截请求 | `add_rule` | 添加 Chrome declarativeNetRequest 规则 |

### 网络请求代理

| 用户说的话（示例） | 操作 | 说明 |
|---|---|---|
| 调用某个接口、带上 Cookie 发一个 HTTP 请求 | `proxy_request` | 代理请求，自动携带浏览器 Cookie |
| 调用某个 mtop 接口、发一个 mtop 请求 | `send_mtop_request` | 在页面上下文中发起 mtop 请求，自动处理签名和 token |

### 浏览器操作

| 用户说的话（示例） | 操作 | 说明 |
|---|---|---|
| 打开一个页面、新建标签页 | `tab_open` | 在浏览器中打开新 Tab 并等待加载完成 |
| 关闭标签页 | `tab_close` | 关闭指定 tabId 的标签页 |
| 列出所有标签页、看下打开了哪些页面 | `tab_list` | 获取当前窗口所有标签页列表 |
| 点击按钮、点击元素、点一下某个东西 | `page_click` | 点击页面元素，支持 JS 点击和 CDP 真实鼠标点击 |
| 输入文字、填写表单、在输入框里输入 | `page_type` | 向输入框填写文本，兼容 React 受控组件 |
| 滚动页面、翻到底部、往下翻 | `page_scroll` | 滚动页面，支持 up/down/top/bottom 四个方向 |
| 执行 JS、在页面上运行脚本 | `page_eval` | 在页面上下文中执行任意 JavaScript 表达式 |
| 按键、按回车、按 Tab | `page_press` | 在页面中按下键盘按键（Enter/Tab/Escape 等） |
| 等待页面加载、等元素出现 | `page_wait` | 等待指定时间或等待某个元素出现 |
| 在当前标签页导航、跳转页面 | `page_navigate` | 在当前标签页内导航到新 URL |
| 上传文件、选择文件、文件上传 | `page_upload` | 向 `<input type="file">` 元素上传本地文件 |

### 页面感知

| 用户说的话（示例） | 操作 | 说明 |
|---|---|---|
| 获取页面结构、看下页面上有什么元素、页面快照 | `page_snapshot` | 获取页面无障碍树快照，返回所有可交互元素的结构化文本 |
| 截图、获取当前页面截图、看一下页面长什么样 | `get_screenshot` | 获取当前浏览器标签页的页面截图 |
| 获取选中元素、看一下这个元素的布局/样式、分析元素 | `get_selected_element` | 获取 Elements 面板当前选中元素的详细信息 |

## 📚 参考文档

- [使用示例](./references/examples.md)（各操作的完整 CLI 调用示例）
- [API 参数详细说明](./references/api-reference.md)（set_mock / proxy_request / get_requests / get_events / get_selected_element 完整参数表及响应结构）
- [socket 故障排查](./references/troubleshooting.md)

