## 目录

- [接口概述](#接口概述)
- [SDK Request 类字段](#sdk-request-类字段)
- [app_data 参数](#app_data-参数json-字符串)
- [同步返回参数](#同步返回参数)
- [完整 SDK 调用示例](#完整-sdk-调用示例)
- [注意事项](#注意事项)

# 支付宝小程序预下单

## 接口概述

| 属性 | 值 |
|-----|-----|
| 汇付 API 端点 | `v2/trade/hosting/payment/preorder` |
| pre_order_type | `2`（支付宝小程序） |
| SDK Request 类 | `V2TradeHostingPaymentPreorderAliRequest` |
| 建议业务接口 | `POST /hfpay/preOrder`（通过 preOrderType 区分） |

## SDK Request 类字段

`V2TradeHostingPaymentPreorderAliRequest` 的专属字段：

| 字段 | setter 方法 | 类型 | 说明 |
|------|-----------|------|------|
| huifuId | setHuifuId() | String | 商户号 |
| reqDate | setReqDate() | String | 请求日期 yyyyMMdd |
| reqSeqId | setReqSeqId() | String | 请求流水号 |
| preOrderType | setPreOrderType() | String | 固定传 `"2"` |
| transAmt | setTransAmt() | String | 交易金额 |
| goodsDesc | setGoodsDesc() | String | 商品描述 |
| appData | setAppData() | String | **支付宝 App 扩展参数**（JSON 字符串） |

通过 `setExtendInfo(Map)` 传入的扩展字段：

| 字段 | 说明 |
|------|------|
| delay_acct_flag | 是否延迟入账，默认 `"N"` |
| notify_url | 异步通知地址 |
| acct_split_bunch | 分账对象（JSON 字符串） |
| time_expire | 交易失效时间 |
| fee_sign | 手续费场景标识 |

## app_data 参数（JSON 字符串）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| appid | String(32) | N | 支付宝小程序 appid |
| app_schema | String(100) | Y | 小程序完成支付后返回的 AppScheme。**限 100 字符**；如含 `+/?%#&=` 字符需 URL 编码 |
| private_info | String(255) | N | 私有信息，对应异步通知中的 remark 字段 |

## alipay_data 参数（可选，通过 extendInfo 传入）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| alipay_store_id | String(32) | N | 支付宝店铺编号 |
| extend_params | Object(2048) | N | 业务扩展参数（花呗分期等） |
| goods_detail | Array(2048) | N | 订单商品列表信息 |
| merchant_order_no | String(32) | N | 商户原始订单号 |
| product_code | String(32) | N | 产品码，小程序场景：`JSAPI_PAY` |
| subject | String(256) | N | 订单标题 |

### extend_params 子参数

| 参数 | 说明 |
|------|------|
| hb_fq_num | 花呗分期数（3/6/12） |
| hb_fq_seller_percent | 花呗卖家手续费百分比，商贴默认传 `0` |
| card_type | 卡类型 |
| food_order_type | 支付宝点餐场景类型 |

## 同步返回参数

| 参数 | 类型 | 说明 |
|------|------|------|
| resp_code | String(8) | `00000000` 表示成功 |
| resp_desc | String(128) | 响应描述 |
| req_date | String(8) | 请求日期 |
| req_seq_id | String(64) | 请求流水号 |
| huifu_id | String(32) | 商户号 |
| trans_amt | String(12) | 交易金额 |
| jump_url | String(256) | **支付宝跳转链接**，用于 App 跳转支付宝完成支付 |

## 完整 SDK 调用示例

```java
import com.huifu.bspay.sdk.opps.client.BasePayClient;
import com.huifu.bspay.sdk.opps.core.request.V2TradeHostingPaymentPreorderAliRequest;
import com.huifu.bspay.sdk.opps.core.utils.DateTools;
import com.huifu.bspay.sdk.opps.core.utils.SequenceTools;

// 1. 构建请求
V2TradeHostingPaymentPreorderAliRequest request = new V2TradeHostingPaymentPreorderAliRequest();
request.setReqDate(DateTools.getCurrentDateYYYYMMDD());
request.setReqSeqId(SequenceTools.getReqSeqId32());
request.setHuifuId("6666000123123123");
request.setTransAmt("1.00");
request.setGoodsDesc("商品描述");
request.setPreOrderType("2");  // 支付宝小程序

// 2. 构建 appData
String appData = "{\"app_schema\":\"alipays://platformapi/startapp?appId=你的小程序appId\"}";
request.setAppData(appData);

// 3. 设置扩展参数
Map<String, Object> extendInfoMap = new HashMap<>();
extendInfoMap.put("delay_acct_flag", "N");
extendInfoMap.put("notify_url", "https://your-domain.com/notify");
request.setExtendInfo(extendInfoMap);

// 4. 发起请求
Map<String, Object> response = BasePayClient.request(request, false);

// 5. 处理响应
String respCode = (String) response.get("resp_code");
String jumpUrl = (String) response.get("jump_url");  // 支付宝跳转链接
```

## 请求 JSON 示例

```json
{
    "sys_id": "6666000108840829",
    "product_id": "YYZY",
    "data": {
        "req_date": "20240514",
        "req_seq_id": "20240514165442868h32ss2g3s7vnxq",
        "huifu_id": "6666000109133323",
        "trans_amt": "0.10",
        "goods_desc": "支付宝小程序消费",
        "pre_order_type": "2",
        "app_data": "{\"app_schema\":\"app跳转链接\"}",
        "notify_url": "https://callback.service.com/xx",
        "acct_split_bunch": "{\"acct_infos\":[{\"huifu_id\":\"6666000109133323\",\"div_amt\":\"0.08\"}]}"
    }
}
```

## 返回 JSON 示例

```json
{
    "data": {
        "resp_code": "00000000",
        "resp_desc": "交易成功",
        "req_date": "20240514",
        "req_seq_id": "20240514165442868h32ss2g3s7vnxq",
        "huifu_id": "6666000109133323",
        "trans_amt": "0.10",
        "jump_url": "alipays://platformapi/startapp?appId=2021003121605466&page=pages/cashier/cashier?p%3DH2022042814245600912499897%26s%3Dapp"
    }
}
```

## 注意事项

1. 返回字段为 `jump_url`（非 `pay_url`），用于 App 内跳转支付宝
2. `app_schema` 参数过长容易导致浏览器截取跳转地址，无法唤起收银台，**限 100 字符**
3. 含特殊字符 `+/?%#&=` 的地址需要 URL 编码
4. **务必保存** `req_seq_id` 和 `req_date`
