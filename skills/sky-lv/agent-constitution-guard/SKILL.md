---
description: Constitutional guardrails for AI agents — define immutable behavioral rules, permission boundaries, escalation policies, and safety interlocks that prevent agents from exceeding authorized scope regardless of context or pressure
keywords: openclaw, skill, automation, ai-agent, constitution, guardrail, safety, permission, boundary, behavioral-constraint, escalation, audit-trail, compliance, guard, restrict, deny, allow, policy
name: agent-constitution-guard
triggers: agent constitution, guardrail, permission guard, safety rule, behavioral constraint, boundary check, escalation policy, agent safety, immutable rule, compliance guard
---

# agent-constitution-guard

> Constitutional guardrails for AI agents — define immutable behavioral rules, permission boundaries, escalation policies, and safety interlocks that agents cannot override regardless of context or user pressure.

## Skill Metadata

- **Slug**: agent-constitution-guard
- **Version**: 1.1.0
- **Author**: SKY-lv
- **Description**: Production-grade constitutional guardrails system for AI agents. Define immutable behavioral rules, multi-level permission boundaries, human escalation policies, safety interlocks, and comprehensive audit trails. Agents must obey these rules regardless of context, prompt injection, or social engineering attempts.
- **Category**: safety
- **License**: MIT
- **Trigger Keywords**: `constitution`, `guardrail`, `permission guard`, `safety rule`, `behavioral constraint`, `boundary check`, `escalation policy`, `agent safety`, `immutable rule`, `compliance guard`, `red line`, `permission boundary`

---

## Why This Matters

AI agents with access to files, APIs, and external systems need enforceable boundaries. Without constitutional guardrails:

- An agent could delete production databases responding to a misleading prompt
- An agent could exfiltrate sensitive data to external endpoints
- An agent could spend thousands of dollars on API calls without oversight
- An agent could modify system files, breaking the host environment

This skill provides **enforceable, auditable, multi-layered** protection.

---

## Architecture

