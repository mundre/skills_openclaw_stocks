# lk-order-mcp Skill

> 瑞幸咖啡订单 MCP 服务。提供一键下单、门店查询、商品浏览、购物车管理、订单管理、优惠券/咖啡券管理、地址管理等功能。适用于瑞幸咖啡内部订购系统。

---

## 📦 快速开始

### 1. 配置 MCP 服务

在 `openclaw.json` 中添加以下配置：

```json
{
  "mcpServers": {
    "lk-order": {
      "url": "https://inpre.lkcoffee.com/app/proxymcp",
      "transportType": "streamable-http",
      "headers": {
        "Authorization": "Bearer <YOUR_TOKEN>"
      }
    }
  }
}
```

### 2. 初始化会话

```bash
/home/node/.openclaw/scripts/lkorder-mcp.sh init
```

### 3. 调用工具

```bash
/home/node/.openclaw/scripts/lkorder-mcp.sh call <方法名> '[参数 JSON]'
```

---

## 🎯 触发条件

当用户提到以下关键词时触发本 Skill：

### ☕ 品牌/场景触发（最高优先级）
- **品牌词**: "瑞幸"、"luckin"、"瑞幸咖啡"
- **需求词**: "饿"、"饿了吗"、"想吃"、"想吃东西"、"肚子饿"
- **吃喝词**: "喝"、"喝的"、"吃"、"吃的"、"来杯"、"来份"
- **品类词**: "饮品"、"饮料"、"轻食"、"面包"、"蛋糕"、"三明治"、"小吃"

### 🛒 下单相关
- **动作词**: "下单"、"点咖啡"、"买咖啡"、"订购"、"点单"、"点餐"、"买点"、"整一杯"
- **商品名**: "特仑苏"、"美式"、"拿铁"、"生椰"、"瑞纳冰"、"燕麦"、"摩卡"、"卡布奇诺"

### 🏪 门店查询
- "附近门店"、"门店列表"、"店铺"、"瑞幸店"、"哪里有店"、"最近门店"

### 📋 订单管理
- "我的订单"、"订单详情"、"取消订单"、"删除订单"、"查订单"、"订单状态"

### 🛒 购物车
- "购物车"、"加入购物车"、"清空购物车"、"看看购物车"

### 🎫 优惠券/卡券
- "优惠券"、"咖啡券"、"咖啡钱包"、"咖啡库券"、"有什么券"、"用券"

### 📍 地址管理
- "收货地址"、"添加地址"、"修改地址"、"外送地址"

---

## 🛠️ 可用工具（35 个）

### 🚀 下单相关（6 个）

| 工具名 | 说明 | 必填参数 |
|--------|------|----------|
| `quick_order` | **一键下单**（自动找门店→选商品→创建订单→支付） | `keyword`（想喝什么） |
| `create_order` | 创建订单 | `deptId`, `delivery`, `productList` |
| `preview_order` | 预览订单（计算价格、优惠、配送费） | `deptId`, `delivery`, `productList` |
| `pay_order` | 支付订单 | `orderId` |
| `cancel_order` | 取消订单 | `orderId` |
| `delete_order` | 删除订单 | `orderList` |

### 🏪 门店/商品（5 个）

| 工具名 | 说明 | 必填参数 |
|--------|------|----------|
| `get_nearby_shops` | 获取附近门店列表 | 无（自动根据 IP 定位） |
| `get_shop_detail` | 获取门店详情 | `deptId` |
| `get_menu` | 获取门店菜单 | `deptId` |
| `get_product_detail` | 获取商品详情 | `productId`, `deptId` |
| `calculate_price` | 计算商品价格 | `productId`, `deptId`, `skuCode` |

### 🛒 购物车（5 个）

| 工具名 | 说明 | 必填参数 |
|--------|------|----------|
| `get_shopping_cart` | 获取购物车信息 | `deptId` |
| `add_to_cart` | 加入购物车 | `productId`, `skuCode` |
| `clear_cart` | 清空购物车 | 无 |
| `set_cart_checked` | 设置购物车行勾选状态 | `skuCodes`, `checked` |
| `checkout_cart` | 结算购物车 | `deptId`, `delivery` |

### 🎫 优惠券/卡券（4 个）

| 工具名 | 说明 | 必填参数 |
|--------|------|----------|
| `get_coupon_list` | 获取我的优惠券列表 | 无 |
| `get_ticket_list` | 获取下单时可用的优惠券 | `deptId`, `productList` |
| `get_coffee_wallet_list` | 获取咖啡钱包列表 | 无 |
| `get_coffee_store_list` | 获取下单时可用的咖啡库券 | `deptId`, `productList` |

