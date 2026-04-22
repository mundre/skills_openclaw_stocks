---
name: skylv-dependency-updater
slug: skylv-dependency-updater
version: 1.0.0
description: "Auto-checks and updates outdated dependencies. Shows changelogs and breaking changes before updating. Triggers: update dependencies, upgrade packages, check outdated, npm update."
author: SKY-lv
license: MIT
tags: [dependencies, npm, pip, update, devops]
keywords: [dependencies, npm, pip, update, upgrade, package]
triggers: update dependencies, upgrade packages, check outdated
---

# Dependency Updater

## Overview
Scans project dependencies and checks for updates, shows changelogs, identifies breaking changes.

## When to Use
- User asks to "update dependencies" or "check for updates"
- Regular maintenance

## How It Works

### Step 1: Detect package manager
package.json -> npm
pyproject.toml -> pip
Cargo.toml -> cargo
go.mod -> go

### Step 2: Check outdated
npm: npm outdated --json
pip: pip list --outdated --format=json
cargo: cargo outdated

### Step 3: Risk assessment
Patch (1.2.3 -> 1.2.4): Low risk - auto-update
Minor (1.2.3 -> 1.3.0): Medium - show changelog
Major (1.2.3 -> 2.0.0): High - show breaking changes

## Output Format
Major Updates: express 4.17.1 -> 5.0.0 [BREAKING changes]
Minor Updates: axios 0.21.1 -> 0.21.4 [Bug fixes]
Patch Updates: debug 4.3.1 -> 4.3.4 [Security patch]

## Update Strategy
1. Show report first - never update blindly
2. Update in stages: patches -> minors -> majors
3. Run tests after each update
4. Commit each update separately