# Amazon Monitoring API Skill

## 基本信息
- **名称**: amazon-monitoring
- **描述**: Sorftime 亚马逊数据监控工具，支持关键词排名监控、榜单监控、跟卖&库存监控等功能
- **激活条件**: 当用户提到亚马逊监控、关键词排名追踪、榜单监控、跟卖监控、库存监控时自动激活
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

| domain值 | 站点代码 | 站点名称 | 关键词监控 | 榜单监控 | 跟卖监控 |
|---------|---------|---------|-----------|---------|---------|
| 1 | us | 美国站 | ✓ | ✓ | ✓ |
| 2 | gb | 英国站 | ✓ | ✓ | ✓ |
| 3 | de | 德国站 | ✓ | ✓ | ✓ |
| 4 | fr | 法国站 | ✓ | ✓ | ✓ |
| 6 | ca | 加拿大站 | ✓ | ✓ | ✓ |
| 7 | jp | 日本站 | ✓ | ✓ | ✓ |
| 8 | es | 西班牙站 | ✓ | ✗ | ✓ |
| 9 | it | 意大利站 | ✓ | ✗ | ✓ |
| 10 | mx | 墨西哥站 | ✗ | ✗ | ✓ |
| 11 | ae | 阿联酋站 | ✗ | ✗ | ✓ |
| 12 | au | 澳大利亚站 | ✗ | ✓ | ✓ |
| 13 | br | 巴西站 | ✗ | ✗ | ✗ |
| 14 | sa | 沙特站 | ✗ | ✗ | ✗ |

---

## 重要说明

### 积分消耗规则
1. **关键词监控**: 
   - 监控一个关键词，每周7天，每天24小时，每小时监控1次，每次监控前3页
   - 每周消耗积分 = 1×7×24×1×3 = 504
   - 日本站每页面消耗2积分，相同频率消耗1008积分
   - 监控任务仅依据关键词扣除积分，与关键词下关注多少ASIN无关

2. **榜单监控**:
   - 监控top100每天消耗10积分
   - 监控top200每天消耗20积分
   - 监控top300每天消耗30积分
   - 监控top400每天消耗40积分

3. **跟卖&库存监控**:
   - 每个ASIN每次监控消耗2积分（日本站4积分）
   - 启用库存检查时，额外消耗1积分（日本站2积分）

4. **积分重置**: 每月10号凌晨自动清空上期未用完积分并发放新积分

### 数据保存期限
- 所有监控结果最多保存30日

---

## 接口列表

### 一、关键词监控

#### 1. 关键词监控注册 (KeywordBatchSubscription)
- **接口说明**: 定时监控ASIN在关键词下的搜索排名，支持使用手机或PC监控
- **消耗**: 0 request，改为消耗积分
- **注意**: 不受关注类目限制，可监控任意关键词
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | keyword | String Array | 是 | 监控关键词列表，如["kw1","kw2"] |
  | mode | Integer | 是 | 监控模式：0=电脑浏览器，1=手机浏览器 |
  | area | String | 条件性 | 监控地区邮编（见下方说明） |
  | page | Integer | 是 | 监控前N页：1,3,5,7（手机模式始终为1，返回约120+产品） |
  | period | String | 是 | 监控频率表达式：<每周哪几日>\|<每天哪些时段>\|<监控频率> |
- **area地区说明**:
  - **PC模式 (mode=0)**:
    - US: 10041(纽约), 60601(芝加哥), 94102(旧金山)
    - GB: N1P 3AA(伦敦)
    - DE: 10115(柏林)
    - FR: 75001(巴黎)
    - CA: V5K 0A1(温哥华)
    - JP: 120-0015(东京)
    - ES: 28001(马德里)
    - IT: 66030(罗马)
  - **手机模式 (mode=1)**:
    - US: 98101(西雅图)
    - GB: B10 0AB(伯明翰)
    - DE: 20095(汉堡)
    - FR: 13001(马赛)
    - CA: V5K 0A1(维多利亚)
    - JP: 550-0004(大阪)
    - ES: 08001(巴塞罗那)
    - IT: 16100(热那亚)
