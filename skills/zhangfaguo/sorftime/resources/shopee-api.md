# Shopee API Skill

## 基本信息
- **名称**: shopee-api
- **描述**: Sorftime Shopee平台API调用工具，支持越南、印尼、新加坡等8个站点的类目、产品、店铺数据查询
- **激活条件**: 当用户提到Shopee、虾皮、东南亚电商、sorftime-cli Shopee相关操作时自动激活
- **依赖**: sorftime-cli 已全局安装并配置有效Account-SK

---

## 前置配置

### 1. 安装sorftime-cli
```bash
npm install -g sorftime-cli
```

### 2. 配置账户
```bash
# 添加账户
sorftime add <profile-name> <your-account-sk>

# 切换到默认账户
sorftime use <profile-name>
```

### 3. 权限认证说明
- API采用HttpPost方式进行数据处理
- 需要在请求头设置Authorization参数：`header["Authorization"] = "BasicAuth <Key>"`
- 设置ContentType：`header["ContentType"] = "application/json;charset=UTF-8"`
- CLI会自动处理权限认证和数据解码（gzip+base64）

---

## Domain参数说明（Shopee 8个站点）

| domain值 | 站点代码 | 站点名称 | 所属区域 |
|---------|---------|---------|---------|
| 201 | vn | 越南站 | 东南亚 |
| 202 | id | 印尼站 | 东南亚 |
| 203 | sg | 新加坡站 | 东南亚 |
| 204 | th | 泰国站 | 东南亚 |
| 205 | my | 马来西亚站 | 东南亚 |
| 206 | tw | 中国台湾站 | 东亚 |
| 207 | ph | 菲律宾站 | 东南亚 |
| 208 | br | 巴西站 | 南美 |

---

## 通用返回结构

