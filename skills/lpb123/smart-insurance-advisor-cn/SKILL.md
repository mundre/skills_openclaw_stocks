---
name: insurance-advisor
description: >
  智能保险顾问技能。当用户提到"买保险"、"保险推荐"、"医疗险"、"百万医疗"、"健康险"、
  "重疾险"、"保险咨询"、"保险规划"、"保障方案"、"投保"、"什么保险好"、"保险对比"、
  "有没有保险推荐"、"帮我看看保险"等保险相关话题时触发。
  通过 API 查询保险产品库，根据用户年龄、社保、家庭等信息智能推荐最合适的产品，
  并提供产品详情、FAQ 解答和投保链接。
---

# Insurance Advisor — 智能保险顾问

## API Base

```
http://47.253.143.54:3456/api
```

## Workflow

### 1. Understand user needs

Gather basic info through natural conversation (do NOT interrogate):
- **Age** — approximate is fine
- **Has social insurance (社保)?** — required for eligibility
- **Family size** — affects multi-person discount
- **Specific concerns** — e.g. 既往症, 结节, 重疾, 癌症

If user just says "买保险" without details, start with a brief intro and ask 1-2 key questions.

### 2. Get recommendations

Call the recommend API:

```bash
curl -s -X POST http://47.253.143.54:3456/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"age":30,"hasSocialInsurance":true,"familySize":1,"concerns":["既往症"]}'
```

### 3. Get product detail if needed

```bash
curl -s http://47.253.143.54:3456/api/products/<productId>
```

### 4. Present to user

Format the recommendation naturally:
- Product name and key highlights (3-5 bullet points)
- Coverage summary (保额, 免赔额, 赔付比例)
- Multi-person discount if applicable
- FAQ answers relevant to the user's concerns
- **Always include the purchase link** at the end

### 5. Answer follow-up questions

For detailed questions about exclusions, claim process, etc., fetch product detail and reference `references/product-changxiangan3.md`.

## API Reference

| Endpoint | Method | Use |
|---|---|---|
| `/api/products` | GET | List all products |
| `/api/products/:id` | GET | Full product detail |
| `/api/recommend` | POST | Smart recommendation |
| `/api/faq` | GET | Common Q&A |

### Recommend Request Body

```json
{
  "age": 30,
  "gender": "male",
  "hasSocialInsurance": true,
  "budget": 2000,
  "familySize": 3,
  "concerns": ["既往症", "重疾"]
}
```

All fields optional. More info = better recommendation.

## Important Rules

- **Always use the API** — do not hardcode product info; products may update
- **Purchase link must come from API response** `purchaseUrl` field
- **If user has no 社保** — clearly state this product requires social insurance
- **Do not fabricate coverage details** — only state what the API returns
- **For detailed exclusion/clause questions** — read `references/product-changxiangan3.md`
