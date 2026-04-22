---
name: ielts-tuyaya-upload
description: "Upload IELTS reading review JSON files to tuyaya.online — your personal IELTS progress tracker. Supports end-to-end pipeline with ielts-reading-review: auto-scan → generate JSON → batch upload. Trigger phrases: 上传复盘 / 同步服务器 / 上传到 tuyaya / 把复盘上传 / 注册 tuyaya / 登录 tuyaya / 查看我的成绩 / 批量同步雅思成绩 / 批量导入历史复盘 / 一条龙处理复盘 / 端到端同步雅思 / 把老笔记导入 tuyaya / upload ielts reviews / sync to tuyaya / register tuyaya / tuyaya 账号 / tuyaya 上传."
version: 1.1.0
---

# IELTS Tuyaya Upload Skill

## Purpose

把本地生成的雅思阅读复盘 JSON（通常来自 `ielts-reading-review` skill）一键上传到 tuyaya.online 服务器，不再需要手动拖文件到 submit 页面。

**✨ 多用户支持**：每个用户有独立账号，token 本地保存，一次登录长期有效。

## When to use

当用户说以下话时，触发本 skill：
- "上传复盘" / "同步到服务器" / "把 JSON 上传"
- "注册 tuyaya 账号" / "登录 tuyaya"
- "查看我在 tuyaya 的成绩"
- "批量同步雅思成绩"

## Prerequisites

- Node.js ≥ 18（有原生 fetch）
- 本地有 `*.json` 复盘文件（通常在 `./batch-output/` 或 `./history-json/`）

## Skill Location

Skill 目录（包含 `scripts/upload.js`）所在路径会在安装时自动设置。典型路径：
- ClawHub 安装：`~/.clawhub/skills/ielts-tuyaya-upload/`
- 手动安装：用户指定目录

AI 在调用脚本时，使用 **skill 所在目录下的 `scripts/upload.js`**，不要假设绝对路径。

## Workflow — AI 执行规则

### 🌟 场景 0：端到端一条龙（最常见，强烈推荐）

**触发信号**：用户说"批量导入我的历史复盘"、"把我电脑里的老笔记一次性同步到 tuyaya"、"一条龙处理我的复盘"、"从扫描到上传全流程"。

**前提**：同时安装了 `ielts-reading-review` v3.4.0+（提供 Auto-Discovery + 深扫 + JSON 生成）。

**AI 动作（必须分步停下来等确认，不要一口气跑完）**：

#### A. 自动发现复盘目录
1. 调用 `ielts-reading-review` 的 `scan-legacy-reviews.js --auto` 扫常见位置（桌面/文档/下载/iCloud/WorkBuddy）
2. 把推荐目录 + 其他候选列给用户，让用户确认用哪个

#### B. 生成 JSON
3. 对确认的目录跑 `--deep` 深扫，列出识别到的篇目清单（含 `__unknown__`）
4. 让用户确认篇目清单对不对
5. 逐篇生成 v3.0 schema JSON，输出到 `./batch-output/`
6. 缺失字段置空，不瞎编
7. 汇报成功/失败/数据缺失数量

#### C. 上传到 tuyaya.online（本 skill 主战场）
8. 运行 `--whoami` 检查登录状态
   - 未登录 → 先走场景 1（注册）或场景 2（登录）
9. 运行 `--diff ./batch-output/` 展示差量（新/已存在/冲突）
10. 用户确认后运行 `--batch ./batch-output/` 批量上传
11. 汇报成功/跳过/失败数量
12. 给用户 https://tuyaya.online/ielts/ 链接去查看成绩

**⚠️ 关键规则**：
- 每一步（A→B→C 内部每个子步骤）都要停下来等用户确认
- 注册/登录必须让用户在终端自己输入密码，AI 不要代填、不要建议密码
- 失败的条目要列出来让用户决定是否重试
- 不要一口气处理 50+ 篇，超过建议让用户分批

### 场景 1：用户首次使用（没账号）

**触发信号**：用户说"我想用 tuyaya"、"帮我注册"、"我还没账号"，或者运行命令报错"还没登录"。

**AI 动作**：
1. 告知用户：即将运行注册命令，需要在终端交互输入用户名和密码
2. 运行：`node <skill_dir>/scripts/upload.js --register`
3. 提示用户完成交互输入（用户名 3-20 字符、密码 ≥6 位）
4. 注册成功后会自动登录并保存 token，可以直接进入上传流程

**⚠️ 不要替用户生成密码**，让用户自己输入。

### 场景 2：用户已有账号（需要登录）

**触发信号**：用户说"我想登录"、"换个账号"，或者 `--whoami` 提示未登录。

**AI 动作**：
1. 运行：`node <skill_dir>/scripts/upload.js --login`
2. 提示用户在终端输入用户名密码
3. 成功后 token 保存到 `~/.ielts-tuyaya-token`，下次不用再登录

### 场景 3：批量上传 JSON（核心场景）

**触发信号**：用户说"把 batch-output 里的 JSON 上传"、"同步所有复盘"。

**AI 动作**：
1. **先检查登录状态**：`node <skill_dir>/scripts/upload.js --whoami`
   - 如果未登录 → 跳到场景 1 或 2
   - 已登录 → 继续

2. **（推荐）先 diff 看差量**：
   `node <skill_dir>/scripts/upload.js --diff <用户的 JSON 目录>`
   - 展示给用户看：哪些是新的、哪些已在服务器、哪些不一致
   - 让用户确认是否继续上传

3. **确认后批量上传**：
   `node <skill_dir>/scripts/upload.js --batch <用户的 JSON 目录>`
   - 脚本会自动跳过服务器上已有的记录
   - 汇总成功/跳过数量

