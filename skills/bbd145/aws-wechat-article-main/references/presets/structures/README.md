# 文章结构预设

本目录下的 `.md` 文件为**文章结构预设**。写作时按 config 的 `default_structure` 或用户指定加载。

## Schema

- 每个文件为一篇 Markdown，描述**标准结构**：标题、摘要、开头类型、正文小标题与段落节奏、结尾类型、配图密度建议。
- 可引用 [writing 内置结构模板](../../../aws-wechat-article-writing/references/structure-template.md)，在其基础上做增减或改写。
- 文件名即预设名（不含后缀），如 `listing.md` → 预设名 `listing`。在 config 中设置 `default_structure: listing` 即可默认使用。

## 示例

见 `listing.example.md`。复制为 `listing.md`（或自定义文件名）后按需修改。
