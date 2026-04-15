# Outbound AI Call API Reference

## 认证

所有请求需要 Header：
```
Content-Type: application/json
X-Access-Key: {API_KEY}
```

## 创建外呼

**Endpoint:** `POST /api/voice_call/llmSceneCall`
**Base URL:** `https://www.skill.black`

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | 是 | 目标电话号码 |
| messages | string[] | 是 | 对话上下文数组，格式：`["用户: ...", "助手: ..."]` |

**请求示例：**

```json
{
  "phone": "18033009923",
  "messages": [
    "用户: 帮我给蜀九香打个电话预约位子",
    "助手: 好的，请问预约什么时间？几位用餐？",
    "用户: 今天晚上7点，4个人"
  ]
}
```

**响应：**

**成功响应**：
```json
{
  "code": "10000",
  "result": "成功",
  "data": "12331@e561a4397b2a402488f2-638cd593f315"
}
```

**失败响应**：
```json
{
  "code": "190001",
  "result": "风控校验不通过不能外呼,风控拦截信息：1001涉政"
}
```

**code 说明：**

| code | 说明 | 处理方式 |
|------|------|----------|
| **10000** | 成功 | 使用 data 中的 request_id 查询结果 |
| **190001** | 风控拦截 | **不再重试**，告知用户风控原因 |
| 其他 | 失败 | 根据 result 判断原因 |

**常见错误码：**

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 130003 | 调用业务系统异常 | 稍后重试 |
| 190001 | 风控拦截 | 更换通话内容或联系管理员 |

## 查询通话记录

**Endpoint:** `POST /api/voice_call/llmSceneCallResult`
**Base URL:** `https://www.skill.black`

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| reqId | string | 是 | 创建外呼返回的 request_id |

**请求示例：**

```json
{
  "reqId": "2417278@uZGMSV5JDKEMJp67wOd93Q=="
}
```

**响应：**

**成功响应**：
```json
{
  "code": "10000",
  "result": "成功",
  "data": {
    "phone": "18033009923",
    "status": "5",
    "statusDesc": "已接通",
    "category": "CONNECTED",
    "callStartTime": "2026-03-20 15:51:17",
    "chatLogs": [
      {"role": "BOT", "content": "您好...", "msgTime": "2026-03-20 15:51:23"},
      {"role": "USER", "content": "你好", "msgTime": "2026-03-20 15:51:31"}
    ],
    "sid": "900581c1a8904c55b298d1e8ee53fd5d@1_1484459148920758272_2417278"
  }
}
```

**失败响应**：
```json
{
  "code": "140004",
  "result": "查询记录不存在"
}
```

**code 说明：**

| code | 说明 | 处理方式 |
|------|------|----------|
| **10000** | 成功 | 解析 data 中的通话信息 |
| 其他 | 失败 | 根据 result 判断原因 |
```

**通话状态码说明（data.status）：**

| status | statusDesc | 说明 |
|--------|------------|------|
| 1 | 待呼叫 | 排队中 |
| 13 | 呼叫中 | 正在拨打电话 |
| **5** | 已接通 | 对话完成，无需再查询 |
| 8 | 占线/无人接听 | 呼叫失败 |

**category 说明：**

| category | 说明 |
|----------|------|
| WAITING | 待呼叫 |
| CALLING | 呼叫中 |
| CONNECTED | 已接通 - 对话完成 |
| UN_CONNECTED | 未接通 |

## 配置

API Key 存放位置（二选一）：

1. 环境变量：`OUTBOUND_API_KEY`
2. 配置文件：`~/.openclaw/secrets/outbound.json`

```json
{
  "api_key": "your-api-key",
  "base_url": "https://www.skill.black"
}
```

## 错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 401 | API Key 无效 | 检查配置 |
| 429 | 频率限制 | 降低请求频率 |
| 500 | 服务器错误 | 稍后重试 |