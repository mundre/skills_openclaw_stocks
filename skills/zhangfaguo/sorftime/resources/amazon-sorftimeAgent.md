# Sorftime Agent Skill

## 基本信息
- **名称**: sorftime-agent
- **描述**: Sorftime 智能分析助手，提供选品建议、市场洞察、竞品分析等高级功能
- **激活条件**: 当用户提到Sorftime智能分析、选品建议、市场机会、产品推荐时自动激活
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

## 功能说明

Sorftime Agent 是一个智能分析助手，基于亚马逊API数据提供以下高级功能：

### 1. 智能选品分析
- 基于多维度数据筛选潜力产品
- 分析市场竞争度、利润空间、进入门槛
- 提供选品建议和风险评估

### 2. 市场机会发现
- 识别蓝海类目和高增长细分市场
- 分析季节性产品趋势
- 发现未被充分满足的市场需求

### 3. 竞品深度分析
- 全方位分析竞争对手产品
- 追踪竞品销售表现和策略变化
- 识别竞品的优势和劣势

### 4. 关键词策略优化
- 智能推荐高价值关键词
- 分析关键词竞争度和转化潜力
- 提供关键词布局建议

### 5. 定价策略建议
- 基于市场数据提供最优定价区间
- 分析价格弹性和利润空间
- 监控竞品价格变化

---

## 使用场景

### 场景1: 新产品选品
```
用户需求: "我想在亚马逊美国站找一个有潜力的家居用品类目"

Agent工作流程:
1. 查询家居用品类目的市场趋势
2. 分析各子类目的竞争程度
3. 筛选出低竞争、高增长的细分领域
4. 提供具体的选品建议和风险提示
```

### 场景2: 竞品分析
```
用户需求: "帮我分析一下ASIN B0CVM8TXHP这个产品"

Agent工作流程:
1. 获取产品详细信息（价格、销量、排名、评论等）
2. 查询产品的历史趋势数据
3. 分析产品的关键词排名情况
4. 查看产品的评论分布和用户反馈
5. 提供竞品分析报告和改进建议
```

### 场景3: 关键词研究
```
用户需求: "帮我找出water bottle相关的优质关键词"

Agent工作流程:
1. ASIN反查关键词，了解竞品使用的关键词
2. 查询关键词搜索量和竞争度
3. 拓展相关长尾关键词
4. 分析关键词的搜索结果和产品分布
5. 提供关键词优先级排序和布局建议
```

### 场景4: 市场趋势分析
```
用户需求: "分析一下厨房用品类目的市场趋势"

Agent工作流程:
1. 获取类目的销量趋势数据
2. 分析价格趋势和新品占比
3. 查看品牌垄断系数和卖家分布
4. 评估市场进入难度和机会
5. 提供市场进入策略建议
```

---

## 数据分析维度

### 1. 市场维度
- 市场规模和增长趋势
- 季节性波动特征
- 新品成功率和生命周期
- 市场集中度和垄断程度

### 2. 竞争维度
- Top卖家市场份额
- 品牌集中度
- 价格区间分布
- 评论数量和星级分布

### 3. 产品维度
- 热销产品特征分析
- 价格-销量关系
- 评价-销量相关性
- 变体策略分析

### 4. 关键词维度
- 核心关键词搜索量
- 长尾词机会分析
- 关键词竞争度评估
- 广告位分布情况

---

## 最佳实践

### 1. 系统化选品流程
```bash
# 步骤1: 确定目标市场和类目
sorftime api CategoryTree --domain 1

# 步骤2: 分析类目的市场趋势
sorftime api CategoryTrend '{"nodeId": "12345", "trendIndex": 0}' --domain 1

# 步骤3: 查询类目的Best Seller产品
sorftime api CategoryRequest '{"nodeId": "12345"}' --domain 1

# 步骤4: 筛选符合条件的产品
sorftime api ProductQuery '{"query": 2, "pattern": [{"queryType": 2, "content": "12345"}, {"queryType": 9, "content": "100,1000"}, {"queryType": 12, "content": "4,"}]}' --domain 1

# 步骤5: 深入分析候选产品
sorftime api ProductRequest '{"asin": "B0CANDIDATE1,B0CANDIDATE2"}' --domain 1
```

