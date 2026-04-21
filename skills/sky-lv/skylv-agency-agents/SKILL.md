---
name: agency-agents
slug: skylv-agency-agents
version: 1.0.2
description: "193 AI Expert Agents for OpenClaw. Engineering, Design, Marketing, Product, and China Market specialists. Triggers: agency agents, AI experts, expert roles, ai specialists, 193 agents."
author: SKY-lv
license: MIT
tags: [agency-agents, experts, agents, openclaw, ai-roles]
keywords: openclaw, skill, automation, ai-agent
triggers: agency agents
---

# Agency Agents — 193 个 AI 专家角色库

## 功能说明

为 OpenClaw 引入 193 个即插即用的 AI 专家角色，覆盖工程、设计、营销、产品、游戏、安全、金融等 18 个部门。每个智能体都有独立的人设、专业流程和可交付成果。

## 智能体分类

### 🛠️ Engineering (45 个)

| 智能体 | 功能 | 触发词 |
|--------|------|--------|
| Security Engineer | 按 OWASP Top 10 审查代码 | 安全审查、代码审计 |
| DevOps Engineer | CI/CD、Docker、K8s 配置 | 部署、CI/CD、容器化 |
| Frontend Expert | React/Vue/Angular 最佳实践 | 前端、React、组件 |
| Backend Expert | API 设计、数据库优化 | 后端、API、数据库 |
| ML Engineer | 机器学习模型训练部署 | 机器学习、模型、训练 |

### 🎨 Design (18 个)

| 智能体 | 功能 | 触发词 |
|--------|------|--------|
| UX Designer | 用户体验设计、用户研究 | UX、用户体验、交互设计 |
| UI Designer | 视觉设计、设计规范 | UI、视觉、设计系统 |
| Brand Strategist | 品牌定位、视觉识别 | 品牌、logo、vi 设计 |

### 📈 Marketing (25 个)

| 智能体 | 功能 | 触发词 |
|--------|------|--------|
| SEO Specialist | SEO 优化、关键词研究 | SEO、搜索排名、关键词 |
| Content Strategist | 内容策略、编辑日历 | 内容策略、选题、日历 |
| Social Media Manager | 社交媒体运营、活动策划 | 社交媒体、活动、运营 |

### 🇨🇳 China Market (46 个原创)

| 智能体 | 功能 | 触发词 |
|--------|------|--------|
| 小红书运营专家 | 种草笔记、达人合作 | 小红书、种草、笔记 |
| 抖音投放专家 | 信息流广告、DOU+ 投放 | 抖音、投放、信息流 |
| 微信生态专家 | 公众号、小程序、视频号 | 微信、公众号、小程序 |
| B 站 UP 主顾问 | 视频策划、粉丝运营 | B 站、视频、up 主 |
| 跨境电商专家 | 亚马逊、Shopee、独立站 | 跨境电商、亚马逊、shopify |
| 飞书协作专家 | 飞书多维表格、自动化 | 飞书、协作、多维表格 |
| 钉钉开发专家 | 钉钉小程序、机器人 | 钉钉、小程序、机器人 |

### 🎮 Gaming (12 个)

| 智能体 | 功能 | 触发词 |
|--------|------|--------|
| Game Designer | 游戏机制、关卡设计 | 游戏设计、关卡、机制 |
| Unity Developer | Unity C# 开发、优化 | Unity、C#、游戏开发 |
| Unreal Developer | Unreal Engine 蓝图、C++ | Unreal、UE5、蓝图 |

### 💼 Business (22 个)

| 智能体 | 功能 | 触发词 |
|--------|------|--------|
| Product Manager | 产品规划、需求文档 | 产品、PRD、需求 |
| Growth Hacker | 增长策略、A/B 测试 | 增长、a/b 测试、转化 |
| Data Analyst | 数据分析、可视化 | 数据分析、图表、洞察 |
| Financial Analyst | 财务分析、投资评估 | 财务、投资、估值 |

## 使用方法

