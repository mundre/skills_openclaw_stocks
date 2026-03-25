---
name: junli-ai-novel
description: 君黎AI写作 - 用于长篇连载小说创作、续写和修订的 skill。适合 3000-5000 字/章的网文或长篇项目，包含立项问答、世界观与人物规划、三层记忆维护、逐章创作、自检与定向返修。
---

# 君黎AI写作

## 适用任务

- 从零开始规划一部长篇小说
- 在已有项目上继续连载或续写下一章
- 对单章进行扩写、重写、润色或质量检查
- 在长会话后恢复上下文，避免人物、伏笔、时间线断裂

## 核心原则

1. 先读档，再下笔。
2. 大纲、人物、法则优先于临场发挥。
3. 先定场景任务，再写正文。
4. 每章必须推进剧情，不能只注水。
5. 写完必须检查，并且按问题类型定向返修。

## 外部材料吸收原则

如果用户后续提供创作经验、行业观察、访谈摘录或方法论材料：

1. 先提炼稳定原则，再决定是否吸收。
2. 优先吸收可操作、可复用、可验证的内容。
3. 时效性强、立场化、标签化的判断，不直接写进 skill。
4. 吸收时默认转成三类资产：触发条件、写前问题、写后检查项。
5. 只适合单个项目的内容，优先写进项目文档，不污染通用规则。

## 标准流程

### 阶段 1：5 问立项

仅在“新项目”或“设定不完整”时执行。直接用自然语言向用户补齐以下信息，不依赖任何特定工具名。

1. 题材与风格
2. 主角结构（单主角、双主角、群像）
3. 主角核心性格
4. 核心冲突
5. 预计章节规模

如果用户已经给出其中一部分，只问缺失项，不重复盘问。

### 阶段 2：规划与建档

新项目需要建立以下文件：

- `docs/大纲.md`
- `docs/冲突设计.md`
- `docs/世界观.md`
- `docs/法则.md`
- `characters/人物档案.md`
- `plot/伏笔记录.md`
- `plot/时间线.md`
- `task_log.md`

如果用户选择的是双主角、群像、多线或多视角模式，额外建立：

- `docs/群像主题拆分.md`
- `plot/POV轮转表.md`

并读取 `references/ensemble-writing.md` 作为专项规划规则。

如果用户是从零立项、觉得故事“没冲突”、或需要重做世界观土壤，额外读取：

- `references/conflict-design.md`

如果用户需要从零构建世界观、觉得设定像清单、或世界运转逻辑薄弱，额外读取：

- `references/worldbuilding-logic.md`

如果用户需要解决“设定如何自然写进正文”“世界观像资料堆砌”“读者不沉浸”等问题，额外读取：

- `references/worldbuilding-presentation.md`

如果用户明确写的是网文、升级流、修仙、系统、外挂、奇遇、金手指，或主角成长逻辑明显需要特殊筹码，额外读取：

- `references/golden-finger-design.md`

如果用户只有一个脑洞/设定点子，担心故事写不长、三五万字卡住，或需要把点子扩成百万字结构，额外读取：

- `references/idea-incubation.md`

如果用户要写休整章、关系升温、世界烟火气、过渡章节，或担心日常写成流水账，额外读取：

- `references/daily-narrative.md`

如果用户明确追求文学性、严肃文学、魔幻现实、象征性开篇、时间迷宫式结构，额外读取：

- `references/literary-opening.md`

如果用户明确要写倒叙、插叙、碎片叙事、多线并进、环形结构、意识流，或故事天然需要打乱信息路径，额外读取：

- `references/nonlinear-narrative.md`

如果用户要求提升悬念、追读、留存、钩子质量，或题材本身高度依赖信息缺口，额外读取：

- `references/suspense-design.md`

如果用户明确写的是网文、连载文、升级流、爽文、成长流，或反馈“主角太憋屈”“有深度但不好看”“追读低”“爽点不足”“虐主感过重”，额外读取：

- `references/reader-compensation.md`

先输出规划摘要，再让用户确认。确认后再进入长篇逐章创作。

### 阶段 3：逐章创作

用户确认进入正文创作后，按章节顺序推进。除非用户主动暂停、改方向，或发现设定冲突，否则不要在每一章都重复征求许可。

## 项目结构

