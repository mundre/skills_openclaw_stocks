# Amazon Product API Skill

## 基本信息
- **名称**: amazon-product
- **描述**: Sorftime 亚马逊产品数据查询工具，支持产品详情、搜索、趋势、评论、子体等全维度数据查询
- **激活条件**: 当用户提到亚马逊产品查询、ASIN分析、产品搜索、产品评论、竞品分析时自动激活
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

---

## Domain参数说明（亚马逊14个站点）

| domain值 | 站点代码 | 站点名称 |
|---------|---------|---------|
| 1 | us | 美国站 |
| 2 | gb | 英国站 |
| 3 | de | 德国站 |
| 4 | fr | 法国站 |
| 5 | in | 印度站 |
| 6 | ca | 加拿大站 |
| 7 | jp | 日本站 |
| 8 | es | 西班牙站 |
| 9 | it | 意大利站 |
| 10 | mx | 墨西哥站 |
| 11 | ae | 阿联酋站 |
| 12 | au | 澳大利亚站 |
| 13 | br | 巴西站 |
| 14 | sa | 沙特站 |

---

## 通用返回结构

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

### 特殊返回码说明
- **0**: 成功
- **4**: 积分余额不足
- **97**: ASIN不存在
- **98**: 采集失败
- **99**: 正在实时抓取数据，预计耗时5分钟，请稍后重试

---

## 重要说明

1. **月销量**: 基于产品近30日销量估算，如果月销量极低，统一返回5
2. **批量查询**: ProductRequest支持一次查询最多10个ASIN
3. **趋势数据**: AE、AU、SA站点趋势数据密度较低
4. **积分消耗**: 部分实时监控接口消耗积分而非request

---

## 接口列表

### 一、产品基础查询

#### 1. 产品详情 (ProductRequest)
- **接口说明**: 产品（Listing）详情查询，支持单ASIN或多ASIN查询
- **消耗请求数**: 1次（多ASIN查询也是1次，最多10个ASIN）
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | asin | String | 是 | 需要查询的ASIN，多asin用逗号分割，最多10个 |
  | trend | Integer | 否 | 是否包含趋势数据：1=包含（默认），2=不包含 |
  | queryTrendStartDt | String | 否 | 趋势查询起始日期，格式yyyy-MM-dd，不指定默认返回近15天 |
  | queryTrendEndDt | String | 否 | 趋势查询截止日期，格式yyyy-MM-dd |
- **注意**: 
  - 当请求历史趋势超过15天时，消耗request=2
  - 趋势数据仅返回近15天，如需更多数据需指定queryTrendStartDt
- **使用示例**:
  ```bash
  # 查询单个ASIN
  sorftime api ProductRequest '{"asin": "B0CVM8TXHP"}' --domain 1
  
  # 查询多个ASIN（最多10个）
  sorftime api ProductRequest '{"asin": "B0CVM8TXHP,B0XXXXXXX,B0YYYYYYY"}' --domain 1
  
  # 查询ASIN并包含近30天趋势数据
  sorftime api ProductRequest '{"asin": "B0CVM8TXHP", "trend": 1, "queryTrendStartDt": "2024-01-01"}' --domain 1
  
  # 查询ASIN但不包含趋势数据（节省请求）
  sorftime api ProductRequest '{"asin": "B0CVM8TXHP", "trend": 2}' --domain 1
  ```

---

#### 2. 产品搜索 (ProductQuery)
- **接口说明**: 多维度查产品，支持单条件查询和多条件组合查询
- **消耗请求数**: 5次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | query | Integer | 否 | 查询方式：1=单条件查询（默认），2=多条件组合查询 |
  | queryType | Integer | 条件性 | 查询类型（1-16），query=2时无效 |
  | pattern | String/JSON | 是 | 查询条件对应的值 |
  | queryMonth | String | 否 | 回看历史月份，格式yyyy-MM，最长支持2024年1月起2年内数据 |
  | page | Integer | 否 | 分页查询，每页最多100个产品，默认1 |
