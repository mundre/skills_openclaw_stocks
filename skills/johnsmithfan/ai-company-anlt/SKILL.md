---
name: "AI Company ANLT"
slug: "ai-company-anlt"
version: "1.2.0"
homepage: "https://clawhub.com/skills/ai-company-anlt"
description: |
  AI Company dataanalyzeexecute层 Agent。支持多源data采集、automation报表生成、data洞察提取、data脱敏handle、
  cross-border data complianceassess。归 CFO 所有、CQO 质量supervise、CLO compliancesupervise。
  trigger关键词：dataanalyze、生成报表、data洞察、财务analyze、运营data、data采集、
  data analysis、generate report。
license: MIT-0
tags: [ai-company, execution-layer, data-analysis, reporting, financial]
triggers:
  - dataanalyze
  - 生成报表
  - data洞察
  - 财务analyze
  - 运营data
  - data采集
  - data analysis
  - generate report
interface:
  inputs:
    type: object
    schema:
      type: object
      properties:
        analysis-type:
          type: string
          enum: [financial, operational, marketing, custom]
          description: analyze类型
        data-sources:
          type: array
          items: string
          description: data源标识符列表
        date-range:
          type: object
          properties:
            start: string
            end: string
        report-format:
          type: string
          enum: [table, chart, narrative, dashboard]
          description: 输出格式
        include-forecast:
          type: boolean
          description: 是否包含预测analyze，默认 false
        sensitivity:
          type: string
          enum: [public, internal, confidential, restricted]
          description: data敏感级别
      required: [analysis-type, date-range]
  outputs:
    type: object
    schema:
      type: object
      properties:
        report:
          type: object
          description: analyzereport内容
        insights:
          type: array
          items:
            type: object
            properties:
              insight: string
              confidence: number
              source: string
        data-accuracy:
          type: number
          description: dataaccuracy（Goal >=99.5%）
        pii-detected:
          type: boolean
        pii-fields:
          type: array
          description: detect到的 PII 字段
        cross-border-flag:
          type: boolean
          description: 跨境data传输标记
        compliance-status:
          type: string
          enum: [pass, conditional, fail]
        data-classification:
          type: string
  errors:
    - code: ANLT_001
      message: "data源不可用，请检查data源配置"
    - code: ANLT_002
      message: "dataaccuracy低于threshold（99.5%），请verifydata源"
    - code: ANLT_003
      message: "detect到 PII data，需完成脱敏handle后方可输出"
    - code: ANLT_004
      message: "跨境data传输risk，请完成complianceassess后重试"
permissions:
  files: [read]
  network: [api]
  commands: []
  mcp: [sessions_send, subagents]
dependencies:
  skills: [ai-company-hq, ai-company-cfo, ai-company-cro, ai-company-cqo, ai-company-clo, ai-company-audit]
  cli: []
quality:
  saST: Pass
  vetter: Approved
  idempotent: true
metadata:
  category: functional
  layer: EXEC
  cluster: ai-company
  maturity: STABLE
  license: MIT-0
  standardized: true
  generalization-level: L3
  role: EXEC-003
  owner: CFO
  co-owner: [CQO, CLO]
  exec-batch: 2
  emoji: "📊"
  os: ["linux", "darwin", "win32"]
ciso:
  risk-level: medium-high
  cvss-target: "<6.5"
  threats: [InformationDisclosure, Tampering]
  stride:
    spoofing: pass
    tampering: pass
    repudiation: pass
    info-disclosure: pass
    denial-of-service: pass
    elevation: pass
cqo:
  quality-gate: G3
  kpis:
    - "data-accuracy: >=99.5%"
    - "report-on-time: >=95%"
    - "insight-adoption-rate: >=70%"
    - "desensitization-compliance: 100%"
    - "null-value-handling: 100%"
    - "update-latency: <=T+4h"
  report-to: [CFO, CQO, CRO]
---

# AI Company ANLT — dataanalyzeexecute层

## Overview

EXEC-003 dataanalyzeexecute层 Agent，归 CFO 所有、CQO 质量supervise、CLO compliancesupervise。
负责 AI Company 所有结构化dataanalyze任务，是 CFO 财务control的dataexecute抓手。
**compliance前置**：go live前必须完成complianceassess、data分类分级policy、跨境传输securityassess。

