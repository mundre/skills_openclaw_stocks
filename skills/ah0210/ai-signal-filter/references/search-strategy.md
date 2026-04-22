# 搜索策略

## 统一内容提取入口
所有站点爬取统一使用该服务，不需要单独处理每个站点的反爬和请求头：
- **markdown.new (https://markdown.new/{url})**：提取速度快，国内网络可用，自动输出纯markdown格式，自动过滤广告和无用内容

---

## 信息源分级

### Tier 1（一手，可单独作为来源）

- 官方博客和公告（OpenAI Blog, Anthropic News, Google AI Blog, Meta AI Blog 等）
- GitHub release 页面
- 论文页面（arXiv 等）
- 官方文档和 changelog

### Tier 2（聚合，需交叉验证）

- Hacker News 热帖
- Reddit（r/LocalLLaMA, r/MachineLearning, r/artificial 等）
- 技术社区首发文章（机器之心、量子位、InfoQ、36氪AI等）
- 中文社区：知乎AI话题热榜、掘金AI板块、少数派AI专栏
- 独立内容源：刘斯坦、半佛仙人等AI领域深度博主
- 国内大模型官方公众号：DeepSeek、月之暗面、MiniMax、百度文心、阿里通义等官方公告
- API status 页面
- 产品更新日志

### Tier 3（分析，只能作为线索）

- 科技媒体深度文章（36kr 等）
- 行业分析师长文
- 播客摘要和访谈记录
- Newsletter（Ben's Bites, a16z AI 等）

## 搜索维度

每次执行至少覆盖以下 8 个维度之一（全部覆盖优先）：

1. **模型能力变化**：新发布、重大更新、能力变化、定价变化
   - 关键词：`AI model release update 2026`, `AI模型发布更新`, `LLM benchmark update`, `大模型价格调整`
2. **工具生态变化**：新产品、重要更新、开源项目里程碑
   - 关键词：`AI tool launch 2026`, `AI工具新品`, `AI open source release`, `开源AI项目更新`
3. **行业结构变化**：融资（战略级）、政策法规、大厂战略调整
   - 关键词：`AI funding 2026`, `AI融资`, `AI policy regulation`, `AI政策法规`, `tech company AI strategy`
4. **办公生态**：新功能、集成变化、合作伙伴动态
   - 关键词：`productivity AI feature update`, `办公AI功能更新`, `workspace AI integration`
5. **开源社区动态**：重大 release、新框架、性能突破
   - 关键词：`open source AI release`, `开源AI框架`, `AI performance breakthrough`, `AI推理优化`
6. **AI 应用层**：新应用模式、用户行为变化、商业模式创新
   - 关键词：`AI application trend 2026`, `AI应用趋势`, `AI business model`, `AI商业化`
7. **AI安全与对齐**：越狱方法、数据泄露、对齐突破、安全漏洞
   - 关键词：`AI security alignment 2026`, `AI安全漏洞`, `大模型越狱`, `AI对齐突破`
8. **监管与合规**：国内生成式AI备案、欧盟AI法案落地、数据合规要求
   - 关键词：`AI regulation compliance 2026`, `生成式AI备案`, `AI监管政策`, `数据合规要求`

## 降权规则

以下信息自动降权，需要额外强的理由才能报：

- 含"最强""颠覆""首个""史上"等营销词的 → 自动降权
- 纯跑分数据（未经实测验证的）→ 必须标注"未经实测验证"
- 小额融资新闻（除非改变了行业格局）→ 不报
- "XX 即将发布"（只有发布了才报）→ 不报预告

## 交叉验证规则

- **今日信号区**：至少 2 个独立来源确认
- **值得留意区**：至少 1 个来源 + 1 个佐证
- **单一来源**：标注"待验证"，不能进"今日信号"

## 动态信息源

读取 `memory/signal/profile.md` 中的信息源评分部分获取动态评分。优先搜索高评分信息源，降低低评分源搜索频率。

搜索完成后，根据本次搜索结果更新 `memory/signal/profile.md` 的信息源评分：
- 某信息源产出的信号通过了质量门控 → 产出次数 +1，通过次数 +1
- 某信息源产出的信号被门控删除 → 产出次数 +1
