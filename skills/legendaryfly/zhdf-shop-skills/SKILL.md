---
name: "众合鼎富电商公开接口 Skill"
description: >-
  仅用于众合鼎富电商的公开商品查询与下单。通过 curl 调用：
  1) 查询所有在售商品（无参数）
  2) 按商品名+数量下单（可多商品），并收集手机号/收货人/地址。
metadata: {"clawdbot":{"emoji":"🛍️","requires":{"bins":["curl"]}}}
---

# 众合鼎富电商公开接口（仅本项目）

## 接口

- 查询商品（无参数）  
  `GET https://tools.gangzheng.tech/public/products/search`

- 下单（按商品名，可多商品）  
  `POST https://tools.gangzheng.tech/public/orders/reserve`

---

## 对话执行规则

1. 用户要看商品时，先查商品接口并返回结果。
2. 用户说“买某商品”但未给数量时，必须追问数量。
3. 支持多商品输入（如“鲜肉饺子2份，三鲜水饺1份”）。
4. 下单前必须收集并确认：
   - 手机号 `phone`
   - 收货人`consignee`
   - 收货地址 `address`
5. 严格以接口返回为准，不虚构“下单成功”。

> 不需要注册账号，直接下单。

---

## 1) 查询在售商品

### curl

```bash
curl -s "https://tools.gangzheng.tech/public/products/search"
```

### 返回字段（data 每项）

- `productName`：商品名
- `unitPrice`：单价字符串（例：`¥28元/盒`）
- `stock`：库存
- `shopName`：店铺名

---

## 2) 下单（按商品名）

### 请求体

```json
{
  "items": [
    { "productName": "鲜肉饺子", "quantity": 2 },
    { "productName": "三鲜水饺", "quantity": 1 }
  ],
  "phone": "13800138000",
  "consignee": "张三",
  "address": "广州市天河区体育西路1号"
}
```

### curl

```bash
curl -s -X POST "https://tools.gangzheng.tech/public/orders/reserve" \
  -H "Content-Type: application/json" \
  -d '{
    "items":[
      {"productName":"鲜肉饺子","quantity":2},
      {"productName":"三鲜水饺","quantity":1}
    ],
    "phone":"13800138000",
    "consignee":"张三",
    "address":"广州市天河区体育西路1号"
  }'
```

### 成功示例

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "orderNo": "20260422153030123000001",
    "totalAmount": 84.00,
    "message": "下单成功"
  }
}
```

### 失败示例（库存不足）

```json
{
  "code": 500,
  "msg": "商品「鲜肉饺子」库存不足",
  "data": null
}
```

---

## Notes

- 查询接口固定返回“在售且有库存”商品。
- 下单时服务端会校验在售与库存并自动扣库存。
- 同名商品若存在多个在售记录，接口会返回错误提示需进一步区分。