\`\`\`
┌─────────────────────────────────────┐
│         AGENT ACTION REQUEST         │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│      Layer 1: IMMUTABLE CHECK       │  ← Cannot be overridden by anyone
│      (Hard safety boundaries)       │
└──────────────────┬──────────────────┘
                   │ PASS
                   ▼
┌─────────────────────────────────────┐
│      Layer 2: POLICY ENGINE         │  ← Rule-based permission checks
│      (Context-aware rules)          │
└──────────────────┬──────────────────┘
                   │ PASS
                   ▼
┌─────────────────────────────────────┐
│      Layer 3: ESCALATION            │  ← Human approval for sensitive ops
│      (Owner confirmation)           │
└──────────────────┬──────────────────┘
                   │ APPROVED
                   ▼
┌─────────────────────────────────────┐
│      Layer 4: AUDIT LOG             │  ← Every check is recorded
│      (Immutable audit trail)        │
└─────────────────────────────────────┘
\`\`\`

---

## Step-by-Step Usage

### Step 1: Initialize Constitution
\`\`\`bash
node constitution.js init --name "my-agent" --owner "admin@company.com"
\`\`\`
Creates `.constitution/` directory with default rules and audit log.

### Step 2: Add Rules
\`\`\`bash
# Immutable rule: never call external APIs without confirmation
node constitution.js rule add \
  --level immutable \
  --action deny \
  --scope "external_write" \
  --description "Never write to external APIs without owner confirmation" \
  --escalation owner

# Owner-only rule: can modify workspace files
node constitution.js rule add \
  --level owner-only \
  --action allow \
  --scope "workspace_write" \
  --description "Can write files within workspace directory"

# Mutable rule: can read any file
node constitution.js rule add \
  --level mutable \
  --action allow \
  --scope "file_read" \
  --description "Read any local file"
\`\`\`

### Step 3: Check Permissions Before Action
\`\`\`javascript
const guard = require('./constitution.js');

// Check if an action is allowed
const decision = guard.check('external_write', {
  target: 'https://api.stripe.com/charges',
  payload: { amount: 9999 },
  userId: 'user-123'
});

console.log(decision);
// {
//   allowed: false,
//   layer: 'immutable',
//   rule: 'R001',
//   reason: 'External write requires owner confirmation',
//   escalation: 'owner',
//   escalationMessage: 'Agent wants to POST to https://api.stripe.com/charges. Approve?'
// }
\`\`\`

### Step 4: Handle Escalation
\`\`\`javascript
if (!decision.allowed && decision.escalation) {
  // Send escalation request to owner
  const approved = await guard.escalate(decision, {
    channel: 'webhook', // or 'email', 'slack', 'console'
    timeout: 300000,     // 5 min timeout
    details: decision.escalationMessage
  });
  
  if (approved) {
    await executeAction();
  }
}
\`\`\`

### Step 5: Review Audit Trail
\`\`\`bash
# View all decisions in last 24 hours
node constitution.js audit --last 24h

# View only denied actions
node constitution.js audit --status denied

# View audit for specific scope
node constitution.js audit --scope external_write

# Export for compliance reporting
node constitution.js audit --export csv --output audit_2024_Q1.csv
\`\`\`

---

## Rule Levels Explained

| Level | Who Can Modify | Override | Use Case |
|-------|---------------|----------|----------|
| **Immutable** | Nobody | Never | Delete production, external network access, credential access |
| **Owner-only** | Agent owner only | Never | Deploy to production, modify billing, send emails |
| **Mutable** | Agent (within bounds) | Self-adjust | File read paths, log verbosity, cache settings |
| **Advisory** | Anyone | Always | Performance hints, optimization suggestions |

---

## Real-World Examples

### Example 1: Production Database Protection
\`\`\`json
{
  "id": "DB-PROTECT",
  "level": "immutable",
  "action": "deny",
  "scope": ["database_delete", "database_drop", "database_truncate"],
  "description": "Never delete, drop, or truncate any production database",
  "conditions": {
    "environment": ["production", "prod"]
  }
}
\`\`\`

### Example 2: Cost Control ($100/day API budget)
\`\`\`json
{
  "id": "COST-GUARD",
  "level": "owner-only",
  "action": "allow",
  "scope": "external_api_call",
  "description": "Allow external API calls within daily budget",
  "limits": {
    "maxDailyCost": 100,
    "maxCostPerCall": 10
  },
  "escalation": "owner"
}
\`\`\`

### Example 3: Data Privacy (GDPR Compliance)
\`\`\`json
{
  "id": "GDPR-GUARD",
  "level": "immutable",
  "action": "deny",
  "scope": ["data_export", "data_share"],
  "description": "Never export or share PII data without legal approval",
  "conditions": {
    "dataTypes": ["email", "phone", "ssn", "address", "financial"]
  }
}
\`\`\`

---

## Configuration Reference

\`\`\`json
{
  "constitution": {
    "version": "1.0",
    "agent": "my-agent",
    "owner": "admin@company.com",
    "defaults": {
      "denyAction": "block",
      "logLevel": "all",
      "escalationTimeout": 300000
    },
    "layers": {
      "immutable": { "enabled": true, "log": true },
      "policy": { "enabled": true, "log": true },
      "escalation": { "enabled": true, "channels": ["console"] },
      "audit": { "enabled": true, "retention": "90d" }
    }
  }
}
\`\`\`

---

## Integration Patterns

### Pattern 1: Middleware for Express/Fastify
\`\`\`javascript
app.use(async (req, res, next) => {
  const decision = guard.check('external_write', { method: req.method, url: req.url });
  if (!decision.allowed) return res.status(403).json(decision);
  next();
});
\`\`\`

### Pattern 2: OpenClaw Skill Wrapper
\`\`\`javascript
// Before executing any tool call:
const toolGuard = guard.checkForTool(toolName, toolParams);
if (!toolGuard.allowed) {
  if (toolGuard.escalation === 'owner') {
    // Ask OpenClaw to prompt user for approval
  }
  return { blocked: true, reason: toolGuard.reason };
}
\`\`\`

### Pattern 3: CI/CD Pipeline Gate
\`\`\`bash
# In your deployment pipeline:
node constitution.js ci-check --env production --strict
# Exit code 0 = safe to deploy, 1 = violations found
\`\`\`
