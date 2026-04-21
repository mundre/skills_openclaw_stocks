# Amazon Keyword API Skill

## 基本信息
- **名称**: amazon-keyword
- **描述**: Sorftime 亚马逊关键词数据查询工具，支持关键词查询、拓展、反查、排名追踪等功能
- **激活条件**: 当用户提到亚马逊关键词研究、ABA关键词、关键词排名、ASIN反查关键词时自动激活
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

## Domain参数说明

| domain值 | 站点代码 | 站点名称 | 备注 |
|---------|---------|---------|------|
| 1 | us | 美国站 | 支持所有关键词功能 |
| 2 | gb | 英国站 | 支持所有关键词功能 |
| 3 | de | 德国站 | 支持所有关键词功能 |
| 4 | fr | 法国站 | 支持所有关键词功能 |
| 6 | ca | 加拿大站 | 不支持KeywordQuery |
| 7 | jp | 日本站 | 支持所有关键词功能 |
| 8 | es | 西班牙站 | 支持所有关键词功能 |
| 9 | it | 意大利站 | 支持所有关键词功能 |
| 10 | mx | 墨西哥站 | 支持所有关键词功能 |
| 11 | ae | 阿联酋站 | 支持所有关键词功能 |
| 12 | au | 澳大利亚站 | 支持所有关键词功能 |
| 13 | br | 巴西站 | 支持所有关键词功能 |
| 14 | sa | 沙特站 | 支持所有关键词功能 |

**注意**: 5 (in/印度站) 不在关键词接口支持列表中

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

---

## 重要说明

1. **ABA关键词**: 大部分关键词接口仅支持Amazon Brand Analytics (ABA) 关键词
2. **历史数据**: 美国站支持最长近两年数据，其他站点仅近30天数据
3. **FR/IT限制**: FR、IT两站的关键词趋势数据仅支持2025年1月起
4. **词库限制**: 单个收藏夹最多只能收藏2000个关键词
5. **API词库**: API的词库（收藏夹）和Sorftime专业版的收藏夹不互通

---

## 接口列表

### 一、关键词基础查询

#### 1. 关键词查询 (KeywordQuery)
- **接口说明**: 查询当前ABA热搜关键词清单
- **消耗请求数**: 5次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | pattern | Object | 是 | 查询模式，见KeywordQueryPatternObject |
  | pageIndex | Integer | 否 | 查询第几页，默认1 |
  | pageSize | Integer | 否 | 每页条数，最小20，默认20，最大200 |
- **使用示例**:
  ```bash
  # 查询热门关键词（第1页，50条）
  sorftime api KeywordQuery '{"pattern": {}, "pageIndex": 1, "pageSize": 50}' --domain 1
  
  # 查询第2页
  sorftime api KeywordQuery '{"pattern": {}, "pageIndex": 2, "pageSize": 50}' --domain 1
  ```

---

#### 2. 关键词详情 (KeywordRequest)
- **接口说明**: 关键词详情查询
- **消耗请求数**: 1次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | keyword | String | 是 | 关键词 |
- **使用示例**:
  ```bash
  sorftime api KeywordRequest '{"keyword": "water bottle"}' --domain 1
  
  sorftime api KeywordRequest '{"keyword": "coffee mug"}' --domain 1
  ```

---

#### 3. 关键词近15日搜索结果产品 (KeywordSearchResults)
- **接口说明**: 近15日关键词搜索结果产品，仅支持ABA热搜词
- **消耗请求数**: 5次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | keyword | String | 是 | 关键词（仅支持ABA关键词） |
  | pageIndex | Integer | 否 | 查询第几页，默认1 |
  | pageSize | Integer | 否 | 每页条数，最小20，默认20，最大200 |
- **使用示例**:
  ```bash
  sorftime api KeywordSearchResults '{"keyword": "water bottle", "pageIndex": 1, "pageSize": 50}' --domain 1
  ```

---

