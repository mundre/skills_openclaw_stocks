# browser-ops

[![GitHub](https://img.shields.io/github/license/lanyasheng/browser-ops)](LICENSE)
[![Skill Version](https://img.shields.io/badge/version-2.7.0-blue)](https://github.com/lanyasheng/browser-ops)

> 浏览器操作的统一入口 Skill —— 拿到 URL 就能用。自动安装工具链、6 层智能路由、Session/Cookie 持久化、反爬绕过。

## 特性

- **自动 Bootstrap** — 首次使用时检测并安装缺失工具
- **6 层智能路由** — 按成本/复杂度自动选择最优方案
- **Session 持久化** — Cookie/登录态跨会话保留，支持按站点隔离
- **反爬绕过** — Zendriver(~90%)/Camoufox(~80%) 通过 Cloudflare 盾
- **省 token** — 能用 Jina 提取正文就不开浏览器

## 安装

```bash
# 手动安装
git clone https://github.com/lanyasheng/browser-ops.git
```

## 快速开始

```
@browser-ops 帮我抓取 https://example.com/article 的正文内容
```

Skill 自动选择最优方案：
1. 先用 Jina AI Reader 提取正文（$0）
2. 失败则升级到 agent-browser
3. 遇到反爬则使用 Zendriver

## 路由决策

```
有 API？ → 直接调用
只要正文？ → Jina（$0）
需要交互？ → agent-browser（$0）/ Stagehand（~$0.001）
需要截图？ → agent-browser screenshot
被反爬拦截？ → Zendriver / Camoufox
```

## 核心工具

| 工具 | 用途 | 安装 |
|------|------|------|
| agent-browser | 命令化浏览器操作 | `npm install -g agent-browser` |
| Jina AI Reader | 正文提取 | 无需安装（HTTP 调用） |
| Stagehand v3 | AI 增强浏览器 | `npm install @browserbasehq/stagehand` |
| Zendriver | 反爬绕过 | `pip install zendriver` |
| Camoufox | 反爬绕过（Firefox） | `pip install camoufox` |

## 已验证能力

| 能力 | 状态 | 说明 |
|------|------|------|
| opencli | ✅ | 实测通过 (HackerNews 20 items) |
| agent-browser | ✅ | 实测通过 (导航/snapshot/截图/JS执行) |
| agent-browser 内网 | ✅ | Cookie 复用访问 ATA 成功 |
| Zendriver | ✅ | Nodriver 继任者，安装并能运行 (需要指定 Chrome 路径) |
| Camoufox | ✅ | 安装并能运行 |
| Stagehand v3 | ✅ | SDK 安装成功，LOCAL 模式可用 (需要 Anthropic/OpenAI API key) |
| Lightpanda | ✅ | 安装成功，省 60-80% 上下文 token (部分企业网络可能受限) |
| Cookie 统一存储 | ✅ | 40 cookies, 9 domains |

## 文档

- [SKILL.md](SKILL.md) — Skill 主文档（路由决策、工具速查、Session 管理）
- [references/setup.md](references/setup.md) — 工具安装与验证
- [references/architecture.md](references/architecture.md) — 6 层架构详解
- [references/routing.md](references/routing.md) — 路由决策树
- [references/state-management.md](references/state-management.md) — Session/Cookie 持久化
- [references/jina-usage.md](references/jina-usage.md) — Jina 正文提取
- [references/anti-detection.md](references/anti-detection.md) — 反爬策略

## 路线图

- [x] v1.0.0 — 初版，6 层架构 + Jina 验证
- [x] v2.0.0 — 可执行 Skill（Bootstrap + Session 持久化 + Stagehand v3）
- [x] v2.1.0 — opencli 桥接层 + 反爬实测
- [x] v2.2.0 — Zendriver 替代 Nodriver + 住宅代理
- [x] v2.3.0 — 批量 API vs opencli 路由逻辑
- [x] v2.4.0 — Playwright MCP 集成 + 内部信息清理
- [x] v2.5.0 — skill-creator 评测 + frontmatter 标准化
- [ ] v3.0.0 — 多站点并发 + 状态池管理 + 触发率优化

## 许可证

MIT License — 详见 [LICENSE](LICENSE)

## Operator Notes

- This skill is **executable** — it installs tools, runs commands, and persists cookies. It is not just advisory.
- **opencli + agent-browser** are required core dependencies. Other tools (Zendriver/Camoufox/Stagehand) are installed on demand.
- **Stagehand** requires an Anthropic/OpenAI/Gemini API key. Compat layers (百炼等) may not support Stagehand's internal endpoints.
- **Lightpanda** is a lightweight browser (省 token + 快 5x). No screenshot support; some enterprise networks may restrict downloads.
- **Zendriver/Camoufox** require Python 3.12+.