- **period频率表达式**: `<每周哪几日>|<每天哪些时段>|<监控频率>`
  - `<每周哪几日>`: 1-7（逗号分割，1=周一，7=周日）
  - `<每天哪些时段>`: 1-6（每个时段4小时，北京时区）
    - 1: 1-4点, 2: 5-8点, 3: 9-12点, 4: 13-16点, 5: 17-20点, 6: 21-0点
  - `<监控频率>`:
    - 1: 时段内任意时刻一次
    - 11-14: 时段内第1-4个时间刻度执行（可能因任务量过多而失败）
    - 2: 时段内每小时1次
    - 3: 时段内每2小时1次（随机双数或单数）
    - 31: 时段内单数小时执行，共2次（可能因任务量过多而失败）
    - 32: 时段内双数小时执行，共2次（可能因任务量过多而失败）
- **使用示例**:
  ```bash
  # 周一至周五，每天5-8点和9-12点，每个时段执行一次，监控前3页，PC模式（纽约）
  sorftime api KeywordBatchSubscription '{"keyword": ["water bottle", "coffee mug"], "mode": 0, "area": "10041", "page": 3, "period": "1,2,3,4,5|2,3|1"}' --domain 1
  
  # 每天全天候，每小时监控1次，手机模式（西雅图）
  sorftime api KeywordBatchSubscription '{"keyword": ["water bottle"], "mode": 1, "page": 1, "period": "1,2,3,4,5,6,7|1,2,3,4,5,6|2"}' --domain 1
  
  # 每天0-4点，每2小时监控一次，PC模式（伦敦），监控首页
  sorftime api KeywordBatchSubscription '{"keyword": ["water bottle"], "mode": 0, "area": "N1P 3AA", "page": 1, "period": "1,2,3,4,5,6,7|1|3"}' --domain 2
  ```
- **返回**: `["keyword:taskId", ...]`，taskId=-999表示注册失败（时段内任务过多）

---

#### 2. 关键词任务查询 (KeywordTasks)
- **接口说明**: 查看全部有效的（非删除的）关键词监控任务
- **消耗请求数**: 0次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | pageIndex | Integer | 否 | 查询第几页，默认1 |
  | pageSize | Integer | 否 | 每页条数，最小20，默认20，最大200 |
  | taskid | String | 否 | 如需指定taskid查询，多个taskid用逗号分割 |
  | keyword | String | 否 | 模糊匹配keyword |
- **使用示例**:
  ```bash
  # 查询所有任务
  sorftime api KeywordTasks '{"pageIndex": 1, "pageSize": 20}' --domain 1
  
  # 查询指定taskid
  sorftime api KeywordTasks '{"taskid": "12345,12346"}' --domain 1
  
  # 模糊匹配keyword
  sorftime api KeywordTasks '{"keyword": "water"}' --domain 1
  ```

---

#### 3. 修改关键词监控任务 (KeywordBatchTaskUpdate)
- **接口说明**: 修改关键词任务（暂停、启动、删除、修改设置）
- **消耗请求数**: 0次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | taskId | Integer | 是 | 关键词监控任务Id |
  | update | Integer | 是 | 0=修改设置，1=暂停，2=启动，9=删除 |
  | mode | Integer | 条件性 | update=0时有效：0=PC，1=手机 |
  | area | String | 条件性 | update=0时有效，地区邮编 |
  | page | Integer | 条件性 | update=0时有效：1,3,5,7 |
  | period | String | 条件性 | update=0时有效，频率表达式 |
- **使用示例**:
  ```bash
  # 暂停任务
  sorftime api KeywordBatchTaskUpdate '{"taskId": 12345, "update": 1}' --domain 1
  
  # 启动任务
  sorftime api KeywordBatchTaskUpdate '{"taskId": 12345, "update": 2}' --domain 1
  
  # 删除任务
  sorftime api KeywordBatchTaskUpdate '{"taskId": 12345, "update": 9}' --domain 1
  
  # 修改任务设置
  sorftime api KeywordBatchTaskUpdate '{"taskId": 12345, "update": 0, "mode": 0, "area": "10041", "page": 3, "period": "1,2,3,4,5|2,3|1"}' --domain 1
  ```
