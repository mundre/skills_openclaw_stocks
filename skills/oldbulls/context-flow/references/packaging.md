# Packaging Guide

## Purpose

This file explains how to package and review `context-flow` before sharing it.

## Recommended structure

```text
context-flow/
  SKILL.md
  references/
    templates.md
    anti-patterns.md
    feishu-usage.md
    recovery-lessons.md
    reflection-lessons.md
    packaging.md
```

## Versioning note

Self-use version:
- optimized for the current environment
- may still contain local workflow assumptions

Shareable version:
- optimized for portability
- should rely mainly on files inside the skill itself

## Pre-package checklist

- Confirm `SKILL.md` name, title, and description are consistent
- Confirm important references are inside `references/`
- Reduce unnecessary local-environment assumptions
- Remove private names, private ids, and machine-specific paths when possible
- Make sure the skill is understandable from `SKILL.md` plus `references/`

## Packaging command

Run the packaging script against your local `context-flow` skill directory, for example:

```bash
scripts/package_skill.py /path/to/context-flow
```

## Practical rule

If the skill still depends on your workspace docs to make sense, it is not fully generalized yet.
