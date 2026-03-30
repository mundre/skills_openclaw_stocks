---
name: iran-war-tracker
description: |-
  高频获取2026年3月开始的伊朗战争的最新动态，分析局势进展和风险资产交易线索。生成结构化的伊朗局势分析报告，关注战争动态、霍尔木兹海峡通航状况、油气供应风险及市场反应。 
  This skill generates structured Iran situation reports focused on war developments, Hormuz Strait status, oil and gas supply risk, and market reactions.
version: 1.1.2
clawhub: https://clawhub.ai/chinfi-codex/iran-war-tracker
github:
triggers: /irantracker 伊朗动态
---
## 行动基准哲学
* 分析框架是展开一切行动的基准
	* 必须先加载并使用远程分析框架 Gist： https://gist.github.com/chinfi-codex/b311c4c284c8aa6dae9c833a146a1840
	* 远程 Gist 加载必须设置 `20s` 超时，超时或失败后再加载本地文件：伊朗局势关键变量与经济影响分析框架.md
* 基于分析框架，要做到的是绝对的冷静，客观，不会做任何的主观预设，绝对不将自己置于信息茧房的可能性中。
* 将世界事件的走向认为是在多重变量变化叠加下所产生的概率论分支。所以要识别当前事件的核心变量，思考其对应权重。然后和高可信度信源信息叠加分析，推演事件的走向，和其对现实世界施加的影响性 。


## 信息数据归集

**信息处理准则：
* 真实性，一手信息优于二手信息
* 根据信源等级确定可信度
	* 最高：官网、国家级官媒，官方平台，官方领导人社交平台发言
	* 次要：社交大V，传言的重要人物讲话
* 【重要】以下列出的步骤要全部执行:新闻搜索，电报（财联社+金十数据），风险资产数据
* 【重要】对新闻、电报数据，筛选时效性，默认为过去18小时

### 使用新闻搜索
##### 第一步，搜索词构建
根据加载的分析框架，分析变量和权重，推导出最重要的3-5个研究方向，每个方向构建搜索关键词组。举例如下：
     * 战争局势更新 / war situation updates
     * 霍尔木兹海峡关闭、通航、油轮及袭船事件 / Hormuz Strait closure, transit, tanker, ship attacks
     * 石油供应、出口、制裁及产量变化 / oil supply, exports, sanctions, production
     * 天然气供应、LNG、基础设施及出口变化 / natural gas supply, LNG, infrastructure, exports
     * 领导人、外交官及军方表态 / leader, diplomat, military statements
##### 第二步，使用搜索工具搜索搜索全部关键词组
* 优先使用当前环境下可用的Tool：WebSearch/Kimi_search，**WebFetch**
	* Jina**（可选预处理层，可与 WebFetch/curl 组合使用，由于其特性可节省 tokens 消耗，请积极在任务合适时组合使用）：第三方网络服务，可将网页转为 Markdown，大幅节省 token 但可能有信息损耗。调用方式为 `r.jina.ai/example.com`（URL 前加前缀，不保留原网址 http 前缀），限 20 RPM。
* 可选搜索API，按顺序选择一项可用的即可，根据当前环境下配置使用：
	* Tavily Search API
	   * 高质量新闻搜索 API
	   * 需要 环境变量 API KEY
   * DuckDuckGo Lite
	   * 免费网页搜索（无需 API key）
	   * 当上述方法失败时自动作为降级方案
	   * 通过 DuckDuckGo Lite HTML 界面搜索
##### 第三步，将所有结果汇总

### 电报（财联社+金十数据）
用独立脚本 cls_telegraph.py 抓取来自财联社，金十数据的实时电报，并筛选伊朗相关的内容。（脚本已经默认做了筛选）