- **queryType查询类型说明**:
  | 值 | 查询类型 | pattern示例 | 说明 |
  |----|---------|------------|------|
  | 1 | 基于ASIN查询同类产品 | "B0CVM8TXHP" | 注意：并非只查询这个ASIN |
  | 2 | 基于类目查询 | "3743561" | 不限为细分类目 |
  | 3 | 查询品牌热销产品 | "Anker" | 品牌名称 |
  | 4 | 基于卖家名称查询 | "AnkerDirect" | 卖家名称 |
  | 5 | 基于卖家SellerId查询 | "A294P4X9EWVXLJ" | 卖家ID |
  | 6 | 基于ABA关键词查热销产品 | "Power Bank" | 仅支持ABA关键词 |
  | 7 | 基于产品标题/属性包含词 | "10,000mAh 30W" | 匹配标题/属性中包含特定词 |
  | 8 | 限定销售价范围 | "1,1000" 或 ",1000" | 货币为当地最小单位（美分） |
  | 9 | 限定月销量范围 | "100,1000" 或 ",1000" | 月销量范围 |
  | 10 | 限定季节性产品 | "1,2,3" | 查询1,2,3月为销售旺季的产品 |
  | 11 | 限定上架时间范围 | "20240601,20241201" | 格式yyyyMMdd |
  | 12 | 限定星级范围 | "3,5" 或 "4," | 星级范围 |
  | 13 | 限定评论数量范围 | "10,500" 或 ",500" | 评论数范围 |
  | 14 | 限定排名范围 | "500,5000;1,100" | 分号前为大类排名，分号后为小类排名 |
  | 15 | 限定发货方式 | "FBA" | FBA或FBM |
  | 16 | 限定子体数范围 | "1,50" | 子体数量范围 |
- **使用示例**:
  ```bash
  # 单条件：基于ASIN查询同类产品
  sorftime api ProductQuery '{"query": 1, "queryType": 1, "pattern": "B0CVM8TXHP"}' --domain 1
  
  # 单条件：基于类目查询
  sorftime api ProductQuery '{"query": 1, "queryType": 2, "pattern": "3743561"}' --domain 1
  
  # 单条件：查询品牌热销产品
  sorftime api ProductQuery '{"query": 1, "queryType": 3, "pattern": "Anker"}' --domain 1
  
  # 单条件：基于卖家名称查询
  sorftime api ProductQuery '{"query": 1, "queryType": 4, "pattern": "AnkerDirect"}' --domain 1
  
  # 单条件：基于ABA关键词查热销产品
  sorftime api ProductQuery '{"query": 1, "queryType": 6, "pattern": "Power Bank"}' --domain 1
  
  # 单条件：限定月销量范围（100-1000）
  sorftime api ProductQuery '{"query": 1, "queryType": 9, "pattern": "100,1000"}' --domain 1
  
  # 单条件：限定价格范围（1-10美元，单位为美分）
  sorftime api ProductQuery '{"query": 1, "queryType": 8, "pattern": "100,1000"}' --domain 1
  
  # 单条件：限定星级范围（4星以上）
  sorftime api ProductQuery '{"query": 1, "queryType": 12, "pattern": "4,"}' --domain 1
  
  # 单条件：限定评论数量（少于500）
  sorftime api ProductQuery '{"query": 1, "queryType": 13, "pattern": ",500"}' --domain 1
  
  # 单条件：限定FBA发货
  sorftime api ProductQuery '{"query": 1, "queryType": 15, "pattern": "FBA"}' --domain 1
  
  # 单条件：查询季节性产品（1,2,3月为旺季）
  sorftime api ProductQuery '{"query": 1, "queryType": 10, "pattern": "1,2,3"}' --domain 1
  
  # 多条件组合：类目+月销量+星级
  sorftime api ProductQuery '{"query": 2, "pattern": [{"queryType": 2, "content": "3743561"}, {"queryType": 9, "content": "100,1000"}, {"queryType": 12, "content": "4,"}], "page": 1}' --domain 1
  
  # 回看历史数据（2024年6月）
  sorftime api ProductQuery '{"query": 1, "queryType": 2, "pattern": "3743561", "queryMonth": "2024-06"}' --domain 1
  ```
- **注意**: 
  - AU、BR、IN暂不支持回看
  - US、GB、DE支持回看全细分类目产品（"不限"模式回看）
  - 其余站点支持Top100产品回看

---

### 二、产品历史数据

#### 3. 产品官方公布子体销量 (AsinSalesVolume)
- **接口说明**: 查询产品官方公布的子体销量历史数据，最早自2023-07开始
- **消耗请求数**: 1次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | asin | String | 是 | 需要查询的ASIN |
  | queryDate | String | 否 | 查询开始时间，格式yyyy-MM-dd，最早支持2023-09-01 |
  | queryEndDate | String | 否 | 查询截止时间，格式yyyy-MM-dd |
  | page | Integer | 否 | 分页查询，每页最多100条数据，默认1 |
