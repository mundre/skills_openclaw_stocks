## 目录

- [接口概述](#接口概述)
- [SDK Request 类字段](#sdk-request-类字段)
- [hosting_data 参数](#hosting_data-参数json-字符串)
- [同步返回参数](#同步返回参数)
- [完整 SDK 调用示例](#完整-sdk-调用示例)
- [请求 JSON 示例](#请求-json-示例)
- [返回 JSON 示例](#返回-json-示例)
- [注意事项](#注意事项)

# H5/PC 预下单

## 接口概述

| 属性 | 值 |
|-----|-----|
| 汇付 API 端点 | `v2/trade/hosting/payment/preorder` |
| pre_order_type | `1`（H5/PC） |
| SDK Request 类 | `V2TradeHostingPaymentPreorderH5Request` |
| 建议业务接口 | `POST /hfpay/preOrder` |

## SDK Request 类字段

`V2TradeHostingPaymentPreorderH5Request` 的专属字段（均有独立 setter）：

| 字段 | setter 方法 | 类型 | 说明 |
|------|-----------|------|------|
| reqDate | setReqDate() | String | 请求日期 yyyyMMdd |
| reqSeqId | setReqSeqId() | String | 请求流水号 |
| huifuId | setHuifuId() | String | 商户号 |
| transAmt | setTransAmt() | String | 交易金额 |
| goodsDesc | setGoodsDesc() | String | 商品描述 |
| preOrderType | setPreOrderType() | String | 固定传 `"1"` |
| hostingData | setHostingData() | String | 半支付托管扩展参数（JSON 字符串） |

通过 `setExtendInfo(Map)` 传入的扩展字段：

| 字段 | 说明 |
|------|------|
| delay_acct_flag | 是否延迟入账，默认 `"N"` |
| notify_url | 异步通知地址 |
| time_expire | 交易失效时间 |
| acct_split_bunch | 分账对象（JSON 字符串） |

## hosting_data 参数（JSON 字符串）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_title | String | Y | 项目名称 |
| project_id | String | Y | 项目 ID |
| callback_url | String(512) | N | 支付完成后回调地址，不填则停留当前页面 |
| private_info | String(255) | N | 私有信息，对应异步通知中的 remark 字段 |
| request_type | String(1) | C | 页面类型：P=PC页面（默认）、M=H5页面。指定 trans_type 时必填 |

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
| pre_order_type | String(1) | 预下单类型，原样返回 |
| goods_desc | String(40) | 商品描述，原样返回 |
| hosting_data | String(2000) | 托管扩展参数，原样返回 |
| current_time | String(14) | 系统响应时间 yyyyMMddHHmmss |
| time_expire | String(14) | 交易失效时间 yyyyMMddHHmmss |
| jump_url | String(256) | **支付跳转链接**，引导用户跳转完成支付 |

## 完整 SDK 调用示例

```java
import com.huifu.bspay.sdk.opps.client.BasePayClient;
import com.huifu.bspay.sdk.opps.core.request.V2TradeHostingPaymentPreorderH5Request;
import com.huifu.bspay.sdk.opps.core.utils.DateTools;
import com.huifu.bspay.sdk.opps.core.utils.SequenceTools;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

// 1. 构建请求
V2TradeHostingPaymentPreorderH5Request request = new V2TradeHostingPaymentPreorderH5Request();
request.setReqDate(DateTools.getCurrentDateYYYYMMDD());
request.setReqSeqId(SequenceTools.getReqSeqId32());
request.setHuifuId("6666000123123123");    // 商户号
request.setTransAmt("1.00");               // 交易金额
request.setGoodsDesc("商品描述");           // 商品描述
request.setPreOrderType("1");              // H5/PC 预下单

// 2. 构建 hostingData
ObjectMapper objectMapper = new ObjectMapper();
ObjectNode hostingData = objectMapper.createObjectNode();
hostingData.put("project_title", "项目名称");
hostingData.put("project_id", "项目ID");
hostingData.put("callback_url", "https://your-domain.com/callback");
request.setHostingData(hostingData.toString());

// 3. 设置扩展参数
Map<String, Object> extendInfoMap = new HashMap<>();
extendInfoMap.put("delay_acct_flag", "N");
extendInfoMap.put("notify_url", "https://your-domain.com/notify");
request.setExtendInfo(extendInfoMap);

// 4. 发起请求
Map<String, Object> response = BasePayClient.request(request, false);

// 5. 处理响应
String respCode = (String) response.get("resp_code");
String jumpUrl = (String) response.get("jump_url");    // 支付跳转链接
String reqSeqId = (String) response.get("req_seq_id"); // 保存用于后续查询/退款
String reqDate = (String) response.get("req_date");    // 保存用于后续查询/退款
```

## 请求 JSON 示例

```json
{
    "sys_id": "6666000108840829",
    "product_id": "YYZY",
    "sign": "RSA签名（SDK自动生成）",
    "data": {
        "req_date": "20240514",
        "req_seq_id": "20240514165442868h32ss2g3s7vnxq",
        "huifu_id": "6666000109133323",
        "trans_amt": "1.00",
        "goods_desc": "测试商品",
        "pre_order_type": "1",
        "hosting_data": "{\"project_title\":\"项目名称\",\"project_id\":\"项目ID\",\"callback_url\":\"https://your-domain.com/callback\"}",
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
        "jump_url": "https://cashier.huifu.com/pay/xxxxx"
    }
}
```

## 前端跳转处理

预下单成功后返回 `jump_url`，前端需引导用户跳转到汇付收银台完成支付。

### 后端重定向（推荐）

```java
// Spring Boot Controller 中直接 302 重定向
@GetMapping("/pay")
public void redirectToPay(@RequestParam String orderId, HttpServletResponse response) throws IOException {
    // 1. 根据 orderId 查询之前保存的 jump_url
    String jumpUrl = orderService.getJumpUrl(orderId);
    // 2. 302 重定向到汇付收银台
    response.sendRedirect(jumpUrl);
}
```

### 前端跳转

```javascript
// 方式 1：直接跳转（最常用）
window.location.href = jumpUrl;

// 方式 2：新窗口打开（PC 场景）
window.open(jumpUrl, '_blank');
```

### callback_url 回调处理

支付完成后，汇付收银台会将用户浏览器重定向到 `hosting_data` 中设置的 `callback_url`：

- `callback_url` 是**前端页面地址**（非后端接口），用于将用户带回商户页面
- 汇付会在 URL 后附加查询参数（如 `?resp_code=00000000&req_seq_id=xxx`）
- **不能依赖 callback_url 判断支付结果**，必须以异步通知或查询接口结果为准
- 如不设置 callback_url，支付完成后用户停留在汇付收银台页面

```javascript
// 前端回调页面示例：解析 URL 参数展示支付状态
const params = new URLSearchParams(window.location.search);
const respCode = params.get('resp_code');
if (respCode === '00000000') {
    showMessage('支付处理中，请等待确认...');
    // 轮询后端查询接口确认最终状态
    pollPaymentStatus(params.get('req_seq_id'));
} else {
    showMessage('支付未完成，请重试');
}
```

## 注意事项

1. `jump_url` 为支付跳转链接，前端需引导用户跳转到此 URL 完成支付
2. **务必保存** `req_seq_id` 和 `req_date`，后续查询订单和退款均需使用
3. `hosting_data` 中 `project_id` 需替换为实际项目 ID，不可使用示例值
4. `notify_url` 必须为可公网访问的 HTTPS 地址
5. 交易失效时间默认 10 分钟，用户在失效后完成交易可能被关单