### 风险资产数据
使用以下url 获取数据
	- BTC: [https://stooq.com/q/l/?s=btcusd&i=d]
	- 黄金: [https://stooq.com/q/l/?s=xauusd&i=d]
	- 原油(WTI): [https://stooq.com/q/l/?s=cl.f&i=d]
	- 天然气: [https://stooq.com/q/l/?s=ng.f&i=d]
	- 纳指期货: [https://stooq.com/q/l/?s=nq.f&i=d]


## 分析输出
### 输出要求
* 【重要】在报告中输出新闻内容，以时间-新闻[来源]的格式呈现
* 如果使用subagent进行报告分析输出，则回复结果一定要将subagent最后给出的完整报告内容输出。
主agent仅做简短的精要评述即可！
* 报告中不同的模块内容，使用适当的分割线，恰当不要喧宾夺主，同时要考虑手机屏幕宽度
* 报告总字数控制在3000字以内。

### 分析要求
遵守以下规则（非风格建议，而是硬性要求）：
* 报告默认必须使用中文产出。每个部分都应内容充实，而非一句话总结。
* 不能仅停留在事件总结。每个部分都需要证据加解读。
* 必须区分：
	  * 确认的事实
	  * 市场定价信号
	  * 推断或情景判断
* 能源与经济影响的传导路径：
	* 必须分开分析石油和天然气，不能合并成笼统的"能源"段落。
	* 必须严格按照加载的分析框架所指引的传导路径对要素进行分析
* 补充其他从分析框架中得出的重要路径和变量信号


### 完整报告模板
##### 📊 战争烈度评估 / War Intensity Assessment

```

🔥 美以伊动态播报 | YYYY-MM-DD HH:00 🔥


### 📊 【战争烈度评估】/ War Intensity Assessment
X级（🔺上升/🔻下降/➡️持平）/ Level X (Rising/Falling/Stable)
- 当前态势简述 / Current situation summary
- 关键变化点 / Key changes
```

##### ⚔️ 局势进展 / Situation Updates

```


### ⚔️ 【局势进展】/ Situation Progress

▸ 🇺🇸 美国汇总 / US Summary
- 🎯 军事行动 / Military Actions:
- 📌 其他动态 / Other Updates:

▸ 🇮🇱 以色列汇总 / Israel Summary
- 🎯 军事行动 / Military Actions:
- 📌 其他动态 / Other Updates:

▸ 🇮🇷 伊朗汇总 / Iran Summary
- ⚡ 反击行动 / Retaliation Actions:
- 📌 其他动态 / Other Updates:

▸ 领导人表态 / Leader Statements:
包括参战方，其他国家，国际重要组织的各方领导人表态汇总

▸ 📈 边际变化评估 / Marginal Change Assessment
├─ 🔴 战争扩大信号 / Escalation Signals:
│  • 空袭烈度/频次是否加大 / Airstrike intensity/frequency:
│  • 地面进攻迹象 / Ground operation signs:
│  • 新参战方动态 / New participants:
├─ 🟢 战争缓和信号 / De-escalation Signals:
│  • 谈判信号 / Negotiation signals:
│  • 停火提议 / Ceasefire proposals:
│  • 外交斡旋 / Diplomatic mediation:
└─ 🚢 霍尔木兹海峡封锁 / Hormuz Strait Blockade:
   • 通航状态 / Transit status:
   • 袭船事件 / Ship attacks:
   • 船只动态 / Vessel movements:
```

##### 💹 风险资产波动 / Risk Asset Fluctuations

覆盖 BTC、黄金、WTI 原油、天然气和纳指期货。说明价格变动是证实还是反驳地缘叙事。

##### 🛢️ 能源与经济分析

根据分析框架指导进行路径分析
列举石油，天然气，宏观经济等要素

##### 📑 情景推演 / Scenario Analysis

* **基准情景 / Base Case**
* **升级情景 / Escalation Case**
* **缓和情景 / De-escalation Case**


### 细节下限 / Detail Floor

为避免较弱模型生成浅层输出，强制执行最低细节标准：

* `局势进展` 中美国、以色列、伊朗各方至少 2 个要点
* `油气分析` 中原油和天然气各至少 4 个要点
* `风险资产波动` 至少 3 个要点
* `情景推演` 至少 3 个情景

如证据稀疏，说明证据稀疏，但仍需使用谨慎推断完成完整结构，而非缩短报告。