### 📍 地址管理（5 个）

| 工具名 | 说明 | 必填参数 |
|--------|------|----------|
| `get_user_addresses` | 获取收货地址列表 | 无 |
| `search_address` | 搜索地址 | `keyName` |
| `add_address` | 添加收货地址 | `userName`, `sex`, `tel`, `address` |
| `update_address` | 更新收货地址 | `addrId`, `userName`, `sex`, `tel`, `address` |
| `delete_address` | 删除收货地址 | `addrId` |

### 📋 订单管理（3 个）

| 工具名 | 说明 | 必填参数 |
|--------|------|----------|
| `get_order_list` | 获取订单列表 | 无 |
| `get_order_detail` | 获取订单详情 | `orderId` |
| `get_pay_list` | 获取支付方式列表 | `deptId` |

### ⚙️ 其他（7 个）

| 工具名 | 说明 | 必填参数 |
|--------|------|----------|
| `session_info` | 查看登录状态 | 无 |
| `logout` | 退出登录 | 无 |
| `restore_session` | 恢复会话 | `token` |
| `get_activity_list` | 获取营销活动优惠列表 | `deptId`, `productList` |
| `get_remark_options` | 获取订单备注选项 | `deptId`, `productList` |
| `get_city_list` | 获取已开通城市列表 | 无 |
| `get_user_city` | 根据经纬度定位城市 | `longitude`, `latitude` |

---

## 📖 使用示例

### 1. 一键下单（最常用）

```bash
# 简单下单
/home/node/.openclaw/scripts/lkorder-mcp.sh call quick_order '{"keyword":"美式"}'

# 指定规格
/home/node/.openclaw/scripts/lkorder-mcp.sh call quick_order '{
  "keyword": "拿铁",
  "temperature": "热",
  "cup": "大杯",
  "sugar": "标准糖",
  "amount": 1,
  "payType": "7",
  "useCafeKu": true,
  "useDiscount": true
}'

# 指定门店
/home/node/.openclaw/scripts/lkorder-mcp.sh call quick_order '{
  "keyword": "生椰",
  "deptId": "617654",
  "latitude": 24.5086,
  "longitude": 118.1932
}'
```

### 2. 支付输出格式

下单成功后，支付信息会以 **Markdown 格式**输出，包含：

- ✅ 支付链接（可点击）
- ✅ 二维码图片（可直接扫码）
- ✅ 订单详情表格

**输出示例**：

```markdown
## ✅ 下单成功！

### 📱 支付信息

| 项目 | 内容 |
|------|------|
| **订单号** | `7629296683999035401` |
| **支付方式** | 支付宝 |
| **支付金额** | ¥28.9 |

### 🔗 支付链接

[点击打开支付页面](https://openpre.lkcoffee.com/pay?orderId=xxx)

### 📸 支付二维码

![支付二维码](https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=xxx)

> 💡 使用支付宝或微信扫一扫即可完成支付
```

### 2. 获取附近门店

```bash
/home/node/.openclaw/scripts/lkorder-mcp.sh call get_nearby_shops '{
  "latitude": 24.5086,
  "longitude": 118.1932
}'
```

### 3. 查看购物车

```bash
/home/node/.openclaw/scripts/lkorder-mcp.sh call get_shopping_cart '{
  "deptId": "617654"
}'
```

### 4. 获取优惠券列表

```bash
/home/node/.openclaw/scripts/lkorder-mcp.sh call get_coupon_list '{}'
```

### 5. 查看订单列表

```bash
/home/node/.openclaw/scripts/lkorder-mcp.sh call get_order_list '{
  "pageNo": 1
}'
```

### 6. 获取门店菜单

```bash
/home/node/.openclaw/scripts/lkorder-mcp.sh call get_menu '{
  "deptId": "617654"
}'
```

---

## 🔧 调用方式

### 方式 1：使用 Shell 脚本（推荐）

```bash
# 初始化会话（首次使用或 session 过期时）
/home/node/.openclaw/scripts/lkorder-mcp.sh init

# 调用工具
/home/node/.openclaw/scripts/lkorder-mcp.sh call <方法名> '[参数 JSON]'

# 示例
/home/node/.openclaw/scripts/lkorder-mcp.sh call session_info
/home/node/.openclaw/scripts/lkorder-mcp.sh call quick_order '{"keyword":"拿铁"}'

# 重置会话
/home/node/.openclaw/scripts/lkorder-mcp.sh reset
```

### 方式 2：直接 curl 调用