#### 4. 关键词搜索结果产品趋势 (KeywordSearchResultTrend)
- **接口说明**: 关键词搜索结果前3页产品历史统计数据报告
- **消耗请求数**: 10次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | keyword | String | 是 | ABA关键词 |
  | queryStart | String | 否 | 趋势数据查询起始月份，格式yyyy-MM，默认2024-01 |
  | queryEnd | String | 否 | 趋势数据查询截止月份，格式yyyy-MM |
- **注意**: FR、IT两站支持2025年1月起数据
- **使用示例**:
  ```bash
  # 查询默认时间范围
  sorftime api KeywordSearchResultTrend '{"keyword": "water bottle"}' --domain 1
  
  # 查询指定时间范围
  sorftime api KeywordSearchResultTrend '{"keyword": "water bottle", "queryStart": "2024-01", "queryEnd": "2024-12"}' --domain 1
  ```

---

### 二、关键词拓展与反查

#### 5. 查延伸关键词 (KeywordExtends)
- **接口说明**: 基于关键词查延伸词
- **消耗请求数**: 5次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | keyword | String | 是 | 查询的ABA关键词 |
  | pageIndex | Integer | 否 | 查询第几页，默认1 |
  | pageSize | Integer | 否 | 每页条数，最小20，默认20，最大200 |
- **使用示例**:
  ```bash
  # 查询"water bottle"的延伸词
  sorftime api KeywordExtends '{"keyword": "water bottle", "pageIndex": 1, "pageSize": 50}' --domain 1
  
  # 查询第2页
  sorftime api KeywordExtends '{"keyword": "water bottle", "pageIndex": 2, "pageSize": 50}' --domain 1
  ```

---

#### 6. 类目反查关键词 (CategoryRequestKeyword)
- **接口说明**: 按类目查询类目相关ABA关键词
- **消耗请求数**: 1次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | nodeid | String | 是 | 需要查询的类目nodeid（仅支持底层类目） |
  | pageIndex | Integer | 否 | 查询第几页，默认1 |
  | pageSize | Integer | 否 | 每页条数，最小20，默认20，最大200 |
- **使用示例**:
  ```bash
  sorftime api CategoryRequestKeyword '{"nodeid": "12345", "pageIndex": 1, "pageSize": 50}' --domain 1
  ```

---

#### 7. ASIN反查关键词 (ASINRequestKeywordv2)
- **接口说明**: 查询该ASIN近30天站内在哪些关键词搜索结果的前3页中曝光
- **消耗请求数**: 1次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | asin | String | 是 | 需要查询的ASIN |
  | pageIndex | Integer | 否 | 查询第几页，默认1 |
  | pageSize | Integer | 否 | 每页条数，最小20，默认20，最大200 |
- **使用示例**:
  ```bash
  sorftime api ASINRequestKeywordv2 '{"asin": "B0CVM8TXHP", "pageIndex": 1, "pageSize": 50}' --domain 1
  ```

---

### 三、关键词排名追踪

#### 8. 关键词搜索结果产品排名 (KeywordProductRanking)
- **接口说明**: 关键词历史月份搜索结果产品排名，仅支持ABA关键词
- **消耗请求数**: 5次
- **注意**: US最长可查询近两年数据，其他站点仅近30天数据
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | keyword | String | 是 | ABA关键词 |
  | month | String | 条件性 | 查询月份，格式yyyy-MM，仅美国站有效 |
  | page | Integer | 否 | 查询第几页，默认1，每页最多200条 |
- **使用示例**:
  ```bash
  # 美国站查询指定月份
  sorftime api KeywordProductRanking '{"keyword": "water bottle", "month": "2024-12"}' --domain 1
  
  # 其他站点（month参数无效，返回近30天数据）
  sorftime api KeywordProductRanking '{"keyword": "water bottle"}' --domain 2
  ```
- **返回字段说明**:
  - positionType: 0=自然曝光，1=广告曝光
  - positionName: 0=自然位，1=SP广告，2=品牌广告，3=视频广告
  - campaignID: 广告活动ID（2025-03月起有效）
  - adID: 广告组ID
  - position: 所处页面位置，如"1/68"表示在第1位，当页共68个产品

