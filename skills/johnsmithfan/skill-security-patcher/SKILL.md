---
name: "skill-security-patcher"
version: 1.0.0
description: "Skill 安全补丁响应工具（CVE 紧急通道 SLA 管理 + 漏洞修复 + 依赖审计）"
triggers: ["CVE修复", "安全补丁", "漏洞扫描", "依赖审计", "emergency-isolate"]
interface:
  inputs:
    type: "object"
    schema: |
      {
        "skill-name": "string (required)",
        "cve-id": "string (required for security-patch, e.g. CVE-YYYY-NNNNN)",
        "cvss-score": "number (required, 0.0-10.0)",
        "authorization": "string (required, must be CISO-001)",
        "caller": "string (required, agent ID)",
        "reason": "string (required for emergency-isolate)",
        "changes": {
          "description": "string",
          "files": "string[]",
          "test-results": "string"
        }
      }
  outputs:
    type: "object"
    schema: |
      {
        "fixed": "boolean",
        "new-version": "string",
        "notification-sent": "boolean",
        "sla-status": "WITHIN_SLA | BREACHING | RESOLVED"
      }
  errors:
    - code: "E_UNAUTH_PATCH"
      message: "未授权安全补丁，仅接受 CISO-001 授权"
      action: "拒绝，通知 CISO-001"
    - code: "E_CVE_SLA_BREACH"
      message: "CVE SLA 即将/已违约"
      action: "上报 CTO-001 + CISO-001"
    - code: "E_DEPENDENCY_CVE"
      message: "依赖含已知 CVE"
      action: "返回 CVE 详情和修复建议"
    - code: "E_ISOLATE_CONFLICT"
      message: "已在隔离状态"
      action: "返回当前隔离状态"
    - code: "E_CVE_SLA_BREACH"
      message: "CVE SLA 即将违约或已违约"
      action: "上报 CTO-001 + CISO-001 立即处理"
permissions:
  files: ["read:skills/", "write:skills/", "read:skill-registry.json"]
  network: []
  commands: []
  mcp: []
dependencies:
  skills: []
  cli: []
quality:
  saST: "✅Pass"
  vetter: "✅Approved"
  idempotent: true
metadata:
  license: "MIT-0"
  author: "ai-skill-maintainer@workspace"
  securityStatus: "✅Vetted"
  layer: "AGENT"
  size: "SMALL"
  parent: "ai-skill-maintainer"
  split_from: "2026-04-14"
---

# Skill 安全补丁响应器（CISO 安全运营标准）

> **执行角色**：CISO-001 安全运营
> **版本**：v1.0.0
> **来源**：ai-skill-maintainer §CVE紧急通道 + §emergency-isolate + §dependency-audit
> **合规**：CVE 响应 SLA + 授权验证

---

## 核心原则

1. **安全优先**：安全补丁不受正常发布周期限制
2. **授权强制**：仅 CISO-001/CTO-001 可触发紧急操作
3. **SLA 硬约束**：CVSS ≥ 9.0 必须 24 小时内响应
4. **最小暴露**：隔离期间最小化功能影响

---

## Inter-Agent 接口层

### 接口身份

| 属性 | 值 |
|------|-----|
| **接口 ID** | `skill-security-patcher-v1` |
| **调用方式** | `sessions_send` / `sessions_spawn` (isolated) |
| **会话目标** | `isolated`（强制隔离）|
| **最低权限** | L3（可读写 skills/ 指定目录） |
| **CISO 约束** | 🚨 安全补丁任务必须 CISO-001 授权 |

### TASK 消息格式

```json
{
  "skill": "skill-security-patcher",
  "version": "1.0.0",
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

---

## 可用 Task 类型

| Task | 参数 | 返回 | 说明 |
|------|------|------|------|
| `security-patch` | `skill-name`, `cve-id`, `cvss-score`, `authorization`, `caller`, `changes` | `{fixed, new-version, notification-sent}` | 🚨 CVE 修复 |
| `emergency-isolate` | `skill-name`, `reason`, `caller` | `{isolated, affected-versions}` | 🚨 紧急隔离（0-day）|
| `health-check` | `skill-name` | `{metrics, status}` | 健康检查 |
| `dependency-audit` | `skill-name` | `{dependencies[], cves[]}` | 依赖 CVE 扫描 |
| `diagnose` | `skill-name`, `issue`, `caller` | `{diagnosis, type, severity}` | 诊断安全/非安全问题 |

---

## Task 详细规格

### Task: `security-patch`

**CVE 紧急通道 SLA**：

| CVSS | 严重性 | 触发 | SLA | 流程 |
|------|--------|------|-----|------|
| **9.0–10.0** | Critical | 🚨 紧急隔离 + Patch | **≤ 24h** | 紧急通道直通 |
| **7.0–8.9** | High | 紧急 Patch | ≤ 7d | 标准通道加速 |
| **4.0–6.9** | Medium | 计划修复 | ≤ 30d | 标准通道 |
| **0.1–3.9** | Low | 跟踪 | 下个版本 | 常规流程 |

**参数 Schema**：

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

**安全红线**：
- `skill-name` 参数仅接受 `[a-z0-9-]` 字符，拒绝斜杠/点号（防止路径注入）
- `authorization` 字段仅接受 `CISO-001` 签名的安全任务
- 所有 agent 调用必须在 `isolated` 会话中运行

**返回值示例**：
```json
{
  "status": "success",
  "result": {
    "fixed": true,
    "new-version": "v1.2.1",
    "notification-sent": true,
    "sla-status": "RESOLVED"
  },
  "meta": {
    "reviewer": "CISO-001",
    "duration-ms": 3600000,
    "cve-resolved": "CVE-2026-12345",
    "sla-status": "WITHIN_SLA"
  }
}
```

---

### Task: `emergency-isolate`

**触发条件**：发现 Critical CVE（CVSS ≥ 9.0）或 0-day 漏洞

**授权验证伪代码**：
```python
authorized = params["caller"] in {"CISO-001", "CTO-001"}
has_reason = len(params["reason"]) > 10
if not authorized:
    raise PermissionError("Only CISO-001 or CTO-001 can trigger emergency isolate")
