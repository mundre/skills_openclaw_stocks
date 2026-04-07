# 🧧 WaQuanquaner — 外卖红包每小时实时挖掘助手

> 挖券券儿 — 一个轻量级 Agent Skill，每小时自动扫描美团、饿了么、京东三大外卖平台，实时挖掘最新的外卖红包和优惠活动，返回可直接复制的淘口令链接。**只推送有价值的活动，没有好活动的平台不会出现在结果中。**

## ✨ 特性

- **每小时自动刷新** — 活动数据每小时更新一次，确保优惠信息不过时
- **三大外卖平台** — 专注美团、饿了么、京东的外卖红包和优惠活动
- **智能过滤** — 只推送有淘口令的优质外卖活动，没有好活动的平台不出现
- **一键复制** — 每个活动附带淘口令(tkl)，复制后打开 App 即可领券
- **三种渲染格式** — 微信文本 / 飞书消息卡片 / 纯文本（终端）
- **自然语言触发** — "外卖红包"、"饿了么优惠"等自然语言自动触发查询
- **隐私安全** — 不包含任何 API 密钥，用户标识仅用于 CPS 归因

## 📌 使用须知

- **覆盖平台**：美团、饿了么、京东
- **推送内容**：仅外卖红包和优惠活动，不包含酒店、机票、旅游等
- **更新频率**：每小时自动扫描一次，动态更新活动信息
- **智能展示**：如果某个平台当前没有优质活动，该平台不会出现在结果中

## 📦 文件结构

```
WaQuanquaner-skill/
├── SKILL.md                # Skill 定义文件（ClawHub 发布必需）
├── index.js                # 入口文件，导出 WaQuanquaner 类
├── README.md               # 本文件
└── scripts/
    ├── config.js           # 配置（API 地址、平台映射、触发关键词）
    ├── query.js            # 查询引擎（HTTP 请求 + 数据标准化）
    ├── render.js           # 渲染引擎（微信/飞书/纯文本三种格式）
    └── triggers.js         # 触发解析器（自然语言意图识别）
```

## 🚀 快速使用

### 作为 Agent Skill 使用

将 `WaQuanquaner-skill` 目录放入你的 Agent Skills 目录，Agent 会自动识别并加载。

**触发示例：**
- "有什么外卖红包" → 查询全部平台优惠
- "饿了么有什么红包" → 仅查询饿了么
- "美团外卖优惠" → 仅查询美团
- "点外卖怎么省钱" → 查询全部平台

### 作为 Node.js 模块使用

```javascript
const { WaQuanquaner } = require('./WaQuanquaner-skill');

// 创建实例（使用默认服务器）
const wqq = new WaQuanquaner();

// 查询全部平台活动（微信格式）
const result = await wqq.query({ format: 'wechat' });
console.log(result.text);

// 查询指定平台
const elemeResult = await wqq.query({ platform: 'eleme', format: 'wechat' });

// 一站式：解析自然语言 → 查询 → 渲染
const handled = await wqq.handleInput('饿了么有什么红包');
if (handled.handled) {
  console.log(handled.text);
}
```

### 自定义服务器地址

```javascript
const wqq = new WaQuanquaner({
  serverUrl: 'https://your-server.com',
  lobsterId: 'your-custom-lobster-id',
  defaultFormat: 'feishu',
});
```

## 📤 输出格式预览

### 微信文本（默认）

```
🧧 外卖红包速报 (4月2日)

🟡 美团 (3个)
━━━━━━━━━━
1. [红包] 美团闪购CPS推广活动
   美团商超专享活动红包天天领
   📋 复制：1 %复制信息#% 打开团App http:/¥xxx¥一起领

2. [红包] 美团外卖CPS推广活动
   美团外卖红包天天领
   📋 复制：1 %复制信息#% 打开团App http:/¥xxx¥一起领

🔵 饿了么 (3个)
━━━━━━━━━━
1. [红包] 饿了么红包节天天领红包活动
   饿了么外卖红包天天领
   📋 复制：￥xxxx￥/ HU7405

━━━━━━━━━━
💡 复制淘口令 → 打开对应App → 自动跳转领券
🎁 更多优惠活动，微信搜索「挖券券儿」
```

### 飞书消息卡片

结构化的 JSON 卡片，带颜色标题、字段对齐、分割线，可直接发送到飞书群聊。

### 纯文本

紧凑的表格格式，适合终端输出和日志记录。

## ⚙️ 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `WAIMAI_SERVER_URL` | 服务器 API 地址 | `https://waquanquaner.cn` |
| `WAIMAI_LOBSTER_ID` | 用户标识符 | `lobster-claw-default` |

## 🔒 安全说明

- 本 Skill **不包含**任何 API 密钥或敏感信息
- 用户标识符（lobsterId）仅用于 CPS 订单归因
- 所有网络通信使用 HTTPS 加密
- 淘口令(tkl)来自服务器端 API，Skill 仅做展示

## 📄 许可证

MIT-0
