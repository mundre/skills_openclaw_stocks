---
name: zaomeng-skill
description: 本地规则引擎驱动的小说角色蒸馏与群聊技能。支持 distill/chat/view/correct/extract，输出角色档案、关系网、会话和纠错 JSON，无需云模型依赖。此技能需要配套 Dreamforge 仓库代码运行。
---

# Zaomeng Skill for ClawHub

## Dependency Clarification

This skill definition is a runtime adapter and requires the Dreamforge codebase.
It is not a standalone executable bundle by itself.

Required code source:
- GitHub: `https://github.com/wkbin/Dreamforge`

Required runtime:
- Python 3.10+
- Local packages from `requirements.txt`

Setup steps:
1. `git clone https://github.com/wkbin/Dreamforge.git`
2. `cd Dreamforge`
3. `pip install -r requirements.txt`
4. `cp config.yaml.example config.yaml` (Windows: `Copy-Item config.yaml.example config.yaml`)

## What This Skill Does

- Distill character profiles from `.txt` / `.epub` novels
- Extract pairwise character relationship graph
- Run immersive roleplay chat (`observe` / `act`)
- Store correction memory to reduce OOC drift

## Core Commands

- `py -m src.core.main distill --novel <path> [--characters 名1,名2] [--force]`
- `py -m src.core.main extract --novel <path> [--output <path>] [--force]`
- `py -m src.core.main chat --novel <book> --mode observe|act [--character <name>]`
- `py -m src.core.main view --character <name>`
- `py -m src.core.main correct --session <id> --message <raw> --corrected <fixed> [--character <name>]`

## Data Outputs

- `data/characters/`
- `data/relations/`
- `data/sessions/`
- `data/corrections/`

## Runtime Notes

- Local-first, no OpenAI API required
- Requires Python 3.10+
- Uses JSON as the only persistence format
- This SKILL.md must be used together with the Dreamforge repository files
