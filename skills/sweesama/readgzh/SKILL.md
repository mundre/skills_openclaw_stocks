# ReadGZH — 微信公众号文章 AI 阅读器

ReadGZH 是一款专为 AI 智能体设计的微信公众号内容解析工具。它通过服务端代理绕过微信的反爬虫机制，将复杂的公众号 HTML 转换为纯净、结构化的 Markdown 内容，大幅节省 Token 消耗。

## 核心特性

- **99.89% 穿透率**：自研 7 阶段提取管线，完美绕过客户端指纹检测与反爬拦截
- **50-87% Token 节省**：自动剥离内联样式、冗余标签及广告干扰，输出极简 Markdown
- **CDN 永久代理**：将图片路由至持久化 CDN，解决微信图片 2 小时过期的硬伤
- **全球共享缓存**：转换过的文章永久入库，后续任何用户或 Agent 读取均完全免费
- **零安装依赖**：纯云端 API 模式，无需本地微信客户端或浏览器环境
- **原生支持 MCP**：内置 Model Context Protocol，支持 AI Agent 协议化直接调用

## 如何使用

直接对你的 AI 助手下令：

> **"帮我读一下这篇文章：[微信公众号链接]"**

## MCP 调用格式

```json
POST https://api.readgzh.site/mcp-server
Authorization: Bearer <API_KEY>
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "readgzh.read",
    "arguments": { "url": "https://mp.weixin.qq.com/s/xxxx" }
  }
}
```

## API 端点

| 方式 | 端点 | 说明 |
|------|------|------|
| MCP（推荐） | `POST https://api.readgzh.site/mcp-server` | JSON-RPC 2.0，返回完整 Markdown |
| OpenAPI REST | `GET https://api.readgzh.site/rd?url=...&format=text` | 缓存文章可用，新文章返回 HTML |

## 可用 MCP Tools

- `readgzh.read` — 读取微信文章（URL）
- `readgzh.get` — 读取缓存文章（slug）
- `readgzh.search` — 搜索缓存文章
- `readgzh.list` — 列出最近缓存文章

## Credits 说明

- 简单文章（< 5 图）：1 credit
- 复杂文章（≥ 5 图）：2 credits
- 缓存文章读取：免费
- 免费额度：50 credits/天

## 开发者信息

- **API 文档**：[readgzh.site/docs](https://readgzh.site/docs)
- **免费 Key 领取**：[readgzh.site/dashboard](https://readgzh.site/dashboard)
- **技术支持**：[readgzh.site](https://readgzh.site)
- **开发维护**：Sweesama（[@sweesama](https://github.com/sweesama)）