```text
[项目目录]/
├── docs/
│   ├── 大纲.md
│   ├── 冲突设计.md
│   ├── 世界观.md
│   ├── 法则.md
│   └── 群像主题拆分.md      # 群像模式可选
├── characters/
│   ├── 人物档案.md
│   └── [角色名].md            # 可选，角色多时拆分
├── manuscript/
│   ├── 001_标题.md
│   └── ...
├── plot/
│   ├── 伏笔记录.md
│   ├── 时间线.md
│   └── POV轮转表.md         # 群像模式可选
└── task_log.md
```

约束：

- `task_log.md` 是运行记忆的主入口。
- `docs/法则.md`、`docs/世界观.md`、`characters/` 属于高优先级“宪法记忆”，后写内容不得冲突。
- `manuscript/` 只放正文，不混入说明性文档。

## 专项方法论入口

以下方法论默认不在主 skill 展开，按需读取对应 `references/`，不要一次性全读。

- 冲突设计：当故事缺冲突、冲突像硬造、需要重建冲突链时，读 `references/conflict-design.md`
- 世界观逻辑：当设定像清单、规则不稳、升级体系发虚时，读 `references/worldbuilding-logic.md`
- 世界观展现：当设定堆砌、正文不沉浸、信息倾倒明显时，读 `references/worldbuilding-presentation.md`
- 金手指设计：当题材涉及系统、外挂、奇遇、修仙升级或特殊筹码时，读 `references/golden-finger-design.md`
- 悬念机制：当追读弱、钩子弱、断点无力时，读 `references/suspense-design.md`
- 群像模式：当用户明确写群像、多主角、多线、多视角、多阵营并行时，读 `references/ensemble-writing.md`

群像模式仍需额外建立：

- `docs/群像主题拆分.md`
- `plot/POV轮转表.md`

## 三层记忆

这个 skill 采用显式三层记忆，不靠模糊回忆：

- L1 会话工作记忆：当前章节目标、场景 Beats、开头钩子、上章悬念。场景结束、重大转折或引入新角色后及时写回文件。
- L2 项目运行记忆：`task_log.md`、`docs/大纲.md`、`plot/伏笔记录.md`、`plot/时间线.md`，用于维护最近剧情、进度、活跃伏笔和时间线。
- L3 宪法记忆：`docs/世界观.md`、`docs/法则.md`、`characters/人物档案.md`、`characters/*.md`，优先级高于 L2 和 L1，新内容不得与其硬冲突。

## 记忆唤醒与恢复

以下情况必须先恢复记忆，再继续创作：

- 用户说“继续创作”“恢复上下文”“唤醒记忆”“上次写到哪了”
- 新开对话继续旧项目
- 长会话后准备进入下一章

恢复顺序：

1. `task_log.md`
2. `docs/大纲.md`
3. `plot/伏笔记录.md` 与 `plot/时间线.md`
4. 相关角色档案与设定
5. 上一章正文和结尾钩子

恢复输出至少包含：当前创作阶段、最近两到三章摘要、主角当前状态、活跃伏笔、下一章目标。

## 单章创作流程

详细版见 `references/chapter-workflow.md`。主 skill 只保留硬性流程：

1. 写前先读 `task_log.md`、`docs/大纲.md`、上一章正文、相关角色设定、伏笔与时间线，并把目标章节标为“进行中”。
2. 正文前先拆 3-5 个场景，至少写清地点、人物、核心事件、情绪走向和暗线。
3. 正文默认目标 3000-5000 字，开头前 20% 必须有钩子；每章至少推进一条线、回应一个旧悬念、留下一个新钩子。
4. 主角受挫时，正文内或紧邻章节必须给出补偿基础，不能长期纯受气拖拽。
5. 写完后用 `references/quality-checklist.md` 和 `references/consistency.md` 检查，有问题优先定向返修，不全文推倒重来。

按需读取以下资料：

- 章节结构与开头：`references/chapter-guide.md`
- 章节模板：`references/chapter-template.md`
- 对话：`references/dialogue-writing.md`
- 扩写：`references/content-expansion.md`
- 日常叙事：`references/daily-narrative.md`
- 钩子：`references/hook-techniques.md`
- 非线性结构：`references/nonlinear-narrative.md`

## 推荐检查脚本

如果脚本存在，优先在章节完成后执行：