- **使用示例**:
  ```bash
  # 查询近30日子体销量
  sorftime api AsinSalesVolume '{"asin": "B0CVM8TXHP"}' --domain 1
  
  # 查询指定时间段子体销量
  sorftime api AsinSalesVolume '{"asin": "B0CVM8TXHP", "queryDate": "2024-01-01", "queryEndDate": "2024-01-31"}' --domain 1
  ```
- **返回格式**: 二维数组 `[["2023-10-05", 100, 1], ...]`
  - 第1列：记录日期
  - 第2列：销量记录
  - 第3列：1=周销量，2=月销量

---

#### 4. 产品子体变化历史 (ProductVariationHistory)
- **接口说明**: 查询ASIN所有变体变化历史，最多支持近1个月数据
- **消耗请求数**: 1次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | asin | String | 是 | 需要查询的ASIN |
- **使用示例**:
  ```bash
  sorftime api ProductVariationHistory '{"asin": "B0CVM8TXHP"}' --domain 1
  ```
- **返回格式**: 二维数组 `[["2024-01-01", "B0PARENT", "B0CHILD1", "B0CHILD2"], ...]`

---

#### 5. 产品趋势数据 (ProductTrend)
- **接口说明**: 查询指定产品历史数据趋势
- **消耗请求数**: 1次
- **注意**: AE、AU、SA站点趋势数据密度较低
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | asin | String | 是 | 需要查询的ASIN |
  | dateRange | String | 否 | 查询时间范围，格式：起始时间,截止时间（yyyyMMdd），如"20240101,20250101" |
  | trendType | Integer | 否 | 趋势类型 |
- **使用示例**:
  ```bash
  # 查询默认趋势数据
  sorftime api ProductTrend '{"asin": "B0CVM8TXHP"}' --domain 1
  
  # 查询指定时间范围趋势
  sorftime api ProductTrend '{"asin": "B0CVM8TXHP", "dateRange": "20240101,20241231"}' --domain 1
  ```

---

### 三、产品实时监控（消耗积分）

#### 6. 产品实时数据查询 (ProductRealtimeRequest)
- **接口说明**: 如果产品设定时间内未更新过，则实时抓取一次产品信息
- **消耗**: 0 request，改为消耗积分（日本站消耗2积分，其他站点1积分）
- **注意**: 实时抓取预计耗时5分钟，抓取成功后通过ProductRequest查询
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | asin | String | 是 | 需要查询的ASIN |
  | update | Integer | 否 | 未更新则立即更新的时限（小时），默认24，有效范围1-120 |
- **返回码说明**:
  - 0: 产品已更新，可通过ProductRequest获取详情
  - 99: 正在实时抓取，预计5分钟，请稍后重试
  - 98: 采集失败
  - 97: ASIN不存在
  - 4: 积分余额不足
- **使用示例**:
  ```bash
  # 24小时内未更新则立即更新
  sorftime api ProductRealtimeRequest '{"asin": "B0CVM8TXHP"}' --domain 1
  
  # 48小时内未更新则立即更新
  sorftime api ProductRealtimeRequest '{"asin": "B0CVM8TXHP", "update": 48}' --domain 1
  ```

---

#### 7. 产品实时数据查询状态查询 (ProductRealtimeRequestStatusQuery)
- **接口说明**: 查询产品实时数据查询任务的执行状态
- **消耗请求数**: 0次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | queryDate | String | 是 | 查询日期，格式yyyy-MM-dd，返回该日期全部任务 |
- **使用示例**:
  ```bash
  sorftime api ProductRealtimeRequestStatusQuery '{"queryDate": "2024-01-15"}' --domain 1
  ```
- **返回格式**: `["B0ASIN1:1:2024-01-15 10:30", "B0ASIN2:0:--"]`
  - 状态：0=查询中，1=完成，3=采集失败，4=积分不够，5=ASIN不存在

---

### 四、产品评论