---

#### 9. ASIN在关键词下排名趋势 (ASINKeywordRanking)
- **接口说明**: ASIN在指定关键词下的排名历史记录，最长可查询近两年数据
- **消耗请求数**: 2次
- **注意**: 目前仅支持美国站ABA关键词
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | keyword | String | 是 | ABA关键词 |
  | ASIN | String | 是 | 需要查询的ASIN |
  | queryStart | String | 否 | 查询起始时间，最长支持两年，为空时返回近1个月 |
  | queryEnd | String | 否 | 查询截止时间 |
  | page | Integer | 否 | 分页查询，默认1，每页最多200条 |
- **使用示例**:
  ```bash
  # 查询近1个月数据
  sorftime api ASINKeywordRanking '{"keyword": "water bottle", "ASIN": "B0CVM8TXHP"}' --domain 1
  
  # 查询指定时间范围
  sorftime api ASINKeywordRanking '{"keyword": "water bottle", "ASIN": "B0CVM8TXHP", "queryStart": "2024-01-01", "queryEnd": "2024-12-31"}' --domain 1
  ```

---

### 四、关键词词库管理

#### 10. 添加关键词到词库 (FavoriteKeyword)
- **接口说明**: 添加关键词到我的关键词词库（不限为ABA词）
- **消耗请求数**: 1次
- **注意**: 相同收藏夹下关键词不能重复（不同收藏夹下可以）
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | keyword | String | 是 | 需要收藏的词（不限为ABA词） |
  | dict | String | 否 | 如果指定，将添加词到指定收藏夹。如果收藏夹不存在则新建。不指定则添加到`未分类`收藏夹 |
- **使用示例**:
  ```bash
  # 添加到未分类收藏夹
  sorftime api FavoriteKeyword '{"keyword": "water bottle"}' --domain 1
  
  # 添加到指定收藏夹
  sorftime api FavoriteKeyword '{"keyword": "water bottle", "dict": "我的词库"}' --domain 1
  
  # 添加到新创建的收藏夹
  sorftime api FavoriteKeyword '{"keyword": "coffee mug", "dict": "厨房用品"}' --domain 1
  ```
- **返回**: 
  - 0: 收藏成功
  - 1: 此关键词已存在无需重复收藏
  - 9: 收藏失败

---

#### 11. 移动/删除词库关键词 (ChangeFavoriteKeyword)
- **接口说明**: 移动关键词到指定收藏夹或删除关键词
- **消耗请求数**: 0次
- **注意**: 单个收藏夹最多只能收藏2000个关键词
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | keyword | String | 是 | 已收藏的词 |
  | dict | String | 否 | 如果指定，将移动/删除指定收藏夹下的词。不指定则操作`未分类`收藏夹下的词 |
  | command | String | 是 | del=删除词；move=<文件夹名称>=移动到指定文件夹 |
- **使用示例**:
  ```bash
  # 删除关键词（从所有文件夹中删除）
  sorftime api ChangeFavoriteKeyword '{"keyword": "water bottle", "command": "del"}' --domain 1
  
  # 删除指定文件夹下的关键词
  sorftime api ChangeFavoriteKeyword '{"keyword": "water bottle", "dict": "我的词库", "command": "del"}' --domain 1
  
  # 移动到指定文件夹（如果文件夹不存在会新建）
  sorftime api ChangeFavoriteKeyword '{"keyword": "water bottle", "command": "move=热门词"}' --domain 1
  
  # 从未分类移动到指定文件夹
  sorftime api ChangeFavoriteKeyword '{"keyword": "water bottle", "command": "move=我的词库"}' --domain 1
  ```
- **返回**: 
  - 0: 操作成功
  - 9: 词未添加收藏

---