- **返回**: taskId > 0 表示成功，-999表示修改失败（时段内任务过多）

---

#### 4. 查询关键词监控任务执行批次 (KeywordBatchScheduleList)
- **接口说明**: 查询关键词监控全部执行任务批次
- **消耗请求数**: 0次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | TaskId | Integer | 是 | 关键词监控任务Id |
  | queryDate | String | 否 | 格式yyyy-MM-dd，默认查询全部，指定则查询该日期到最近的数据 |
- **使用示例**:
  ```bash
  # 查询全部批次
  sorftime api KeywordBatchScheduleList '{"TaskId": 12345}' --domain 1
  
  # 查询指定日期后的批次
  sorftime api KeywordBatchScheduleList '{"TaskId": 12345, "queryDate": "2024-01-15"}' --domain 1
  ```
- **返回格式**: 
  ```json
  ["202401151030:batch123:1:202401151035", "202401150930:batch122:0:--"]
  ```
  - 格式：`<执行时间yyyyMMddHHmm>:<批次Id>:<状态0=执行中,1=完成>:<完成时间>`

---

#### 5. 提取关键词监控产品列表详细数据 (KeywordBatchScheduleDetail)
- **接口说明**: 提取某次关键词监控搜索结果全部ASIN列表数据
- **消耗请求数**: 0次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | ScheduelId | String | 是 | 批次任务Id，支持多任务Id查询（逗号分割），最多20个 |
- **使用示例**:
  ```bash
  # 查询单个批次
  sorftime api KeywordBatchScheduleDetail '{"ScheduelId": "batch123"}' --domain 1
  
  # 查询多个批次（最多20个）
  sorftime api KeywordBatchScheduleDetail '{"ScheduelId": "batch123,batch124,batch125"}' --domain 1
  ```
- **返回格式**: 二维数组
  ```json
  [
    "B0ASIN,<主图链接>,<产品标题>,<曝光类型0/1>,<标志AC/BS/Deal/Lowest>,<曝光排名>,<曝光位置>,<coupon>,<星级>,<评价数量>,<销售价>,<跟卖数量>,<sellerName>,<sellerId>,<shipsFrom>,<配送费>,<品牌>,<变体数>,<prime标志>,<scheduleId>"
  ]
  ```
- **注意**:
  - 曝光类型：0=自然曝光，1=广告曝光
  - 销售价：当地货币最小单位（如$15.99记作1599）
  - 跟卖数量：未读取到时展示为0
  - sellerName、sellerId、shipsFrom：来自Sorftime库
  - 品牌：优先从搜索页获取，否则来自Sorftime库
  - 变体数：来自Sorftime库

---

### 二、榜单监控

#### 6. 榜单监控任务注册 (BestSellerListSubscription)
- **接口说明**: 注册榜单监控任务，所注册的类目需先为关注类目
- **消耗**: 0 request，改为消耗积分
- **注意**: 
  - 监控频率：每天1次或12次
  - top100每天10积分，top200每天20积分，top300每天30积分，top400每天40积分
  - 有些类目在对应榜单并没有足量的数据，扣取积分按任务设置而非实际数量
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | nodeid | String | 是 | 需要监控的nodeid |
  | Range | Integer | 是 | 最多监控的榜单数据范围：1=top100 |
  | Period | Integer | 是 | 监控频率（见下方说明） |
  | BestSellerListType | Integer | 是 | 榜单类型（见下方说明） |
- **Period监控频率**:
  - 100: 每天1次，（北京时间）每天0点
  - 106: 每天1次，（北京时间）每天6点
  - 112: 每天1次，（北京时间）每天12点
  - 118: 每天1次，（北京时间）每天18点
  - 200: 每天12次，双数小时执行（0,2,4,6,8,10,12,14,16,18,20,22）
  - 201: 每天12次，单数小时执行（1,3,5,7,9,11,13,15,17,19,21,23）
