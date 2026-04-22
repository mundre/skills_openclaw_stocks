---
name: api-tester
description: API testing assistant. Tests REST API endpoints, validates responses, and generates test reports. Triggers: api testing, rest api, http test, endpoint validation.
metadata: {"openclaw": {"emoji": "🧪"}}
---

# API Tester — API测试助手

## 功能说明

测试和验证REST API接口。

## 使用方法

### 1. 基础接口测试

```
用户: 测试 GET https://api.example.com/users
```

执行步骤：
1. 发送请求
2. 记录响应时间
3. 验证状态码
4. 解析响应体
5. 输出测试结果

### 2. 完整接口测试

```
用户: 测试以下API：
POST https://api.example.com/users
Headers: Content-Type: application/json
Body: {"name": "test", "email": "test@example.com"}
```

执行步骤：
1. 构造请求
2. 发送并计时
3. 验证响应：
   - 状态码是否符合预期
   - 响应格式是否正确
   - 必要字段是否存在
4. 输出详细报告

### 3. 批量测试

```
用户: 批量测试以下接口列表：
1. GET /users
2. GET /users/1
3. POST /users
4. PUT /users/1
5. DELETE /users/1
```

执行步骤：
1. 依次测试每个接口
2. 记录每个接口的结果
3. 汇总成功/失败数量
4. 计算平均响应时间

### 4. 性能测试

```
用户: 对 GET /api/data 进行性能测试，发送100次请求
```

执行步骤：
1. 循环发送请求
2. 记录每次响应时间
3. 计算统计指标：
   - 平均响应时间
   - 最小/最大响应时间
   - P95/P99 延迟
4. 识别慢请求

## 示例输出

```
API 测试报告

接口: GET https://api.example.com/users
时间: 2026-04-06 10:00:00

请求信息:
- 方法: GET
- URL: https://api.example.com/users
- Headers: Authorization: Bearer xxx

响应信息:
- 状态码: 200 OK ✓
- 响应时间: 156ms
- 响应大小: 2.3KB

响应体验证:
✓ status 字段存在
✓ data 字段为数组
✓ data 包含 25 条记录
✓ 每条记录包含 id, name, email

性能指标:
- 平均: 156ms
- 最小: 98ms
- 最大: 312ms
- P95: 245ms

结论: 测试通过 ✓
```

## 认证支持

- Bearer Token
- API Key (Header/Query)
- Basic Auth
- OAuth 2.0
