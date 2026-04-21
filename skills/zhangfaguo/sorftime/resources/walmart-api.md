# Walmart API Skill

## 基本信息
- **名称**: walmart-api
- **描述**: Sorftime Walmart平台API调用工具，支持美国站的类目、产品、关键词数据查询
- **激活条件**: 当用户提到Walmart、沃尔玛电商、sorftime-cli Walmart相关操作时自动激活
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
- CLI会自动处理权限认证

---

## Domain参数说明

| domain值 | 站点代码 | 站点名称 | 备注 |
|---------|---------|---------|------|
| 21 | us | 美国站 | 唯一支持的站点 |

**注意**: Walmart API仅支持美国站（domain=21）

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

### 1. 销量说明
- **预估月销量** (listingSalesVolumeOfMonth): 基于产品当前的排名预估未来30天的销量，评估产品销量时建议使用这个值
- **月销量**: 过去30天销量
- **与Sorftime软件/插件的区别**: Sorftime软件/插件的月销量均为预估月销量，而API明确区分两者

### 2. 类目权限
- 如果客户未开通通用类目权限，查询数据时默认限于专属类目

### 3. 积分系统
- 监控相关功能涉及积分消耗
- 每月10号凌晨自动清空上期未用完部分并发放新积分

### 4. 货币单位
- 价格、销售额等数值单位为当地货币最小单位
- 例如美国站：单位为美分，1999表示$19.99

### 5. 请求频率
- 最高10次/秒，建议批量查询时控制速度

---

## 接口列表

### 一、类目市场类接口

#### 1. 类目树 (CategoryTree)
- **接口说明**: 返回Walmart全量类目树结构
- **消耗请求数**: 5次
- **注意**: 
  - 返回数据很大（约10MB+），建议设置较长超时时间
  - 可选gzip压缩参数
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | gzip | Integer | 否 | 0或1，默认为0。设置为1时使用gzip压缩并返回base64字符串 |
- **使用示例**:
  ```bash
  # Walmart美国站类目树（不压缩）
  sorftime api CategoryTree --domain 21
  
  # 启用gzip压缩（需要手动解码）
  sorftime api CategoryTree --domain 21 --params '{"gzip": 1}'
  ```
- **返回字段说明** (CategoryTreeObject):
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | id | Integer | 类目ID |
  | parentId | Integer | 父级类目ID，为0表示第一级 |
  | nodeid | String | 类目nodeid |
  | name | String | 类目名称 |
  | cnName | String | 类目中文名称 |
  | url | String | 类目URL地址 |

---

#### 2. 类目市场报告 (CategoryRequest)
- **接口说明**: 查询类目Best Seller Top 80产品数据
- **消耗请求数**: 5次
- **注意**: 数据范围为best seller top 80
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | nodePath | String | 是 | 需要查找的类目节点路径 |
- **使用示例**:
  ```bash
  sorftime api CategoryRequest '{"nodePath": "Electronics/Computers"}' --domain 21
  ```
- **返回数据**: ProductSummeryObject Array，产品列表

---

### 二、产品类接口

#### 3. 产品数据查询 (ProductRequest)
- **接口说明**: 查询单个产品的详细信息
- **消耗请求数**: 1次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | productId | String | 是 | 需要查询的产品Id |
- **使用示例**:
  ```bash
  sorftime api ProductRequest '{"productId": "12345678"}' --domain 21
  ```