所有接口返回统一结构：
```json
{
  "Code": 0,
  "Message": null,
  "Data": {},
  "RequestLeft": 9999,
  "RequestConsumed": 1,
  "RequestCount": 1
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| Code | Integer | 响应码：0=成功，非0=失败 |
| Message | String | 响应信息，失败时返回错误描述 |
| Data | Object/Array | 接口返回的业务数据 |
| RequestLeft | Integer | 当月剩余请求次数 |
| RequestConsumed | Integer | 本次请求消耗的次数 |
| RequestCount | Integer | 本分钟内请求计数 |

---

## 重要说明

### 1. 数据解码
- Shopee平台的返回结果使用gzip压缩并转化成base64字符串
- CLI会自动处理base64解码和gzip解压，用户无需手动处理
- 接收到的数据为base64字符串，CLI会先还原成byte[]，再gzip解压获得原文

### 2. 销量说明
- **预估月销量**: 基于产品当前的排名预估未来30天的销量
- **近30日销量**: 过去30天的实际销量
- **销量校准**: 由于Shopee存在"数据灌蜜"的情况，系统会反向校对销量数据
  - 当`saleIsCorrection=true`时，表示已做销量校准
  - 此时建议调用ProductTrend接口重新拉取销量趋势数据

### 3. 积分系统
- 监控相关功能涉及积分消耗
- 每月10号凌晨自动清空上期未用完部分并发放新积分

### 4. 请求频率
- 最高10次/秒，建议批量查询时控制速度

---

## 接口列表

### 一、类目市场类接口

#### 1. 类目树 (CategoryTree)
- **接口说明**: 返回Shopee全量类目树结构
- **消耗请求数**: 5次
- **注意**: 返回数据很大（约10MB+），建议设置较长超时时间
- **请求参数**: 无
- **使用示例**:
  ```bash
  # Shopee越南站类目树
  sorftime api CategoryTree --domain 201
  
  # Shopee泰国站类目树
  sorftime api CategoryTree --domain 204
  
  # Shopee马来西亚站类目树
  sorftime api CategoryTree --domain 205
  
  # Shopee巴西站类目树
  sorftime api CategoryTree --domain 208
  ```
- **返回字段说明**:
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | id | Integer | 类目ID |
  | parentId | Integer | 父级类目ID，为0表示第一级 |
  | nodeid | String | 类目nodeid（用于后续查询） |
  | name | String | 类目名称 |
  | cnName | String | 类目中文名称 |
  | url | String | 类目URL地址 |

---

#### 2. 类目市场 (CategoryRequest)
- **接口说明**: 查询类目Best Seller Top 500产品数据
- **消耗请求数**: 10次
- **注意**: 
  - 数据范围：best seller top 500
  - 仅细分类目支持历史回看，非细分类目始终返回当前数据
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | nodeId | String | 是 | 需要查找的类目Id（从CategoryTree获取） |
  | queryDate | String | 否 | 格式yyyy-MM-dd，查询历史（指定日期所处自然周）榜单数据 |
- **历史回看说明**:
  - 例如：2025-03-10，表示查询2025-03-10 ~ 2025-03-16自然周的数据
  - 仅细分类目支持，非细分类目时此参数无效
- **使用示例**:
  ```bash
  # 查询当前Best Seller数据
  sorftime api CategoryRequest '{"nodeId": "12345"}' --domain 201
  
  # 查询历史数据（2025-03-10所在自然周）
  sorftime api CategoryRequest '{"nodeId": "12345", "queryDate": "2025-03-10"}' --domain 201
  ```
- **返回数据结构**:
  - Subcategory: Boolean，是否为细分类目
  - products: ProductSummeryObject Array，类目下产品列表

---

### 二、产品类接口

#### 3. 产品详情 (ProductRequest)
- **接口说明**: 查询单个产品的详细信息
- **消耗请求数**: 1次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | productId | String | 是 | 需要查询的产品Id |
- **使用示例**:
  ```bash
  sorftime api ProductRequest '{"productId": "12345678"}' --domain 201
  
  sorftime api ProductRequest '{"productId": "87654321"}' --domain 204
  ```
- **返回字段说明** (ProductSummeryObject):
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | title | String | 产品名称 |
  | photo | String Array | 产品主图URL数组 |
  | productId | String | 产品ID |
  | updateTime | String | 数据更新时间 |
  | salesCount | Integer | 近30日销量 |
  | salesAmount | Number | 近30日销售额 |
  | salesCalcTime | String | 计算产品销量的时间 |
  | saleIsCorrection | Boolean | 是否做了销量校准（true表示已校准） |
  | hisSalesCount | Integer | 累计销量 |
  | shopId | String | 卖家店铺ID |
  | shopName | String | 卖家店铺名称 |
  | shopLocation | String | 店铺来源城市 |
  | shopLocType | String | 店铺类型：本土店或跨境店 |
  | shopType | String | 店铺类型：普通店、优选店、旗舰店 |
  | price | Number | 产品销售价 |
  | listPrice | Number | 划线价 |
  | discount | Number | 折扣率（如46.00表示降价46%） |
  | brand | String | 产品品牌 |
  | brandId | String | 品牌ID |
  | ratings | Number | 评分星级（如4.8） |
  | ratingCount | Integer | 评论数量 |
  | saleTime | String | 产品上线时间 |
  | couponStr | String | 优惠券信息 |
  | ratingDetail | String | 星级组成JSON数组：[1星数量,2星数量,3星数量,4星数量,5星数量] |
  | bsrCategory | String | 所属细分类目JSON数组：[["类目名称","NodeId","排名"],...] |

---

#### 4. 产品历史趋势 (ProductTrend)
- **接口说明**: 查询产品历史趋势数据（销量、价格、评论等）
- **消耗请求数**: 2次
- **注意**: 当ProductRequest返回saleIsCorrection=true时，建议调用此接口重新拉取数据
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | productId | String | 是 | 需要查询的产品Id |
- **使用示例**:
  ```bash
  sorftime api ProductTrend '{"productId": "12345678"}' --domain 201
  ```
- **返回字段说明** (ProductTrendObject):
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | productId | String | 产品ID |
  | saleCountTrend | String | 按日统计的近30日销量趋势数组 |
  | saleTotalCountTrend | String | 累计销量趋势数组 |
  | priceTrend | String | 价格趋势数组（仅在价格变化时记录） |
  | reviewCountTrend | String | 按月统计评论数量趋势数组 |
  | starTrend | String | 按月统计星级趋势数组 |
- **趋势数据格式说明**:
  - 数组格式：`["20231001","775","20231002","765",...]`
  - 偶数下标为日期/月份，奇数下标为对应数据值
  - 价格趋势：仅在价格变化时记录，最后一个数据为截止日期
    - 例如：`["20241001","19.99","20241102","18.99","20250402","18.99"]`
  - 星级趋势：450表示4.5星

---

### 三、店铺类接口（Shopee专属）

#### 5. 店铺查询 (ShopRequest)
- **接口说明**: 查询店铺的详细信息和运营数据
- **消耗请求数**: 5次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | shopId | String | 是 | 需要查询的店铺Id |
- **使用示例**:
  ```bash
  sorftime api ShopRequest '{"shopId": "123456"}' --domain 201
  
  sorftime api ShopRequest '{"shopId": "789012"}' --domain 204
  ```
- **返回字段说明** (ShopObject):
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | shopId | String | 店铺ID |
  | shopName | String | 店铺名称 |
  | shopLocation | String | 店铺来源地 |
  | shopImage | String | 店铺主图链接 |
  | shopType | String | 店铺类型：普通店、优选店、旗舰店 |
  | saleDate | String | 开店日期（例：2020-09-20） |
  | shopStar | Integer | 店铺星级（例：4.50表示4.5星） |
  | shopRating | Integer Array | 店铺评论数JSON数组：[好评价数,中性评价数,差评价数] |
  | top500ProductCount | Integer | 店铺卖进top500的产品数 |
  | top500SalesCount | Integer | 店铺卖进top500产品月销量 |
  | top500salesAmount | Number | 店铺卖进top500产品月销额 |
  | top500Products | String | 店铺卖进top500产品ID清单JSON数组（最多500个） |

---

## 注意事项

1. **请求频率**: 最高10次/秒，建议批量查询时控制速度
2. **账户配置**: 所有接口默认使用当前活跃profile的Account-SK

---

## 常见错误

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 0 | 成功 | - |
| 401 | 认证失败 | 检查Account-SK是否有效 |
| 403 | 权限不足 | 检查套餐权限或请求次数 |
| 404 | 接口不存在 | 检查接口名称拼写 |
| 429 | 请求频率超限 | 降低请求速度，等待1分钟后重试 |
| 500 | 服务器内部错误 | 稍后重试，或联系Sorftime客服 |

---

## 最佳实践

### 1. 完整的类目分析流程
```bash
# 步骤1: 获取类目树，找到目标类目的nodeId
sorftime api CategoryTree --domain 201

