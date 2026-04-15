# POST https://cwork-api.mediportal.com.cn/ai-report/moban/delMoban

## 作用

删除指定模版。仅创建者和管理员可操作。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `mobanId` | string | 是 | 目标模版 ID |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["mobanId"],
  "properties": {
    "mobanId": { "type": "string", "minLength": 1 }
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
    "data": { "type": ["object", "boolean", "null"] }
  }
}
```

## 脚本映射
- `../../scripts/moban/delete-moban.py`
