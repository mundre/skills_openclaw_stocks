# cms-find-skills · Skill Registry & ZIP 校验契约

本文档描述 `cms-find-skills` 与平台 Skill 注册中心的交互契约，以及下载 Skill ZIP 包后的安全/完整性校验规则。

## 1. 接口概览

| 用途 | 接口 | 方法 |
|------|------|------|
| 列出 Skill | `POST {API_BASE}/api/skill/list` | 公开，无需鉴权 |

`API_BASE` 默认 `https://skills.mediportal.com.cn`，可通过环境变量 `CMS_API_BASE` 覆盖。

返回结构（典型）：
```json
{
  "resultCode": 1,
  "data": [
    {
      "skillCode": "im-robot",
      "displayName": "IM 机器人",
      "version": "1.2.0",
      "downloadUrl": "https://.../im-robot.zip",
      "description": "...",
      "metadata": { "openclaw": { "tags": [] }, "xgjk": { "isInternal": true } }
    }
  ]
}
```

成功判定：`resultCode in (None, 1)`。

## 2. 下载与解压

`install_skill.py` 流程：
1. 通过 `get_skills.py` 找到 `downloadUrl`，或直接使用用户传入的 `--url`。
2. 下载到临时目录，校验 `zipfile.is_zipfile()`。
3. 安全解压（见下）。
4. 校验解压后的目录中存在 `SKILL.md`。

## 3. ZIP 安全校验规则（必须遵守）

- 使用 `_normalize_zip_member()`：
  - 拒绝空路径、根 `.`。
  - 拒绝 `..` 越界路径。
  - 统一斜杠分隔符。
- 使用 `_safe_extract()`：
  - 通过 `os.path.realpath` 拼接目标，确认仍在 `destination` 内（防 symlink/路径穿越）。
  - 跳过软链接（不写入 symlink），仅展开文件与目录。
- 解压后必须存在 `SKILL.md`，否则视为非合法 Skill 包，安装失败。

## 4. 与 cms-create-skill 的关系

`cms-create-skill/scripts/skill-management/get_skills.py` 是本目录中 `get_skills.py` 的薄封装，**事实来源（source of truth）位于本 Skill**。修改逻辑请只改本目录下的版本。

## 5. 校验脚本

`verify_skill.py` 提供下载后的离线结构校验，可被 `install_skill.py` 或 CI 调用。