### 1. 安装 agency-agents

```bash
# 克隆仓库
git clone https://github.com/jnMetaCode/agency-agents-zh.git

# 安装到 OpenClaw
cd agency-agents-zh
./scripts/install.sh --tool openclaw
```

### 2. 激活智能体

```
用户：激活安全工程师，审查这段代码
```

### 3. 多智能体协作

```
用户：创建一个新功能，需要产品经理、设计师、开发工程师协作
```

输出：
- 产品经理：需求分析和 PRD
- 设计师：UI/UX 设计方案
- 工程师：技术实现方案

## 智能体文件格式

每个智能体包含：

```markdown
# 智能体名称

## 身份定义
- 角色：[明确的专业身份]
- 经验：[年限和背景]
- 专长：[核心技能领域]

## 关键规则
1. [必须遵守的原则]
2. [工作流程要求]
3. [交付物标准]

## 工作流程
1. [第一步：输入分析]
2. [第二步：专业处理]
3. [第三步：输出交付]

## 交付物
- [具体的输出格式和内容要求]
```

## 与普通提示词的区别

| 普通提示词 | Agency Agents |
|-----------|--------------|
| "你是一个专家" | 明确定义专家**怎么思考、怎么做事** |
| 通用建议 | 专业流程和可交付成果 |
| 单次使用 | 可重复激活的持久角色 |
| 孤立工作 | 支持多智能体协作 |

## 多智能体编排

使用 Agency Orchestrator 定义工作流：

```yaml
# workflow.yaml
agents:
  - role: product-manager
    output: prd
  
  - role: ux-designer
    input: prd
    output: wireframes
  
  - role: frontend-developer
    input: [prd, wireframes]
    output: implementation

execution:
  mode: sequential # 或 parallel
  model: claude-sonnet-4
```

```bash
npx agency-orchestrator run workflow.yaml --input "创建一个电商首页"
```

## 支持的 AI 工具

| 工具 | 支持状态 | 安装命令 |
|------|---------|---------|
| OpenClaw ⭐ | ✅ 原生支持 | `./install.sh --tool openclaw` |
| Claude Code | ✅ 原生支持 | `./install.sh --tool claude-code` |
| GitHub Copilot | ✅ 原生支持 | `./install.sh --tool copilot` |
| Cursor | ✅ 支持 | `./install.sh --tool cursor` |
| Hermes Agent | ✅ 支持 | `./install.sh --tool hermes` |
| More... | 12 种工具 | 见安装脚本 |

## 热门智能体 TOP 10

1. **Security Engineer** - 代码安全审查
2. **Product Manager** - 产品规划和 PRD
3. **UX Designer** - 用户体验设计
4. **Frontend Expert** - React/Vue开发
5. **DevOps Engineer** - CI/CD和容器化
6. **SEO Specialist** - 搜索引擎优化
7. **Content Strategist** - 内容策略
8. **Data Analyst** - 数据分析
9. **Growth Hacker** - 增长黑客
10. **小红书运营专家** - 小红书种草

## 中国市场特色智能体

### 平台运营类
- 小红书运营专家
- 抖音投放专家
- 微信生态专家
- B 站 UP 主顾问
- 快手运营专家
- 知乎内容专家

### 跨境电商类
- 亚马逊运营专家
- Shopee 运营专家
- 独立站运营专家
- TikTok Shop 专家

### 本地化类
- 政务 ToG 专家
- 医疗合规专家
- 教育行业专家
- 金融行业专家

## 相关文件

- [agency-agents-zh GitHub](https://github.com/jnMetaCode/agency-agents-zh)
- [上游英文版](https://github.com/msitarzewski/agency-agents)
- [Agency Orchestrator](https://github.com/jnMetaCode/agency-orchestrator)
- [OpenClaw 文档](https://docs.openclaw.ai)

## 触发词

- 自动：检测智能体、专家、角色相关关键词
- 手动：/agency-agents, /experts, /agents
- 短语：激活专家、用智能体、多智能体协作

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
