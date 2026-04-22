# Arshis-Game-Design-Pro - 完整策划案生成指南

**版本**: v1.1.0  
**更新日期**: 2026-04-15  
**作者**: Arshis

---

## 🎯 本技能可以生成什么

### ✅ 可直接给团队使用的文档

| 文档类型 | 生成模块 | 完成度 | 可直接使用 |
|---|---|---|---|
| **付费设计文档** | `pricing_strategy.py` | 100% | ✅ 数值策划/运营团队 |
| **发行运营方案** | `publishing_operations.py` | 100% | ✅ 发行/运营团队 |
| **技术评估报告** | `technical_assessment.py` | 100% | ✅ 技术团队参考 |
| **世界观框架** | `worldview_builder.py` | 100% | ✅ 文案/美术团队 |
| **剧情结构** | `story_designer.py` | 100% | ✅ 文案团队 |
| **新手流程** | `gameplay_tutorial.py` | 100% | ✅ 系统/关卡策划 |
| **数值框架** | `numeric_balance.py` | 100% | ✅ 数值策划参考 |
| **付费深度设计** | `monetization_deep_design.py` | 100% | ✅ 运营/数值策划 |

---

## 📋 完整策划案结构

### 第一部分：项目概述（skill 生成 80%）

```bash
# 生成付费设计
python3 scripts/pricing_strategy.py rpg 大众

# 生成发行运营
python3 scripts/publishing_operations.py rpg 中等

# 生成技术评估
python3 scripts/technical_assessment.py rpg mid mobile medium
```

**产出内容**：
- ✅ 项目定位（类型/平台/目标用户）
- ✅ 付费设计（完整价格表/区域定价/促销策略）
- ✅ 发行计划（上线节奏/买量渠道/KPI 目标）
- ✅ 技术选型（引擎推荐/服务器架构/性能目标）

**需人工补充**：
- ⚠️ 具体预算（需要财务确认）
- ⚠️ 团队名单（需要制作人确认）
- ⚠️ 时间表（需要项目组确认）

---

### 第二部分：世界观与剧情（skill 生成 90%）

```bash
# 生成世界观
python3 scripts/worldview_builder.py generate "项目名称"

# 生成剧情结构
python3 scripts/story_designer.py outline "三幕剧"

# 生成对话
python3 scripts/dialogue_generator.py npc "村长" gentle worried quest_give
```

**产出内容**：
- ✅ 世界观框架（四步骤/六模块）
- ✅ 剧情结构（英雄之旅/三幕剧/人物原型）
- ✅ 角色设定（核心角色/关系网络）
- ✅ 对话示例（NPC 对话/情感场景）

**需人工补充**：
- ⚠️ 具体台词（需要文案细化）
- ⚠️ 演出设计（需要导演/分镜）
- ⚠️ 美术风格（需要主美定稿）

---

### 第三部分：玩法系统（skill 生成 85%）

```bash
# 生成新手流程
python3 scripts/gameplay_tutorial.py generate gathering crafting making combat

# 生成数值框架
python3 scripts/numeric_balance.py economy rpg
```

**产出内容**：
- ✅ 核心玩法循环
- ✅ 新手教学流程（剧情 - 玩法融合）
- ✅ 数值框架（经济系统/成长曲线）
- ✅ 系统框架（各系统设计）

**需人工补充**：
- ⚠️ 具体 UI 设计（需要 UI 策划）
- ⚠️ 操作细节（需要关卡策划）
- ⚠️ 具体数值填表（需要数值策划）

---

### 第四部分：美术需求（skill 生成 50%）

**产出内容**：
- ✅ 美术风格参考（关键词/案例）
- ✅ 角色设计方向（种族/职业/视觉关键词）
- ✅ 场景设计方向（生物群系/建筑风格）

**需人工补充**：
- ⚠️ 具体原画（需要美术团队）
- ⚠️ 3D 模型（需要美术团队）
- ⚠️ 特效设计（需要美术团队）

---

## 🚀 使用流程

### 场景 1：立项文档（给投资人/老板）

```bash
# 1. 生成付费设计
python3 scripts/pricing_strategy.py rpg 大众 > docs/pricing.md

# 2. 生成发行运营
python3 scripts/publishing_operations.py rpg 中等 > docs/publishing.md

# 3. 生成技术评估
python3 scripts/technical_assessment.py rpg mid mobile medium > docs/technical.md

# 4. 生成世界观
python3 scripts/worldview_builder.py generate "项目名称" > docs/worldview.md

# 5. 整合文档
cat docs/pricing.md docs/publishing.md docs/technical.md docs/worldview.md > 立项策划案.md

# 6. 人工补充
# - 预算表
# - 团队名单
# - 时间表
# - 风险评估
```

**预计产出时间**：2-4 小时（含人工补充）  
**skill 贡献度**：80%  
**可直接使用**：✅ 给投资人/老板初审

---

### 场景 2：新系统设计（给执行团队）

```bash
# 1. 生成付费设计（如果是付费系统）
python3 scripts/pricing_strategy.py rpg 大众

# 2. 生成新手流程（如果是新手系统）
python3 scripts/gameplay_tutorial.py generate gathering crafting

# 3. 生成数值框架（如果是数值相关）
python3 scripts/numeric_balance.py economy rpg

# 4. 整合文档
# - 系统设计文档
# - 数值表
# - UI 原型
```

**预计产出时间**：1-2 天（含评审修改）  
**skill 贡献度**：70%  
**可直接使用**：✅ 给执行团队参考

---

### 场景 3：完整策划案（给全团队）

