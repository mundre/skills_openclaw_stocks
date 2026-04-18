# Yaf PHP Audit Checklist

Use this checklist to keep reviews consistent across many similar PHP/Yaf projects.

## 1. Target Project

- Confirm project root.
- Confirm whether the project is really Yaf-style.
- Confirm whether the runtime target is PHP 7.3.
- Check whether there is a project-level `AGENTS.md` with extra constraints.

## 2. Structure Overview

Record:

- main directories
- `public` entrypoints
- controller/model/library/module layout
- config files
- task/callback/payment-related directories if present

## 3. Entry and Request Flow

Review:

- `public/api`
- `public/www`
- `public/web`
- `public/adm`
- `public/nav`
- `public/pwa`

Check:

- where bootstrap happens
- how routing reaches controllers
- whether there are custom dispatch rules
- whether entrypoints have mixed responsibilities

## 4. Security Checks

Look for:

- raw SQL concatenation
- direct use of `$_GET`, `$_POST`, `$_REQUEST` without validation
- dangerous functions: `eval`, `exec`, `shell_exec`, `system`, `passthru`, `unserialize`
- file upload and path handling risks
- callback signature or source verification weaknesses
- auth/permission checks that appear easy to bypass
- secrets or credentials committed to config/code
- hardcoded passwords / api_key / token literal strings (`password = 'value'`, `api_key = "value"`)
- login, logout, session, auth, permission, role, privilege keyword clusters (confirm auth coverage)

## 5. Performance Checks

Look for:

- database access inside loops
- repeated model queries in loops
- `SELECT *` on large tables
- missing pagination limits
- Redis anti-patterns
- blocked external calls on request path
- no timeout / connect_timeout on HTTP requests
- `foreach` / `for` / `while` containing direct model or DB call (N+1 pattern)
- `static $cache = []` or `static $var = array()` used as in-process cache antipattern

## 6. Reliability Checks

Look for:

- callback re-entry and idempotency problems
- status changes without transaction protection
- cache/database inconsistency windows
- weak retry behavior
- missing error handling and failure logs
- fragile batch and task scripts

## 7. Compatibility Checks

Look for code that assumes PHP 7.4+ or 8.x features, including:

- match expressions
- constructor property promotion
- union types
- attributes
- nullsafe operator
- enums
- readonly

## 8. High-Risk Business Flows

Review with extra care:

- payment
- callback / notify
- login/session
- user status changes
- risk-control logic
- scheduled tasks
- batch processing
- data sync jobs

## 9. Risk Grading

### High

- exploitable security risk
- payment/callback/login state inconsistency
- clear data corruption or major reliability risk
- obvious full-scan / N+1 / blocking external dependency on critical path
- hardcoded credential (password, api_key, secret) confirmed in source code

### Medium

- significant maintainability problem with operational impact
- probable performance issue under load
- weak validation or weak logging on sensitive path
- structure issues that increase defect risk

### Low

- style issue with little operational impact
- low-confidence suspicion with limited evidence
- documentation/naming issues only

## 10. Batch Audit Workflow

When auditing many similar projects:

1. Run `scripts/scan_workspace.sh <workspace-root> [output-dir]`.
2. Review `summary.csv` or `summary.md` first.
3. Sort by `risk_level`, then prioritize projects tagged `payment-heavy`, `callback-heavy`, `task-heavy`, or `dangerous-fns`.
4. Only deep-read the highest-risk projects first.
5. Keep the per-project reports as evidence snapshots, not final audit conclusions.

## 11. Report Template

### Target project

- project name:
- path:
- type:

### Audit conclusion

- one-paragraph summary

### Project structure overview

- entrypoints:
- main modules:
- notable directories:

### Current logic summary

- request flow:
- key business areas:

### Risk findings

For each finding record:

- level:
- file:
- summary:
- impact:
- recommendation:
- confidence: confirmed / suspected

### Priority suggestions

- P0:
- P1:
- P2:

### Verification suggestions

- syntax check
- minimal functional path
- callback retry path
- repeated request/idempotency path
- SQL/Redis hotspot validation if applicable