- **返回字段说明** (ProductSummeryObject):
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | title | String | 产品名称 |
  | photo | String Array | 产品主图URL数组 |
  | listingSalesVolumeOfMonth | Integer | 链接预估月销量（不区分子体），评估产品销量时建议使用 |
  | listingSalesOfMonth | Integer | 链接预估月销售额（单位为美分，如10000表示$100.00） |
  | productId | String | 产品ID |
  | parentProductId | String | 父级产品ID |
  | price | Integer | 产品销售价（单位为美分，如1999表示$19.99） |
  | brand | String | 产品品牌 |
  | seller | String | 采集时的卖家 |
  | shipedby | String | 采集时的发货方式 |
  | wfsFee | Integer | FBA费用（单位为美分） |
  | attribute | String Array | 产品属性数组：["属性1","值1","属性2","值2",...] |
  | firstReviewsDate | String | 首个评论日期（yyyy-MM-dd） |
  | reviewsCount | Integer | 评论数量 |
  | ratings | Number | 评分星级（如4.8） |
  | nodePath | String Array | 产品所属类目节点数组 |
  | label | String Array | 产品标志数组（如pickup、savewith、bestsell等） |
  | popularPick | Integer | Popular Pick标志，存在时为1 |
  | clearance | Integer | Clearance标志，存在时为1 |
  | reducedPrice | Integer | Reduced Price标志，存在时为1 |
  | rollback | Integer | Rollback标志，存在时为1 |
  | flashDeal | Integer | Flash Deal标志，存在时为1 |
  | size | String Array | 外包装尺寸：["最长边","第二长边","最短边"]，单位cm |
  | weight | Integer | 产品重量，单位g |
  | variants | String Array | 子体信息JSON数组 |
  | numberOfStar | String Array | 各星级评论数量：["5","101","4","90",...] |
- **nodePath格式**:
  ```json
  [
    "类目节点名称", "类目节点", "排名时间", "排名",
    "类目节点名称", "类目节点", "排名时间", "排名"
  ]
  ```
- **variants格式**:
  ```json
  [
    {
      "VariantId": "3146561534",
      "Url": "https://...",
      "Property": ["Actual Color", "C"],
      "PriceUpdate": "2024-01-01",
      "DetailUpdate": "-"
    }
  ]
  ```
  - DetailUpdate: 当详情更新时间大于30天时，显示为"-"

---

#### 4. 产品历史趋势 (ProductTrendRequest)
- **接口说明**: 查询产品历史趋势数据（销量、价格、评论、排名等）
- **消耗请求数**: 2次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | productId | String | 是 | 需要查询的产品Id |
- **使用示例**:
  ```bash
  sorftime api ProductTrendRequest '{"productId": "12345678"}' --domain 21
  ```
- **返回字段说明** (ProductTrendObject):
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | productId | String | 产品ID |
  | listingSalesVolumeOfMonth | Integer | 链接预估月销量 |
  | listingSalesOfMonth | Integer | 链接预估月销售额（美分） |
  | listingSalesVolumeOfMonthTrend | String Array | 月销量历史趋势数组 |
  | listingSalesOfMonthTrend | String Array | 月销额历史趋势数组（美分） |
  | priceTrend | String Array | 价格趋势数组（美分） |
  | reviewsTrend | String Array | 评论数量趋势数组 |
  | starTrend | String Array | 星级趋势数组（450表示4.5星） |
  | rankTrend | two dimensional String Array | 各类目中的排名趋势 |
- **趋势数据格式**:
  - 数组格式：`["2025-01-01",100,"2025-01-02",200,...]`
  - 偶数下标为日期，奇数下标为对应数据值
- **rankTrend格式**:
  ```json
  [
    [
      "<类目节点名称>",
      "<类目节点>",
      "<日期yyyy-MM-dd>",
      "<排名>",
      "<日期yyyy-MM-dd>",
      "<排名>",
      ...
    ]
  ]
  ```

---

#### 5. 产品官方公布子体销量 (ProductSalesVolume)
- **接口说明**: 查询产品官方公布的产品销量历史数据，最早自2024-01开始
- **消耗请求数**: 1次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | productId | String | 是 | 需要查询的产品Id |
  | queryDate | String | 否 | 查询开始时间（yyyy-MM-dd），最早支持2023-09-01 |
  | queryEndDate | String | 否 | 查询截止时间（yyyy-MM-dd） |
  | pageIndex | Integer | 否 | 分页查询，默认1，每页最多100条数据 |
