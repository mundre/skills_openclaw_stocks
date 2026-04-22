---
name: ai-skill-maintainer
version: 1.1.0
description: |
  AI公司 Skill 维护工作流（CTO 版本治理 + CISO 安全运营标准版）。当需要对已发布的 Skill 进行版本更新、bug修复、功能增强、依赖升级、安全补丁、废弃（deprecation）管理时触发。触发关键词：更新技能、更新 Skill、修复 Skill bug、增强 Skill、升级依赖、打安全补丁、废弃技能、Skill 废弃。
  整合 CTO 版本治理规范（semver + changelog + rollback）+ CISO 安全运营标准（漏洞响应 SLA + 补丁管理）。
metadata:
  {"openclaw":{"emoji":"🔧","os":["linux","darwin","win32"]}}
---

# AI Skill 维护工作流（CTO × CISO 标准）

> **执行角色**：Skill 维护者（CTO 版本治理 + CISO 安全运营）
> **版本**：v1.0.0（CTO-001 版本治理 × CISO-001 安全运营）
> **合规状态**：✅ 维护操作需记录，🚨 安全补丁走紧急通道

---

## 核心原则

1. **变更可追溯**：所有修改必须记录版本历史
2. **向后兼容**：MINOR/PATCH 变更不得破坏现有功能
3. **安全优先**：CISO 安全补丁走紧急通道，不受正常发布周期限制
4. **最小变更**：只改必要的，不要过度工程化

---

## Agent 调用接口（Inter-Agent Interface）

> **版本**：v1.1.0（新增接口层）
> **安全约束**：接口本身零新增攻击面，所有输入参数均经过验证

---

### 接口身份

| 属性 | 值 |
|------|-----|
| **接口 ID** | `skill-maintainer-v1` |
| **调用方式** | `sessions_send` / `sessions_spawn` (isolated) |
| **会话目标** | `isolated`（强制隔离）|
| **最低权限** | L3（可读写 skills/ 指定目录） |
| **CISO 约束** | 🚨 安全补丁任务必须 CISO-001 授权，紧急通道优先 |

---

### TASK 消息格式

```json
{
  "skill": "ai-skill-maintainer",
  "version": "1.1.0",
  "task": "<task-type>",
  "params": { ... },
  "context": {
    "caller": "<caller-agent-id>",
    "priority": "<P0|P1|P2|P3>",
    "emergency": false,
    "isolated": true
  }
}
```

### 可用 Task 类型

| Task | 参数 | 返回 | 说明 |
|------|------|------|------|
| `diagnose` | `skill-name`, `issue`, `caller` | `{diagnosis, type, severity}` | 诊断问题 |
| `patch` | `skill-name`, `version`, `changes`, `caller` | `{new-version, status}` | 实施修复 |
| `security-patch` | `skill-name`, `cve-id`, `authorization`, `caller` | `{fixed, new-version, notification-sent}` | 🚨 CVE 修复 |
| `deprecate` | `skill-name`, `reason`, `replacement`, `caller` | `{deprecated-version, status}` | 废弃 Skill |
| `emergency-isolate` | `skill-name`, `reason`, `caller` | `{isolated, affected-versions}` | 🚨 紧急隔离（0-day）|
| `health-check` | `skill-name` | `{metrics, status}` | 健康检查 |
| `dependency-audit` | `skill-name` | `{dependencies[], cves[]}` | 依赖 CVE 扫描 |

### Task 参数 Schema

#### `security-patch` 参数

```json
{
  "skill-name":     "string (required, skill slug)",
  "cve-id":         "string (required, e.g. CVE-YYYY-NNNNN)",
  "cvss-score":     "number (required, 0.0-10.0)",
  "authorization":  "string (required, must be CISO-001)",
  "caller":         "string (required, agent ID)",
  "changes": {
    "description":  "string (what was changed)",
    "files":        "string[] (list of modified files)",
    "test-results": "string (test outcome summary)"
  }
}
```

**CVE 紧急通道 SLA**：

| CVSS | 触发 | SLA | 流程 |
|------|------|-----|------|
| 9.0-10.0 | 🚨 紧急隔离 + Patch | ≤ 24h | 紧急通道直通 |
| 7.0-8.9 | 紧急 Patch | ≤ 7d | 标准通道加速 |
| 4.0-6.9 | 计划修复 | ≤ 30d | 标准通道 |
| 0.1-3.9 | 跟踪 | 下个版本 | 常规流程 |

