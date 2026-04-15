# POST https://cwork-api.mediportal.com.cn/ai-report/task/listTaskByPage

## 作用

按目录、状态、关键词等条件分页查询 AI 情报报告列表。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `pageNum` | number | 是 | 页码，从 0 开始 |
| `pageSize` | number | 是 | 每页条数 |
| `dirId` | string | 否 | 目录 ID，按目录筛选 |
| `mobanTypeId` | string | 否 | 模版类型 ID |
| `state` | number | 否 | 状态：0 未开始，1 进行中，2 已完成，3 失败 |
| `searchKey` | string | 否 | 搜索关键词（报告标题） |
| `reportType` | number | 否 | 报告来源：1 普通，2 定时，3 系统 |
| `delFlag` | number | 否 | 删除标记，0 未删除 |
| `onlyMine` | string | 否 | 是否仅看我的，传 `true` |
| `onlyMineStatus` | number | 否 | 与 `onlyMine` 配合，筛选状态 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["pageNum", "pageSize"],
  "properties": {
    "pageNum": { "type": "number", "minimum": 0 },
    "pageSize": { "type": "number", "minimum": 1 },
    "dirId": { "type": ["string", "null"] },
    "mobanTypeId": { "type": ["string", "null"] },
    "state": { "type": ["number", "null"] },
    "searchKey": { "type": ["string", "null"] },
    "reportType": { "type": "number" },
    "delFlag": { "type": "number" },
    "onlyMine": { "type": ["string", "null"] },
    "onlyMineStatus": { "type": ["number", "null"] }
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
    "data": {
      "type": "object",
      "properties": {
        "pageContent": { "type": "array", "items": { "type": "object" } },
        "total": { "type": "number" }
      }
    }
  }
}
```

## 脚本映射
- `../../scripts/task/list-task-by-page.py`