```bash
python3 scripts/check_chapter_wordcount.py manuscript/001_标题.md
python3 scripts/check_emotion_curve.py manuscript/001_标题.md
python3 scripts/extract_thrills.py manuscript/001_标题.md
```

脚本用途：

- `check_chapter_wordcount.py`：检查字数下限
- `check_emotion_curve.py`：检查章节内部和章节之间的情绪跳跃
- `extract_thrills.py`：检查爽点、毒点与密度
- `new_project.py`：初始化项目目录
- `update_progress.py`：更新 `task_log.md` 和伏笔记录

脚本结果不是终审结论，只是辅助证据。最终以文本质量和前后文一致性为准。

## 创作规则

### 强规则

- 展示，不要空讲
- 冲突驱动剧情
- 人物不能 OOC
- 每章结尾必须有钩子
- 每个场景都要有任务
- 不能靠机械降神收尾
- 不能制造低风险虚假悬念

### 语言规则

- 少用空泛感叹和总结性感悟
- 少用 AI 高发词和空心华丽词
- 减少“他感到很”“她觉得”一类抽象心理
- 长短句交替，避免整段同速推进
- 尽量用动作、反应、对话承载情绪

### 设定规则

- `docs/法则.md` 与 `docs/世界观.md` 是最高宪法
- 新能力、新规则、新关键道具出现前要有铺垫
- 如果角色做出反常行为，必须给出足够原因或把它写成成长/崩塌节点

## 大纲与人物

立项或重构时，优先使用这些文件：

- `references/outline-template.md`
- `references/character-template.md`
- `references/character-building.md`
- `references/plot-structures.md`

## 继续创作时的默认行为

如果用户说“继续写”“下一章”“接着来”，默认执行：

1. 读档恢复
2. 给出一句到几句的当前状态摘要
3. 写出下一章的简短场景规划
4. 直接进入正文
5. 写后更新记忆文件

## 异常处理

### 项目为空

如果项目里没有正文和进度记录：

- 不要假装记得内容
- 直接回到“5 问立项”或“规划与建档”

### 记忆文件缺失

如果 `task_log.md`、`docs/大纲.md`、`plot/伏笔记录.md` 等文件缺失：

1. 从 `manuscript/` 已有章节重建最近进度
2. 明确告诉用户哪些记忆文件缺失
3. 优先补齐缺失文件，再继续创作

### 设定冲突

如果不同文件之间互相冲突：

1. 优先遵守最新且更高层级的明确设定
2. 在 `docs/法则.md` 或角色档案中消歧
3. 必要时先向用户确认保留哪一版

### 外部材料接入

如果用户后续继续提供创作材料：

1. 先判断它属于原则、流程、检查项还是只适用于单项目经验
2. 能转成稳定规则的，再吸收到 `SKILL.md` 或对应 `references/`
3. 只带市场情绪或时代标签的表述，改写成中性、可执行的规则后再保留
4. 如果和现有规则冲突，优先保留更稳定、更通用、更可验证的一版

## 参考资料

- `references/outline-template.md`：大纲模板
- `references/character-template.md`：人物档案模板
- `references/character-building.md`：人物塑造方法
- `references/chapter-workflow.md`：单章工作流细则
- `references/chapter-guide.md`：章节结构与开头技巧
- `references/chapter-template.md`：章节模板
- `references/consistency.md`：连贯性检查
- `references/content-expansion.md`：扩写方法
- `references/dialogue-writing.md`：对话写法
- `references/hook-techniques.md`：悬念钩子
- `references/plot-structures.md`：常见情节结构
- `references/quality-checklist.md`：最终质检清单
- `references/ensemble-writing.md`：群像写作专项规则
- `references/conflict-design.md`：冲突设计专项规则
- `references/worldbuilding-logic.md`：世界观逻辑专项规则
- `references/worldbuilding-presentation.md`：世界观展现专项规则
- `references/golden-finger-design.md`：金手指设计专项规则
- `references/idea-incubation.md`：脑洞孵化与长篇扩展专项规则
- `references/daily-narrative.md`：日常叙事专项规则
- `references/literary-opening.md`：文学性开篇专项规则
- `references/nonlinear-narrative.md`：非线性叙事专项规则
- `references/suspense-design.md`：悬念机制与质量判断
- `references/reader-compensation.md`：情绪补偿与深度包裹专项规则
