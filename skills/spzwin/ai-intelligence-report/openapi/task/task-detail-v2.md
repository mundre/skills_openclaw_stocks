# POST https://cwork-api.mediportal.com.cn/ai-report/task/taskDetailV2

## 作用

查询单个报告任务详情，包括章节与子章节内容。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `taskId` | string | 是 | 报告任务 ID |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["taskId"],
  "properties": {
    "taskId": { "type": "string" }
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
- `../../scripts/task/task-detail-v2.py`