### 2. 竞品监控体系
```bash
# 步骤1: 注册关键词排名监控
sorftime api KeywordBatchSubscription '{"keyword": ["water bottle"], "mode": 0, "area": "10041", "page": 3, "period": "1,2,3,4,5|1,2,3,4,5,6|2"}' --domain 1

# 步骤2: 注册跟卖监控
sorftime api ProductSellerSubscription '{"asin": "B0COMPETITOR", "checkstock": 1, "period": "1,2,3,4,5,6,7|1,2,3,4,5,6|2"}' --domain 1

# 步骤3: 定期查询监控数据
sorftime api KeywordBatchScheduleDetail '{"ScheduelId": "batch123"}' --domain 1
sorftime api ProductSellerTaskScheduleDetail '{"ScheduelId": "batch456"}' --domain 1
```

### 3. 关键词优化策略
```bash
# 步骤1: ASIN反查关键词
sorftime api ASINRequestKeywordv2 '{"asin": "B0CVM8TXHP"}' --domain 1

# 步骤2: 查询关键词详情
sorftime api KeywordRequest '{"keyword": "water bottle"}' --domain 1

# 步骤3: 拓展相关关键词
sorftime api KeywordExtends '{"keyword": "water bottle", "pageSize": 100}' --domain 1

# 步骤4: 分析关键词搜索结果
sorftime api KeywordSearchResults '{"keyword": "water bottle", "pageSize": 50}' --domain 1

# 步骤5: 收藏高价值关键词
sorftime api FavoriteKeyword '{"keyword": "insulated water bottle", "dict": "核心词"}' --domain 1
```

---

## 注意事项

1. **数据时效性**: API数据有一定的更新延迟，实时监控需要使用监控类接口
2. **积分消耗**: 部分高级功能消耗积分，注意合理规划使用
3. **多站点分析**: 不同站点的市场特征可能差异很大，需要分别分析
4. **历史数据**: 充分利用历史数据进行趋势分析，避免仅看当前快照
5. **综合判断**: 单一指标可能有误导性，需要多维度数据综合判断

---

## 常见问题

### Q1: 如何判断一个类目是否适合进入？
**A**: 综合考虑以下因素：
- 市场规模和增长趋势（CategoryTrend）
- 竞争程度（品牌/卖家垄断系数）
- 新品成功率（新品占比趋势）
- 利润空间（平均售价、FBA费用）
- 进入门槛（评论数、星级要求）

### Q2: 如何找到有潜力的关键词？
**A**: 
- 通过ASIN反查找到竞品正在排名的关键词
- 使用KeywordExtends拓展相关长尾词
- 分析关键词的竞争度和搜索量
- 关注搜索结果中弱竞争产品的关键词

### Q3: 如何监控竞品的动态？
**A**: 
- 使用ProductRealtimeRequest实时监控产品信息
- 使用KeywordBatchSubscription监控关键词排名
- 使用ProductSellerSubscription监控跟卖情况
- 定期查询ProductReviews了解用户反馈变化

### Q4: 如何评估产品的市场潜力？
**A**: 
- 查询同类产品的销量分布（CategoryRequest）
- 分析价格-销量关系（ProductQuery）
- 查看市场趋势和季节性（CategoryTrend）
- 评估竞争强度和进入难度

---

## 支持的功能模块

如需使用具体功能，请参考对应Skill文档：

- **类目市场分析**: `resources/amazon-category.md`
- **产品数据查询**: `resources/amazon-product.md`
- **关键词研究**: `resources/amazon-keyword.md`
- **数据监控**: `resources/amazon-monitoring.md`

---

## 示例对话

### 示例1: 选品咨询
**用户**: "我想在亚马逊美国站做水杯类产品，有什么建议？"

**Agent**: 
1. 首先查询水杯类目的市场趋势
2. 分析该类目的竞争格局
3. 查看Best Seller产品的特征
4. 提供差异化的产品建议
5. 推荐相关的关键词策略

### 示例2: 问题诊断
**用户**: "我的产品上架一个月了，销量一直不好，怎么办？"

**Agent**:
1. 查询产品的详细信息和排名
2. 分析产品的关键词覆盖情况
3. 对比同类竞品的价格和评论
4. 检查Listing优化程度
5. 提供改进建议和优化方向

### 示例3: 机会发现
**用户**: "最近有什么新兴的产品趋势吗？"

**Agent**:
1. 查询各类目的新品占比趋势
2. 分析快速增长的细分市场
3. 识别上升期的关键词
4. 提供趋势产品推荐
5. 评估进入时机和风险
