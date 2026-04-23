---
name: skylv-readme-generator
slug: skylv-readme-generator
version: 1.0.0
description: "Auto-generates professional README.md from code structure, package.json, and directory analysis. Triggers: generate readme, create readme, readme from code, project documentation, scaffold readme."
author: SKY-lv
license: MIT
tags: [readme, documentation, generator, github]
keywords: [readme, documentation, github, markdown, generator]
triggers: readme generator, generate readme, create readme
---

# README Generator

## Overview
Automatically analyzes a codebase and generates a comprehensive, professional README.md.

## When to Use
- User asks to "generate a README", "create documentation", or "document this project"
- New project needs a README but none exists
- Existing README is outdated or incomplete

## How It Works

### Step 1: Analyze project structure

Run: dir /b /s /a:d (Windows) or find . -maxdepth 2 -type d (macOS/Linux)

### Step 2: Detect project type

Check for: package.json (JS), setup.py/pyproject.toml (Python), Cargo.toml (Rust), go.mod (Go), pom.xml (Java)

### Step 3: Generate README sections

1. Project Title - from package.json name or directory name
2. Badges - CI status, version, license, downloads
3. One-liner Description
4. Features - auto-detect from exports and main functions
5. Installation - standard install for detected type
6. Usage - realistic examples from source code
7. API Reference - parse function signatures
8. Contributing + License

## Output Format

Write a complete README.md with all sections. Keep descriptions under 80 chars per line.
Include real badges (shields.io) and actual code examples from the source.