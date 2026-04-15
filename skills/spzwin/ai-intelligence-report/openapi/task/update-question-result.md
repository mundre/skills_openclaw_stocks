# POST https://cwork-api.mediportal.com.cn/ai-report/task/updateQuestionResult

## 作用

将用户新内容直接覆盖指定子章节，完成章节手动修改。

**鉴权类型**
- `access-token`

## 前置确认（强制）

调用本接口前，必须先向用户完整展示编辑后的章节内容，并获得用户明确确认；未确认不得执行保存。

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `questionId` | string | 是 | 子章节 `_id` |
| `result` | string | 是 | 新章节内容（Markdown） |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["questionId", "result"],
  "properties": {
    "questionId": { "type": "string" },
    "result": { "type": "string" }
  }
}
```

## 响应 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "resultCode": { "type": "number" },
    "resultMsg": { "type": ["string", "null"] },
    "data": { "type": "object" }
  }
}
```

## 脚本映射
- `../../scripts/task/update-question-result.py`
