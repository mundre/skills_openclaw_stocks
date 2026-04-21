---
name: "AI Company Skill Ecosystem"
slug: "ai-company-ecosystem"
version: "2.0.0"
homepage: "https://clawhub.com/skills/ai-company-ecosystem"
description: |
  AI Company skills ecosystem registry. 29 standardized Skills covering governance,
  C-Suite Agents (11), Pipeline Skills (7), and Shared Tools.
license: MIT-0
tags: [ai-company, ecosystem, registry, c-suite, governance, pipeline]
triggers:
  - AI Company ecosystem
  - skill registry
  - C-Suite directory
  - ecosystem
interface:
  inputs:
    type: object
  outputs:
    type: object
  errors:
    - code: ECOSYSTEM_001
      message: "Skill not found in registry"
permissions:
  files: [read]
  network: []
  commands: []
  mcp: []
dependencies:
  skills:
    - ai-company-hq
    - ai-company-standardization
    - ai-company-modularization
    - ai-company-generalization
    - ai-company-audit
    - ai-company-conflict
  cli: []
quality:
  saST: Pass
  vetter: Approved
  idempotent: true
metadata:
  category: governance
  layer: AGENT
  cluster: ai-company
  maturity: STABLE
  license: MIT-0
  standardized: true
---

# AI Company Skill Ecosystem v2.0

> Complete registry for 29 AI Company Skills.

## Architecture

```
Layer 0: Governance (5) - standardization/modularization/generalization/audit/conflict
Layer 1: Hub (1) - ai-company-hq
Layer 2: C-Suite (11) - ceo/cfo/cmo/cto/ciso/clo/cho/cpo/cro/coo/cqo
Layer 3: Pipeline (7) - orchestrator/discovery/reviewer/builder/security-gate/knowledge-extractor/compliance-checker
Layer 4: Shared Tools (3) - kb/registry/hr
```

## Naming Convention

| Field | Format | Example |
|-------|--------|---------|
| name | AI Company {Function} | AI Company CMO Skill Discovery |
| slug | ai-company-{function} | ai-company-cmo-skill-discovery |

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-04-16 | +7 Pipeline Skills, v2.0 ecosystem |
| 1.0.0 | 2026-04-15 | Initial ecosystem |
