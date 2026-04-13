# rag：RAG 知识库检索（仅文案）

与 Siluzan-RAG-sys-ui `MultiFileChat.vue` / `queryKnowledges` 一致：**只用于写稿、三库流程**。

## 接口

- `GET {csoBaseUrl}/cutapi/v1/material/queryknowledges`

## 默认值（与 `three-lib-content-workflow/libraries.md` 对齐）

| 参数 | 默认行为 |
|------|----------|
| **belongToId** | 不传时，使用 **GET `/query/account/me`** 响应中的 **`companyId`**（亦尝试 `companyInfo.id`） |
| **tags** | 不传 `--tags` 时，默认三个标签：**`流量因子库`**、**`产品资产库`**、**`烹调方法库`**（与三库章节标题一致）。若传入 `--tags`，则**完全以参数为准**（可传空字符串表示不按标签过滤，视后端行为而定） |
| **source-id / folder-id** | 可选；用于缩小到指定素材或文件夹，与网页勾选文件/文件夹一致 |

## 命令

```text
siluzan-cso rag query -q "<关键词>"
siluzan-cso rag query -q "<关键词>" --belong-to-id <企业ID>
siluzan-cso rag query -q "<关键词>" --source-id <id1,id2>
```

| 选项 | 说明 |
|------|------|
| `-q, --query` | 检索关键词或问句（必填） |
| `--tags` | 见上表默认三库标签 |
| `--top-k` | 3–30，默认 `7` |
| （默认） | **完整 Markdown** 打印检索结果|
| `--json` | JSON，含 `belongToId`、`tags`、完整 `output` |

若未传 `--belong-to-id` 且 `/query/account/me` 无 `companyId`，需手动传入。

## 与三库工作流

拆素材、对齐业务事实时引用向量片段；标签与三库命名一致，便于知识库侧按库打标。
