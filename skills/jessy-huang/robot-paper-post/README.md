# Robot Paper Post

机器人论文深度推文撰写技能包，为"Mbot具身智能实验室"打造专业级技术内容生产工具。

## 快速安装

```bash
npx clawhub@latest install robot-paper-post
```

**ClawHub 地址**: https://clawhub.ai/skills/robot-paper-post

**GitHub 地址**: https://github.com/Jessy-Huang/robot-paper-post

## 功能概述

本 Skill 能够将机器人/具身智能领域的学术论文转化为结构化、硬核且易读的技术推文，具备以下核心能力：

| 能力 | 描述 |
|------|------|
| 多源检索 | 自动搜索论文原文、GitHub 代码、项目主页、演示视频 |
| 核心拆解 | 提取 SOTA 指标、创新架构、硬件配置 |
| 技术溯源 | 识别研究团队，梳理技术演进脉络 |
| 深度撰写 | 生成符合公众号风格的专业技术推文 |
| **自动截图** | 使用 Playwright 自动采集论文/项目主页图片并插入推文 |

## 使用方法

### 触发方式

向智能体提供以下任意信息即可触发：

```
请帮我为这篇论文撰写推文：[论文标题]
```

或

```
请分析这篇论文并生成技术文章：[Arxiv ID]
```

### 输出结构

生成的推文包含以下模块：

1. **标题**（3 选 1）：硬核、有信息量、带节奏感
2. **导语**：极客感十足，点出"破坏力"
3. **硬核科普**：术语通俗化解释，200 字以内
4. **核心突破**：痛点 → 方案 → 效果的完整拆解
5. **实验表现**：泛化能力、鲁棒性测试、视频演示
6. **技术溯源**：团队脉络、技术演进对比
7. **资源直达**：论文、代码、项目主页链接

## 目录结构

```
robot-paper-post/
├── SKILL.md                         # 主入口：工作流程与风格指南
├── README.md                        # 项目说明文档
├── package.json                     # Node.js 依赖配置（含 Playwright）
├── references/
│   ├── paper-structure.md           # 推文结构详解
│   ├── tech-terms-glossary.md       # 机器人技术术语库
│   ├── research-teams.md            # 主流研究团队索引
│   └── classic-papers.md            # 经典论文索引
├── assets/
│   └── post-template.md             # 推文生成模板
└── scripts/
    └── capture_imgs.js              # 论文图片自动采集脚本
```

## 截图采集功能（新增 v1.2）

### 功能说明

新增的截图功能可以自动从 arXiv 论文页面和项目主页采集图片，无需手动截图。

### 安装依赖

```bash
npm install
npx playwright install chromium
```

### 使用方法

```bash
# 基本用法（使用默认 arXiv ID）
node scripts/capture_imgs.js 2604.00202

# 或在 Node.js 代码中调用
const { capturePaperFigures } = require('./scripts/capture_imgs.js');
await capturePaperFigures('2604.00202');
```

### 输出

采集的图片将保存在 `paper_imgs/` 目录：
- `arxiv_fig_1.png` - Figure 1
- `arxiv_fig_2.png` - Figure 2
- ...以此类推
- `10_arxiv_html.png` - arXiv 论文页面概览
- `11_project_page.png` - 项目主页截图（如有）

### 在推文中使用

1. 将采集的图片复制到推文同目录
2. 在推文中使用相对路径引用：

```markdown
![Figure 1](arxiv_fig_1.png)
```

## 资源说明

### references/paper-structure.md

推文结构的标准规范，包含：
- 标题生成模板（3 种风格）
- 导语写法（数据冲击型、范式突破型、场景代入型）
- 术语科普格式
- 核心突破结构
- 实验表现描述要点
- 技术溯源框架
- 资源列表格式

### references/tech-terms-glossary.md

收录 9 个机器人领域核心术语的通俗化解释：
- Action Chunking（动作分块）
- Diffusion Policy（扩散策略）
- VLA（视觉-语言-动作模型）
- Flow Matching（流匹配）
- Imitation Learning（模仿学习）
- 世界模型
- 具身智能
- RT 系列
- ACT

### references/research-teams.md

收录 7 个主流机器人研究团队的研究脉络：
- Google DeepMind
- Stanford Vision and Learning Lab
- UC Berkeley
- Physical Intelligence (Pi Team)
- Tesla Optimus
- MIT CSAIL
- CMU Robotics Institute

### references/classic-papers.md

收录 20+ 篇经典论文，按类别组织：
- 模仿学习：ACT、ALOHA、Diffusion Policy
- VLA 模型：RT-1、RT-2、RT-X、OpenVLA、π0
- 扩散策略：3D Diffusion Policy、IDP3
- 世界模型：Dreamer、Dreamer V3、DayDreamer
- 强化学习：Decision Transformer、Gato、Q-Transformer
- 操作与抓取：CLIPort、AnyGrasp、DexGraspNet

### assets/post-template.md

可直接填充的推文模板，包含完整的结构和占位符。

## 风格规范

### 深度优先

不仅写"是什么"，更要写：
- "为什么这么做"（设计动机）
- "它的局限性"（诚实分析）

### 视觉描述

在提示插图时，描述必须具体：

```
错误："插入一张实验对比图"

正确："插入一张展示机器人在不同光照条件下（正常光照/暗光/强光）抓取透明物体的成功率对比柱状图"
```

### 术语科普

必须通俗易懂，目标读者：大二相关专业学生

```
错误：堆砌公式和专业术语

正确：使用类比和直观解释
```

## 约束条件

1. **数据准确**：所有实验指标必须与原文一致
2. **代码敏感**：代码未公开时标注"Code Coming Soon"
3. **引用规范**：提及他人工作时准确标注出处

## 示例输出

```markdown
## 标题

DeepMind 新作：突破机器人泛化瓶颈，RT-X 开源代码已收录

## 导语

在跨任务泛化能力上，RT-X 将未见任务成功率从 32% 提升到 67%——我们终于看到了机器人"举一反三"能力的曙光。

## 硬核科普

**VLA（Vision-Language-Action）**
一句话定义：将视觉理解、语言指令、动作执行统一在一个模型中的架构。
类比说明：就像你听到"帮我把桌上的苹果拿来"后，眼睛找到苹果、大脑规划路线、手脚协同完成抓取。

## 核心突破：RT-X 深度拆解

### 痛点
之前的方法（如 RT-1）只能在单一机器人上训练，无法利用跨平台数据...

### 方案
RT-X 构建了百万级跨机构机器人数据集...

[此处插入论文 Figure 1：模型总体架构图]

### 效果
- 未见任务成功率：67%（RT-1：32%，提升 109%）
- 跨机器人迁移：支持 22 种机器人平台

## 资源直达

- 论文地址：https://arxiv.org/abs/2310.08864
- 项目主页：https://robotics-transformer-x.github.io/
- 代码仓库：https://github.com/google-deepmind/rt_x

> 关注 Mbot 具身智能实验室，第一时间追踪机器人前沿干货。
```

## 更新日志

- **v1.2**：新增自动截图采集功能
  - 添加 Playwright 截图脚本 `scripts/capture_imgs.js`
  - 添加 `package.json` 依赖配置
  - 更新 SKILL.md 工作流程说明
- **v1.1**：新增经典论文索引（20+ 篇）
- **v1.0**：初始版本，包含核心工作流程和参考资源

## 许可证

本项目采用 [MIT License](LICENSE) 开源协议。