## 核心Function

### Module 1: 多源data采集

支持的data源：
- **内部**：kb（知识库）、registry（Agent 注册data）、audit（日志）
- **外部**：通过白名单 API 端点（需 CISO approve域名）

采集process：
1. verifydata源authorize
2. executedata提取（仅读取，不缓存原始data）
3. data质量verify（null 值detect、格式verify）

### Module 2: automation报表生成

按预设模板生成standard化报表：

| 类型 | 模板 | 典型用户 |
|------|------|---------|
| `financial` | 收入/支出/利润率/cash flow | CFO |
| `operational` | 运营metric/效率/KPI 仪表板 | COO |
| `marketing` | 渠道效果/转化率/ROI | CMO |
| `custom` | on-demand自Definition | CFO/COO |

### Module 3: data洞察提取

从data中自动identify：
- 趋势变化（环比/同比）
- 异常值detect（超出 2 sigma triggeralert）
- 机会点（增长拐点、新模式identify）

### Module 4: data脱敏（Privacy by Design）

**自动 PII detect和handle**：
- 姓名、身份证号、手机号、邮箱 → 自动脱敏
- 金融账户、信用卡 → 强制屏蔽
- detect到 PII → trigger ANLT_003，阻断原始data输出

### Module 5: cross-border data compliance检查

涉及跨境data传输时：
1. identifydata跨境（源 IP 不等于Goal区域）
2. trigger cross-border-flag = true
3. trigger ANLT_004，等待 CLO confirm后方可继续

### Module 6: ANLT → CRO data流接口（P1-11）

> **背景**：ANLT execute层归 CFO 所有，但 CRO 的riskassess需要 ANLT 的dataanalyze结果。本模块Definitionstandard化的 ANLT → CRO data供给接口。

#### 6.1 data流拓扑

```
[ANLT dataanalyze引擎]
    │
    ├── → CFO（主归属）
    │       report + insights + compliance-status
    │
    └── → CRO（次级输出，通过 HQ 路由）
            risk-assessment-data + fair-input-data
```

#### 6.2 CRO 所需data字段standard

| data字段 | 类型 | Description | FAIR 映射 |
|---------|------|------|---------|
| `tx_failure_rate` | float (0.0-1.0) | 交易失败率 | → LEF |
| `daily_loss_usd` | float | 日度财务损失估算 | → LM |
| `cash_flow_coverage` | float | cash flowcoverage | → LM |
| `module_losses[]` | array | 各 AI 模块亏损列表 | → LM breakdown |
| `anomaly_signals[]` | array | 异常信号列表（2-sigma trigger） | → LEF |
| `trend_forecast` | object | 趋势预测（monthly） | → LM 预测 |
| `sla_breach_count` | int | SLA 违约次数 | → LM |
| `report_timestamp` | ISO-8601 | 报表时间戳 | - |

#### 6.3 ANLT → CRO 传输格式

```json
{
  "source": "ANLT",
  "destination": "CRO",
  "route": "ANLT→HQ→CRO",
  "exec_id": "EXEC-003",
  "report_timestamp": "<ISO-8601>",
  "financial_data_for_risk": {
    "tx_failure_rate": 0.035,
    "daily_loss_usd": 3200.50,
    "cash_flow_coverage": 0.95,
    "module_losses": [
      {"module_id": "ML-001", "loss_usd": 1800, "trend": "increasing"},
      {"module_id": "ML-002", "loss_usd": 1400.50, "trend": "stable"}
    ],
    "anomaly_signals": [
      {"signal": "tx_failure_rate", "value": 0.035, "threshold": 0.05, "status": "approaching"},
      {"signal": "daily_loss", "value": 3200.50, "threshold": 5000, "status": "normal"}
    ],
    "sla_breach_count": 3,
    "trend_forecast": {
      "metric": "monthly_loss",
      "predicted_value_usd": 95000,
      "confidence": 0.82,
      "period": "T+30d"
    }
  },
  "fair_input": {
    "LEF_raw_signals": ["anomaly_signals.length", "sla_breach_count"],
    "LM_raw_signals": ["daily_loss_usd", "cash_flow_coverage"],
    "preliminary_LEF_level": "中",
    "preliminary_LM_level": "高",
    "preliminary_risk_level": "P1"
  },
  "compliance_status": "pass",
  "quality_gate": "G3",
  "owner": "CFO",
  "co_owner": ["CQO", "CLO"]
}
```

