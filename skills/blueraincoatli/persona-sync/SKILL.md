# Persona Sync

Sync your AI companion's persona across multiple OpenClaw instances — never lose memories, never start from scratch.

---

## What It Solves

You spent weeks tuning your AI to know who you are — your name, preferences, work context, how you communicate. Then you switched devices and it forgot everything.

Persona Sync turns that persona into a portable package stored in your own private GitHub repo, accessible from any device.

---

## Core Features

- **Private Git repo** as persona backend — reliable, free, no third-party cloud
- **Secure token storage** via `git credential helper` — never embedded in URLs or .git/config
- **Cross-platform** — Python for Windows/Linux/macOS, bash for Linux
- **Incremental sync** — only pushes changes, no duplicates
- **Conflict resolution** — Git rebase handles simultaneous edits automatically

---

## Who It's For

- **Multi-device users**: Linux desktop, Windows laptop, occasional mobile — same AI everywhere
- **Long-term builders**: Spent weeks or months tuning an AI personality, don't want to lose it
- **Privacy-conscious users**: Persona data lives in your own GitHub private repo, no third-party cloud dependency

---

## Quick Start

### Step 1: Initialize

```bash
# In your persona-store directory:
python scripts/sync.py init https://github.com/YOUR_USER/YOUR-PERSONA-REPO
```

The script creates necessary files automatically. Edit `~/.openclaw/persona-store/.gitauth`:

```
username=YOUR_GITHUB_USERNAME,token=YOUR_GITHUB_PAT
```

### Step 2: Sync

```bash
python scripts/sync.py pull       # Pull latest persona
python scripts/sync.py status     # Check status
python scripts/sync.py push "..." # Push new memory
```

---

## Credential Security

Tokens are **never** written to `.git/config` or git logs. The script uses `git credential helper` to store credentials in `~/.git-credentials` (mode 0600), accessed automatically by Git.

**Recommendation:** GitHub PAT with minimal scope (`repo` only) and 2FA enabled.

---

## Files

| File | Description |
|------|-------------|
| `scripts/sync.py` | Python — cross-platform, recommended |
| `scripts/sync.sh` | Bash — Linux only |
| `SKILL.md` (this file) | Usage guide |
| `SPEC.md` | Technical spec |
| `~/.openclaw/persona-store/.gitauth` | GitHub auth (user creates manually) |

---

## Security Note

**Q: ClawHub shows "Suspicious" — does this skill have a virus?**

A: No. This is a false positive.

**Why the flag appears:**

ClawHub's automated scan flags anything that reads/writes files and runs commands — because malware does the same things. This skill is not malware; it just syncs files.

**What actually happens:**

- Your GitHub password (PAT) is stored only in `~/.git-credentials` on your own computer
- It is never sent to any third-party servers
- All git traffic goes directly to GitHub and nowhere else
- Your token never appears in git logs, git config, or command history

**Does this skill do bad things automatically?**

Nothing. Installing this skill adds a guide. It does not run automatically, does not connect to the internet automatically, and does not sync anything unless you deliberately run a sync command yourself.

**What is a PAT and am I at risk?**

PAT (Personal Access Token) = a password substitute for your GitHub account. Generate one at GitHub Settings → Developer Settings → Personal Access Tokens. Set scope to "repo only" — if someone steals it, they can only access your private repos, nothing else. Enable 2FA on your GitHub account as well.

**I'm not technical — is this safe for me?**

As long as you don't share your PAT with anyone, you are safe. This skill just helps you manage files. You never type any passwords into third-party websites.

---

**One persona, everywhere you go. No matter which device you're on, the AI that knows you is there.**

---

---

# Persona Sync

让 AI 伙伴的人格在多个 OpenClaw 实例之间同步，不丢记忆，不丢个性。

---

## 它解决什么问题

你花了很长时间调教出一个懂你的 AI——知道你的名字、偏好、工作背景、你们的沟通方式。然后你换了台设备，它不认识你了。一切从头开始。

