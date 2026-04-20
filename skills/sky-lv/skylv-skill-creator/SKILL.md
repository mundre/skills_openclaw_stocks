---
name: skill-creator
slug: skylv-skill-creator
version: 1.0.2
description: "OpenClaw Skill Generator. Create production-ready OpenClaw Skills from descriptions. Triggers: create skill, build skill, new skill, skill template, OpenClaw skill development."
author: SKY-lv
license: MIT
tags: [openclaw, skill, generator, template]
keywords: skill, scaffolding, template, creation
triggers: skill creator
---

# Skill Creator — OpenClaw Skill 生成助手

## 功能说明

帮助用户从零创建生产级 OpenClaw Skills。自动生成完整的 SKILL.md 文件，包含正确的 frontmatter、触发词、权限声明等。

## 使用场景

1. **创建新 Skill** - 根据功能描述生成完整 Skill
2. **Skill 模板** - 提供标准 Skill 结构参考
3. **批量生成** - 为多个相关功能生成 Skills
4. **Skill 优化** - 改进现有 Skill 的描述和触发词

## 使用方法

### 1. 创建新 Skill

```
用户：帮我创建一个 Skill，功能是帮助用户管理待办事项
```

输出：
- SKILL.md 完整文件（含 frontmatter）
- 推荐的触发词列表
- 权限要求说明
- 测试建议

### 2. Skill 模板参考

```
用户：OpenClaw Skill 的标准格式是什么？
```

输出：
```yaml
---
name: skill-name
slug: skylv-skill-name
version: 1.0.0
description: Clear description (80-150 chars)
author: Your Name
license: MIT
tags: [category, openclaw, skill]
---

# Skill Name

Description and usage instructions.
```

### 3. 批量生成

```
用户：我需要创建 5 个 Skills，分别是：Git 助手、Docker 助手、SQL 助手、Redis 助手、MongoDB 助手
```

输出：
- 5 个完整的 SKILL.md 文件
- 每个 Skill 的目录结构
- 批量发布到 ClawHub 的脚本

## 输出格式

### 完整 Skill 结构

```yaml
---
name: todo-manager
slug: skylv-todo-manager
version: 1.0.0
description: Todo and task management assistant. Create, organize, and track tasks with priorities and deadlines. Triggers: todo, task, reminder, deadline, task list.
author: SKY-lv
license: MIT
tags: [productivity, todo, openclaw, skill]
---

# Todo Manager — 待办事项管理助手

## 功能说明

帮助用户管理待办事项、任务清单和提醒。

## 使用方法

### 1. 创建任务

```
用户：创建一个任务，明天下午 3 点开会
```

### 2. 查看任务

```
用户：我今天的任务有哪些？
```

### 3. 完成任务

```
用户：标记任务"写报告"为已完成
```

## 权限要求

- FileRead/Write: 读取和写入任务文件
- Calendar: 访问日历设置提醒（可选）

## 触发词

- 自动：检测任务相关关键词
- 手动：/todo, /task, /tasks
```

## 最佳实践

### 1. 描述优化
- 长度：80-150 字符
- 语言：英文（更好的 ClawHub 搜索排名）
- 包含：核心功能 + 触发词提示

### 2. 触发词设计
- 主触发词：2-3 个核心词
- 长尾触发：5-10 个相关短语
- 命令触发：/command 格式

### 3. Slug 命名
- 格式：skylv-{skill-name}
- 小写 + 连字符
- 避免与现有 Skills 冲突

## ClawHub 发布

### 发布命令

```bash
clawhub publish ./skills/todo-manager \
  --slug skylv-todo-manager \
  --version 1.0.0 \
  --changelog "Initial release"
```

### 发布前检查清单

- [ ] SKILL.md frontmatter 完整
- [ ] description 80-150 字符
- [ ] slug 唯一（加 skylv- 前缀）
- [ ] version 符合语义化版本
- [ ] license 明确（MIT/MIT-0）
- [ ] tags 相关且精准

## 示例输出

创建 Skill 后，用户可以直接：

1. 本地测试 Skill 功能
2. 发布到 ClawHub
3. 分享给其他 OpenClaw 用户

## 相关文件

- ClawHub 文档：https://docs.openclaw.ai/tools/clawhub
- Skill 创建指南：https://docs.openclaw.ai/skills/creating
- 技能市场：https://clawhub.ai

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