- **注意**: 
  - 默认（不传参数或参数无效时）返回近30日数据
  - 最早支持从2023年09月01日开始
- **使用示例**:
  ```bash
  # 查询近30日数据
  sorftime api ProductSalesVolume '{"productId": "12345678"}' --domain 21
  
  # 查询指定时间段
  sorftime api ProductSalesVolume '{"productId": "12345678", "queryDate": "2024-01-01", "queryEndDate": "2024-01-31"}' --domain 21
  ```
- **返回格式**: 二维数组
  ```json
  [
    ["2023-10-05", 100, 2],
    ...
  ]
  ```
  - 第1列：记录日期
  - 第2列：销量记录
  - 第3列：2=昨日销量

---

### 三、关键词类接口

#### 6. 关键词查询 (KeywordQuery)
- **接口说明**: 查询当前热搜关键词清单
- **消耗请求数**: 5次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | pattern | Object | 是 | 查询模式，见KeywordQueryPatternObject |
  | pageIndex | Integer | 否 | 查询第几页，默认1 |
  | pageSize | Integer | 否 | 每页条数，最小20，默认20，最大200 |
- **KeywordQueryPatternObject结构**:
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | keyword | String | 查询的关键词 |
  | rankCondition | String Array | 周排名筛选条件：[最小值,最大值] |
  | searchVolumeCondition | String Array | 近30日搜索量筛选条件：[最小值,最大值] |
- **使用示例**:
  ```bash
  # 查询热门关键词
  sorftime api KeywordQuery '{"pattern": {}, "pageIndex": 1, "pageSize": 50}' --domain 21
  
  # 筛选排名1-5000的关键词
  sorftime api KeywordQuery '{"pattern": {"rankCondition": ["1", "5000"]}, "pageIndex": 1, "pageSize": 50}' --domain 21
  
  # 筛选搜索量大于10000的关键词
  sorftime api KeywordQuery '{"pattern": {"searchVolumeCondition": ["10000"]}, "pageIndex": 1, "pageSize": 50}' --domain 21
  ```

---

#### 7. 关键词近15日搜索结果产品 (KeywordSearchResults)
- **接口说明**: 近15日关键词搜索结果产品，仅支持当前的热搜词
- **消耗请求数**: 5次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | keyword | String | 是 | 关键词 |
  | pageIndex | Integer | 否 | 查询第几页，默认1 |
  | pageSize | Integer | 否 | 每页条数，最小20，默认20，最大200 |
- **使用示例**:
  ```bash
  sorftime api KeywordSearchResults '{"keyword": "water bottle", "pageIndex": 1, "pageSize": 50}' --domain 21
  ```
- **返回数据**: ProductSummeryObject Array

---

#### 8. 关键词详情 (KeywordRequest)
- **接口说明**: 关键词详情查询
- **消耗请求数**: 1次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | keyword | String | 是 | 关键词 |
- **使用示例**:
  ```bash
  sorftime api KeywordRequest '{"keyword": "water bottle"}' --domain 21
  ```
- **返回字段说明** (KeywordSummeryObject):
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | keyword | String | 关键词 |
  | keywordCNName | String | 关键词中文名称 |
  | images | String Array | 某次搜索结果前10个产品图片 |
  | update | String | 最新更新时间 |
  | rank | Integer | 周搜索排名 |
  | searchVolume | Integer | 近30天搜索量 |
  | productCount | Integer | 竞品数量 |
  | searchFirstPageAvgPrice | Integer | 首页自然位产品平均价格（美分） |
  | searchFirstPageAvgReviews | Integer | 首页自然位产品平均评论数 |
  | searchFirstPageAvgStar | Number | 首页自然位产品平均星级（如4.5） |

---

