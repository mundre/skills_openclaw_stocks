# Revolution 系统配置 v2.0

**更新日期：** 2026-03-29  
**版本：** 2.0（强制审核 + 模型回退）

---

## 🎯 核心改进

### 1. 超时时间延长

| 角色 | 之前 | 现在 |
|------|------|------|
| Reviewer | 180 秒 (3m) | **300 秒 (5m)** ⭐ |
| Executor | 180 秒 (3m) | **300 秒 (5m)** ⭐ |
| Auditor | 120 秒 (2m) | **180 秒 (3m)** ⭐ |

### 2. 模型回退机制

**Reviewer/Auditor:**
```
优先：高级模型
 ↓ 认证失败 (401)
回退：备用模型
```

**Executor:**
```
优先：默认模型（代码能力强）
 ↓ 超时/失败
回退：协调模型（稳定快速）
```

### 3. 强制审核流程

**规则：** Executor 完成后**必须**经过 Auditor 审核才能标记完成

```
审阅 (Reviewer) → 执行 (Executor) → 审核 (Auditor) → 更新任务 JSON
                                          ↓
                                   ❌ 审核失败 → 打回重做
```

**配置：** `enforceAudit: true`

---

## 📋 完整流程

### Step 1: 审阅 (Reviewer)

**超时：** 300 秒  
**模型：** `高级模型` → fallback → `备用模型`

**任务：**
1. 读取所有 reference_files
2. 技术选型审查（依赖必要性/场景匹配/复杂度/集成）
3. 判断 verdict（approve/revise/reject）
4. 生成详细执行指令

**输出：**
```json
{
  "verdict": "approve|revise|reject",
  "instructions": "详细执行指令",
  "feedback": "审阅意见",
  "technical_review": "技术选型审查说明"
}
```

---

### Step 2: 执行 (Executor)

**超时：** 300 秒  
**模型：** `默认模型` → fallback → `协调模型`

**任务：**
1. 严格按 Reviewer 指令执行
2. 每步修改后运行验证命令
3. 失败时尝试修复（最多 3 次）
4. 输出 JSON 结果

**输出：**
```json
{
  "status": "success|failed",
  "summary": "执行摘要",
  "files_modified": ["路径列表"],
  "verification": "验证结果"
}
```

---

### Step 3: 审核 (Auditor) ⭐ 强制

**超时：** 180 秒  
**模型：** `高级模型` → fallback → `备用模型`

**任务：**
1. 对比原始指令与执行结果
2. 审核标准：
   - 指令遵循：是否严格按指令执行？
   - 代码质量：代码是否正确、可运行？
   - 测试验证：验证命令是否通过？
   - 技术选型：是否有不合理的依赖或设计？
3. 判断 verdict（pass/fail）

**输出：**
```json
{
  "verdict": "pass|fail",
  "feedback": "审核意见",
  "issues": ["问题列表"]
}
```

**审核通过：** 更新任务 JSON，标记 completed  
**审核失败：** current_iteration++，打回重做（最多 3 次）

---

### Step 4: 更新任务 JSON

**审核通过后：**
```json
{
  "history": [
    {
      "subtask_index": 0,
      "subtask": "创建 message.md 文档",
      "status": "completed",
      "completed_at": "2026-03-29T12:05:00+08:00",
      "summary": "✅ 审阅→执行→审核 完整流程通过"
    }
  ],
  "current_subtask": 1
}
```

---

## 🔧 配置文件

**位置：** `config/models.json`

```json
{
  "roles": {
    "reviewer": {
      "primary": "高级模型",
      "fallback": "备用模型"
    },
    "executor": {
      "primary": "默认模型",
      "fallback": "协调模型"
    },
    "auditor": {
      "primary": "高级模型",
      "fallback": "备用模型"
    },
    "coordinator": "协调模型"
  },
  "timeouts": {
    "reviewer": 300,
    "executor": 300,
    "auditor": 180
  },
  "enforceAudit": true
}
```

---

## ⚠️ 违规处理

**跳过审核直接标记完成：**
- ❌ 禁止
- 系统应拒绝更新任务 JSON
- 必须重新执行 Auditor 步骤

**审核失败但仍标记完成：**
- ❌ 禁止
- 必须 current_iteration++
- 达到 max_iterations 后标记 failed

---

## 📊 执行统计

**目标指标：**
- 审核覆盖率：100%（所有子任务必须经过 Auditor）
- 一次通过率：>80%
- 平均执行时间：<10 分钟/子任务

---

**最后更新：** 2026-03-29  
**维护者:** Auto Revolution