- **BestSellerListType榜单类型**:
  - 1: New Releases
  - 3: Most Wished For
  - 4: Gift Ideas
  - 5: Best Sellers
- **使用示例**:
  ```bash
  # 监控Best Sellers榜单，top100，每天0点执行
  sorftime api BestSellerListSubscription '{"nodeid": "12345", "Range": 1, "Period": 100, "BestSellerListType": 5}' --domain 1
  
  # 监控New Releases榜单，top100，每天12次（双数小时）
  sorftime api BestSellerListSubscription '{"nodeid": "12345", "Range": 1, "Period": 200, "BestSellerListType": 1}' --domain 1
  
  # 监控Most Wished For榜单，top100，每天6点执行
  sorftime api BestSellerListSubscription '{"nodeid": "12345", "Range": 1, "Period": 106, "BestSellerListType": 3}' --domain 1
  ```
- **返回**: taskId（Integer）

---

#### 7. 榜单监控任务查询 (BestSellerListTask)
- **接口说明**: 查看全部榜单监控任务
- **消耗请求数**: 0次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | pageIndex | Integer | 否 | 查询第几页，默认1 |
  | pageSize | Integer | 否 | 每页条数，最小20，默认20，最大200 |
- **使用示例**:
  ```bash
  sorftime api BestSellerListTask '{"pageIndex": 1, "pageSize": 20}' --domain 1
  ```
- **返回格式**: 二维数组
  ```json
  [["<nodeid>", "<BestSellerListType>", "<taskId>", "<Period>", "<status>", "<监控开始日期>", "<监控结束时间>"]]
  ```
  - status: 1=正常，2=已停止，9=榜单不存在
  - 当任务被删除时才有监控结束时间，否则显示为空

---

#### 8. 榜单监控任务删除 (BestSellerListDelete)
- **接口说明**: 删除已注册的榜单监控任务
- **消耗请求数**: 0次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | nodeid | String | 是 | 需要删除监控的nodeid |
  | BestSellerListType | Integer | 是 | 榜单类型：1,3,4,5 |
- **使用示例**:
  ```bash
  sorftime api BestSellerListDelete '{"nodeid": "12345", "BestSellerListType": 5}' --domain 1
  ```
- **返回**: 删除成功返回原始taskId，否则返回-1

---

#### 9. 榜单监控数据提取 (BestSellerListDataCollect)
- **接口说明**: 查询已监控榜单的数据
- **消耗请求数**: 0次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | nodeid | String | 是 | 需要查询的nodeid |
  | BestSellerListType | Integer | 是 | 榜单类型：1,3,4,5 |
  | queryDate | String | 否 | 提取监控榜单日期，格式yyyy-MM-dd HH，最早支持从监控日期开始（最长2年） |
- **注意**: 
  - 当不输入查询小时数时，默认返回当日的第一批数据
  - 当任务为每天1次时，返回自查询小时数开始6个小时内的第一批数据
  - 当任务为每天12次时，返回自查询小时数开始2个小时内的第一批数据
- **使用示例**:
  ```bash
  # 查询当日第一批数据
  sorftime api BestSellerListDataCollect '{"nodeid": "12345", "BestSellerListType": 5}' --domain 1
  
  # 查询指定日期数据
  sorftime api BestSellerListDataCollect '{"nodeid": "12345", "BestSellerListType": 5, "queryDate": "2024-01-15 00"}' --domain 1
  
  # 查询指定小时的数据
  sorftime api BestSellerListDataCollect '{"nodeid": "12345", "BestSellerListType": 5, "queryDate": "2024-01-15 06"}' --domain 1
  ```

---

### 三、跟卖&库存监控

