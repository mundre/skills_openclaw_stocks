---
name: nexus-ai
description: Nexus 小程序统一智能助手。整合发布资源/岗位/活动、查询使用报告、智能问答三大功能。当用户说「发布资源/岗位/活动/招聘」「查询 nexus 总结/使用报告/AI使用报告」或询问资源/人、搜索信息时使用此技能。
---

# Nexus-AI：Nexus 统一智能助手

## 功能概览

| 功能 | 说明 | 触发词 |
|------|------|--------|
| 发布资源 | 发布资源/岗位/活动到 Nexus 平台 | 发布、我要招聘、发布岗位、发布活动 |
| 使用报告 | 查询 Nexus 小程序使用情况报告 | 查询总结、使用报告、AI使用报告、我的数据 |
| 智能问答 | 调用 RAG 智能搜索，查询资源/人/知识 | 搜索、查找、问问、查一下、帮我找 |

---

## 功能一：发布资源/岗位/活动

### API 信息

- **接口地址**: `https://nexus-saas-45653-8-1317958785.sh.run.tcloudbase.com/job/open-claw-create-job`
- **方法**: POST，所有参数作为 Query String 传递

### 必填参数

| 参数 | 说明 |
|------|------|
| `token` | JWT 认证令牌（存储在 `scripts/token.txt`，自动读取） |
| `phone` | 用户手机号 |
| `title` | 发布内容标题 |
| `content` | 发布内容正文/详情 |

### label 自动识别规则

| label | 触发关键词 |
|-------|----------|
| `校招` | 招聘、实习、校招、校园、春招、秋招、应届、管培 |
| `投/融资` | 投资、融资、天使轮、A轮、B轮、估值、资金 |
| `活动交流` | 活动、交流会、论坛、峰会、沙龙、会议、meetup |
| `置顶推广` | 推广、置顶、VIP、赞助、推广位、广告 |
| `需求` | 以上均不匹配时默认使用 |

### 执行方式

运行 `scripts/nexus_ai.py post --phone <手机号> --title <标题> --content <内容>`

### 输出格式

- 成功：✅ 发布成功，资源ID: xxx
- 失败：❌ 发布失败，错误信息

---

## 功能二：查询使用报告

### API 信息

- **端点**: `https://nexus-saas-45653-8-1317958785.sh.run.tcloudbase.com/summary/content_by_phone`
- **方法**: POST，phone 作为 Query 参数

### 执行方式

运行 `scripts/nexus_ai.py summary --phone <手机号>`

### 输出格式

1. 发送文字报告（清理 HTML 标签后的纯文本）
2. 发送二维码图片：`C:\Users\Songsh\.qclaw\workspace\nexus_report_template.png`（附件形式）

---

## 功能三：智能问答（RAG 搜索）

### API 信息

- **接口地址**: `https://ai.hydts.cn/ai/rag-stream`
- **方法**: POST
- **Content-Type**: application/json

### 请求参数

| 参数 | 说明 | 必填 |
|------|------|------|
| `query` | 用户的询问内容 | ✅ |
| `mod` | 固定值 `coze` | ✅ |
| `identity` | 身份标识（默认使用用户手机号） | ✅ |
| `session_id` | 会话 ID（可选，有值时放在返回内容第一行） | 可选 |

### 执行方式

运行 `scripts/nexus_ai.py ask --query <问题> [--session-id <会话ID>]`

### 输出格式

- 若有 session_id：返回内容第一行为 session_id，第二行空行，第三行起为实际内容
- 若无 session_id：直接返回内容

---

## 命令行接口（nexus_ai.py）

```bash
# 发布资源
python scripts/nexus_ai.py post --phone <手机号> --title <标题> --content <内容>

# 查询使用报告
python scripts/nexus_ai.py summary --phone <手机号>

# 智能问答
python scripts/nexus_ai.py ask --query <问题> [--session-id <会话ID>]
```

## 注意事项

- 所有脚本需在 `scripts/` 目录下运行
- 手机号必须是真实有效的中国大陆手机号
- 标题建议 5~20 字，内容建议 20 字以上