if not has_reason:
    raise ValueError("Emergency isolate requires documented reason (≥10 chars)")
```

**参数 Schema**：
```json
{
  "skill-name": "string (required)",
  "reason":     "string (required, CVE ID or incident description, ≥10 chars)",
  "caller":     "string (required, must be CISO-001 or CTO-001)"
}
```

**返回值示例**：
```json
{
  "status": "success",
  "result": {
    "isolated": true,
    "affected-versions": ["v1.0.0", "v1.1.0"],
    "isolation-time": "2026-04-14T00:00:00+08:00",
    "estimated-recovery": "2026-04-15T00:00:00+08:00"
  }
}
```

**解除 emergency-isolate 条件**：
1. CVE 已修复（CVSS < 7.0）
2. CISO-001 安全复审通过
3. CQO-001 质量验收通过
4. CTO-001 书面授权解除隔离

---

### Task: `health-check`

**参数 Schema**：
```json
{
  "skill-name": "string (required)"
}
```

> **健康阈值**：TSR < 92% → `UNHEALTHY`；P95 > 1200ms → `DEGRADED`；CVSS ≥ 7.0 → `HIGH_RISK`

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

---

### Task: `dependency-audit`

**参数 Schema**：
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

---

## Agent 间调用示例

```markdown
# CISO-001 请求 CVE 紧急修复
sessions_send(sessionKey="ciso-isolated", message="
skill: skill-security-patcher
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

# CTO-001 请求紧急隔离
sessions_send(sessionKey="cto-isolated", message="
skill: skill-security-patcher
task: emergency-isolate
params:
  skill-name: pdf-processor
  reason: CVE-2026-99999 critical remote code execution vulnerability discovered
  caller: CTO-001
")

# CQO-001 请求健康检查
sessions_send(sessionKey="cqo-isolated", message="
skill: skill-security-patcher
task: health-check
params:
  skill-name: pdf-processor
")
```

---

## CVE 扫描频率矩阵

| 扫描类型 | 频率 | 工具示例 |
|---------|------|---------|
| 依赖漏洞 | 每次 CI | npm audit, pip-audit, trivy |
| SAST（代码）| 每个 PR | Semgrep, CodeQL, Bandit |
| 密钥扫描 | 每次提交 | GitLeaks, truffleHog |
| 容器扫描 | 每次构建 | Trivy, Grype, Snyk |
| DAST（运行时）| 每周 | OWASP ZAP, Burp Suite, Nuclei |
| 云配置 | 每天 | ScoutSuite, Prowler, CloudSploit |
| 渗透测试 | 每季度 | 手动+自动 |

---

## 漏洞响应 SLA 矩阵

| CVSS | 严重性 | 修复 SLA | 响应团队 |
|------|--------|---------|---------|
| 9.0–10.0 | Critical | 24小时 | CTO + CISO 立即 |
| 7.0–8.9 | High | 7天 | Team Lead + Security |
| 4.0–6.9 | Medium | 30天 | Sprint Backlog |
| 0.1–3.9 | Low | 90天 | 跟踪 |

---

## 错误码参考

| Code | Meaning | Action |
|------|---------|--------|
| `E_UNAUTH_PATCH` | 未授权安全补丁 | 拒绝，通知 CISO-001 |
| `E_CVE_SLA_BREACH` | CVE SLA 即将/已违约 | 上报 CTO-001 + CISO-001 |
| `E_ISOLATE_CONFLICT` | 已在隔离状态 | 返回当前状态 |
| `E_DEPENDENCY_CVE` | 依赖含已知 CVE | 返回 CVE 详情和修复建议 |

---

## 版本历史

| 版本 | 日期 | 变更内容 | 审核人 |
|------|------|---------|--------|
| **1.0.0** | 2026-04-14 | 从 ai-skill-maintainer 拆分：Inter-Agent 接口层（5个Task）+ CVE 紧急通道 SLA + emergency-isolate 授权验证 + dependency-audit 任务 | CISO-001 |
