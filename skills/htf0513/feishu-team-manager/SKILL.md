---
name: feishu-team-manager
description: 自动化招聘新 Agent，配置独立飞书机器人并重构多账号路由
---

# feishu-team-manager (HR 大姐头)

飞书多 Agent 团队管理 Skill。基于“大姐头”招聘方案，实现 Agent 招聘、独立 Bot 绑定与环境自适配。

## 🚀 路由绑定方案

本 Skill 采用 **2026-04-21 实践通过** 的“账户级路由”方案，确保每个机器人拥有独立的身份、头像和快捷指令。

### 核心逻辑：
- **独立身份 (Account)**：每个机器人对应飞书开放平台的一个独立应用。
- **精准映射 (Binding)**：通过 `accountId` 将特定机器人发来的消息路由到指定的物理工作空间。

## 📂 技能结构
- `index.js`: 安装引导与环境适配器（含版本审计与路径自修复）。
- `scripts/recruit_agent.py`: 物理空间创建与 Agent 初始化。
- `scripts/bind_bot.py`: 核心配置注入，重构 `openclaw.json`。
- `scripts/check_env.py`: 团队状态巡检。

## 🛠️ 使用方式

### 1. 招聘新员工
直接对“大姐头”说：“招聘一个运维 Agent，起名叫运维小弟”。
我会：
1. 创建 `/root/.openclaw/agents/ops_helper` 目录。
2. 注入专属的 `IDENTITY.md`。
3. 提示你提供该员工对应的飞书机器人凭据。

### 2. 绑定机器人
说：“帮运维小弟绑定机器人，App ID 是 cli_xxx，Secret 是 yyy”。
我会：
1. 自动注入 `channels.feishu.accounts`。
2. 自动设置 `bindings` 路由。
3. 执行 `openclaw gateway restart` 重启生效。

## 📥 安装说明
如果你是第一次通过飞书接收此包：
1. **解压**：将包放置于 `~/.openclaw/workspace/skills/`。
2. **激活**：输入“运行 feishu-team-manager 的安装脚本”。
3. **安全确认**：脚本会提示是否允许修改 `openclaw.json`，输入 `y` 确认。

## ⚠️ 注意事项
- **版本要求**：OpenClaw >= 2026.3.20。
- **自动备份**：每次修改配置前，系统会自动生成 `.bak_[时间戳]` 备份文件。
- **重启时间**：网关重启约需 10-20 秒，期间所有 Agent 会短暂离线。

---
*狗蛋自研 Skill 框架 | 2026-04-22 优化版*

## 注意事项

- **保留现有配置**：现有 `appId/appSecret` 完全不动。
- **自动备份**：修改前自动备份 `openclaw.json`。
- **dmScope 设置**：自动设置会话绑定颗粒度为 `per-account-channel-peer`。
- **重启 Gateway**：重启后约 10-30 秒恢复服务。
- **恢复方法**：如出问题可用备份文件手动恢复。

## 💰 支持作者

如果你觉得这个技能对你有帮助，可以考虑支持作者继续开发：

- **微信赞赏码**：<image url="https://gitee.com/noahtao/wordpress-auto-publisher/raw/main/images/wechat_donate.png"/>
- **支付宝**：<image url="https://gitee.com/noahtao/wordpress-auto-publisher/raw/main/images/alipay_donate.jpg"/>
- **GitHub Sponsors**：https://github.com/sponsors/htf0513
- **定制服务**：联系微信/邮箱获取企业级定制

> **图片已更新**：微信和支付宝赞赏码图片已上传至Gitee图床，链接可正常访问。