#### `emergency-isolate` 参数

```json
{
  "skill-name": "string (required)",
  "reason":     "string (required, CVE ID or incident description)",
  "caller":     "string (required, must be CISO-001 or CTO-001)"
}
```

#### `health-check` 参数

```json
{
  "skill-name": "string (required)"
}
```

> **健康阈值**（CTO-001 KPI 对齐）：TSR < 92% → `UNHEALTHY`；P95 > 1200ms → `DEGRADED`；CVSS ≥ 7.0 → `HIGH_RISK`

**返回值示例**：
```json
{
  "status": "success",
  "result": {
    "skill-name": "pdf-processor",
    "metrics": {
      "tsr": 94.2,
      "p95-latency-ms": 850,
      "cvss-score": 3.8
    },
    "status": "HEALTHY",
    "recommendations": []
  }
}
```

#### `dependency-audit` 参数

```json
{
  "skill-name": "string (required)"
}
```

**返回值示例**：
```json
{
  "status": "success",
  "result": {
    "dependencies": [
      {"name": "requests", "version": "2.28.0", "latest": "2.32.0"}
    ],
    "cves": [
      {"id": "CVE-2024-XXXX", "severity": "critical", "fix": "upgrade to 2.32.0+"}
    ]
  }
}
```

**隔离决策验证**：
```python
# 伪代码
authorized = params["caller"] in {"CISO-001", "CTO-001"}
has_reason = len(params["reason"]) > 10
if not authorized:
    raise PermissionError("Only CISO-001 or CTO-001 can trigger emergency isolate")
if not has_reason:
    raise ValueError("Emergency isolate requires documented reason")
```

### 返回值 Schema

```json
{
  "status":   "success | error | pending | isolated",
  "task":     "<task-type>",
  "result":   { ... },
  "meta": {
    "reviewer":    "<agent-id>",
    "duration-ms": "<elapsed>",
    "cve-resolved": "<CVE-ID if security-patch>",
    "sla-status":  "WITHIN_SLA | BREACHING | RESOLVED"
  }
}
```

### 错误码

| Code | Meaning | Action |
|------|---------|--------|
| `E_SKILL_NOT_FOUND` | Skill 不存在 | 返回可用版本列表 |
| `E_UNAUTH_PATCH` | 未授权安全补丁 | 拒绝，通知 CISO |
| `E_CVE_SLA_BREACH` | CVE SLA 即将/已违约 | 上报 CTO + CISO |
| `E_ISOLATE_CONFLICT` | 已在隔离状态 | 返回当前状态 |
| `E_DEPENDENCY_CVE` | 依赖含已知 CVE | 返回 CVE 详情和修复建议 |
| `E_VERSION_CONFLICT` | 版本号冲突 | 返回正确版本号建议 |

### Agent 间调用示例

```markdown
# CTO-001 请求诊断
sessions_send(sessionKey="cto-isolated", message="
skill: ai-skill-maintainer
task: diagnose
params:
  skill-name: pdf-processor
  issue: User reports skill crashes when processing large files
  caller: CTO-001
priority: P2
isolated: true
")

# CISO-001 请求 CVE 紧急修复
sessions_send(sessionKey="ciso-isolated", message="
skill: ai-skill-maintainer
task: security-patch
params:
  skill-name: pdf-processor
  cve-id: CVE-2026-12345
  cvss-score: 9.1
  authorization: CISO-001
  caller: CISO-001
  changes:
    description: Fixed command injection via path parameter
    files: [scripts/process.py]
    test-results: All regression tests pass
emergency: true
")

# CQO-001 请求健康检查
sessions_send(sessionKey="cqo-isolated", message="
skill: ai-skill-maintainer
task: health-check
params:
  skill-name: pdf-processor
")
```

### 安全约束（接口层）

```
🚨 接口安全红线：
• skill-name 参数仅接受 [a-z0-9-] 字符，拒绝斜杠/点号（防止路径注入）
• authorization 字段仅接受 CISO-001 签名的安全任务
• emergency-isolate 仅接受 CISO-001 或 CTO-001 授权
• 隔离执行：所有 agent 调用必须在 isolated 会话中运行
• CVE 响应：CVSS ≥ 9.0 必须 15 分钟内响应，否则 SLA 违约告警
• 日志脱敏：返回结果不得含 caller 私人数据
```