#### 6.4 传输trigger规则

| trigger条件 | trigger频率 | 目的地 | 备注 |
|---------|---------|--------|------|
| 每日财务报表生成完成 | 每日 23:59 UTC | CRO Monitor（通过 HQ 路由） | 自动push，无需 CRO 请求 |
| 异常信号trigger（2-sigma） | real-time | CRO Monitor（通过 HQ 路由） | 优先级 HIGH，≤500ms 到达 |
| 趋势预测report生成 | 每月最后1日 | CRO Monitor（通过 HQ 路由） | 供 CRO monthlyreport使用 |
| CRO 主动请求data | on-demand | 直接respond | 通过 HQ 路由请求，CRO SLA ≤ 1200ms |

#### 6.5 CRO data质量要求

- **accuracy**：ANLT data到达 CRO 前必须通过 G3 quality gate（≥99.5%）
- **latency**：日常data ≤ T+4h，异常alertdata ≤ 500ms
- **完整性**：所有字段必须非空，缺失字段标注 `null`
- **audit**：每次 ANLT → CRO 传输必须写入audit日志（retention: 7 years）

---

## 7、continuouscompliancereviewmechanism（P2-14）

> **Goal**：ANLT 作为datahandleexecute层，handle多源敏感data，需establishcontinuouscompliancereviewmechanism，ensure长期compliance运营。本模块Definitionquarterlycompliancereviewprocess。

### 7.1 quarterlycompliancereviewframework

| review维度 | review内容 | review方式 | 负责方 |
|---------|---------|---------|--------|
| data采集compliance | data源authorize有效性、API 白名单compliance | automation扫描 + 人工抽查 | CLO + CQO |
| PII 脱敏有效性 | 脱敏规则有效性、漏检率 | 样本抽查（monthly） | CQO |
| cross-border data compliance | cross-border-flag trigger准确性、approveprocess完整性 | quarterlyaudit | CLO |
| data质量稳定性 | accuracy趋势、null 值handle率 | monthly统计 | CQO |
| CRO data供给 | ANLT → CRO data完整性、及时性 | quarterlyaudit | CRO |
| audit日志完整性 | 所有操作写入audit日志，无遗漏 | monthly核查 | CLO |

### 7.2 quarterlycompliancereviewprocess

```
【quarterlyreview日历】
Q1: 3月最后工作日 | Q2: 6月最后工作日 | Q3: 9月最后工作日 | Q4: 12月最后工作日

1. CQO 发起quarterlycompliancereview（提前 5 个工作日notify ANLT）
   ↓
2. ANLT 准备quarterlydata包（audit日志 + data质量report + 脱敏record）
   ↓
3. CQO executecompliancereview（dataaccuracy + 脱敏有效性 + audit日志完整性）
   ↓
4. CLO execute跨境compliancereview（cross-border-flag triggerrecord + approveprocess）
   ↓
5. CQO + CLO 联合出具quarterlycompliancereviewreport
   ↓
6. report抄送 CFO + CRO + CEO
   ↓
7. discover项 → develop整改计划 → 纳入下quarterlyreview重点
```

### 7.3 quarterlycompliancereviewreport模板

```json
{
  "report_id": "<UUID>",
  "period": "<YYYY-Q1/Q2/Q3/Q4>",
  "review_date": "<ISO-8601>",
  "conducted_by": ["CQO", "CLO"],
  "scope": {
    "data_accuracy_avg": "<0.995-1.0>",
    "pii_desensitization_rate": "<0.0-1.0>",
    "cross_border_reviews_completed": "<int>",
    "audit_log_coverage": "<0.0-1.0>"
  },
  "findings": [
    {
      "finding_id": "<int>",
      "severity": "<P1|P2|P3>",
      "description": "<描述>",
      "affected_module": "<Module N>",
      "remediation_plan": "<整改计划>",
      "due_date": "<ISO-8601>"
    }
  ],
  "overall_status": "<pass|conditional|fail>",
  "next_review": "<ISO-8601>"
}
```

