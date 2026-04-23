---
name: "git-helper"
slug: skylv-git-helper
version: 1.0.2
description: "Git Operations Assistant. Handle Git operations, resolve conflicts, manage branches. Triggers: Git, commit, merge, branch, pull request, conflict."
author: SKY-lv
license: MIT-0
tags: [git, openclaw, agent]
keywords: git, version-control, conflict-resolution
triggers: git helper
---

# Git Helper — Git操作助手

## 功能说明

辅助Git版本控制操作，解决常见问题。

## 使用方法

### 1. 常用操作指导

```
用户: 如何撤销最后一次commit但保留修改？
```

回答：
```bash
git reset --soft HEAD~1
```

### 2. 冲突解决

```
用户: 帮我解决这个合并冲突
```

### 3. 分支策略

```
用户: 推荐什么Git分支策略？
```

### 4. 提交规范

```
用户: 检查commit message是否规范
```

## 常见问题

- 撤销操作
- 合并冲突
- 分支管理
- 回退版本

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
