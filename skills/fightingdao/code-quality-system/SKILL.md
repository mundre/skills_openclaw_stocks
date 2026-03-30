---
name: code-quality-system
description: 完整的代码质量分析系统，包含前后端服务和数据库。一键安装、简单配置即可使用。支持周/月维度分析、AI代码审查、Teams消息通知、邮件报告等功能。
version: 1.0.0
author: OpenClaw
---

# 代码质量分析系统

完整的代码质量分析解决方案，开箱即用。

## 一、快速开始

### 1. 安装技能

```bash
clawhub install code-quality-system
```

### 2. 让 AI 助手帮你初始化

```
请帮我初始化代码质量分析系统
```

AI 助手会自动：
1. 检查环境（Node.js、PostgreSQL）
2. 安装依赖
3. 初始化数据库
4. 询问配置信息
5. 启动服务

### 3. 你只需要提供三个配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| 代码仓库目录 | 所有项目已拉取完成的根目录 | `/Users/xxx/projects/` |
| Teams 配置 | Webhook 地址（含 token）和 secret | 在 Teams 群里创建机器人获取 |
| SMTP 配置 | 邮箱发送配置 | QQ邮箱、企业邮箱等 |

### 4. 访问系统

- 前端界面：http://localhost:5173
- 后端 API：http://localhost:3000/api/v1

---

## 二、配置说明

### 2.1 配置文件位置

```
~/.openclaw/skills/code-quality-system/config.json
```

### 2.2 配置模板

```json
{
  "codebaseDir": "/path/to/your/codebase",
  "teams": {
    "webhookUrl": "https://im.360teams.com/api/qfin-api/rce-app/robot/send?access_token=xxx",
    "secret": "your-teams-secret"
  },
  "smtp": {
    "host": "smtp.qq.com",
    "port": 465,
    "secure": true,
    "user": "your-email@qq.com",
    "pass": "your-auth-code",
    "fromName": "代码质量分析助手"
  },
  "emailRecipients": ["recipient@example.com"]
}
```

### 2.3 Teams 配置获取方式

1. 在 360Teams 群里添加"群预警机器人"
2. 开通"对话服务"
3. 复制 **Webhook 地址**（包含 access_token）和 **secret**

**Webhook 地址格式**：
```
https://im.360teams.com/api/qfin-api/rce-app/robot/send?access_token=xxxxxxxxx
```

### 2.4 SMTP 配置示例

**QQ邮箱**：
```json
{
  "host": "smtp.qq.com",
  "port": 465,
  "secure": true,
  "user": "your-qq@qq.com",
  "pass": "授权码（不是密码）"
}
```

**企业邮箱**：
```json
{
  "host": "smtp.exmail.qq.com",
  "port": 465,
  "secure": true,
  "user": "your-name@company.com",
  "pass": "邮箱密码"
}
```

---

## 三、数据库配置

### 3.1 后端环境变量

```
~/.openclaw/skills/code-quality-system/backend/.env
```

```env
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/code_quality?schema=public"
PORT=3000
NODE_ENV=development
JWT_SECRET=your-secret-key
```

### 3.2 创建数据库

```bash
# macOS (Homebrew)
createdb code_quality

# 或使用 psql
psql -U postgres -c "CREATE DATABASE code_quality;"
```

---

## 四、使用方法

### 4.1 启动服务

告诉 AI 助手：

```
帮我启动代码质量分析系统
```

### 4.2 执行分析

```
帮我分析本周的代码质量
```

或

```
帮我分析 2026 年 3 月的代码质量
```

### 4.3 AI 助手会自动完成

1. **拉取最新代码** - `git fetch` 所有项目
2. **分析代码变更** - 统计提交、增删行、任务等
3. **AI 质量评分** - 分析代码质量并评分
4. **AI 代码审查** - 识别代码问题
5. **同步数据库** - 写入分析结果
6. **发送通知** - Teams 消息和邮件

### 4.4 配置团队成员

在前端界面的"小组管理"页面添加团队成员：

1. 点击"添加成员"
2. 填写姓名、邮箱、Git 用户名
3. 只有添加的用户才会被统计

---

## 五、分析流程详解

### 5.1 周维度分析

**周期值规则**：使用**周四的日期**（YYYYMMDD）

示例：
- 2026-03-30（周一）→ 周期值 `20260402`（周四）
- 2026-04-01（周三）→ 周期值 `20260402`（周四）

**分支匹配规则**：
- 查找分支名包含周期值的版本分支
- 如 `feature/xxx-20260402`

### 5.2 月维度分析

**周期值规则**：使用月份（YYYYMM）

示例：
- 2026 年 3 月 → 周期值 `202603`
- 2026 年 4 月 → 周期值 `202604`

**统计范围**：该月所有分支的所有提交

### 5.3 数据同步顺序