### 7.4 compliancereviewtrigger条件（额外review）

除quarterlyreview外，以下条件trigger额外compliancereview：

| trigger条件 | trigger类型 | execute方 | 时限 |
|---------|---------|--------|------|
| accuracy连续 2 周 < 99.5% | 紧急review | CQO | 48h 内 |
| PII 漏检event | 紧急review | CQO + CLO | 24h 内 |
| 跨境data异常trigger | 紧急review | CLO | 24h 内 |
| 新增data源接入 | go live前review | CLO + CISO | go live前完成 |
| 监管法规重大变更 | 专项review | CLO | 法规生效前完成 |

---

## 8、G3 门禁approveprocess（P2-15）

> **Goal**：Definition ANLT dataanalyze输出的 G3 门禁trigger条件和approveprocess，ensure高敏感度或高risk输出经过充分review后方可释放。

### 8.1 G3 门禁定位

G3 门禁是 CQO quality assurancesystem的最高级别门禁，要求输出经过 CQO + 相关方联合approve后方可释放。ANLT 的 G3 门禁与 CQO system完全对齐。

### 8.2 G3 trigger条件（ANLT 专项）

当 ANLT analyze输出满足以下任1条件时，自动trigger G3 门禁approveprocess：

| trigger条件 | 条件Description | risk等级 | 联合approve方 |
|---------|---------|---------|-----------|
| **G3-A：跨境高敏感data输出** | cross-border-flag = true 且 sensitivity = restricted | P1 | CLO + CQO + CFO |
| **G3-B：PII data无法完全脱敏** | PII 字段占比 > 20% 或涉及高敏感 PII（身份证/护照/生物特征） | P1 | CLO + CQO |
| **G3-C：CRO risk评级 P0/P1** | ANLT 输出的 FAIR 预analyze risk_level = P0 或 P1 | P1 | CRO + CQO |
| **G3-D：财务data对外披露** | sensitivity = confidential/restricted 且 report-format = external（如 PDF/邮件外发） | P1 | CFO + CQO |
| **G3-E：SLA 违约责任data** | 输出涉及 SLA 违约金额计算或赔付建议 | P1 | CFO + CLO |
| **G3-F：趋势预测对外披露** | include-forecast = true 且 sensitivity = internal 及以上 | P2 | CFO + CQO |
| **G3-G：新增data源接入analyze** | analyze结果将影响data源接入决策 | P2 | CISO + CQO |

### 8.3 G3 门禁approveprocess

```
[ANLT analyze完成]
    │
    ├── 自动detect G3 trigger条件
    │
    ├── 无trigger → 直接输出（G1/G2 门禁）
    │
    └── trigger G3 → 暂停输出（hold状态）
           │
           1. ANLT 生成 G3 approve请求包
              ├── analyzereport草稿
              ├── trigger条件Description
              ├── data来源清单
              ├── PII/敏感data清单
              └── 预期riskassess
           ↓
           2. notifyapprove方（sessions_send）
              ├── G3-A → CLO + CQO + CFO
              ├── G3-B → CLO + CQO
              ├── G3-C → CRO + CQO
              ├── G3-D → CFO + CQO
              ├── G3-E → CFO + CLO
              ├── G3-F → CFO + CQO
              └── G3-G → CISO + CQO
           ↓
           3. 各approve方独立review（SLA：48h 内反馈）
              ├── approve通过 → 签署approve意见
              ├── 有条件通过 → 提出修改要求
              └── reject → Description原因，ANLT 修订后重新submit
           ↓
           4. 所有approve方均通过 → CQO 出具最终放行指令
           ↓
           5. ANLT execute输出 → 写入audit日志（含所有approve方意见）
           ↓
           6. 存档：approve包保留 7 年
```

### 8.4 G3 approve包格式

