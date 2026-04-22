# AIDSO_虾搜GEO

让 爱搜AI 成为你的 GEO 操盘手。随时诊断，随时生成，随时优化。

---

## ✨ 核心能力

| 能力 | 说明 |
|------|------|
| **📎 一键品牌GEO诊断** | 输入品牌名称，生成GEO诊断报告 |
| **📚 品牌知识库** | 支持品牌知识库存储、查询与后续内容沉淀管理 |
| **🎤 GEO内容生产** | 输入品牌 + 问题 + 大模型平台，生成适合 GEO 优化的文本内容 |

---

## 💡 使用场景

### 🔍 随手诊断品牌GEO现状

> 👤 帮我做一个 斯凯奇 的GEO诊断报告
>
> 🤖 此次诊断将消耗20积分，是否确认？
>
> 👤 确认
>
> 🤖 诊断已发起，报告生成中，大约需要3~10分钟，请稍后……
>
> 🤖 最终返回：GEO诊断报告文件

---

### ✏️ GEO 内容生产

> 👤 给 斯凯奇 生成一篇 GEO 优化内容，优化问题是 “运动鞋品牌推荐”， 优化的平台是“豆包”
>
> 🤖 返回适合 GEO 优化铺排的正文内容

---

### 🔗 品牌知识库

**品牌线上资料太少**

> 👤 帮我把这些品牌介绍和产品资料存到 欧莱雅 品牌知识库
>
> 🤖 已保存到品牌知识库，后续会基于这些资料做更准确的 GEO 诊断和内容生产。

**补充品牌官网和产品文档**

> 👤 把官网链接、产品手册和品牌介绍文件都加入到 欧莱雅 的品牌知识库
>
> 🤖 已加入品牌知识库，AI 后续会结合这些资料理解品牌信息。

---

## 📦 安装

### 方式一：通过 ClawHub 安装

```bash
clawhub install aidso_xiasou_geo
```

### 方式二：让 龙虾 安装（推荐）

> 帮我安装 https://clawhub.ai/tangyuanmile-coder/aidso-xiasou-geo-diagnosis

---

## 🔑 配置

### 自动配置（默认）

安装后首次使用时，AI 会自动发起 API Key：

1. 你说「GEO诊断」或任何GEO相关操作
2. AI 检测到未配置，提供API Key获取链接
3. 点击链接，获取API key
4. 输入给龙虾，继续执行你的请求

> 💡 需要 [API Key的账户有积分]才能使用 API

---

## 🛠 支持的知识库类型

| 类型 | 说明 | 支持 |
|------|------|------|
| `plain_text` | 纯文本 | ✅ 读写 |
| `link` | 链接 | ✅ 读写 |
| `file` | 上传文件（pdf、word、PPT、md等） | 📖 仅读取 |

---

## 📜 相关链接

- [爱搜官网](https://aidso.com)
- [ClawHub](https://clawhub.ai/tangyuanmile-coder/aidso-xiasou-geo-diagnosis)
- [官网虾搜下载](https://geo.aidso.com/setting?type=apiKey&platform=GEO)
- [品牌诊断页面](https://geo.aidso.com/completeAnalysis)

---
## License

MIT-0 (MIT No Attribution) · Published on [ClawHub](https://clawhub.ai)

---

pip install requests markdown weasyprint