### 与其他 Skill 的接口关系

| 调用方 | Task | 触发条件 |
|--------|------|---------|
| **CTO-001** | `diagnose`, `patch`, `emergency-isolate` | 版本管理/紧急响应 |
| **CISO-001** | `security-patch`, `emergency-isolate`, `dependency-audit` | CVE 处理/安全事件 |
| **CQO-001** | `health-check`, `diagnose` | 质量监控 |
| **ai-skill-creator** | `patch` (子 Skill) | 创作流程中发现 bug |
| **ai-skill-optimizer** | `dependency-audit` | 优化前基线检查 |

---

## 维护场景分类

| 场景 | 触发关键词 | 版本升级 | 安全审查 |
|------|-----------|---------|---------|
| Bug 修复 | "修复 bug"、"修复错误" | PATCH | 正常 |
| 功能增强 | "增强功能"、"新增功能" | MINOR | 正常 |
| 不兼容变更 | "Breaking Change"、"重构" | MAJOR | 正常 |
| 依赖安全补丁 | "安全补丁"、"CVE 修复" | PATCH | 🚨 紧急通道 |
| 废弃通知 | "废弃技能"、"停用" | PATCH | 正常 |

---

## 标准维护流程（五步）

### Step 1 — 诊断（Diagnosis）

**输入**：用户描述的问题或需求

**诊断清单**：

```markdown
## 诊断记录

Skill 名称：<name>
当前版本：<version>
问题类型：[Bug / 功能缺失 / 安全漏洞 / 依赖过时 / 其他]

### 问题描述
<用户描述>

### 复现步骤（如适用）
1.
2.
3.

### 影响范围
- 影响的功能：
- 影响的用户/Agent：

### 初步判断
- 根因：
- 修复方案：
- 版本影响：[PATCH / MINOR / MAJOR]
```

**CISO 安全场景判断**：

| 判断条件 | 结论 | 流程 |
|---------|------|------|
| 涉及 CVE/漏洞 | 🚨 安全紧急 | 跳至安全补丁流程 |
| 涉及凭证泄露 | 🚨 安全紧急 | 立即通知 + 紧急修复 |
| 涉及 PII 泄露 | 🚨 安全紧急 | 立即通知 + 紧急修复 |
| 其他 | ✅ 正常维护 | 继续标准流程 |

---

### Step 2 — 分析（Analysis）

**输出**：[references/maintenance-log.md](references/maintenance-log.md) 记录

#### 2.1 变更范围分析

```markdown
### 受影响文件
| 文件 | 变更类型 | 风险评估 |
|------|---------|---------|
| SKILL.md | [修改/新增/删除] | 🟢 低 |
| scripts/*.py | ... | ... |

### 兼容性影响
- 向后兼容：✅ / ❌
- 触发关键词变更：✅ / ❌（如有变更需通知用户）
- 工具权限变更：✅ / ❌

### 测试计划
- [ ] 本地测试用例：
- [ ] 回归测试：
```

#### 2.2 安全影响分析（CTO + CISO）

| 分析维度 | 检查项 | 结论 |
|---------|--------|------|
| **功能影响** | 修改是否改变核心功能？ | |
| **权限影响** | 权限是否变更？ | |
| **依赖影响** | 依赖是否新增/升级/删除？ | |
| **数据影响** | 是否影响数据处理？ | |
| **安全影响** | 变更是否影响安全边界？ | |

---

### Step 3 — 实施（Implementation）

#### 3.1 版本号更新

```bash
# 根据变更类型确定版本
# Bug 修复          → vX.Y.Z → vX.Y.(Z+1)
# 功能增强          → vX.Y.Z → vX.(Y+1).0
# Breaking Change   → vX.Y.Z → (X+1).0.0
# 安全补丁          → vX.Y.Z → vX.Y.(Z+1)  （强制）
```

#### 3.2 SKILL.md 更新

**更新 Frontmatter 版本**：
```yaml
---
name: <skill-name>
version: X.Y.Z   # ← 更新版本号
description: |   # ← 如有变更同步更新
  ...
---
```

**更新版本历史**（在文件顶部或底部）：
```markdown
## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| X.Y.Z | YYYY-MM-DD | <变更摘要> |
| ... | ... | ... |
```

