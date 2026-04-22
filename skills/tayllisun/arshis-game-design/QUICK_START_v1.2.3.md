# Arshis-Game-Design-Pro v1.2.3 - 快速使用指南

**版本**: 1.2.3  
**更新日期**: 2026-04-15  
**适用对象**: 策划/制作人/独立开发者

---

## 🚀 5 分钟快速开始

### 1. 安装
```bash
# 技能已安装在
/root/.openclaw/workspace/skills/Arshis-Game-Design-Pro-release/
```

### 2. 测试运行
```bash
# 测试定价策略
python3 scripts/pricing_strategy.py rpg 大众

# 测试系统策划
python3 scripts/system_design.py rpg combat

# 测试台词演出
python3 scripts/dialogue_performance.py village_elder gentle quest_give
```

---

## 📋 常用场景速查

### 场景 1：生成付费设计
```bash
# 完整定价策略报告
python3 scripts/pricing_strategy.py rpg 大众 > output/pricing.md

# 深度付费设计
python3 scripts/monetization_deep_design.py report rpg 大众 > output/monetization.md
```
**产出**: 完整价格表/区域定价/促销策略/付费模式组合  
**完成度**: 95%  
**使用**: 数值策划/运营团队

---

### 场景 2：生成发行运营方案
```bash
python3 scripts/publishing_operations.py rpg 中等 > output/publishing.md
```
**产出**: 上线节奏/买量渠道/KPI 目标/留存提升策略  
**完成度**: 90%  
**使用**: 发行/运营团队

---

### 场景 3：生成技术评估
```bash
python3 scripts/technical_assessment.py rpg mid mobile medium > output/technical.md
```
**产出**: 引擎推荐/服务器架构/性能目标/团队配置  
**完成度**: 85%  
**使用**: 技术团队参考

---

### 场景 4：生成系统策划案
```bash
# 战斗系统
python3 scripts/system_design.py rpg combat > output/combat.md

# 成长系统
python3 scripts/system_design.py rpg progression > output/progression.md

# 经济系统
python3 scripts/system_design.py rpg economy > output/economy.md
```
**产出**: 系统框架/UI 设计/交互流程/系统循环/技术需求  
**完成度**: 90%  
**使用**: 系统策划团队

---

### 场景 5：生成台词演出
```bash
# 村长温柔给予任务
python3 scripts/dialogue_performance.py village_elder gentle quest_give > output/dialogue1.md

# 战士愤怒冲突对峙
python3 scripts/dialogue_performance.py warrior angry conflict_confrontation > output/dialogue2.md

# 法师神秘剧情反转
python3 scripts/dialogue_performance.py mage mysterious plot_twist > output/dialogue3.md
```
**产出**: 具体台词/分镜设计/配音指导/情绪曲线  
**完成度**: 90%  
**使用**: 文案/配音团队

---

### 场景 6：生成活动配置
```bash
# 季节活动
python3 scripts/event_configuration.py rpg seasonal_event 2 周 > output/event1.md

# 限定卡池
python3 scripts/event_configuration.py rpg limited_gacha 3 周 > output/event2.md

# 战斗通行证
python3 scripts/event_configuration.py moba battle_pass 8 周 > output/event3.md
```
**产出**: 奖励配置/时间安排/数值平衡/执行清单  
**完成度**: 90%  
**使用**: 运营/数值策划

---

### 场景 7：生成完整策划案
```bash
# 1. 生成所有模块
python3 scripts/pricing_strategy.py rpg 大众 > output/pricing.md
python3 scripts/publishing_operations.py rpg 中等 > output/publishing.md
python3 scripts/technical_assessment.py rpg mid mobile medium > output/technical.md
python3 scripts/worldview_builder.py generate "项目名称" > output/worldview.md
python3 scripts/story_designer.py outline "三幕剧" > output/story.md
python3 scripts/system_design.py rpg combat > output/combat.md
python3 scripts/gameplay_tutorial.py generate gathering crafting > output/tutorial.md
python3 scripts/numeric_balance.py economy rpg > output/numeric.md

# 2. 整合文档
cat output/*.md > 完整策划案.md

# 3. 人工补充（10-15%）
# - 具体项目参数
# - 美术资源
# - 技术实现细节
# - 团队评审确认
```
**完成度**: 90%  
**使用**: 全团队执行参考

