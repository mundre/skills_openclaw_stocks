## 目录

- [接口概述](#接口概述)
- [SDK Request 类字段](#sdk-request-类字段)
- [miniapp_data 请求参数](#miniapp_data-请求参数json-字符串)
- [同步返回参数](#同步返回参数)
- [完整 SDK 调用示例](#完整-sdk-调用示例)
- [前端跳转小程序示例](#前端跳转小程序示例)
- [注意事项](#注意事项)

# 微信小程序预下单

## 接口概述

| 属性 | 值 |
|-----|-----|
| 汇付 API 端点 | `v2/trade/hosting/payment/preorder` |
| pre_order_type | `3`（微信小程序） |
| SDK Request 类 | `V2TradeHostingPaymentPreorderWxRequest` |
| 建议业务接口 | `POST /hfpay/preOrder`（通过 preOrderType 区分） |

## SDK Request 类字段

`V2TradeHostingPaymentPreorderWxRequest` 的专属字段：

| 字段 | setter 方法 | 类型 | 说明 |
|------|-----------|------|------|
| preOrderType | setPreOrderType() | String | 固定传 `"3"` |
| reqDate | setReqDate() | String | 请求日期 yyyyMMdd |
| reqSeqId | setReqSeqId() | String | 请求流水号 |
| huifuId | setHuifuId() | String | 商户号 |
| transAmt | setTransAmt() | String | 交易金额 |
| goodsDesc | setGoodsDesc() | String | 商品描述 |
| miniappData | setMiniappData() | String | **微信小程序扩展参数**（JSON 字符串） |

通过 `setExtendInfo(Map)` 传入的扩展字段：

| 字段 | 说明 |
|------|------|
| delay_acct_flag | 是否延迟入账，默认 `"N"` |
| notify_url | 异步通知地址 |
| acct_split_bunch | 分账对象（JSON 字符串） |
| time_expire | 交易失效时间 |
| fee_sign | 手续费场景标识 |

## miniapp_data 请求参数（JSON 字符串）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| seq_id | String(64) | N | 应用号。为空则使用汇付收银台小程序；自有渠道小程序需填写。微信插件方式不需要 |
| private_info | String(255) | N | 私有信息，对应异步通知中的 remark 字段 |
| need_scheme | String(1) | Y | 是否生成 scheme_code。**Y**=用于 APP/短信/邮件/外部网页跳转小程序场景；**N**=微信插件方式 |

## wx_data 参数（可选，通过 extendInfo 传入）

微信相关扩展参数：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sub_appid | String(32) | N | 微信子商户 appid |
| sub_openid | String(128) | N | 微信用户标识（JSAPI/小程序必填） |
| attach | String(127) | N | 附加数据，在查询和通知中原样返回 |
| body | String(128) | N | 商品描述（格式：品牌-城市-产品） |
| goods_tag | String(32) | N | 订单优惠标记 |
| detail | Object(6000) | N | 商品详情（单品优惠功能） |
| scene_info | Object(2048) | N | 场景信息（门店信息等） |
| device_info | String(32) | N | 设备号：1=iOS APP、2=Android APP、3=iOS H5、4=Android H5 |
| limit_payer | String(5) | N | 指定支付者，ADULT=仅成人可支付 |

## 同步返回参数

| 参数 | 类型 | 说明 |
|------|------|------|
| resp_code | String(8) | `00000000` 表示成功 |
| resp_desc | String(128) | 响应描述 |
| req_date | String(8) | 请求日期 |
| req_seq_id | String(64) | 请求流水号 |
| huifu_id | String(32) | 商户号 |
| trans_amt | String(12) | 交易金额 |
| pre_order_id | String(64) | 预下单订单号 |
| miniapp_data | String(2000) | **微信小程序跳转参数**（JSON 字符串） |

### miniapp_data 返回子字段

| 参数 | 说明 |
|------|------|
| gh_id | 小程序原始 ID（如 `gh_1ad0a7231d39`） |
| path | 小程序页面路径（如 `pages/cashier/cashier`） |
| scheme_code | 小程序跳转码（如 `weixin://dl/business/?t=xxx`）。need_scheme=N 时为空 |

## 完整 SDK 调用示例

```java
import com.huifu.bspay.sdk.opps.client.BasePayClient;
import com.huifu.bspay.sdk.opps.core.request.V2TradeHostingPaymentPreorderWxRequest;
import com.huifu.bspay.sdk.opps.core.utils.DateTools;
import com.huifu.bspay.sdk.opps.core.utils.SequenceTools;

// 1. 构建请求
V2TradeHostingPaymentPreorderWxRequest request = new V2TradeHostingPaymentPreorderWxRequest();
request.setReqDate(DateTools.getCurrentDateYYYYMMDD());
request.setReqSeqId(SequenceTools.getReqSeqId32());
request.setHuifuId("6666000123123123");
request.setTransAmt("1.00");
request.setGoodsDesc("商品描述");
request.setPreOrderType("3");  // 微信小程序

// 2. 构建 miniappData（注意字段是 seq_id/need_scheme，不是 sub_appid/openid）
String miniappData = "{\"need_scheme\":\"Y\"}";
// 如使用自有渠道小程序：miniappData = "{\"seq_id\":\"你的应用号\",\"need_scheme\":\"Y\"}";
request.setMiniappData(miniappData);

// 3. 设置扩展参数
Map<String, Object> extendInfoMap = new HashMap<>();
extendInfoMap.put("delay_acct_flag", "N");
extendInfoMap.put("notify_url", "https://your-domain.com/notify");
// 如需指定微信子商户 openid
// extendInfoMap.put("wx_data", "{\"sub_appid\":\"wxXXX\",\"sub_openid\":\"oXXX\"}");
request.setExtendInfo(extendInfoMap);

// 4. 发起请求
Map<String, Object> response = BasePayClient.request(request, false);

// 5. 处理响应 —— 返回的是 miniapp_data（非 pay_info）
String respCode = (String) response.get("resp_code");
String miniappDataResp = (String) response.get("miniapp_data");  // 小程序跳转参数
String preOrderId = (String) response.get("pre_order_id");       // 预下单订单号
```

## 前端跳转小程序示例

此接口返回 `miniapp_data`（含 `gh_id`、`path`、`scheme_code`），用于从 APP/H5 跳转到微信小程序收银台完成支付。

### 方式一：通过 scheme_code 跳转（APP/H5/短信场景，need_scheme=Y）

```javascript
// 后端返回 miniapp_data 后
const miniData = JSON.parse(response.miniapp_data);
// 直接跳转 scheme_code 唤起微信小程序
window.location.href = miniData.scheme_code;
// scheme_code 示例: weixin://dl/business/?t=c1HAi9XnUnt
```

### 方式二：通过 gh_id + path 跳转（微信插件方式，need_scheme=N）

```javascript
// 在微信小程序内使用插件方式
const miniData = JSON.parse(response.miniapp_data);
wx.navigateToMiniProgram({
    appId: miniData.gh_id,  // 小程序原始 ID
    path: miniData.path,    // 收银台页面路径
    success(res) { console.log('跳转成功'); },
    fail(err) { console.log('跳转失败', err); }
});
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
        "trans_amt": "1.00",
        "goods_desc": "微信小程序消费",
        "pre_order_type": "3",
        "miniapp_data": "{\"need_scheme\":\"Y\"}",
        "delay_acct_flag": "N",
        "notify_url": "https://your-domain.com/notify"
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
        "trans_amt": "1.00",
        "pre_order_id": "H2024051416544200912503288",
        "miniapp_data": "{\"gh_id\":\"gh_1ad0a7231d39\",\"path\":\"pages/cashier/cashier\",\"scheme_code\":\"weixin://dl/business/?t=c1HAi9XnUnt\"}"
    }
}
```

## 拆单支付参数（可选）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| split_pay_flag | String(1) | N | Y=拆单支付、N=普通支付（默认）。需提前开通 |
| split_pay_data | String(2000) | N | 拆单支付参数集合 |
| callback_url | String(512) | N | 支付完成后回调地址，需提前向汇付报备 |

## 注意事项

1. `miniapp_data` 请求字段是 `seq_id`、`private_info`、`need_scheme`，**不是** `sub_appid`/`openid`
2. 同步返回的是 `miniapp_data`（含 `gh_id`/`path`/`scheme_code`），**不是** `pay_info`
3. 此接口用于 APP/H5/外部网页 **跳转微信小程序收银台**，不是微信 JSAPI 支付
4. `need_scheme=Y` 时生成 `scheme_code` 用于 URL Scheme 跳转
5. `need_scheme=N` 时适用于微信插件方式，`scheme_code` 为空
6. `sub_appid` 和 `sub_openid` 放在 `wx_data` 扩展参数中（非 `miniapp_data`）
7. **务必保存** `req_seq_id` 和 `req_date`