```
1. code_analyses - 分析记录
2. code_issues - AI代码审查问题
3. code_reviews - 提交记录详情
4. team_statistics - 团队统计
5. project_statistics - 项目统计
```

---

## 六、功能清单

### 6.1 前端页面

| 页面 | 路由 | 功能 |
|------|------|------|
| 项目概览 | `/projects` | 项目列表、筛选、跳转详情 |
| 项目报告 | `/projects/:id/report` | 项目详细分析报告 |
| 代码审查 | `/projects/:id/code-review` | 代码问题明细 |
| 用户详情 | `/users/:id` | 个人代码评审详情 |
| 小组管理 | `/team` | 团队成员管理 |
| 小组报告 | `/team/report` | 团队整体分析报告 |

### 6.2 后端 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/projects` | GET | 项目列表 |
| `/api/v1/users` | GET | 用户列表 |
| `/api/v1/dashboard/overview` | GET | 大盘数据 |
| `/api/v1/projects/:id/report` | GET | 项目报告 |
| `/api/v1/code-review/:id` | GET | 代码审查问题 |
| `/api/v1/teams/user-names` | GET | 团队成员用户名列表 |

---

## 七、项目结构

```
code-quality-system/
├── config.json              # 主配置文件
├── config.example.json      # 配置模板
├── SKILL.md                 # 本文档
├── backend/                 # NestJS 后端
│   ├── src/
│   │   ├── modules/
│   │   │   ├── projects/    # 项目管理
│   │   │   ├── users/       # 用户管理
│   │   │   ├── teams/       # 团队管理
│   │   │   ├── dashboard/   # 数据大盘
│   │   │   └── code-review/ # 代码审查
│   │   └── common/          # 公共模块
│   ├── prisma/
│   │   └── schema.prisma    # 数据库 Schema
│   └── package.json
├── frontend/                # React 前端
│   ├── src/
│   │   ├── pages/           # 页面组件
│   │   ├── components/      # 通用组件
│   │   ├── api/             # API 客户端
│   │   └── stores/          # 状态管理
│   └── package.json
└── scripts/                 # 脚本
    ├── analyze-code-v2.js   # 分析脚本
    ├── sync-to-db.js        # 同步脚本
    ├── notify-teams.js      # Teams 通知
    └── weekly-analysis.sh   # 一键分析
```

---

## 八、⚠️⚠️⚠️ 重要注意事项（必读！）

### 8.1 分析前必须做的事

```
□ git fetch 拉取所有项目最新变更
□ 确认数据库服务已启动
□ 确认后端服务已启动
```

### 8.2 数据同步注意事项

| 问题 | 后果 | 解决方案 |
|------|------|---------|
| fileChanges 字段为空 | 类型分布显示空 | 分析脚本必须收集文件变更 |
| code_issues 无数据 | 问题与建议显示空 | 必须执行 AI 代码审查 |
| code_reviews 无数据 | 提交记录详情空 | 必须同步 commits 数据 |
| team_statistics 无数据 | 大盘视图为 0 | 必须同步统计表 |
| AI 评分缺失 | 评分显示默认值 | 必须执行 AI 评分 |

### 8.3 用户管理规则

**用户必须在前端"小组管理"页面预先添加，否则不会被统计！**

流程：
1. 前端添加成员 → 写入 `users` 表
2. 分析脚本读取 `users` 表
3. 只统计已添加用户的提交
4. 未匹配的提交直接跳过

### 8.4 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 分支找不到 | 周期值不是周四 | 使用周四日期 |
| 用户数据丢失 | 用户未在小组管理中添加 | 先添加用户再分析 |
| 历史数据异常 | 字段名不一致 | 检查历史数据结构 |

---

## 九、技术栈

### 后端
- NestJS 10
- Prisma 5
- PostgreSQL 16

### 前端
- React 18
- TypeScript 5
- Vite 5
- Ant Design 5
- Zustand 4

### 脚本
- Node.js 18+
- Git 命令行

---

## 十、更新记录

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| 1.0.0 | 2026-03-30 | 初始版本，开箱即用 |

---

## 十一、常见问题

### Q: 如何添加新项目？

A: 项目会自动识别。只要代码目录下有 `.git` 文件夹，就会被扫描到。

### Q: 如何修改分析周期？

A: 在前端页面顶部切换"周/月"维度，选择日期即可。

### Q: 数据可以导出吗？

A: 可以通过 API 导出，或直接查询 PostgreSQL 数据库。

### Q: 支持哪些 Git 平台？

A: 支持 Git、GitLab、GitHub、Gitee 等所有 Git 托管平台。

### Q: 可以自定义评分规则吗？

A: AI 评分由 AI 助手完成，评分标准在 SKILL.md 中定义。可以修改评分标准。

---

## 十二、联系支持

遇到问题？直接告诉 AI 助手：

```
代码质量分析系统启动失败，帮我看看
```

AI 助手会自动诊断并解决问题。