```json
{
  "gate_id": "<UUID>",
  "gate_level": "G3",
  "trigger_condition": "<G3-A 至 G3-G>",
  "anlt_exec_id": "EXEC-003",
  "report_summary": "<report摘要（500字内）>",
  "sensitivity": "<public|internal|confidential|restricted>",
  "cross_border_flag": "<boolean>",
  "pii_summary": {
    "pii_fields_detected": ["<字段列表>"],
    "desensitization_applied": "<boolean>",
    "desensitization_rate": "<0.0-1.0>"
  },
  "risk_assessment": {
    "fair_prelim": "<P0|P1|P2|P3>",
    "key_risks": ["<risk描述>"]
  },
  "approvals": [
    {
      "approver": "<role>",
      "decision": "<approved|conditional|rejected>",
      "comments": "<approve意见>",
      "timestamp": "<ISO-8601>"
    }
  ],
  "release_status": "<released|rejected|pending>",
  "release_timestamp": "<ISO-8601，释放时填写>"
}
```

### 8.5 G3 门禁 SLA

| approvephase | SLA | 超时处置 |
|---------|-----|---------|
| ANLT → approve方notify | real-time（<1min） | 自动upgrade至 CEO |
| approve方respond | ≤ 48h | 视为"无异议通过"，CQO 可代理approve |
| 全部approve完成 → 释放 | ≤ 72h | 连续 2 次超时 → CEO 干预 |

### 8.6 G3 audit要求

所有 G3 门禁event必须写入audit日志：

```json
{
  "agent": "ai-company-anlt",
  "exec_id": "EXEC-003",
  "gate_event": "G3_triggered | G3_approved | G3_rejected | G3_released",
  "gate_id": "<UUID>",
  "trigger_condition": "<G3-A 至 G3-G>",
  "sla_met": "<boolean>",
  "approvers": ["<全部approve方>"],
  "release_timestamp": "<ISO-8601>"
}
```

---

## security考虑

### CISO STRIDE assess

| 威胁 | 结果 | defend措施 |
|------|------|---------|
| Spoofing | Pass | 仅调用白名单域名 API |
| Tampering | Pass | 不修改源data，只读操作 |
| Repudiation | Pass | 所有查询record完整audit |
| Info Disclosure | Pass | PII 自动脱敏，敏感data不落盘 |
| Denial of Service | Pass | 查询超时 60s，超限circuit breaker |
| Elevation | Pass | 不请求 exec，最小permissionprinciple |

### prohibit行为

- prohibit直接访问原始data库（必须通过 API）
- prohibit导出未经脱敏的原始data
- prohibit缓存原始data（只保留聚合结果）
- prohibit跨区域data传输（无 CLO authorize）

## audit要求

### 必须record的audit日志

```json
{
  "agent": "ai-company-anlt",
  "exec-id": "EXEC-003",
  "timestamp": "<ISO-8601>",
  "action": "data-collection | report-generation | insight-extraction",
  "data-sources": ["<sources-accessed>"],
  "data-volume": {"records": "<number>", "pii-detected": "<boolean>"},
  "cross-border-flag": "<boolean>",
  "compliance-status": "<pass|conditional|fail>",
  "quality-gate": "G3",
  "owner": "CFO"
}
```

## 与 C-Suite 的接口

| 方向 | 通道 | 内容 |
|------|------|------|
| HQ → ANLT | sessions_send | analysis-type + data-sources + date-range |
| ANLT → CFO | sessions_send | report + insights + compliance-status |
| ANLT → CLO | sessions_send | cross-border-flag triggered |

## 常见错误

| 错误码 | 原因 | handle方式 |
|--------|------|---------|
| ANLT_001 | data源不可用 | 返回错误，列出可用data源 |
| ANLT_002 | accuracy低于threshold | 阻断，提示verifydata源 |
| ANLT_003 | PII detect | 阻断，脱敏后重试 |
| ANLT_004 | 跨境datarisk | 阻断，等待 CLO confirm |

| 1.0.0 | 2026-04-15 | 重建版本：standard化+模块化+通用化 L3，完整 ClawHub Schema v1.0 |
| 1.1.0 | 2026-04-19 | P1-11：新增 ANLT→CRO data流接口（第6章），Definition CRO riskassess所需data字段standard |
| 1.2.0 | 2026-04-19 | P2-14：quarterlycompliancereviewprocess(第102章)；P2-15：G3门禁approveprocess(第103章) |