#### 3.3 scripts/ 更新

**更新检查清单**：
```markdown
- [ ] 脚本已更新
- [ ] 脚本版本号已更新（如有版本机制）
- [ ] 依赖已更新（如有）
- [ ] 新增依赖已记录
- [ ] 脚本测试已通过
```

---

### Step 4 — 安全审查（Security Review）

> ⚠️ **强制门禁**：所有变更必须通过 CISO 安全审查

#### 4.1 变更 diff 审查

**审查变更内容**（对比上一版本）：
- 新增的代码是否含 RED FLAGS？
- 修改的代码是否引入新漏洞？
- 删除的代码是否影响安全边界？

#### 4.2 依赖审查

**检查依赖变更**：
```bash
# 列出新增/升级的依赖
# 检查 CVE
```

**CVE 响应 SLA**：

| CVSS | 严重性 | 修复 SLA |
|------|--------|---------|
| 9.0-10.0 | Critical | 24小时 |
| 7.0-8.9 | High | 7天 |
| 4.0-6.9 | Medium | 30天 |
| 0.1-3.9 | Low | 下个版本 |

#### 4.3 安全补丁紧急通道

**触发条件**：发现 Critical/High CVE

```
🚀 紧急通道流程：

1. 立即隔离：停止问题版本分发
2. 评估影响：确定受影响的 Skill 和版本
3. 紧急修复：最短路径修复漏洞
4. 快速审查：CISO 紧急审查（可跳过部分正常流程）
5. 紧急发布：Patch 版本，立即发布
6. 用户通知：通知所有受影响用户
```

---

### Step 5 — 验证与发布（Verify & Publish）

#### 5.1 验证清单

```markdown
## 发布前验证

- [ ] 变更内容与诊断一致
- [ ] 版本号符合变更类型
- [ ] 安全审查通过
- [ ] 脚本测试通过
- [ ] changelog 已更新
- [ ] SKILL.md 已同步更新
```

#### 5.2 发布命令

```bash
# 打包
clawhub package ./<skill-name> --output ./dist

# 发布
clawhub publish ./<skill-name> \
  --slug <skill-name> \
  --name "<Skill Name>" \
  --version X.Y.Z \
  --changelog "<变更摘要>"
```

#### 5.3 通知（如有必要）

```markdown
## 用户通知

如有 Breaking Change 或重要安全修复：
- 通知方式：在 Skill 描述中注明
- 通知内容：
  • 变更摘要
  • 升级建议
  • 兼容性问题（如有）
```

---

## 版本历史（Changelog）

| 版本 | 日期 | 变更内容 | 审核人 |
|------|------|---------|--------|
| **1.1.0** | 2026-04-13 | 新增 Agent 调用接口层（Inter-Agent Interface）：7个 Task 类型（diagnose/patch/security-patch/deprecate/emergency-isolate/health-check/dependency-audit）；CVE 紧急通道 SLA 体系；emergency-isolate 授权验证；与 ai-skill-creator / ai-skill-optimizer 接口关系定义 | CTO-001 / CISO-001 |
| **1.0.0** | 2026-04-11 | 初始版本：CTO 版本治理五步维护流程 + CISO 安全运营标准（漏洞响应 SLA + 补丁管理）+ 废弃管理流程 | CTO-001 / CISO-001 |

## 回滚策略（Rollback）

> 如维护操作失败，执行以下步骤恢复：

```bash
# 恢复到上一个可用版本
git checkout tags/v<上一版本> -- SKILL.md scripts/ references/

# 验证回滚成功
git log --oneline -3
```

**回滚触发条件**：
- `emergency-isolate` 后：满足 CVE 已修复 + CISO-001 复审通过 + CQO-001 验收通过后方可解除隔离
- `patch` 失败：回滚到隔离前版本，通知 CTO-001
- `deprecate` 误操作：恢复 `deprecated: false`，通知 CRO-001

---

## 废弃（Deprecation）管理

### 废弃流程

```
废弃通知（vX.Y.Z）→ 过渡期（建议 30天）→ 正式废弃（vX.Y.Z+1）
```

### 废弃 SKILL.md 模板