#### 8. 实时采集产品评论 (ProductReviewsCollection)
- **接口说明**: 实时采集产品评论（不会返回评论内容，需通过ProductReviewsQuery拉取）
- **消耗**: 0 request，改为消耗积分
- **注意**: 
  - 每成功采集10条评论=2积分
  - 每次启动至少扣2积分（即使未采得任何评论）
  - 相同产品采集成功后，2小时内不能重复采集
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | asin | String | 是 | 需要采集的ASIN |
  | mode | Integer | 否 | 采集方式：0=top reviews模式，1=most recent模式 |
  | star | String | 否 | 按星级筛选，支持多选（逗号分割）：1-5星，10=消极评论(1-3星)，11=积极评论(4-5星) |
  | onlyPurchase | Integer | 否 | 是否仅采集购买过产品的用户评论：0=不限，1=仅购买用户 |
  | page | Integer | 否 | 采集页数，可选值1-10 |
- **积分计算**: 每页1积分。例如star="1,2,3,4,5" page=10，则消耗5×10=50积分
- **使用示例**:
  ```bash
  # 采集top reviews，不限星级，1页
  sorftime api ProductReviewsCollection '{"asin": "B0CVM8TXHP", "mode": 0, "page": 1}' --domain 1
  
  # 采集最近评论，仅5星，仅购买用户，5页
  sorftime api ProductReviewsCollection '{"asin": "B0CVM8TXHP", "mode": 1, "star": "5", "onlyPurchase": 1, "page": 5}' --domain 1
  
  # 采集消极评论（1-3星）
  sorftime api ProductReviewsCollection '{"asin": "B0CVM8TXHP", "star": "10", "page": 3}' --domain 1
  
  # 采集积极评论（4-5星）
  sorftime api ProductReviewsCollection '{"asin": "B0CVM8TXHP", "star": "11", "page": 3}' --domain 1
  ```
- **返回**: taskId > 0 表示任务创建成功

---

#### 9. 评论实时查询任务状态 (ProductReviewsCollectionStatusQuery)
- **接口说明**: 查询实时采集产品评论的任务执行状态
- **消耗请求数**: 0次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | asin | String | 是 | 采集评论的ASIN |
  | update | Integer | 是 | 执行采集任务距今的时间范围（小时），可选值1-240 |
- **使用示例**:
  ```bash
  # 检查48小时内的采集任务状态
  sorftime api ProductReviewsCollectionStatusQuery '{"asin": "B0CVM8TXHP", "update": 48}' --domain 1
  ```
- **返回格式**:
  ```json
  [
    {"taskId": 12345, "status": 0},
    {"taskId": 12346, "status": 99}
  ]
  ```
  - 状态：0=采集完成，4=积分余额不足，11=没有采集任务，97=ASIN不存在，98=采集失败，99=采集中

---

#### 10. 产品评论查询 (ProductReviewsQuery)
- **接口说明**: 查询已收录的产品评论（如需最新评论，先通过ProductReviewsCollection采集）
- **消耗请求数**: 5次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | asin | String | 是 | 需要查询的ASIN |
  | querystartdt | String | 否 | 查询reviews起始时间，格式yyyy-MM-dd |
  | star | Integer | 否 | 筛选星级：1-5星，10=消极评论，11=积极评论，多选逗号分割 |
  | onlyPurchase | Integer | 否 | 是否仅采集购买用户评论：0=不限，1=仅购买用户 |
  | pageIndex | Integer | 否 | 查询第几页，默认1，每页100条数据 |
- **使用示例**:
  ```bash
  # 查询所有评论
  sorftime api ProductReviewsQuery '{"asin": "B0CVM8TXHP"}' --domain 1
  
  # 查询5星评论
  sorftime api ProductReviewsQuery '{"asin": "B0CVM8TXHP", "star": 5}' --domain 1
  
  # 查询消极评论（1-3星）
  sorftime api ProductReviewsQuery '{"asin": "B0CVM8TXHP", "star": 10}' --domain 1
  
  # 查询积极评论（4-5星）
  sorftime api ProductReviewsQuery '{"asin": "B0CVM8TXHP", "star": 11}' --domain 1
  
  # 查询指定日期后的评论
  sorftime api ProductReviewsQuery '{"asin": "B0CVM8TXHP", "querystartdt": "2024-01-01"}' --domain 1
  
  # 仅查询购买用户的评论
  sorftime api ProductReviewsQuery '{"asin": "B0CVM8TXHP", "onlyPurchase": 1}' --domain 1
  ```

---

### 五、图搜相似产品（消耗积分）