#### 10. 跟卖&库存监控注册 (ProductSellerSubscription)
- **接口说明**: 定时监控ASIN的跟卖卖家（最多前30个卖家）
- **消耗**: 0 request，改为消耗积分
- **注意**: 
  - 每个ASIN每次监控消耗2积分（日本站4积分）
  - 启用库存检查时，额外消耗1积分（日本站2积分）
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | asin | String | 是 | 需要监控的ASIN |
  | checkstock | Integer | 否 | 0=不检查库存（默认），1=检查库存 |
  | period | String | 是 | 监控频率表达式：<每周哪几日>\|<每天哪些时段>\|<监控频率> |
- **period频率表达式**: 同关键词监控
- **使用示例**:
  ```bash
  # 不检查库存，周一至周五，每天5-8点和9-12点，每个时段执行一次
  sorftime api ProductSellerSubscription '{"asin": "B0CVM8TXHP", "checkstock": 0, "period": "1,2,3,4,5|2,3|1"}' --domain 1
  
  # 检查库存，每天全天候，每小时监控1次
  sorftime api ProductSellerSubscription '{"asin": "B0CVM8TXHP", "checkstock": 1, "period": "1,2,3,4,5,6,7|1,2,3,4,5,6|2"}' --domain 1
  
  # 不检查库存，每天0-4点，每2小时监控一次
  sorftime api ProductSellerSubscription '{"asin": "B0CVM8TXHP", "checkstock": 0, "period": "1,2,3,4,5,6,7|1|3"}' --domain 1
  ```
- **返回**: `["asin:taskId", ...]`

---

#### 11. 跟卖&库存监控任务查询 (ProductSellerTasks)
- **接口说明**: 查看全部有效的（非删除的）跟卖监控任务
- **消耗请求数**: 0次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | pageIndex | Integer | 否 | 查询第几页，默认1 |
  | pageSize | Integer | 否 | 每页条数，最小20，默认20，最大200 |
- **使用示例**:
  ```bash
  sorftime api ProductSellerTasks '{"pageIndex": 1, "pageSize": 20}' --domain 1
  ```

---

#### 12. 修改跟卖&库存监控任务 (ProductSellerTaskUpdate)
- **接口说明**: 修改跟卖监控任务（暂停、启动、删除、修改设置）
- **消耗请求数**: 0次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | taskId | Integer | 是 | 任务Id |
  | update | Integer | 是 | 0=修改设置，1=暂停，2=启动，9=删除 |
  | period | String | 条件性 | update=0时有效，频率表达式 |
- **使用示例**:
  ```bash
  # 暂停任务
  sorftime api ProductSellerTaskUpdate '{"taskId": 12345, "update": 1}' --domain 1
  
  # 启动任务
  sorftime api ProductSellerTaskUpdate '{"taskId": 12345, "update": 2}' --domain 1
  
  # 删除任务
  sorftime api ProductSellerTaskUpdate '{"taskId": 12345, "update": 9}' --domain 1
  
  # 修改任务设置
  sorftime api ProductSellerTaskUpdate '{"taskId": 12345, "update": 0, "period": "1,2,3,4,5|2,3|1"}' --domain 1
  ```
- **返回**: taskId > 0 表示成功，-999表示修改失败

---

#### 13. 查询跟卖&库存监控任务执行批次 (ProductSellerTaskScheduleList)
- **接口说明**: 查询跟卖监控全部执行任务批次
- **消耗请求数**: 0次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | TaskId | Integer | 是 | 任务Id |
- **使用示例**:
  ```bash
  sorftime api ProductSellerTaskScheduleList '{"TaskId": 12345}' --domain 1
  ```
- **返回格式**: 
  ```json
  ["202401151030:batch123", "202401150930:batch122"]
  ```

---

#### 14. 提取跟卖&库存监控执行结果详细数据 (ProductSellerTaskScheduleDetail)
- **接口说明**: 提取某次跟卖监控结果数据
- **消耗请求数**: 0次
- **请求参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | ScheduelId | String | 是 | 批次任务Id |
- **使用示例**:
  ```bash
  sorftime api ProductSellerTaskScheduleDetail '{"ScheduelId": "batch123"}' --domain 1
  ```

---

## 注意事项