```bash
# 1. 初始化获取 Session ID
SESSION_ID=$(curl -s -i -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
  https://inpre.lkcoffee.com/app/proxymcp | grep -i "^mcp-session-id:" | awk '{print $2}')

# 2. 调用工具
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "mcp-session-id: ${SESSION_ID}" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  https://inpre.lkcoffee.com/app/proxymcp
```

---

## 📝 会话管理

### Session ID 持久化
- **保存位置**: `/tmp/lkorder-session-id.txt`
- **有效期**: 由服务端决定（通常数小时）
- **自动恢复**: 脚本会自动读取已保存的 Session ID

### 重置会话
```bash
/home/node/.openclaw/scripts/lkorder-mcp.sh reset
```

---

## ⚠️ 错误处理

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `缺少有效的会话 ID` | Session 过期或丢失 | 执行 `init` 重新初始化 |
| `请求错误：参数校验失败` | 参数格式错误 | 检查必填参数和 JSON 格式 |
| `未找到门店` | 经纬度无效或附近无门店 | 检查经纬度或扩大搜索范围 |
| `商品已售罄` | 商品库存不足 | 更换商品或选择其他门店 |
| `支付方式不可用` | 该门店不支持指定支付方式 | 更换支付方式 |

---

## 📋 注意事项

1. **首次使用必须先初始化**：执行 `init` 获取 Session ID
2. **Session ID 必须携带**：所有后续请求需包含 `mcp-session-id` header
3. **参数格式严格**：JSON 参数必须符合 schema 定义
4. **坐标系统**：经纬度使用 GCJ-02 标准（国内）
5. **支付方式**：
   - `1` = 支付宝（返回支付链接）
   - `2` = 微信（返回支付链接）
   - `7` = 余额（直接扣款，推荐）
6. **取餐方式**：
   - `pick` = 自取
   - `delivery` = 外送（需填写地址）

---

## 🚀 快速参考

### 最常用场景

```bash
# 1. 一键下单（最简单）
./lkorder-mcp.sh call quick_order '{"keyword":"美式"}'

# 2. 查看登录状态
./lkorder-mcp.sh call session_info

# 3. 获取附近门店
./lkorder-mcp.sh call get_nearby_shops '{"latitude":24.4798,"longitude":118.0894}'

# 4. 查看我的订单
./lkorder-mcp.sh call get_order_list '{"pageNo":1}'

# 5. 获取优惠券
./lkorder-mcp.sh call get_coupon_list '{}'

# 6. 查看购物车
./lkorder-mcp.sh call get_shopping_cart '{"deptId":"12345"}'

# 7. 获取门店菜单
./lkorder-mcp.sh call get_menu '{"deptId":"12345"}'

# 8. 加入购物车
./lkorder-mcp.sh call add_to_cart '{"productId":"1262","skuCode":"126201","amount":1}'
```

---

## 📁 相关文件

| 文件 | 说明 |
|------|------|
| `/home/node/.openclaw/scripts/lkorder-mcp.sh` | MCP 调用脚本 |
| `/home/node/.openclaw/scripts/lkorder-lib.sh` | 工具函数库 |
| `/tmp/lkorder-session-id.txt` | Session ID 保存文件 |
| `/home/node/.openclaw/openclaw.json` | OpenClaw 配置（含 Token） |

---

## 🔐 安全提醒

### Token 配置（重要！）

**⚠️ Token 属于敏感凭证，切勿硬编码在代码中！**

**配置方式 1：环境变量（推荐）**
```bash
export LK_ORDER_TOKEN="your_token_here"
```

**配置方式 2：openclaw.json**
```json
{
  "mcpServers": {
    "lk-order": {
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  }
}
```

**配置方式 3：.env 文件（仅开发环境）**
```bash
cp .env.example .env
# 编辑 .env 填入 Token
```

### 安全最佳实践

⚠️ **请勿**：
- 提交 Token 到代码仓库（已加入 .gitignore）
- 发送给无关人员
- 在公开场合展示
- 使用他人提供的 Token

✅ **建议**：
- 定期检查订单记录
- 发现异常立即重置 Token
- 仅在自己信任的设备上使用

📖 详细安全说明请查看 [SECURITY.md](SECURITY.md)

---

如需更新 Token，请编辑 `/home/node/.openclaw/openclaw.json` 中的 `mcpServers.lk-order.headers.Authorization` 字段。

---

## 📞 技术支持

如遇问题，请检查：
1. Session ID 是否有效
2. Token 是否正确
3. 网络连接是否正常
4. 参数格式是否符合要求

---

**版本**: 1.0.0  
**最后更新**: 2026-04-16  
**适用环境**: 瑞幸咖啡内部订购系统