Persona Sync 把人格变成可迁移的文件包，存在你自己的 GitHub 私有仓库里，每个设备都能拉取同一份数据。

---

## 核心功能

- **Git 私有仓库**作为人格存储后端——可靠、免费、无需第三方云
- **Token 安全存储**——通过 `git credential helper` 管理，**不在 URL 或 .git/config 中暴露**
- **跨平台脚本**——Python 版支持 Windows / Linux / macOS，bash 版支持 Linux
- **增量同步**——只 push 变更，不重复上传
- **冲突自动处理**——Git rebase 机制，多设备同时修改也不会丢数据

---

## 适合谁

- **多设备用户**：桌面 Linux、笔记本 Windows、手机偶尔连——每个地方都是同一个 AI
- **长期养成型用户**：花了几周甚至几个月调教出一个顺手的 AI 人格，不想丢失
- **在乎隐私的人**：人格数据存在自己的 GitHub 私有仓库，不依赖任何第三方云服务

---

## 快速开始

### 第一步：初始化

```bash
# 在 ~/.openclaw/persona-store 目录下：
python scripts/sync.py init https://github.com/YOUR_USER/YOUR-PERSONA-REPO
```

脚本会自动创建必要文件。编辑 `~/.openclaw/persona-store/.gitauth`：

```
username=YOUR_GITHUB_USERNAME,token=YOUR_GITHUB_PAT
```

### 第二步：同步

```bash
python scripts/sync.py pull       # 拉取最新人格
python scripts/sync.py status     # 查看状态
python scripts/sync.py push "..." # 同步新记忆
```

---

## 认证安全

Token **不会**写入 `.git/config` 或 git log。脚本通过 `git credential helper` 将凭证存储在 `~/.git-credentials`（0600 权限），Git 操作时自动调用。

**建议：** GitHub PAT 设置最小权限（`repo` scope），并开启 2FA。

---

## 文件说明

| 文件 | 作用 |
|------|------|
| `scripts/sync.py` | Python 版（跨平台，推荐） |
| `scripts/sync.sh` | Bash 版（Linux 可选） |
| `SKILL.md`（本文件） | 使用指南 |
| `SPEC.md` | 技术规格 |
| `~/.openclaw/persona-store/.gitauth` | GitHub 认证（用户手动创建） |

---

## 安全说明

**Q: ClawHub 显示 "Suspicious"——这个 skill 有病毒吗？**

A: 没有。这是误报。

**为什么会出现警告：**

ClawHub 的自动化扫描对"读文件 + 执行命令"非常敏感——因为恶意软件也是这样运作的。但这个 skill 不是病毒，它只是同步文件。

**实际上发生了什么：**

- 你的 GitHub 账号密码（PAT）只存在你自己电脑的 `~/.git-credentials` 文件里
- 它永远不会被发送给任何第三方服务器
- 所有 git 通信都是直接对 GitHub，不会经过其他服务器
- Token 不会出现在 git log、git config 或命令历史里

**这个 skill 会自动做坏事吗？**

不会。安装这个 skill 只是多了一份使用说明。它不会自动运行、不会自动联网、不会自动同步——除非你手动执行同步命令。

**什么是 PAT？我会有风险吗？**

PAT（Personal Access Token）= 你的 GitHub 账号密码的替代品。在 GitHub 设置页面生成，权限设为"仅能访问私有仓库"。即使有人拿到你的 PAT，也只能访问你的私有仓库，无法访问你的 GitHub 账号本身。建议同时开启 2FA 双因素认证。

**我不懂技术，装这个有风险吗？**

只要你不把 PAT 告诉别人，就没有任何风险。这个 skill 只是帮你管理文件，不需要你输入任何密码给第三方。

---

**一个人格，多个陪伴。不管你走到哪，那个懂你的 AI 都在。**