1. **积分管理**: 监控类接口都消耗积分，每月10号凌晨重置
2. **数据保存**: 所有监控结果最多保存30日
3. **任务注册失败**: 当设定某些频率时（11-14, 31-32），可能因时段内任务量过多而注册失败，返回taskId=-999
4. **榜单监控前提**: 所注册的类目需先为关注类目
5. **跟卖监控限制**: 最多监控前30个卖家

---

## 常见错误

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 0 | 成功 | - |
| 4 | 积分余额不足 | 充值积分或等待下月重置 |
| -999 | 任务注册/修改失败 | 时段内任务过多，尝试其他时段或频率 |
| 401 | 认证失败 | 检查Account-SK是否有效 |
| 403 | 权限不足 | 检查套餐权限或请求次数 |

---

## 最佳实践

### 1. 关键词排名监控
```bash
# 注册监控任务：工作日白天每小时监控一次
sorftime api KeywordBatchSubscription '{"keyword": ["water bottle", "coffee mug"], "mode": 0, "area": "10041", "page": 3, "period": "1,2,3,4,5|1,2,3,4,5,6|2"}' --domain 1

# 查询任务列表
sorftime api KeywordTasks '{"keyword": "water"}' --domain 1

# 查询执行批次
sorftime api KeywordBatchScheduleList '{"TaskId": 12345}' --domain 1

# 提取某次监控的详细数据
sorftime api KeywordBatchScheduleDetail '{"ScheduelId": "batch123"}' --domain 1
```

### 2. 榜单监控
```bash
# 注册Best Sellers榜单监控，每天0点执行
sorftime api BestSellerListSubscription '{"nodeid": "12345", "Range": 1, "Period": 100, "BestSellerListType": 5}' --domain 1

# 查询榜单监控任务
sorftime api BestSellerListTask '{"pageIndex": 1, "pageSize": 20}' --domain 1

# 查询榜单数据
sorftime api BestSellerListDataCollect '{"nodeid": "12345", "BestSellerListType": 5, "queryDate": "2024-01-15 00"}' --domain 1

# 删除榜单监控任务
sorftime api BestSellerListDelete '{"nodeid": "12345", "BestSellerListType": 5}' --domain 1
```

### 3. 跟卖监控
```bash
# 注册跟卖监控，每小时检查一次，不检查库存
sorftime api ProductSellerSubscription '{"asin": "B0CVM8TXHP", "checkstock": 0, "period": "1,2,3,4,5,6,7|1,2,3,4,5,6|2"}' --domain 1

# 查询跟卖监控任务
sorftime api ProductSellerTasks '{"pageIndex": 1, "pageSize": 20}' --domain 1

# 暂停任务
sorftime api ProductSellerTaskUpdate '{"taskId": 12345, "update": 1}' --domain 1

# 恢复任务
sorftime api ProductSellerTaskUpdate '{"taskId": 12345, "update": 2}' --domain 1

# 查询执行批次
sorftime api ProductSellerTaskScheduleList '{"TaskId": 12345}' --domain 1

# 提取监控结果
sorftime api ProductSellerTaskScheduleDetail '{"ScheduelId": "batch123"}' --domain 1
```

### 4. 综合监控策略
```bash
# 场景：监控核心产品的关键词排名、榜单位置和跟卖情况

# 1. 关键词排名监控（工作时段每小时）
sorftime api KeywordBatchSubscription '{"keyword": ["water bottle"], "mode": 0, "area": "10041", "page": 3, "period": "1,2,3,4,5|1,2,3,4,5,6|2"}' --domain 1

# 2. 榜单监控（每天0点）
sorftime api BestSellerListSubscription '{"nodeid": "12345", "Range": 1, "Period": 100, "BestSellerListType": 5}' --domain 1

# 3. 跟卖监控（每小时，含库存检查）
sorftime api ProductSellerSubscription '{"asin": "B0CVM8TXHP", "checkstock": 1, "period": "1,2,3,4,5,6,7|1,2,3,4,5,6|2"}' --domain 1
```