#### 9. 产品反查关键词 (ProductRequestKeywordv2)
- **接口说明**: 查询该产品近30天站内在哪些关键词搜索结果的前3页中曝光
- **消耗请求数**: 1次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | productId | String | 是 | 需要查询的productId |
  | pageIndex | Integer | 否 | 查询第几页，默认1 |
  | pageSize | Integer | 否 | 每页条数，最小20，默认20，最大200 |
- **使用示例**:
  ```bash
  sorftime api ProductRequestKeywordv2 '{"productId": "12345678", "pageIndex": 1, "pageSize": 50}' --domain 21
  ```
- **返回字段说明** (ProductKeywordItemObject):
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | ShowShare | Number | 在此产品的反查关键词中，此词贡献的流量占比 |
  | recentlyPosition | String | 最近一次曝光位，格式："1,2/18"表示第1页第2位，共18个位置 |
  | organicPosition | String | 最近一次自然曝光位 |
  | adPosition | String | 最近一次广告曝光位 |
  | keyword | Object | 关键词详情（KeywordSummeryObject） |

---

#### 10. 查延伸关键词 (KeywordExtends)
- **接口说明**: 基于关键词查延伸词
- **消耗请求数**: 5次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | keyword | String | 是 | 查询的关键词 |
  | pageIndex | Integer | 否 | 查询第几页，默认1 |
  | pageSize | Integer | 否 | 每页条数，最小20，默认20，最大200 |
- **使用示例**:
  ```bash
  sorftime api KeywordExtends '{"keyword": "water bottle", "pageIndex": 1, "pageSize": 50}' --domain 21
  ```

---

### 四、关键词词库管理

#### 11. 添加关键词到词库 (FavoriteKeyword)
- **接口说明**: 添加关键词到我的关键词词库（不限为热搜关键词）
- **消耗请求数**: 1次
- **注意**: 
  - API的词库和Sorftime专业版的收藏夹不互通
  - 相同收藏夹下关键词不能重复（不同收藏夹下可以）
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | keyword | String | 是 | 需要收藏的词 |
  | dict | String | 否 | 指定收藏夹，不存在则新建。不指定则添加到`未分类` |
- **使用示例**:
  ```bash
  # 添加到未分类收藏夹
  sorftime api FavoriteKeyword '{"keyword": "water bottle"}' --domain 21
  
  # 添加到指定收藏夹
  sorftime api FavoriteKeyword '{"keyword": "water bottle", "dict": "我的词库"}' --domain 21
  ```
- **返回**: 
  - 0: 收藏成功
  - 1: 此关键词已存在无需重复收藏
  - 9: 收藏失败

---

#### 12. 移动/删除词库关键词 (ChangeFavoriteKeyword)
- **接口说明**: 移动关键词到指定收藏夹或删除关键词
- **消耗请求数**: 0次
- **注意**: 单个收藏夹最多只能收藏2000个关键词
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | keyword | String | 是 | 已收藏的词 |
  | dict | String | 否 | 指定收藏夹，不指定则操作`未分类`收藏夹 |
  | command | String | 是 | del=删除；move=<文件夹名称>=移动 |
- **使用示例**:
  ```bash
  # 删除关键词
  sorftime api ChangeFavoriteKeyword '{"keyword": "water bottle", "command": "del"}' --domain 21
  
  # 移动到指定文件夹
  sorftime api ChangeFavoriteKeyword '{"keyword": "water bottle", "command": "move=热门词"}' --domain 21
  ```
- **返回**: 
  - 0: 操作成功
  - 9: 词未添加收藏

---

#### 13. 查询词库关键词 (GetFavoriteKeyword)
- **接口说明**: 查询词库
- **消耗请求数**: 1次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | command | String | 是 | all=全部词；dict=<名称>=指定文件夹；dict=文件夹列表 |
  | page | Integer | 否 | 分页查询，默认1，每页最多100条 |
