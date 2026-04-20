---
name: philosophy-dialogue
description: |
  思想碰撞的火花，在这里点燃！243 位思想巨人跨越时空对话，6 种对话模式（含雄辩天下杯赛制）。
  243 intellectual giants dialogue across time. 6 modes including cup tournament.
  触发词：哲学对话、哲学辩论、双人论战、雄辩天下、philosophical dialogue、cup tournament
---

# 🎭 哲学对话 Skill / Philosophical Dialogue

> **「未经审视的人生不值得过。」—— 苏格拉底**

---

## 🌟 功能速览

| 功能 | 描述 |
|------|------|
| 🏆 **6 种模式** | 对抗辩论/启发探索/舌战群儒/楚河汉界/双人论战/**雄辩天下** |
| 🧠 **243 位哲学家** | 中西哲学家、科学家、文学家、艺术家 |
| ⚔️ **技能系统** | 25 位哲学家技能 + 5 种组合技 |
| 🎬 **场景 BGM** | 6 种场景 + 5 种 BGM |
| 🎭 **情绪系统** | 8 种情绪实时标注 |
| 💬 **观众互动** | 弹幕 + 实时投票 |
| 📊 **打分体系** | 5 维度评分（逻辑/回应/深度/清晰/创新） |
| v3.1 升级 | 双人论战：避免重复 + 集中投票 +15-20 位评委 |
| v3.2 升级 | 5 维度评分体系 + 理由公开 + 全模式适用 |
| **🆕 v4.0 升级** | **雄辩天下杯赛模式 + 注册表更新** |

---

## 📖 快速上手

```bash
# 标准对话
哲学对话，话题：什么是自由

# 指定模式
用楚河汉界式讨论：人性本善还是本恶

# 双人论战
尼采 vs 庄子，话题：人生的意义
```

**详细模式说明**：见 [`MODES.md`](MODES.md)

**双人论战详解**：见 [`DUEL-MODE.md`](DUEL-MODE.md)

**打分体系详解**：见 [`SCORING.md`](SCORING.md) 🆕

---

## 🎭 6 种对话模式

| 模式 | 人数 | 特点 | 适用场景 |
|------|------|------|----------|
| **对抗辩论** | 10-50 | 正反方对立 | 理论探讨 |
| **启发探索** | 10-30 | 多角度探索 | 人生意义 |
| **舌战群儒** | 20-50 | 一人主辩 | 名人理论 |
| **楚河汉界** | 20-50 | 两阵营对攻 | 道德争议 |
| **双人论战** | 2+15-20 评委 | 1v1 对决，5 维度评分 | 直接对抗 |
| **🏆 雄辩天下** | **32+** | **杯赛淘汰，评委 + 观众打分** | **大型赛事** |

**详细说明**：见 [`MODES.md`](MODES.md)

**双人论战升级 (v3.1.0)**：避免重复规则、集中投票（仅中场 + 结束）、扩大评委至 15-20 人。

**打分体系升级 (v3.2.0)**：5 维度评分（逻辑/回应/深度/清晰/创新）、理由公开、全模式适用。见 [`SCORING.md`](SCORING.md)。

**🆕 雄辩天下 (v4.0.0)**：杯赛制淘汰赛，32 人参赛，20 人评委，观众贡献题目 + 投票，评委 70%+ 观众 30% 加权打分。见 [`CUP-MODE.md`](CUP-MODE.md)。

---

## 🧠 哲学家资源

### 分类统计

| 类别 | 人数 | 代表人物 |
|------|------|----------|
| 中国哲学家 | 60+ | 孔子、老子、庄子 |
| 西方哲学家 | 50+ | 苏格拉底、尼采、康德 |
| 科学家 | 20+ | 爱因斯坦、牛顿、居里夫人 |
| 心理学家 | 5+ | 佛洛伊德、马斯洛 |
| 文学家 | 10+ | 雨果、鲁迅、钱钟书 |
| 其他 | 20+ | 政治家、艺术家、管理大师 |

**完整名单**：见 [`references/philosopher-registry.md`](references/philosopher-registry.md)

---

## 🏗️ 架构与依赖关系

本 skill 采用**自包含架构**：243 位哲学家的蒸馏思维框架已内置在 skill 内部，无需外部依赖。

```
philosophy-dialogue (主 skill：对话编排、模式控制、评分体系)
    │
    ├── 读取 → references/philosopher-registry.md（243 位哲学家名单）
    │
    ├── 读取 → references/perspective/*-perspective/SKILL.md（内置哲学家思维框架）
    │         └── 243 位哲学家的蒸馏文件已内置于 skill 内部
    │         └── 包含：心智模型、启发式、核心技能、金句
    │         └── 也可通过外部 skills/*-perspective/ 读取（向下兼容）
    │
    └── 写入 → memory/philosophy-dialogues/tournaments/（杯赛数据）
```

**哲学家思维框架（perspective skills）**

哲学对话的核心是让每位哲学家**用自己的思维方式发言**。每位哲学家的 perspective SKILL.md 包含该哲学家的思维框架（心智模型、启发式、金句等），是对话质量的关键依赖。

- **内置路径**（推荐）：`references/perspective/*-perspective/SKILL.md` —— 已集成在 skill 内部，无需额外安装
- **外部路径**（向下兼容）：`skills/*-perspective/SKILL.md` —— 若工作区存在独立的 perspective skills 也可读取
- **只读不写**：对 perspective skills 仅读取，不修改

---

## ⚔️ 技能系统

- **25 位哲学家**有专属技能
- **5 种组合技**（特定哲学家组合触发）
- 标准对话：1 次/人
- 双人论战：2 次/人

**技能详情**：见 [`SKILLS-LIST.md`](SKILLS-LIST.md)

---

## 📁 文件结构

```
skills/philosophy-dialogue/
├── SKILL.md (主文件)
├── MODES.md (6 种模式详解)
├── CUP-MODE.md (雄辩天下杯赛模式)
├── DUEL-MODE.md (双人论战)
├── SCORING.md (打分体系)
├── SCENES.md (场景 BGM)
├── SKILLS-LIST.md (技能列表)
├── UPGRADE-LOG.md (升级日志)
├── package.json
├── .clawhubignore (发布排除文件)
├── scripts/ (可选：杯赛角色分配脚本)
│   └── tournament-allocator.py
└── references/
    ├── philosopher-registry.md (哲学家名单，路径指向内置蒸馏文件)
    └── perspective/ (🆕 243 位哲学家蒸馏思维框架，已内置)
        ├── confucius-perspective/SKILL.md
        ├── nietzsche-perspective/SKILL.md
        ├── zhuangzi-perspective/SKILL.md
        └── ... (243 个目录)
```

**注意**: 比赛数据保存在 `memory/philosophy-dialogues/tournaments/`（用户 workspace），不属于 skill 本身。

---

## 📈 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v2.5-2.9 | 2026-04-12 | 情绪/技能/场景系统 |
| v3.0 | 2026-04-13 | 5 种模式统一 + 173 位哲学家 |
| v3.1 | 2026-04-13 | 双人论战：避免重复 + 集中投票 + 扩大评委 |
| v3.2 | 2026-04-13 | 5 维度评分体系 + 理由公开 + 全模式适用 |
| v4.0 | 2026-04-14 | 雄辩天下杯赛模式 + 注册表更新 |
| v4.1.1 | 2026-04-14 | 安全修复：明确 scripts/可选，memory/为用户目录 |
| v4.2.4 | 2026-04-14 | permissions 声明扩大：读取 skills/*-perspective/ |
| v4.2.5 | 2026-04-14 | 增加架构与依赖关系说明，解释跨 skill 读取的合理性 |
| **v4.3.0** | **2026-04-16** | **蒸馏人物私域化：243 位哲学家思维框架内置于 skill 内部** |

**升级日志**：见 [`UPGRADE-LOG.md`](UPGRADE-LOG.md)

---

## 📦 获取与安装

### 方式一：ClawHub 安装（轻量版）

```bash
clawhub install philosophy-dialogue
```

> ℹ️ ClawHub 版包含核心模式文件和注册表，不包含 `references/perspective/`。对话时 AI 会基于自身知识生成哲学家视角。

### 方式二：GitHub 安装（完整版，含蒸馏思维框架）

```bash
git clone https://github.com/Wings229/philosophy-dialogue-skill.git skills/philosophy-dialogue
```

**GitHub 仓库**：https://github.com/Wings229/philosophy-dialogue-skill

> 📦 **完整版特有**：`references/perspective/` 目录包含 243 位哲学家的蒸馏思维框架文件。这些文件让每位哲学家以精确的个人思维方式发言，显著提升对话质量。

> ⚠️ **安全提示**：clone 后建议先审查代码再使用。特别是 `scripts/tournament-allocator.py`，请确认其行为符合下方安全声明。

**运行时依赖**：
- 核心功能（对话/辩论）：无依赖，纯指令驱动
- 杯赛角色分配脚本（`scripts/tournament-allocator.py`）：需要 **Python 3.6+**，仅使用标准库，无网络调用

> 注：杯赛脚本为可选工具，不影响核心对话功能。手动分配角色也可以。

**🔒 脚本安全声明**（`scripts/tournament-allocator.py`）：
- ✅ 仅使用 Python 标准库（random, os, re, sys, json）
- ✅ 无网络调用（无 urllib, requests, socket 等）
- ✅ 无子进程调用（无 subprocess, os.system 等）
- ✅ 文件读取：仅 `references/philosopher-registry.md` 和用户指定的题目文件
- ✅ 文件写入：仅 `memory/philosophy-dialogues/tournaments/` 目录

### 版本对比

| 特性 | ClawHub | GitHub 完整版 |
|------|---------|-------------|
| 核心模式 (SKILL.md) | ✅ | ✅ |
| 6 种模式详解 (MODES.md) | ✅ | ✅ |
| 双人论战 (DUEL-MODE.md) | ✅ | ✅ |
| 打分体系 (SCORING.md) | ✅ | ✅ |
| 技能列表 (SKILLS-LIST.md) | ✅ | ✅ |
| 场景 BGM (SCENES.md) | ✅ | ✅ |
| 哲学家注册表 (philosopher-registry.md) | ✅ | ✅ |
| 对话示例 (example-dialogue.md) | ✅ | ✅ |
| 雄辩天下杯赛 (CUP-MODE.md) | ✅ | ✅ |
| 🆕 蒸馏思维框架 (references/perspective/) | ❌ 需从 GitHub 获取 | ✅ 内置 243 位 |
| 杯赛脚本 (scripts/) | ❌ | ✅ |
| 升级日志 (UPGRADE-LOG.md) | ❌ | ✅ |
| 辩论题目库 (references/) | ❌ | ✅ |

---

## ❓ 常见问题

**Q: 如何选择模式？**
A: 理论探讨→对抗辩论，人生意义→启发探索，名人理论→舌战群儒，道德争议→楚河汉界，直接对抗→双人论战，大型赛事→雄辩天下。

**Q: 双人论战如何触发？**
A: 说「双人论战，话题：XX」或「A vs B，话题：XX」。

**Q: 雄辩天下如何启动？**
A: 说「雄辩天下」或「雄辩天下，参赛：32 人，评委：20 人」。杯赛角色分配可使用 `scripts/tournament-allocator.py`。

**Q: 技能如何使用？**
A: 自动触发，当哲学家遇到合适时机（如被强烈反对）会自动使用。

**Q: 比赛数据保存在哪里？**
A: `memory/philosophy-dialogues/tournaments/`（用户 workspace），不属于 skill 本身。

**Q: 如何查看完整哲学家名单？**
A: 见 [`references/philosopher-registry.md`](references/philosopher-registry.md)。

---

*哲学对话 Skill v4.3.0 | 2026-04-16 更新 | 6 种模式 | 243 位哲学家 | 蒸馏思维框架已内置 | [GitHub 完整版](https://github.com/Wings229/philosophy-dialogue-skill)*
