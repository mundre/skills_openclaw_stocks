# POST https://cwork-api.mediportal.com.cn/ai-report/moban/changeMobanState

## 作用

切换指定模版的发布状态（上架/下架）。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `mobanId` | string | 是 | 模版 ID |
| `state` | number | 是 | 状态：`0` 未发布（下架），`1` 已发布（上架） |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["mobanId", "state"],
  "properties": {
    "mobanId": { "type": "string", "minLength": 1 },
    "state": { "type": "number", "enum": [0, 1] }
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
    "data": { "type": ["object", "null"] }
  }
}
```

## 脚本映射
- `../../scripts/moban/change-moban-state.py`