- **使用示例**:
  ```bash
  # 查询全部词
  sorftime api GetFavoriteKeyword '{"command": "all", "page": 1}' --domain 21
  
  # 查询指定文件夹
  sorftime api GetFavoriteKeyword '{"command": "dict=我的词库", "page": 1}' --domain 21
  
  # 查询文件夹列表
  sorftime api GetFavoriteKeyword '{"command": "dict"}' --domain 21
  ```
- **返回格式**: JSON数组 `["kw1","kw2",...]`

---

## 注意事项

1. **数据准确性**: 
   - 预估月销量基于当前排名预估未来30天销量
   - 评估产品销量时建议使用listingSalesVolumeOfMonth字段

2. **货币单位**: 
   - 所有价格、销售额、费用等单位为当地货币最小单位（美分）
   - 例如：1999表示$19.99，10000表示$100.00

3. **类目权限**: 如果未开通通用类目权限，查询时默认限于专属类目

4. **产品标志**: 
   - popularPick、clearance、reducedPrice、rollback、flashDeal
   - 存在标志时值为1，不存在时为0或null

5. **子体信息**: variants数组中的DetailUpdate，当详情更新时间大于30天时显示为"-"

6. **请求频率**: 最高10次/秒

7. **账户配置**: 所有接口默认使用当前活跃profile的Account-SK

---

## 常见错误

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 0 | 成功 | - |
| 401 | 认证失败 | 检查Account-SK是否有效 |
| 403 | 权限不足 | 检查套餐权限或请求次数，确认类目权限 |
| 404 | 接口不存在 | 检查接口名称拼写 |
| 429 | 请求频率超限 | 降低请求速度，等待1分钟后重试 |
| 500 | 服务器内部错误 | 稍后重试，或联系Sorftime客服 |

---

## 最佳实践

### 1. 完整的类目分析流程
```bash
# 步骤1: 获取类目树
sorftime api CategoryTree --domain 21

# 步骤2: 查询类目Best Seller Top 80
sorftime api CategoryRequest '{"nodePath": "Electronics/Computers"}' --domain 21

# 步骤3: 查询具体产品详情
sorftime api ProductRequest '{"productId": "12345678"}' --domain 21

# 步骤4: 查询产品历史趋势
sorftime api ProductTrendRequest '{"productId": "12345678"}' --domain 21
```

### 2. 关键词研究流程
```bash
# 步骤1: 产品反查关键词
sorftime api ProductRequestKeywordv2 '{"productId": "12345678"}' --domain 21

# 步骤2: 查询关键词详情
sorftime api KeywordRequest '{"keyword": "water bottle"}' --domain 21

# 步骤3: 拓展相关关键词
sorftime api KeywordExtends '{"keyword": "water bottle", "pageSize": 100}' --domain 21

# 步骤4: 查询关键词搜索结果
sorftime api KeywordSearchResults '{"keyword": "water bottle", "pageSize": 50}' --domain 21

# 步骤5: 收藏高价值关键词
sorftime api FavoriteKeyword '{"keyword": "water bottle", "dict": "核心词"}' --domain 21
```

### 3. 产品销量分析
```bash
# 查询官方公布的子体销量历史
sorftime api ProductSalesVolume '{"productId": "12345678", "queryDate": "2024-01-01", "queryEndDate": "2024-03-31"}' --domain 21
```

### 4. 关键词筛选
```bash
# 筛选周排名1-5000且搜索量大于10000的关键词
sorftime api KeywordQuery '{"pattern": {"rankCondition": ["1", "5000"], "searchVolumeCondition": ["10000"]}, "pageSize": 100}' --domain 21
```

### 5. 产品对比分析
```bash
# 批量查询多个产品
sorftime api ProductRequest '{"productId": "prod1"}' --domain 21
sorftime api ProductRequest '{"productId": "prod2"}' --domain 21
sorftime api ProductRequest '{"productId": "prod3"}' --domain 21

# 对比它们的价格、销量、评论等指标
```
