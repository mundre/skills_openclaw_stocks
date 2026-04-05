# ClawHub Publish Guide | ClawHub 发布指南

## Two-step publishing workflow | 两步发布工作流

### Step 1: Pre-publish checks | 第一步：发布前检查

**A. Run full checklist | 完整清单核对**
Verify all items in the "Skill creation/modification checklist" section of SKILL.md:
逐项核对 SKILL.md 中"技能制作/修改清单"的全部项目。

**B. File size check | 文件大小检查**
```bash
du -sh <skill-dir>
```
If the directory **exceeds 50MB**, the upload will fail.
- Report to user immediately.
- Move oversized files (e.g., model files) to a workspace backup location. Wait for explicit user confirmation.
- After upload succeeds, move files back. Wait for user confirmation again.
如果目录**超过 50MB**，上传会失败。立即报告用户，等待明确指示后再操作。

**C. Draft changelog | 拟定 changelog**
- English first, Chinese after.
  英文在前,中文在后。
- Formal release-note tone only.
  仅使用正式发布说明语气。

**Changelog format | changelog 格式：**
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

### Step 2: Detailed report → Wait for second confirmation | 第二步：详细汇报 → 等待用户再次确认

Report the following to user. **Do NOT upload until user explicitly confirms.**

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
| Full publish command | `clawhub publish ...` |

**Restart rule | 重启规则：**
Each user modification request → restart from Step 1.
每次用户提出修改，都必须从第一步重新开始。

## CLI commands | CLI 命令

```bash
clawhub publish <path> --slug <slug> --name "<name>" --version <version> --changelog "<text>"
clawhub delete <slug> --yes
clawhub hide <slug> --yes
clawhub unhide <slug> --yes
clawhub undelete <slug> --yes
clawhub sync
```

## Version conflict | 版本冲突

If publish fails with `Version already exists`, bump the version and republish only after confirming with the user.
如果发布失败并提示 `Version already exists`，应先与用户确认，再升版本号重新发布。
