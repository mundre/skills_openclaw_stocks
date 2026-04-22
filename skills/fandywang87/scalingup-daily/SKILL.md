---
name: scalingup-daily
description: "搜广推领域模型 Scaling Up 日报生成技能。每日自动检索6类优先级信息源（ArXiv论文、微信公众号、知乎、技术博客、GitHub Trending、行业会议），生成结构化日报并写入IMA知识库。触发词：搜广推日报、ScalingUp日报、推荐系统日报、推荐Scaling Law日报、生成式推荐日报、TokenMixer日报、搜广推ScalingUp。"
description_zh: "搜广推领域模型 Scaling Up 日报生成（6类信息源检索 + IMA知识库写入）"
description_en: "Search/Rec/Ads Scaling Up daily report generator with 6 source types and IMA integration"
version: 1.0.0
allowed-tools: Bash,Read,web_search,use_skill
metadata:
  clawdbot:
    emoji: "📊"
    requires:
      bins:
        - node
        - python3
---

# 搜广推领域模型 Scaling Up 日报生成技能

## 适用场景

- 用户说"生成今天的搜广推日报"或"跑一下 ScalingUp 日报"
- 自动化任务每日 08:00 触发
- 需要系统性追踪搜广推领域最新论文、技术文章、开源项目动态

## 信息源（6类优先级）

### 优先级1：ArXiv论文 - 最新学术论文
使用 `web_search` 搜索以下关键词（最近7天的新论文）：
- `"arxiv recommendation system scaling law {year}"`
- `"arxiv CTR prediction transformer {year}"`
- `"arxiv generative recommendation advertising {year}"`
- `"arxiv sequential recommendation token mixer {year}"`
- `"arxiv unified modeling search recommendation {year}"`
- `"arxiv recommendation foundation model {year}"`
- `"arxiv scaling law recommendation {year}"`
- `"arxiv ads ranking model {year}"`
每个搜索取前5条结果。
对每篇论文记录：标题、arXiv ID、作者/机构、核心贡献、链接。

### 优先级2：微信公众号 - 国内技术文章
使用 `wechat-article-search` skill 搜索以下关键词（最近7天）：
- `"推荐系统 Scaling Law"`
- `"搜广推 大模型"`
- `"序列建模 推荐"`
- `"生成式推荐"`
- `"TokenMixer 排序"`
每个关键词搜索3-5条。
对每篇文章记录：标题、公众号名、链接、发布日期、核心内容。

**微信搜索命令格式**：
```bash
cd {skill_dir} && NODE_PATH={skill_dir}/node_modules {node_path} scripts/search_wechat.js "关键词" -n 5
```
其中 `{skill_dir}` 为本 skill 的安装路径，`{node_path}` 为 Node.js 可执行文件路径。

### 优先级3：知乎 - 深度技术分析
使用 `web_search` 搜索以下关键词（最近7天）：
- `"site:zhuanlan.zhihu.com 推荐系统 Scaling Law {year}"`
- `"site:zhuanlan.zhihu.com TokenMixer 推荐 {year}"`
- `"site:zhuanlan.zhihu.com 生成式推荐 广告 {year}"`
- `"site:zhuanlan.zhihu.com 搜广推 序列建模 {year}"`
- `"site:zhuanlan.zhihu.com OneRec OneRanker GR4AD"`
- `"site:zhuanlan.zhihu.com 推荐系统 大模型 {year}"`
- `"site:zhuanlan.zhihu.com UniMixer 推荐 {year}"`
- `"site:zhuanlan.zhihu.com 推荐系统 MoE 稀疏 {year}"`
每个搜索取前5条结果。
对每篇文章记录：标题、作者、链接、发布日期、核心观点。

### 优先级4：技术博客 - 大厂团队博客
使用 `web_search` 搜索以下关键词：
- `"site:ai.meta.com blog recommendation {year}"`
- `"site:research.google blog recommendation {year}"`
- `"美团技术团队 推荐 {year}"`
- `"字节跳动技术博客 推荐 {year}"`
- `"阿里巴巴技术 推荐系统 {year}"`
- `"快手技术博客 生成式推荐 {year}"`
- `"腾讯技术 推荐系统 {year}"`
对每篇文章记录：标题、发布平台/团队、链接、发布日期、主要内容。