```markdown
---
name: <deprecated-skill>
version: X.Y.Z
description: |
  ⚠️ 【已废弃】此 Skill 已废弃，建议使用 `<new-skill>`。
  废弃日期：YYYY-MM-DD
  最后支持日期：YYYY-MM-DD
  迁移指南：见 references/migration.md
deprecated: true
replacement: <new-skill-name>
metadata:
  {"openclaw":{"emoji":"⚠️","os":["linux","darwin","win32"]}}
---

# ⚠️ 已废弃：<Skill Name>

## 废弃通知

此 Skill 已于 **YYYY-MM-DD** 正式废弃。

### 为什么废弃？
<原因>

### 替代方案
请使用 **<new-skill-name>**：
- 链接：clawhub install <new-skill>

### 时间线
- 废弃通知：YYYY-MM-DD（vX.Y.Z）
- 最后支持：YYYY-MM-DD（vX.Y.Z+1）
- 完全移除：待定

### 迁移指南
详见 [references/migration.md](references/migration.md)
```

---

## 维护记录

### 记录模板（保存至 `references/maintenance-log.md`）

```markdown
# Skill 维护记录

## Skill 信息
- 名称：<name>
- 当前版本：<version>
- 维护者：<maintainer>

## 维护历史

### 维护 #N — YYYY-MM-DD

**类型**：[Bug修复/功能增强/安全补丁/废弃/其他]
**版本**：<old> → <new>
**变更摘要**：<summary>

#### 变更详情
<detailed changes>

#### 安全审查
- CVSS：<score>
- 结论：[通过/拒绝/条件通过]

#### 测试结果
- [ ] 测试通过

#### 发布信息
- 发布日期：YYYY-MM-DD
- ClawHub 版本：<version>
```

---

## 快速参考

### 触发命令

| 用户请求 | 执行动作 |
|---------|---------|
| "修复 Skill XX 的 bug" | 诊断 → 分析 → 实施 → 安全审查 → 发布 |
| "为 Skill XX 增加 XX 功能" | 需求确认 → 分析 → 实施 → 安全审查 → 发布 |
| "升级 Skill XX 的依赖" | 依赖检查 → 兼容性分析 → 更新 → 安全审查 → 发布 |
| "发现 Skill XX 有安全漏洞" | 🚨 紧急通道 → 立即隔离 → 紧急修复 → 紧急发布 |
| "废弃 Skill XX" | 废弃评估 → 通知用户 → 发布废弃版本 → 保留迁移指南 |

### 常见错误

1. **版本号错误**：Bug 修复用 MAJOR 升级 → 应为 PATCH
2. **跳过安全审查**：紧急修复未做安全审查 → 必须补审
3. **不更新 changelog**：变更未记录 → 版本历史不完整
4. **Breaking Change 未通知**：未告知用户 → 用户升级后功能损坏
5. **废弃 Skill 未提供替代**：用户无法迁移 → 影响用户体验

---

## 版本历史（Changelog）

| 版本 | 日期 | 变更内容 | 审核人 |
|------|------|---------|--------|
| **1.1.0** | 2026-04-13 | 新增 Agent 调用接口层（Inter-Agent Interface）：7个 Task 类型（diagnose/patch/security-patch/deprecate/emergency-isolate/health-check/dependency-audit）；CVE 紧急通道 SLA 体系；emergency-isolate 授权验证；与 ai-skill-creator / ai-skill-optimizer 接口关系定义 | CTO-001 / CISO-001 |
| **1.0.0** | 2026-04-11 | 初始版本：CTO 版本治理五步维护流程 + CISO 安全运营标准（漏洞响应 SLA + 补丁管理）+ 废弃管理流程 | CTO-001 / CISO-001 |

## 回滚策略（Rollback）

> 如维护操作失败，执行以下步骤恢复：

```bash
# 恢复到上一个可用版本
git checkout tags/v<上一版本> -- SKILL.md scripts/ references/

# 验证回滚成功
git log --oneline -3
```

**回滚触发条件**：
- `emergency-isolate` 后：满足 CVE 已修复 + CISO-001 复审通过 + CQO-001 验收通过后方可解除隔离
- `patch` 失败：回滚到隔离前版本，通知 CTO-001
- `deprecate` 误操作：恢复 `deprecated: false`，通知 CRO-001

**解除 emergency-isolate 条件**：
1. CVE 已修复（CVSS < 7.0）
2. CISO-001 安全复审通过
3. CQO-001 质量验收通过
4. CTO-001 书面授权解除隔离