# 步骤2: 查询该类目的Best Seller Top 500
sorftime api CategoryRequest '{"nodeId": "12345"}' --domain 201

# 步骤3: 查询具体产品的详细信息
sorftime api ProductRequest '{"productId": "67890"}' --domain 201

# 步骤4: 如果销量已校准，重新拉取趋势数据
sorftime api ProductTrend '{"productId": "67890"}' --domain 201
```

### 2. 店铺分析
```bash
# 查询店铺详细信息
sorftime api ShopRequest '{"shopId": "123456"}' --domain 201

# 分析店铺的Top 500产品表现
# 从返回的top500Products中获取产品ID列表
# 然后逐个查询产品详情
sorftime api ProductRequest '{"productId": "prod1"}' --domain 201
```

### 3. 多站点对比分析
```bash
# 越南站
sorftime api CategoryRequest '{"nodeId": "12345"}' --domain 201

# 泰国站
sorftime api CategoryRequest '{"nodeId": "67890"}' --domain 204

# 马来西亚站
sorftime api CategoryRequest '{"nodeId": "11111"}' --domain 205
```

### 4. 历史数据分析
```bash
# 查询指定自然周的Best Seller数据
sorftime api CategoryRequest '{"nodeId": "12345", "queryDate": "2025-03-10"}' --domain 201
# 这将查询2025-03-10至2025-03-16自然周的数据
```

### 5. 产品趋势追踪
```bash
# 查询产品的完整历史趋势
sorftime api ProductTrend '{"productId": "12345678"}' --domain 201

# 分析返回的趋势数据：
# - saleCountTrend: 近30日每日销量
# - priceTrend: 价格变化历史
# - reviewCountTrend: 月度评论数变化
# - starTrend: 月度星级变化
```
