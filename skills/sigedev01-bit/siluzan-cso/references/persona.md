# persona：人设列表（GetPersonas）

对应 Web / MarkAI `getPersonas()`：`POST {csoBaseUrl}/cso/v1/platformdata/GetPersonas`，请求体 `{}`。返回人设列表，含 **`styleGuide`**（Markdown 风格指南）、`materials`、`taskStatus` 等，供文案与三库工作流使用。

## 命令

```text
siluzan-cso persona list [选项]
```

| 选项 | 说明 |
|------|------|
| `-t, --token <token>` | 凭据（可选，默认读 `~/.siluzan/config.json`） |
| `--id <id>` | 只显示指定人设 id |
| `--name <text>` | 按人设名称子串过滤（客户端过滤） |
| `--json` | 输出完整 JSON（含完整 `styleGuide`） |
| `--unicode` | 表格使用 Unicode 线框 |
| `--verbose` | 打印详细错误 |

## 字段说明

| 字段 | 含义 |
|------|------|
| `personaName` | 人设名称 |
| `styleGuide` | 风格指南正文（Markdown） |
| `materials` | 参考素材（文件名、URL 等） |
| `taskStatus` | `1` 待生成 · `2` 生成中 · `3` 生成完成 · `4` 生成失败 |

终端表格仅展示 `styleGuide` 摘要；需要全文时用 `--json`。

## 与 Skill 的关系

编写口播/成稿前应先拿到目标人设的 `styleGuide`，再结合 `three-lib-content-workflow/` 中的 SOP。详见上级 `SKILL.md`「三库内容工作流」。
