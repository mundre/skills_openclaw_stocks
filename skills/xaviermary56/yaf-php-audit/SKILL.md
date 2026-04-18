---
name: yaf-php-audit
version: 1.1.0
description: Audit legacy PHP projects, especially Yaf-based PHP 7.3 codebases, for architecture issues, security risks, performance problems, compatibility risks, and maintainability concerns. Works best with Yaf-style projects, but is also useful for first-pass triage of many traditional PHP codebases with similar structure. Use when reviewing a PHP/Yaf project, producing a structured code audit report, or triaging many similar projects with consistent audit dimensions.
emoji: 🔍
user-invocable: true
homepage: https://github.com/XavierMary56/OmniPublish
metadata:
  openclaw:
    requires:
      bins:
        - bash
        - grep
        - find
---

# Yaf PHP Audit

Audit a legacy PHP project with a focus on Yaf-style structure, PHP 7.3 compatibility, and practical risk discovery.

## Overview

Use this skill to produce a structured audit report for a single PHP project or to apply the same audit dimensions across many similar projects. Prefer evidence from code over assumptions. Prefer small, realistic remediation advice over broad refactors.

## Audit Workflow

1. Confirm the target project directory.
2. Identify the main entrypoints under `public`.
3. Read the request flow from entrypoint to controller, then to library/model/config where relevant.
4. Summarize the current structure before listing risks.
5. Focus on security, performance, reliability, and maintainability issues that have operational impact.
6. Distinguish confirmed issues from suspected risks.
7. Use `references/checklist.md` as the audit checklist and report skeleton.
8. Use `scripts/scan_project.sh` to perform a first-pass static scan before deeper manual review.

## Scope

Prioritize review of:

- `public`
- `application/controllers`
- `application/models`
- `application/library`
- `application/modules`
- `conf`

If present, also inspect:

- callback handlers
- payment flows
- cron/task scripts
- login/auth logic
- Redis usage
- external HTTP/RPC calls

## What to Check

### Structure and Architecture

Check for:

- mixed or unclear entry responsibilities
- controllers containing heavy business logic
- duplicated logic across controllers/modules
- scattered DB/Redis/HTTP calls without stable encapsulation
- confusing naming or inconsistent layering

### Security

Check for:

- SQL injection risk
- unsafe SQL string concatenation
- missing input validation
- weak callback verification
- upload/file handling risk
- dangerous functions such as `eval`, `exec`, `shell_exec`, `system`, `passthru`
- missing `timeout` / `connect_timeout` in external HTTP calls
- auth / permission bypass risk
- sensitive operations without sufficient logging

### Performance

Check for:

- N+1 query patterns
- queries inside loops
- excessive `SELECT *`
- missing cache abstraction
- Redis misuse
- expensive Redis commands such as `sdiff` / `sdiffstore`
- large batch tasks without chunking
- pagination / sorting patterns with full-scan risk

### Reliability and Consistency

Check for:

- idempotency problems in callbacks or retry paths
- race conditions around status updates
- missing transaction boundaries
- inconsistent cache update strategy
- fragile cron/task implementations
- missing failure logging on critical paths

### PHP 7.3 Compatibility

Flag syntax or patterns that require newer PHP versions. Do not recommend PHP 7.4+ or 8.x-only syntax unless you clearly mark it as incompatible with PHP 7.3.

### Business High-Risk Areas

Always pay extra attention to:

- payment
- callback / notify
- user status changes
- login/session
- risk-control logic
- scheduled jobs
- bulk processing
- data synchronization

## Reporting Format

Structure the audit output as:

1. target project
2. audit conclusion
3. project structure overview
4. current logic summary
5. risk findings
6. risk level and priority
7. remediation suggestions
8. verification suggestions

For each important finding, include:

- file path
- problem summary
- impact
- recommendation

## Bulk Audit Guidance

When many similar projects exist:

1. Apply the same checklist to every project.
2. Generate a short per-project summary first.
3. Rank projects by risk level and business criticality.
4. Spend the most attention on payment, callback, auth, Redis, SQL, and task-heavy projects.
5. Avoid writing long narrative reports for every low-risk project.

## Resource Usage

- Read `references/checklist.md` when you need the detailed checklist, risk grading guidance, or report template.
- Run `scripts/scan_project.sh <project-root> [output-file]` for a first-pass scan that highlights likely hotspots and optionally writes a text report to disk.
- Run `scripts/scan_workspace.sh <workspace-root> [output-dir]` to batch-scan many sibling projects and generate a summary table, high-risk list, and per-project text reports.

## Output Preference

Be concise but complete. The report should help humans decide what to fix first.
