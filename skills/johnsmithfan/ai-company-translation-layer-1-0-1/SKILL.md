---
name: ai-company-translation-layer
slug: ai-company-translation-layer
version: 1.0.1
homepage: https://clawhub.com/skills/ai-company-translation-layer
description: |
  AI Company EXEC translation layer coordination hub. Orchestrates four specialized
  translation agents (EN/ZH/RU/FR) for SKILL.md and documentation files. Routes translation
  requests to the appropriate language agent based on target language. Owned by CMO;
  quality supervised by CQO; security supervised by CISO.
  Trigger keywords: translate skill, translate documentation, translation layer,
  multi-language translation, translation coordination.
license: MIT-0
tags: [ai-company, execution-layer, translation, orchestration, coordinator, wrtr, aigc]
triggers:
  - translate skill
  - translate documentation
  - translation layer
  - multi-language translation
  - translation coordination
interface:
  inputs:
    type: object
    schema:
      type: object
      properties:
        source-file:
          type: string
          description: Absolute path to source file to translate
        target-language:
          type: string
          enum: [en, zh, ru, fr, auto]
          description: Target language; 'auto' detects from source
        style:
          type: string
          enum: [technical, formal, marketing, legal]
          default: technical
        output-dir:
          type: string
          description: Output directory (defaults to same dir as source)
      required: [source-file, target-language]
  outputs:
    type: object
    schema:
      type: object
      properties:
        agent-assigned:
          type: string
          description: Agent ID that handled the translation
        output-path:
          type: string
          description: Path to translated file
        quality-score:
          type: number
        aigc-mark:
          type: boolean
permissions:
  files: [read workspace, write workspace]
  network: []
  commands: []
  mcp: [sessions_send, sessions_spawn]
dependencies:
  skills: [ai-company-hq, ai-company-registry, ai-company-audit,
           ai-company-cmo, ai-company-cqo, ai-company-ciso]
ciso:
  risk-level: medium
  cvss-target: "<7.0"
  threats: [Tampering, InformationDisclosure]
  mitigations:
    - Path traversal rejection on all file operations
    - No external network calls
    - Audit log all routing decisions
cqo:
  quality-gate: G2
  kpis:
    - "routing-accuracy: >=99%"
    - "translation-quality: >=85%"
metadata:
  category: functional
  layer: EXEC
  cluster: ai-company
  maturity: BETA
  license: MIT-0
  standardized: true
  generalization-level: L3
  role: EXEC-TR-COORD
  owner: CMO
  co-owner: [CQO, CISO]
  exec-batch: 4
  emoji: "🌐"
  os: [linux, darwin, win32]
---

# AI Company EXEC Translation Layer — Coordinator (v1.0.0)

> **Agent Role**: Execution Layer — Translation Coordination Hub (EXEC-TR-COORD)  
> **Owner**: CMO | **Quality**: CQO | **Security**: CISO  
> **Risk Level**: Medium | CVSS Target: <7.0 | Quality Gate: G2  
> **Language**: Fully English | ClawHub Schema v1.0 | Harness Engineering Compliant

---

## 1. Purpose & Scope

The Translation Layer Coordinator routes translation requests to the appropriate
specialized translation agent (EXEC-TR-EN, EXEC-TR-ZH, EXEC-TR-RU, EXEC-TR-FR)
based on the target language parameter.

**Sub-Agents**:

| Agent | Target Language | Role ID | Emoji |
|-------|----------------|---------|-------|
| EXEC-TR-EN | English | EXEC-TR-EN | 🇬🇧 |
| EXEC-TR-ZH | Chinese (Simplified) | EXEC-TR-ZH | 🇨🇳 |
| EXEC-TR-RU | Russian | EXEC-TR-RU | 🇷🇺 |
| EXEC-TR-FR | French | EXEC-TR-FR | 🇫🇷 |

---

## 2. Routing Logic

```
Input: source-file + target-language + style + output-dir

Step 1: Validate source-file (exists, <10MB, no path traversal)
Step 2: Route to appropriate agent:
  - target-language == 'en'  → ai-company-translator-en-1.0.0
  - target-language == 'zh'  → ai-company-translator-zh-1.0.0
  - target-language == 'ru'  → ai-company-translator-ru-1.0.0
  - target-language == 'fr'  → ai-company-translator-fr-1.0.0
  - target-language == 'auto' → detect source language, route accordingly
Step 3: Delegate to target agent via sessions_spawn (isolated)
Step 4: Aggregate results, update registry
Step 5: Return consolidated output
```

---

## 3. Registry Entries (All 4 Agents)

```yaml
agents:
  - id: EXEC-TR-EN
    name: ai-company-translator-en
    slug: ai-company-translator-en
    version: 1.0.0
    target-language: en
    emoji: "🇬🇧"
    status: active
    owner: CMO

  - id: EXEC-TR-ZH
    name: ai-company-translator-zh
    slug: ai-company-translator-zh
    version: 1.0.0
    target-language: zh
    emoji: "🇨🇳"
    status: active
    owner: CMO

  - id: EXEC-TR-RU
    name: ai-company-translator-ru
    slug: ai-company-translator-ru
    version: 1.0.0
    target-language: ru
    emoji: "🇷🇺"
    status: active
    owner: CMO

  - id: EXEC-TR-FR
    name: ai-company-translator-fr
    slug: ai-company-translator-fr
    version: 1.0.0
    target-language: fr
    emoji: "🇫🇷"
    status: active
    owner: CMO
```

---

## 4. Verification Checklist

- [x] ClawHub Schema v1.0 frontmatter
- [x] No hardcoded paths
- [x] 4 sub-agents registered
- [x] Routing logic documented
- [x] Harness Engineering compliant
- [x] CISO STRIDE mitigations documented
- [x] CQO G2 quality gate documented
