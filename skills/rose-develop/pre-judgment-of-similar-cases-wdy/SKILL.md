---
name: pre-judgment-of-similar-cases-wdy
description: "类案预判(法律检索 + 类似案例)。当用户描述一个纠纷或案件时（如'被骗了2万'、'朋友借钱不还'、'被打伤了'），自动检索相关法律条文和类似判例，分析法律后果、胜诉概率、可主张的赔偿及建议下一步行动。适用于：侵权责任、诈骗欺诈、合同纠纷、债务纠纷、治安纠纷、专利/商标/著作权等。"
---

# pre-judgment-of-similar-cases-wdy：类案预判(法律检索 + 类似案例)

## 配置说明

1. 获取 API Key：打开 https://open.wintaocloud.com/home 登录后在个人中心或开发者中心获取
2. **WENDAOYUN_API_KEY 必须通过环境变量配置**，不写入磁盘文件
   ```bash
   export WENDAOYUN_API_KEY=你的 API Key
   ```
3. 每日调用额度100次

> ⚠️ API Key 属于敏感信息，请妥善保管，不要泄露给他人。发现泄露请及时在问道云开放平台作废。
>
> ⚠️ **隐私与数据泄露风险（重要）**：本技能将用户描述的案件内容（可能包含姓名、金额、纠纷细节等个人隐私）发送至问道云第三方 API 进行检索。这是一种固有风险——案件信息会被传输至外部服务器。如处理涉及当事人隐私的案件时，请确认符合当地隐私法规和道德准则，必要时建议用户自行判断是否适合使用本技能，或改用本地法律数据库替代。

---

## 配置

- **Base URL**: `https://h5.wintaocloud.com`
- **认证**: `Authorization: Bearer {WENDAOYUN_API_KEY}`
- **请求方式**: POST
- **载荷**: `{"content": "检索内容", "top_k": 3}`（top_k 默认 3，最大 5）

## 接口

| 接口 | 完整路径 | 用途 |
|------|----------|------|
| 法律条文 | `https://h5.wintaocloud.com/prod-api/api/invoke/get-laws` | 查询相关法律条文 |
| 类似案例 | `https://h5.wintaocloud.com/prod-api/api/invoke/get-cases` | 查询类似判例 |

## 调用方式

直接用 `exec` + `curl` 调用：

**法律条文检索**：
```bash
curl -s -X POST "https://h5.wintaocloud.com/prod-api/api/invoke/get-laws" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${WENDAOYUN_API_KEY}" \
  -d '{"content": "检索关键词", "top_k": 3}'
```

**类似案例查询**：
```bash
curl -s -X POST "https://h5.wintaocloud.com/prod-api/api/invoke/get-cases" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${WENDAOYUN_API_KEY}" \
  -d '{"content": "案例描述", "top_k": 3}'
```

## 输出格式

### 法律条文
```json
{
  "code": 200,
  "data": [{
    "legalNature": "法律",
    "laws": [{
      "legalName": "中华人民共和国专利法",
      "total": 2,
      "items": [{
        "dataName": "第七十七条",
        "chapterName": "第一章",
        "content": "条文内容...",
        "score": 0.6233
      }]
    }]
  }]
}
```

### 类似案例
```json
{
  "code": 200,
  "data": [{
    "caseNumber": "（2024）粤知民终XX号",
    "caseFact": "案情摘要...",
    "content": "判决书内容...",
    "score": 0.6275
  }]
}
```

展示时需格式化：
- 法律条文：标题 → 条号/章节 → 内容 → 相关度
- 类似案例：案号 → 摘要 → 预览（取前100字）

---

## 调用前检查

**必须在使用 skill 之前检查 WENDAOYUN_API_KEY 是否已配置。**

检查方式：运行 `[ -n "${WENDAOYUN_API_KEY}" ]` 或 `test -n "${WENDAOYUN_API_KEY}"`，根据退出码判断是否已配置（退出码0=已设置，非0=未设置）。**严禁使用 `echo` 打印 WENDAOYUN_API_KEY 内容**，否则会泄露到日志或对话历史中。

- **未配置时** → 立即告知用户"法律检索服务需要配置 WENDAOYUN_API_KEY 才能使用"，并提供获取步骤。不再尝试调用接口。
- **已配置时** → 正常调用接口。

> ⚠️ 严禁在未确认 WENDAOYUN_API_KEY 存在的情况下直接调用接口，失败后再告知用户。这是本 skill 的硬性规则，违者视为 bug。

---

## 错误处理

- 未设置 WENDAOYUN_API_KEY → **事前告知**（见上方"调用前检查"）
- 接口返回非 200 → 告知用户检查网络或 token
- 请求超时 → 告知用户稍后重试

---

## 触发场景

- 用户询问法律条文、法律依据
- 用户描述纠纷案例（"小明骗我2万"、"签合同被坑"）
- 用户明确说"帮我查 XX 的类似案例"
- 模糊时主动询问："需要我帮你检索相关法律条文和类似案例吗？"