#### 12. 查询词库关键词 (GetFavoriteKeyword)
- **接口说明**: 查询词库
- **消耗请求数**: 1次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | command | String | 是 | all=查询全部词；dict=<文件夹名称>=查询指定文件夹；dict=查询文件夹列表 |
  | page | Integer | 否 | 分页查询，默认从1开始，每页最多返回100条数据 |
- **使用示例**:
  ```bash
  # 查询全部词
  sorftime api GetFavoriteKeyword '{"command": "all", "page": 1}' --domain 1
  
  # 查询指定文件夹
  sorftime api GetFavoriteKeyword '{"command": "dict=我的词库", "page": 1}' --domain 1
  
  # 查询文件夹列表（只返回列表不返回词）
  sorftime api GetFavoriteKeyword '{"command": "dict"}' --domain 1
  ```
- **返回格式**: JSON数组 `["kw1","kw2",...]` 或文件夹名列表

---

## 注意事项

1. **ABA关键词**: 大部分接口仅支持Amazon Brand Analytics关键词
2. **历史数据限制**: 
   - 美国站：最长近两年
   - 其他站点：仅近30天
   - FR、IT：关键词趋势从2025年1月开始
3. **词库管理**: API词库与Sorftime专业版不互通
4. **分页查询**: 每页最多200条数据，建议合理设置pageSize

---

## 常见错误

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 0 | 成功 | - |
| 401 | 认证失败 | 检查Account-SK是否有效 |
| 403 | 权限不足 | 检查套餐权限或请求次数 |
| 429 | 请求频率超限 | 降低请求速度，等待1分钟后重试 |
| 500 | 服务器内部错误 | 稍后重试，或联系Sorftime客服 |

---

## 最佳实践

### 1. 完整的关键词研究流程
```bash
# 步骤1: ASIN反查关键词，找出竞品在哪些词下曝光
sorftime api ASINRequestKeywordv2 '{"asin": "B0COMPETITOR"}' --domain 1

# 步骤2: 查询关键词详情，了解搜索量等信息
sorftime api KeywordRequest '{"keyword": "water bottle"}' --domain 1

# 步骤3: 拓展相关关键词
sorftime api KeywordExtends '{"keyword": "water bottle", "pageSize": 100}' --domain 1

# 步骤4: 查询关键词搜索结果产品
sorftime api KeywordSearchResults '{"keyword": "water bottle", "pageSize": 50}' --domain 1

# 步骤5: 将有价值的关键词加入收藏夹
sorftime api FavoriteKeyword '{"keyword": "water bottle", "dict": "核心词"}' --domain 1
```

### 2. 类目关键词挖掘
```bash
# 通过类目反查关键词
sorftime api CategoryRequestKeyword '{"nodeid": "12345", "pageSize": 100}' --domain 1
```

### 3. 关键词排名监控
```bash
# 查询ASIN在关键词下的历史排名
sorftime api ASINKeywordRanking '{"keyword": "water bottle", "ASIN": "B0CVM8TXHP", "queryStart": "2024-01-01", "queryEnd": "2024-12-31"}' --domain 1
```

### 4. 关键词趋势分析
```bash
# 查询关键词搜索结果的产品趋势
sorftime api KeywordSearchResultTrend '{"keyword": "water bottle", "queryStart": "2024-01", "queryEnd": "2024-12"}' --domain 1
```

### 5. 词库管理
```bash
# 批量添加关键词到不同收藏夹
sorftime api FavoriteKeyword '{"keyword": "water bottle", "dict": "核心词"}' --domain 1
sorftime api FavoriteKeyword '{"keyword": "insulated water bottle", "dict": "长尾词"}' --domain 1
sorftime api FavoriteKeyword '{"keyword": "coffee mug", "dict": "相关产品"}' --domain 1

# 查询某个收藏夹的所有关键词
sorftime api GetFavoriteKeyword '{"command": "dict=核心词", "page": 1}' --domain 1

# 移动关键词到另一个收藏夹
sorftime api ChangeFavoriteKeyword '{"keyword": "water bottle", "command": "move=高优先级"}' --domain 1
```
