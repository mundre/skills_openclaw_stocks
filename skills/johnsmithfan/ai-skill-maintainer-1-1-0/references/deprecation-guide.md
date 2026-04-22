# Skill 废弃管理指南

> **版本**：v1.0.0
> **依据**：CTO 版本治理最佳实践

---

## 废弃决策树

```
发现 Skill 需要废弃？
│
├─ 是否有替代 Skill？
│   ├─ 是 → 推荐替代方案，进入废弃流程
│   └─ 否 → 评估是否完全移除，或保留最小功能
│
├─ 是否有用户在使用？
│   ├─ 是 → 必须提供迁移路径 + 过渡期
│   └─ 否 → 可快速废弃
│
└─ 是否有安全紧急原因？
    ├─ 是 → 🚨 紧急废弃，无过渡期
    └─ 否 → 标准废弃流程
```

---

## 废弃类型

### 类型 A：替换废弃

```
旧 Skill → 新 Skill（功能相同或增强）
过渡期：30天
```

### 类型 B：功能废弃

```
Skill 部分功能废弃，但核心功能保留
过渡期：60天
```

### 类型 C：完全废弃

```
Skill 完全移除
过渡期：90天
```

### 类型 D：紧急废弃

```
安全原因，无过渡期
立即通知用户
```

---

## 废弃 SKILL.md 模板

```yaml
---
name: <skill-name>
version: X.Y.Z
description: |
  ⚠️ 【已废弃】此 Skill 已废弃。
  废弃日期：YYYY-MM-DD
  迁移至：<new-skill-name>
deprecated: true
replacement: <new-skill-name>
metadata:
  {"openclaw":{"emoji":"⚠️","os":["linux","darwin","win32"]}}
---

# ⚠️ 已废弃：<Skill Name>

## 废弃通知

**废弃日期**：YYYY-MM-DD
**最后支持日期**：YYYY-MM-DD
**替代方案**：<new-skill-name>

### 废弃原因
<详细原因>

### 迁移步骤
1. <步骤1>
2. <步骤2>
3. <步骤3>

### 如有问题
<联系方式或帮助链接>
```

---

## 迁移文档模板（`references/migration.md`）

```markdown
# 从 <old-skill> 迁移到 <new-skill>

## 概述

<old-skill> 已于 YYYY-MM-DD 废弃，请迁移到 <new-skill>。

## 主要变更

### 功能对比

| 功能 | <old-skill> | <new-skill> |
|------|-------------|-------------|
| 功能1 | ✅ 支持 | ✅ 支持 |
| 功能2 | ✅ 支持 | ✅ 增强 |
| 功能3 | ✅ 支持 | ❌ 不支持（替代方案：<alternative>）|

### Breaking Changes

- <变更1>
- <变更2>

## 迁移步骤

### Step 1：安装新 Skill

```bash
clawhub install <new-skill>
```

### Step 2：更新触发命令

旧：
```
<old-trigger-command>
```

新：
```
<new-trigger-command>
```

### Step 3：验证

<验证步骤>

## 常见问题

**Q：<问题1>**
**A：<答案1>**

**Q：<问题2>**
**A：<答案2>**
```

---

## 废弃通知模板

```markdown
## ⚠️ Skill 废弃通知

**Skill**：<name>
**废弃版本**：vX.Y.Z
**生效日期**：YYYY-MM-DD
**替代 Skill**：<new-skill>

### 发生了什么？

<废弃原因>

### 我需要做什么？

1. 了解新 Skill：<link>
2. 迁移指南：[migration.md](references/migration.md)
3. 过渡期截止：YYYY-MM-DD

### 时间线

- **废弃公告**：YYYY-MM-DD
- **最后支持**：YYYY-MM-DD
- **完全移除**：YYYY-MM-DD（待定）

### 支持

如有问题，请联系：<contact>
```