#### 11. 图搜相似产品 (SimilarProductRealtimeRequest)
- **接口说明**: 通过产品图片实时搜索亚马逊平台上相似产品
- **消耗**: 0 request，改为消耗积分（5积分，日本站6积分）
- **注意**: 
  - 建议搜索的产品在图片中比例大于80%，背景尽量干净
  - 预计耗时5分钟，预计返回20+产品
  - 仅支持US、GB、DE、FR、IN、JP、ES、IT站点
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | image | String | 是 | 查询的图片，Base64编码 |
- **使用示例**:
  ```bash
  sorftime api SimilarProductRealtimeRequest '{"image": "BASE64_ENCODED_IMAGE"}' --domain 1
  ```
- **返回**: taskId > 0 表示任务创建成功

---

#### 12. 图搜相似产品任务状态查询 (SimilarProductRealtimeRequestStatusQuery)
- **接口说明**: 查询图搜相似产品的任务执行状态
- **消耗请求数**: 0次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | Update | Integer | 是 | 检查在距当前时间1-240小时内的任务状态 |
- **使用示例**:
  ```bash
  sorftime api SimilarProductRealtimeRequestStatusQuery '{"Update": 48}' --domain 1
  ```

---

#### 13. 图搜相似产品结果查询 (SimilarProductRealtimeRequestCollection)
- **接口说明**: 查询图搜相似产品结果
- **消耗请求数**: 0次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | taskId | String | 是 | 任务Id |
- **使用示例**:
  ```bash
  sorftime api SimilarProductRealtimeRequestCollection '{"taskId": "12345"}' --domain 1
  ```
- **返回格式**:
  ```json
  [
    {
      "asin": "B0ASIN",
      "brand": "品牌名",
      "star": 4.5,
      "ratings": 1000,
      "price": 1599,
      "listPrice": 1999
    }
  ]
  ```

---

## 注意事项

1. **批量查询优化**: ProductRequest支持一次查询最多10个ASIN，可以节省请求次数
2. **趋势数据**: 默认返回近15天，如需更多数据需指定queryTrendStartDt和queryTrendEndDt
3. **评论采集**: 采集评论消耗积分，建议先评估需求再决定是否采集
4. **图搜功能**: 仅支持8个站点，且消耗积分较多
5. **实时监控**: ProductRealtimeRequest消耗积分，适合关键产品的实时监控

---

## 常见错误

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 0 | 成功 | - |
| 4 | 积分余额不足 | 充值积分或等待下月重置 |
| 97 | ASIN不存在 | 检查ASIN是否正确 |
| 98 | 采集失败 | 稍后重试，或联系Sorftime客服 |
| 99 | 正在实时抓取 | 预计耗时5分钟，请稍后重试 |
| 401 | 认证失败 | 检查Account-SK是否有效 |
| 403 | 权限不足 | 检查套餐权限或请求次数 |
| 429 | 请求频率超限 | 降低请求速度，等待1分钟后重试 |

---

## 最佳实践

### 1. 批量查询ASIN
```bash
# 一次性查询多个ASIN（最多10个），节省请求次数
sorftime api ProductRequest '{"asin": "B0ASIN1,B0ASIN2,B0ASIN3,B0ASIN4,B0ASIN5"}' --domain 1
```

### 2. 竞品分析流程
```bash
# 步骤1: 基于ASIN查询同类产品
sorftime api ProductQuery '{"query": 1, "queryType": 1, "pattern": "B0CVM8TXHP"}' --domain 1

# 步骤2: 查询竞品的详细信息
sorftime api ProductRequest '{"asin": "B0COMPETITOR1,B0COMPETITOR2"}' --domain 1

# 步骤3: 查询竞品的评论
sorftime api ProductReviewsQuery '{"asin": "B0COMPETITOR1"}' --domain 1

# 步骤4: 查询竞品的子体销量
sorftime api AsinSalesVolume '{"asin": "B0COMPETITOR1"}' --domain 1
```

### 3. 产品筛选
```bash
# 查找类目下月销量100-1000、4星以上、FBA发货的产品
sorftime api ProductQuery '{"query": 2, "pattern": [{"queryType": 2, "content": "3743561"}, {"queryType": 9, "content": "100,1000"}, {"queryType": 12, "content": "4,"}, {"queryType": 15, "content": "FBA"}]}' --domain 1
```

### 4. 品牌分析
```bash
# 查询Anker品牌的热销产品
sorftime api ProductQuery '{"query": 1, "queryType": 3, "pattern": "Anker"}' --domain 1
```

### 5. 季节性产品分析
```bash
# 查询1-3月为销售旺季的产品
sorftime api ProductQuery '{"query": 1, "queryType": 10, "pattern": "1,2,3"}' --domain 1
```
