# ClawHub Publish Guide | ClawHub 发布指南

## Two-step publishing workflow | 两步发布工作流

**无论改动多小、无论第几次修改，两步验证不可跳过。**

### 第一步（AI 内部执行，不输出给用户）

**A. Run full checklist | 完整清单核对**
Verify all items in the "Skill creation/modification checklist" section of SKILL.md:
逐项核对 SKILL.md 中"技能制作/修改清单"的全部项目。

**B. Security verification | 安全性检查**

⚠️ **If the skill contains scripts (Python/Bash/etc.), manually inspect each script:**
如果技能包含脚本，必须手动检查每个脚本：

| 风险类型 | 检查要点 | 高危模式 |
|---------|---------|---------|
| **Shell 注入** | `os.system()`, `subprocess.call(..., shell=True)`, `eval()` 用于无过滤的用户输入 | `os.system(f"arecord ... {filepath}")` |
| **Python 代码注入** | `exec()`/`eval()` 构建自用户/远程输入；`python3 -c` 内字符串插值 | `f"python3 -c '...{user_input}...'"` |
| **路径注入** | 文件路径与无过滤的用户/远程输入直接拼接 | `subprocess.run(f"convert {filename}")` |
| **日志/输出泄露** | API Key、Token、凭证出现在日志、报错、返回值中 | 凭证明文出现在错误信息中 |
| **依赖不完整** | 代码 import 的包未出现在 `requirements.txt` / `package.json` 中 | 代码 import `av`，requirements.txt 没有 |

**C. File size check | 文件大小检查**
```bash
du -sh <skill-dir>
```
If the directory **exceeds 50MB**, the upload will fail.
- Report to user immediately.
- Move oversized files (e.g., model files) to a workspace backup location. Wait for explicit user confirmation.
- After upload succeeds, move files back. Wait for user confirmation again.
如果目录**超过 50MB**，上传会失败。立即报告用户，等待明确指示后再操作。

**D. Draft changelog | 拟定 changelog**

⚠️ **Changelog 不写在 SKILL.md 里！** Changelog 是 ClawHub 网站上的发布说明，在 `clawhub publish` 时通过 `--changelog` 参数传入。SKILL.md 模板中不应包含"更新日志"章节（除非是永久保留的完整更新历史）。

- English first, Chinese after.
  英文在前,中文在后。
- Formal release-note tone only.
  仅使用正式发布说明语气。

**Changelog format | changelog 格式：**
Changelog 内容通过 `--changelog "..."` 参数传递给 `clawhub publish` 命令，显示在 ClawHub 网站的版本历史中。格式为英文在前、中文在后的数字序号列表。

Use plain numbered list (1. 2. 3.) with English first, Chinese after for each point.
使用纯数字序号分点，每点英文在前、中文在后。

**Changelog template | 模板：**
```
1. [English update]. [中文更新]。
2. [English update]. [中文更新]。
3. [English update]. [中文更新]。
```

**Recommended examples | 推荐示例：**
```
1. Initial release. 首次发布。
```
```
1. Add comprehensive pre-publish checklist and two-step publishing workflow. 新增发布前检查清单和两步发布流程。
2. Consolidate naming/writing standards and changelog rules into SKILL.md body. 整合命名写作规范与changelog规则至SKILL.md正文。
```

**Strictly avoid | 严格禁止：**
- personal corrections / 个人纠错
- format-only adjustments / 格式调整
- private debugging notes / 私人调试记录
- jokes, self-deprecation, apology-style wording / 玩笑、自嘲、道歉式表述

### 第二步（输出给用户，等待明确确认）

Report the following to user. **⚠️ Do NOT run `clawhub publish` until user explicitly confirms.**
**发布类操作（clawhub publish / git push / gh release create / 推广发帖等）必须经过两步验证，不可跳过。**

| Item | 内容 |
|---|---|
| Skill name + slug | 准确拼写 |
| ClawHub current published version | 来自 `clawhub inspect <slug>` |
| New version number | 在已发布版本上递增 |
| Changelog | 完整英中文双语内容 |
| Primary update summary | 一句话概括 |
| File size | 是否超 50MB |
| De-identification | 确认通过/需调整 |
| Scientificity | 确认通过/需调整 |
| AI readability | 确认通过/需调整 |
| Contextual coherence | 确认通过/需调整 |
| Stability | 确认通过/需调整 |
| **Code security** | 确认通过/需调整（Shell注入/Python代码注入/路径注入/依赖完整性） |
| Full publish command | `clawhub publish ...` |

**Restart rule | 重启规则：**
Each user modification request → restart from Step 1.
每次用户提出修改，都必须从第一步重新开始。

## CLI commands | CLI 命令

```bash
# 发布（--slug --name 可省略，从 _meta.json 读取）
clawhub publish <path> --version <version> --changelog "<text>"

# 管理
clawhub delete <slug> --yes
clawhub hide <slug> --yes
clawhub unhide <slug> --yes
clawhub undelete <slug> --yes
clawhub sync
```

## Version conflict | 版本冲突

If publish fails with `Version already exists`, bump the version and republish only after confirming with the user.
如果发布失败并提示 `Version already exists`，应先与用户确认，再升版本号重新发布。

## 查看安全扫描结果 | View Security Scan Results

发布后查看完整 Assessment 步骤：

1. 打开 ClawHub 技能页面（如 `https://clawhub.ai/skills/<slug>`）
2. 找到 **Security Scan** 区域
3. 找到 **OpenClaw Benign/Suspicious** 徽章旁边的 **Details ▾** 按钮
4. **点击 Details ▾ 展开** 才能看到完整的 Assessment 内容
5. Assessment 是 ClawHub 对技能的详细安全分析，包含 Purpose、Install Mechanism、Credentials 等项目的逐一评估

⚠️ **注意**：Summary 只是一句话概括，**必须展开 Details 才能看到完整 Assessment**。