---

## 📊 模块选择指南

| 需求 | 推荐模块 | 完成度 |
|---|---|---|
| **定价/付费设计** | `pricing_strategy.py` + `monetization_deep_design.py` | 95% |
| **发行运营** | `publishing_operations.py` | 90% |
| **技术评估** | `technical_assessment.py` | 85% |
| **系统策划** | `system_design.py` | 90% |
| **台词演出** | `dialogue_performance.py` | 90% |
| **活动配置** | `event_configuration.py` | 90% |
| **世界观** | `worldview_builder.py` | 90% |
| **剧情** | `story_designer.py` | 85% |
| **新手流程** | `gameplay_tutorial.py` | 80% |
| **数值框架** | `numeric_balance.py` | 75% |

---

## 🎯 支持的游戏类型

| 类型 | 支持度 | 推荐模块 |
|---|---|---|
| **RPG** | ✅ 完美 | 所有模块 |
| **MOBA** | ✅ 完美 | 系统/台词/活动 |
| **FPS** | ✅ 完美 | 系统/技术/发行 |
| **SLG** | ✅ 完美 | 付费/系统/运营 |
| **二次元** | ✅ 完美 | 台词/付费/活动 |
| **模拟经营** | ✅ 完美 | 系统/数值/运营 |
| **Roguelike** | ✅ 完美 | 系统/玩法/数值 |
| **MMORPG** | ✅ 完美 | 所有模块 |

---

## 💡 最佳实践

### ✅ 推荐用法

1. **先用 skill 生成框架**（快速产出 85-90%）
2. **团队评审**（制作人/主策/主程/主美）
3. **补充人工内容**（具体参数/资源/实现）
4. **整合定稿**（统一格式/最终评审）

### ❌ 避免用法

1. **完全依赖 skill**（需要人工确认）
2. **不做评审直接用**（需要团队确认）
3. **期望 100% 自动化**（skill 是辅助工具）

---

## 🔧 常见问题

### Q1: 如何修改输出格式？
A: 修改对应模块的 `generate_report()` 函数，支持 Markdown/JSON/TXT 格式

### Q2: 如何添加自定义模板？
A: 在 `templates/` 目录添加新模板文件，参考现有模板格式

### Q3: 如何保存生成结果？
A: 使用重定向：`python3 scripts/xxx.py > output/result.md`

### Q4: 如何批量生成？
A: 使用循环：
```bash
for type in rpg moba fps; do
  python3 scripts/system_design.py $type combat > output/${type}_combat.md
done
```

### Q5: 如何反馈问题？
A: 查看 `RELEASE_NOTES_v1.2.3.md` 获取联系方式

---

## 📁 文件结构

```
Arshis-Game-Design-Pro-release/
├── scripts/                      # 核心模块（26 个）
│   ├── pricing_strategy.py       # 定价策略 ⭐
│   ├── publishing_operations.py  # 发行运营 ⭐
│   ├── technical_assessment.py   # 技术评估 ⭐
│   ├── dialogue_performance.py   # 台词演出 ⭐
│   ├── event_configuration.py    # 活动配置 ⭐
│   ├── system_design.py          # 系统策划 ⭐
│   └── ... (其他 20 个模块)
├── docs/                         # 文档（40+ 个）
│   ├── README.md                 # 本文件
│   ├── RELEASE_NOTES_v1.2.3.md   # 发布说明 ⭐
│   ├── COMPLETE_PITCH_GUIDE.md   # 完整策划案指南
│   └── ... (其他 37+ 个文档)
├── case_studies/                 # 案例分析（9 个）
└── templates/                    # 模板库（8 种游戏类型）
```

---

## 🎉 总结

**Arshis-Game-Design-Pro v1.2.3**:
- ✅ **26 个核心模块**
- ✅ **40+ 个文档**
- ✅ **90% 策划案完成度**
- ✅ **3-4 倍效率提升**

**定位**: 资深策划顾问 + 效率工具

**使用**: 生成框架 → 团队评审 → 补充人工 → 整合定稿

---

*Arshis-Game-Design-Pro v1.2.3*
*让游戏策划更专业、更高效、更有依据！✨*
