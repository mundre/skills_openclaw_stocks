# POST https://cwork-api.mediportal.com.cn/ai-report/task/startTask

## 作用

基于指定模版发起异步报告生成任务，返回 `taskId`。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `mobanId` | string | 是 | 模版 ID |
| `taskName` | string | 是 | 报告名称 |
| `dirId` | string | 否 | 目录 ID（可选，不传时由后端按默认规则处理） |
| `context` | object | 否 | 报告生成上下文 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["mobanId", "taskName"],
  "properties": {
    "mobanId": { "type": "string" },
    "taskName": { "type": "string" },
    "dirId": { "type": ["string", "null"] },
    "context": { "type": ["object", "null"] }
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
- `../../scripts/task/start-task.py`