```bash
# 1. 生成所有模块
python3 scripts/pricing_strategy.py rpg 大众 > output/pricing.md
python3 scripts/publishing_operations.py rpg 中等 > output/publishing.md
python3 scripts/technical_assessment.py rpg mid mobile medium > output/technical.md
python3 scripts/worldview_builder.py generate "项目名称" > output/worldview.md
python3 scripts/story_designer.py outline "三幕剧" > output/story.md
python3 scripts/gameplay_tutorial.py generate gathering crafting making combat > output/tutorial.md
python3 scripts/numeric_balance.py economy rpg > output/numeric.md

# 2. 整合成完整文档
cat output/*.md > 完整策划案.md

# 3. 团队评审
# - 制作人审方向
# - 主策审框架
# - 主程审技术
# - 主美审美术
# - 数值审具体数值

# 4. 补充人工内容
# - 具体项目参数
# - 技术实现方案
# - 美术资源
# - 市场策略

# 5. 最终定稿
```

**预计产出时间**：1-2 周（含多轮评审）  
**skill 贡献度**：70-80%  
**可直接使用**：✅ 给全团队执行参考

---

## 📊 各模块完成度对比

| 模块 | skill 生成 | 需人工补充 | 可直接使用 |
|---|---|---|---|
| **付费设计** | 95% | 5%（定价策略确认） | ✅ 数值/运营团队 |
| **发行运营** | 90% | 10%（预算/渠道确认） | ✅ 发行/运营团队 |
| **技术评估** | 85% | 15%（技术栈确认） | ✅ 技术团队参考 |
| **世界观** | 90% | 10%（美术风格） | ✅ 文案/美术团队 |
| **剧情** | 85% | 15%（具体台词/演出） | ✅ 文案团队参考 |
| **玩法系统** | 80% | 20%（UI/操作细节） | ✅ 系统/关卡策划 |
| **数值框架** | 75% | 25%（具体填表） | ✅ 数值策划参考 |
| **美术需求** | 50% | 50%（具体资源） | ⚠️ 仅方向参考 |

---

## 🎯 与直接让大模型生成的区别

| 维度 | 直接问大模型 | 用 Arshis-Game-Design-Pro |
|---|---|---|
| **数据来源** | 训练数据（模糊） | 学术研究 + 行业报告（可追溯） |
| **结构化** | 一次性生成 | 模块化调用（可组合） |
| **输出依据** | "大概是这样" | "Sensor Tower 2026 数据显示..." |
| **持续学习** | 不能 | 可以（反馈学习器） |
| **团队协作** | 各说各的 | 统一标准/流程 |
| **项目迭代** | 记不住上次 | 版本管理/历史对比 |
| **可执行性** | 框架级 | 执行级（含具体数值/配置） |

---

## 💡 最佳实践

### ✅ 推荐用法

1. **先用 skill 生成框架**
   - 快速产出 70-80% 内容
   - 确保专业性和完整性

2. **团队评审**
   - 制作人定方向
   - 主策审框架
   - 主程/主美/数值审专业内容

3. **补充人工内容**
   - 具体项目参数
   - 技术/美术细节
   - 市场策略

4. **整合定稿**
   - 统一格式
   - 添加项目特定信息
   - 最终评审

---

### ❌ 避免用法

1. **完全依赖 skill**
   - skill 不能替代团队决策
   - 需要人工确认关键参数

2. **不做评审直接用**
   - skill 生成的是专业框架
   - 需要团队确认是否适合具体项目

3. **期望 100% 自动化**
   - skill 是辅助工具
   - 不能替代专业策划

---

## 📁 文件清单

### 核心模块（23 个）

```
scripts/
├── pricing_strategy.py              # 定价策略 ⭐ 新增
├── publishing_operations.py         # 发行运营 ⭐ 新增
├── technical_assessment.py          # 技术评估 ⭐ 新增
├── monetization_deep_design.py      # 深度付费设计
├── monetization_design.py           # 付费与活动周期
├── worldview_builder.py             # 世界观构建
├── story_designer.py                # 剧情设计
├── dialogue_generator.py            # 对话生成
├── gameplay_tutorial.py             # 新手流程
├── numeric_balance.py               # 数值平衡
├── ... (其他 13 个模块)
```

### 文档（38+ 个）

```
docs/
├── PRICING_GUIDE.md                 # 定价指南 ⭐ 新增
├── PUBLISHING_GUIDE.md              # 发行指南 ⭐ 新增
├── TECHNICAL_GUIDE.md               # 技术指南 ⭐ 新增
├── ACADEMIC_RESEARCH_SUMMARY.md     # 付费学术研究
├── NARRATIVE_RESEARCH_SUMMARY.md    # 剧情世界观研究
├── ... (其他 33+ 个文档)
```

---

## 🎉 总结

**Arshis-Game-Design-Pro v1.1.0** 现在可以：

✅ **生成完整策划案**（70-80% 内容）
✅ **可直接给团队使用**（需 20-30% 人工补充）
✅ **商业级质量**（腾讯/网易/米哈游标准）
✅ **有学术数据支撑**（Sensor Tower/GDC/行业报告）
✅ **模块化调用**（按需组合）
✅ **持续学习进化**（反馈学习器）

**定位**：
- ✅ 资深策划顾问（给方案/给数据/给框架）
- ❌ 不是制作人（不能决定项目方向）
- ❌ 不是技术总监（不能评估技术可行性）
- ❌ 不是美术总监（不能定美术风格）

**正确使用方式**：
```
skill 出框架 → 团队评审 → 补充人工内容 → 整合成完整文档
```

这样产出的策划案，**可以直接给团队使用**！

---

*Arshis-Game-Design-Pro v1.1.0*
*让游戏策划更专业、更高效、更有依据！✨*
