# POST https://cwork-api.mediportal.com.cn/ai-report/moban/listMobanByPageV2

## 作用

按分页、关键词、目录、仅看我的条件检索模版列表。

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
| `dirId` | string | 否 | 目录筛选 |
| `searchKey` | string | 否 | 模版名关键词 |
| `onlyMine` | string | 否 | 是否仅看我的，传 `true` |

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
    "searchKey": { "type": ["string", "null"] },
    "onlyMine": { "type": ["string", "null"] }
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
- `../../scripts/moban/list-moban.py`
