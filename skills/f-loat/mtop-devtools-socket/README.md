# Mtop DevTools Socket Skill

通过本地 Unix Socket 连接 [Mtop DevTools](https://mtop-devtools.io.alibaba-inc.com) 浏览器插件，让 AI Agent 能够直接操控浏览器、调试 API、管理 Mock 和抓取页面数据。

## 支持的能力

### 📊 数据获取

| 能力 | 说明 |
|------|------|
| **get_requests** | 获取浏览器网络请求，支持 mtop 和普通 HTTP 请求，可按数量、关键词过滤 |
| **get_logs** | 获取浏览器控制台日志，支持按级别（error / warn / info）过滤 |
| **get_events** | 获取 RUM / aplus 埋点事件，支持按来源、事件类型、关键词过滤 |
| **get_api_schema** | 获取 mtop API 的 JSON Schema 和 HSF 接口信息（服务名、方法、版本） |
| **get_screenshot** | 获取当前页面截图，支持 PNG / JPEG 格式，可指定质量和保存路径 |
| **get_selected_element** | 获取 Elements 面板当前选中元素的详细信息，包括布局、计算样式、DOM 属性，可附带节点截图 |

### 🔧 Mock & 请求规则

| 能力 | 说明 |
|------|------|
| **set_mock** | 设置 API Mock 数据，支持按字段路径精确修改响应内容，也支持整体替换 |
| **get_mocks** | 查看当前所有生效的 Mock 配置 |
| **add_rule** | 添加 Chrome declarativeNetRequest 规则，支持请求重定向、修改请求头、拦截阻断 |
| **proxy_request** | 代理 HTTP 请求，自动携带浏览器 Cookie；支持 SPA 页面渲染模式，等待 JS 渲染后提取页面内容 |

### 🌐 浏览器操作

| 能力 | 说明 |
|------|------|
| **tab_open** | 打开新标签页并等待加载完成，支持前台/后台打开 |
| **tab_close** | 关闭指定标签页 |
| **tab_list** | 列出当前窗口所有标签页（ID、URL、标题、激活状态） |
| **page_navigate** | 在当前标签页内导航到新 URL，等待加载完成后返回 |
| **page_snapshot** | 获取页面无障碍树快照，返回所有可交互元素的结构化文本和 `@ref` 引用，用于后续精确交互 |
| **page_click** | 点击页面元素，支持 CSS 选择器和 `@ref` 引用；提供 JS 点击（快速）和 CDP 真实鼠标点击（可触发文件对话框等） |
| **page_type** | 向输入框填写文本，默认先清空再输入，兼容 React 受控组件 |
| **page_press** | 按下键盘按键（Enter / Tab / Escape / Space 等），支持 Ctrl / Shift / Alt / Meta 组合键 |
| **page_scroll** | 滚动页面，支持 up / down / top / bottom 四个方向，可自定义滚动距离 |
| **page_wait** | 等待指定毫秒数，或等待某个 CSS 选择器对应的元素出现（支持超时设置） |
| **page_eval** | 在页面上下文中执行任意 JavaScript 表达式，返回执行结果 |
| **page_upload** | 向 `<input type="file">` 元素上传本地文件，支持单文件和多文件上传 |

## 全局命令

初始化时会自动注册全局命令 `mtop-devtools`，可在任意终端直接使用：

```bash
# 获取最近 5 条请求
mtop-devtools get_requests --payload '{"count": 5}'

# 获取页面截图
mtop-devtools get_screenshot --output ./screenshot.png

# 查看帮助
mtop-devtools --help
```

其他 skill 也可以直接通过 `mtop-devtools` 命令调用浏览器插件能力，无需关心脚本路径。

## 更多拓展能力

https://ali-skills.alibaba-inc.com/skills/trip/mtop-devtools
