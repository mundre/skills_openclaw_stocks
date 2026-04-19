---
name: cms-find-skills
description: 用于"安装 Skill / 下载 Skill / 找一个能做 X 的 Skill / 把某个 Skill 装到本地 / 列出平台 Skill"。从 CMS 平台搜索已有 Skill 并按 downloadUrl 下载 ZIP 解压到本地 ~/.claude/skills。仅负责查找与安装，不负责创建或发布
skillCode: cms-find-skills
---

**当前版本**: v1.6.0

# cms-find-skills

只做两件事：

1. 调用 `get-skills` 查看平台上已有的 Skill。
2. 根据 `downloadUrl` 下载 ZIP 并解压到本地。

不要登录，不要授权，不要扩展上传、发布、更新、下架能力。

## 当前目录

- `SKILL.md`
- `references/skill-registry/README.md`
- `scripts/skill_registry/get_skills.py`
- `scripts/skill_registry/install_skill.py`

所有说明文档统一使用 Markdown；本 Skill 不再维护旧接口文档目录。

## 路由

- 查看列表：`python3 cms-find-skills/scripts/skill_registry/get_skills.py`
- 搜索：`python3 cms-find-skills/scripts/skill_registry/get_skills.py --search "关键词"`
- 查看详情：`python3 cms-find-skills/scripts/skill_registry/get_skills.py --detail "code 或 name"`
- 取下载地址：`python3 cms-find-skills/scripts/skill_registry/get_skills.py --url "code 或 name"`
- 安装到本地：`python3 cms-find-skills/scripts/skill_registry/install_skill.py --code "code"`
- 已知下载地址时安装：`python3 cms-find-skills/scripts/skill_registry/install_skill.py --url "https://..."`

## 规则

1. 统一以 `get-skills` 返回的数据为准。
2. 安装方式固定为：下载 ZIP -> 解压到目标目录。
3. 默认安装到脚本所在 workspace 的 `skills/` 目录，可用 `--target` 覆盖。
4. 本地已存在同名 Skill 时默认跳过，加 `--force` 可删除旧目录并重新安装。
5. 只维护 Markdown 说明和 Python 脚本，不维护旧接口文档副本。