### 优先级5：GitHub Trending - 热门开源项目
使用 `web_search` 搜索以下关键词：
- `"GitHub recommendation system trending {year} stars"`
- `"GitHub awesome recommendation system {year}"`
- `"GitHub bytedance recommendation model open source"`
- `"GitHub Meta HSTU recommendation"`
- `"GitHub Kuaishou OneRec OpenOneRec"`
- `"github.com/trending 机器学习 推荐系统"`
对每个项目记录：项目名称（含owner）、GitHub链接、Star数、简要描述、最近更新时间。

### 优先级6：行业会议 - KDD/WWW/ICML/NeurIPS/SIGIR等
使用 `web_search` 搜索以下关键词：
- `"KDD {year} accepted papers recommendation"`
- `"WWW {year} recommendation system paper"`
- `"ICML {year} recommendation transformer paper"`
- `"NeurIPS {year} recommendation system paper accepted"`
- `"SIGIR {year} recommendation scaling sequential"`
- `"RecSys {year} accepted papers call"`
- `"WSDM {year} recommendation paper"`
- `"AAAI {year} recommendation system paper"`
对每篇论文记录：标题、作者/机构、会议名称和年份、arXiv链接、核心贡献。

## 重点关注的技术方向

- Scaling Law 在搜广推领域的验证与落地（Wukong/SUAN/EST/TokenMixer-Large路线）
- TokenMixer架构演进（RankMixer -> TokenMixer-Large -> UniMixer）
- 生成式端到端统一建模（OneRec/OneRanker/GR4AD）
- 稀疏注意力与MoE高效扩展（ULTRA-HSTU/LightSUAN）
- 多行为序列推荐与基础模型

## 已知核心论文（去重用，不需要重复列出）

参考 `references/known_papers.md` 文件。

## 日报生成格式

1. 标题：搜广推领域模型 Scaling Up 日报 | {当天日期}
2. 趋势概览：简要总结当日最重要的2-3个动态
3. 按信息源优先级分章节展示内容
4. 每个条目必须包含：标题/论文名、来源、链接、核心要点
5. 论文条目须标注 arXiv 原始链接
6. 文末附「引文索引」，按平台分类整理所有链接
7. 在每个章节末尾标注当日该源检索到的条目数量

日报模板参考 `templates/daily_report_template.md`。

## IMA 知识库写入

日报生成后，使用 `ima-skills` skill 将内容写入 IMA 知识库。

**IMA 知识库配置**（需在安装时设置）：
- 知识库名称：龙虾-模型ScalingUp
- 知识库 ID：需要在新账号中创建后填入

**上传步骤**：
1. 使用 `ima-skills` skill 的知识库上传功能
2. 将生成的日报 Markdown 文件上传到指定知识库
3. 确认上传成功

**备选方案**（如 ima-skills 不可用）：
```bash
python3 {skill_dir}/scripts/ima_upload.py --file {report_file} --kb-id {kb_id} --title {report_title}
```

## 输出文件

将日报保存为：`{workspace_dir}/搜广推ScalingUp日报_{当天日期}.md`

## 自动化任务配置

创建每日 08:00 执行的自动化任务：
- 任务名称：搜广推ScalingUp日报生成
- 执行时间：每天 08:00
- 工作目录：用户的 WorkBuddy workspace

## 依赖说明

### 前置 Skill
- `wechat-article-search`：微信公众号文章搜索（需先安装）
- `ima-skills`：IMA 知识库操作（需先安装）

### 运行时依赖
- Node.js >= 18（微信搜索脚本）
- Python 3（IMA 上传脚本）
- npm 包：cheerio（微信搜索脚本依赖）

### IMA API 凭证
需要配置 IMA API 凭证文件：
- `~/.config/ima/client_id`
- `~/.config/ima/api_key`

## 安装后首次运行检查清单

1. 确认 `wechat-article-search` skill 已安装
2. 确认 `ima-skills` skill 已安装
3. 运行 `npm install` 安装 cheerio 依赖
4. 确认 IMA API 凭证已配置
5. 创建 IMA 知识库并记录 KB ID
6. 配置自动化任务
7. 执行一次测试运行验证全流程
