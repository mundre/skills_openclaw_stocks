# POST https://cwork-api.mediportal.com.cn/ai-report/task/listResultVersion

## 作用

查询指定子章节历史修改版本，用于回溯与比较。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `questionId` | string | 是 | 子章节 `_id` |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["questionId"],
  "properties": {
    "questionId": { "type": "string" }
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
    "data": { "type": "array", "items": { "type": "object" } }
  }
}
```

## 脚本映射
- `../../scripts/task/list-result-version.py`