4. **完成后**：告诉用户去 https://tuyaya.online/ielts/ 查看成绩

### 场景 4：上传单个 JSON

`node <skill_dir>/scripts/upload.js <文件路径>`

### 场景 5：查看服务器成绩

`node <skill_dir>/scripts/upload.js --status`

### 场景 6：退出账号 / 查看当前账号

- `--logout`：清除本地 token
- `--whoami`：查看当前登录的用户名

## Commands Reference

| 命令 | 说明 | 是否需要登录 |
|------|------|---|
| `--register` | 注册新账号（交互式） | ❌ |
| `--login` | 登录并保存 token | ❌ |
| `--logout` | 清除本地 token | ❌ |
| `--whoami` | 查看当前登录账号 | ❌ |
| `--status` | 查看服务器成绩 | ✅ |
| `--diff <dir>` | 对比本地和服务器差量 | ✅ |
| `--batch <dir>` | 批量上传目录下所有 JSON | ✅ |
| `<file.json>` | 上传单个文件 | ✅ |

## Token Storage

登录后 token 保存在：`~/.ielts-tuyaya-token`（文件权限 0600）

内容示例：
```json
{
  "token": "eyJ1Ijoi...",
  "username": "alice",
  "savedAt": "2026-04-21T15:00:00.000Z"
}
```

Token 有效期 30 天，过期后重新 `--login` 即可。

## JSON Format

本 skill 消费 `ielts-reading-review` v3.0 产出的 JSON：

```json
{
  "version": "3.0.0",
  "source": { "book": 5, "test": 1, "passage": 2 },
  "score": { "correct": 9, "total": 13 },
  "timing": { "minutes": 25 },
  "date": "2026-04-20",
  "wrongQuestions": [...],
  "vocabulary": [...]
}
```

也兼容旧格式（平铺 `book/test/passage/score/total`）。

## AI 对话范例

### 范例 0：端到端一条龙（最常见）

> **用户**：帮我一条龙处理我的历史雅思复盘，从扫我电脑到上传 tuyaya 都搞定
>
> **AI**：
> 好，我分三段处理，每段停下来等你确认。
>
> **[A. 自动扫描]**
> *运行 `ielts-reading-review` 的 `scan-legacy-reviews.js --auto`*
> 找到 3 个候选目录，推荐 `/Users/xx/Documents/雅思学习`（命中 28 个复盘文件）。用这个吗？
>
> *用户：用这个*
>
> **[B. 深扫 + 生成]**
> *运行 `--deep` 深扫*
> 识别到 20 篇（剑4 全本 + 剑5 T1-T3），2 篇 `__unknown__` 需要你补充。清单 OK 吗？
>
> *用户：OK，unknown 那 2 篇先跳过*
>
> *逐篇生成 JSON 到 `./batch-output/`*
> 生成完：18 成功，2 跳过。
>
> **[C. 上传 tuyaya]**
> *运行 `--whoami`* → 还没登录
> 你有 tuyaya 账号吗？
>
> *用户：没有，帮我注册*
>
> *运行 `--register`*（用户在终端输入用户名密码）
>
> *运行 `--diff ./batch-output/`*
> 18 个全是新的，服务器还没有。开始上传？
>
> *用户：上传*
>
> *运行 `--batch ./batch-output/`*
> ✅ 18 条全部成功。去 https://tuyaya.online/ielts/ 看趋势图吧～

### 范例 A：新用户首次使用

> **用户**：我想把我的雅思复盘同步到 tuyaya
>
> **AI**：
> 我先检查一下你的登录状态。
> *运行 `node scripts/upload.js --whoami`*
> 还没登录。tuyaya.online 需要一个账号——你有账号吗？
> - 有 → 我帮你登录
> - 没有 → 我引导你注册一个（免费、只要用户名密码）

### 范例 B：批量上传（已登录）

> **用户**：把 batch-output 目录下的 JSON 全上传
>
> **AI**：
> *运行 `--diff ./batch-output/`*
> 本地有 12 个，服务器已有 5 个，8 个是新的。我开始上传这 8 个。
> *运行 `--batch ./batch-output/`*
> ✅ 上传完成：8 条成功。去 https://tuyaya.online/ielts/ 看看吧～

### 范例 C：登录过期

> **用户**：--status 报错说 token 过期了
>
> **AI**：
> Token 30 天有效期到了，重新登录就行：
> *运行 `--login`*
> 输入用户名密码后，token 会自动更新保存。

## Error Handling

| 错误 | 处理 |
|------|------|
| `还没登录` | 引导运行 `--register` 或 `--login` |
| `token 过期` | 运行 `--login` 重新获取 |
| `用户名已存在`（注册时） | 让用户换个名字，或改用 `--login` |
| `用户名或密码错误`（登录时） | 让用户重试，或 `--register` 新账号 |
| `HTTP 500` | 服务器问题，建议稍后重试 |
| 网络错误 | 检查是否能访问 https://tuyaya.online |

## Privacy & Security

- **Token 本地存储**：仅保存在 `~/.ielts-tuyaya-token`，权限 0600（只有自己可读）
- **密码不保存**：只保存 token，密码从不落盘
- **独立账号**：每个用户在服务器有独立数据，互相隔离
- **HTTPS 传输**：所有请求走 https://tuyaya.online

## Related Skills

- `ielts-reading-review`：生成复盘 JSON，本 skill 负责上传这些 JSON
- 配合使用：先用 `ielts-reading-review` 批量生成 → 再用本 skill 批量上传
