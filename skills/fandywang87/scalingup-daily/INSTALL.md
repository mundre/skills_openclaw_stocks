# 搜广推 ScalingUp 日报 Skill 安装指引

## 概述

`scalingup-daily` 是一个 WorkBuddy Skill，每日自动检索6类优先级信息源，生成搜广推领域模型 Scaling Up 日报并写入 IMA 知识库。

## 文件结构

```
scalingup-daily-skill/
├── SKILL.md                          # Skill 主描述文件（核心配置）
├── package.json                      # npm 依赖声明（cheerio）
├── scripts/
│   ├── search_wechat.js              # 微信公众号文章搜索脚本
│   └── ima_upload.py                 # IMA 知识库上传脚本
├── references/
│   └── known_papers.md               # 已知核心论文列表（去重用）
├── templates/
│   └── daily_report_template.md      # 日报模板
└── INSTALL.md                        # 本安装指引
```

## 安装步骤

### 第1步：安装前置 Skill

在新账号的 WorkBuddy 中，需要先安装两个前置 Skill：

1. **wechat-article-search** — 微信公众号文章搜索
   - 在 WorkBuddy 中搜索并安装该 Skill
   - 或从 Skill 市场安装

2. **ima-skills**（或"腾讯ima"） — IMA 知识库操作
   - 在 WorkBuddy 中搜索并安装该 Skill
   - 配置 IMA API 凭证（见下方）

### 第2步：复制 Skill 目录

将 `scalingup-daily-skill` 整个目录复制到新账号的 user-level skills 目录：

```bash
cp -r scalingup-daily-skill ~/.workbuddy/skills/
```

或者如果是项目级安装：

```bash
cp -r scalingup-daily-skill {项目目录}/.workbuddy/skills/
```

### 第3步：安装 Node.js 依赖

进入 Skill 目录安装 cheerio（微信搜索脚本的依赖）：

```bash
cd ~/.workbuddy/skills/scalingup-daily-skill
npm install
```

如果使用 WorkBuddy 管理的 Node.js 运行时：

```bash
cd ~/.workbuddy/skills/scalingup-daily-skill
PATH="~/.workbuddy/binaries/node/versions/22.12.0/bin:$PATH" npm install
```

### 第4步：配置 IMA API 凭证

创建 IMA API 凭证文件：

```bash
mkdir -p ~/.config/ima

# 写入 client_id（从 IMA 开放平台获取）
echo "你的_client_id" > ~/.config/ima/client_id

# 写入 api_key（从 IMA 开放平台获取）
echo "你的_api_key" > ~/.config/ima/api_key
```

**获取 IMA 凭证的方法**：
1. 打开 IMA 应用（腾讯文档/知识库）
2. 进入「设置」→「开放平台」或「API 管理」
3. 创建应用获取 client_id 和 api_key

### 第5步：创建 IMA 知识库

1. 打开 IMA 应用
2. 创建一个新知识库，命名为「龙虾-模型ScalingUp」（或其他你喜欢的名字）
3. 记录知识库 ID（KB ID）

知识库 ID 的获取方法：
- 在 IMA 知识库的 URL 中可以找到
- 或使用 ima_search.py 脚本搜索：
  ```bash
  python3 ~/.workbuddy/skills/scalingup-daily-skill/scripts/../../ima-skills/scripts/search_kb.py "龙虾"
  ```

**重要**：将获取到的 KB ID 记录下来，后续配置自动化任务时需要用到。

### 第6步：配置自动化任务

在 WorkBuddy 中创建自动化任务：

**方式一：通过 WorkBuddy UI 配置**

1. 打开 WorkBuddy → 自动化 → 新建任务
2. 配置如下：
   - **任务名称**：搜广推ScalingUp日报生成
   - **执行时间**：每天 08:00
   - **工作目录**：选择你的 WorkBuddy workspace
   - **Prompt**：见下方 Prompt 模板

**方式二：通过命令行配置**

在 WorkBuddy 对话中输入：

```
帮我创建一个每天早上8点执行的自动化任务，名称为"搜广推ScalingUp日报生成"，使用 scalingup-daily skill 生成日报
```

**自动化任务 Prompt 模板**：

```
你是搜广推（搜索、推荐、广告）领域的技术日报生成器。请使用 scalingup-daily skill，按6类优先级信息源系统性地检索并生成当日日报。

信息源（按优先级）：
1. ArXiv论文 → web_search
2. 微信公众号 → wechat-article-search skill
3. 知乎 → web_search site:zhuanlan.zhihu.com
4. 技术博客 → web_search
5. GitHub Trending → web_search
6. 行业会议 → web_search

日报格式要求：
- 标题：搜广推领域模型 Scaling Up 日报 | {当天日期}
- 每个条目必须含：标题、来源、链接、核心要点
- 论文条目须标注 arXiv 原始链接
- 文末附引文索引，按平台分类
- 每章节末标注该源检索到的条目数量

已知核心论文参考 scalingup-daily skill 的 references/known_papers.md。

日报生成后，使用 ima-skills skill 将内容写入 IMA 知识库「龙虾-模型ScalingUp」（kb_id: {替换为实际KB_ID}）。

输出文件：{workspace_dir}/搜广推ScalingUp日报_{当天日期}.md
```

### 第7步：验证安装

执行一次测试运行：

1. 在 WorkBuddy 对话中输入：
   ```
   使用 scalingup-daily skill 生成今天的搜广推日报
   ```

2. 检查以下项目：
   - [ ] ArXiv 论文检索正常
   - [ ] 微信公众号搜索正常
   - [ ] 知乎文章检索正常
   - [ ] 技术博客检索正常
   - [ ] GitHub 项目检索正常
   - [ ] 行业会议论文检索正常
   - [ ] 日报文件正确生成
   - [ ] IMA 知识库写入成功

3. 如果微信搜索报错，检查：
   - cheerio 是否已安装：`ls ~/.workbuddy/skills/scalingup-daily-skill/node_modules/cheerio/`
   - Node.js 路径是否正确

4. 如果 IMA 上传报错，检查：
   - 凭证文件是否存在：`ls ~/.config/ima/`
   - KB ID 是否正确
   - ima-skills skill 是否已安装

## 常见问题

### Q: 微信搜索返回空结果怎么办？
A: 搜狗微信搜索有反爬机制，偶尔会返回空结果。可以尝试：
1. 更换关键词
2. 稍后重试
3. 检查 IP 是否被临时封禁

### Q: IMA 上传失败怎么办？
A: 检查以下几点：
1. IMA API 凭证是否正确
2. KB ID 是否有效
3. 文件大小是否超过限制
4. 可以尝试使用 ima-skills skill 直接在对话中上传

### Q: 如何添加新的搜索关键词？
A: 编辑 `SKILL.md` 文件中对应信息源的搜索关键词部分。

### Q: 如何更新已知论文列表？
A: 编辑 `references/known_papers.md` 文件，按格式添加新论文。

### Q: 如何更换 IMA 知识库？
A: 更新自动化任务 Prompt 中的 kb_id 即可。

## 技术架构

```
┌──────────────────────────────────────────────┐
│          WorkBuddy 自动化任务调度              │
│          (每天 08:00 触发)                    │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│         scalingup-daily Skill                │
│         (SKILL.md 定义工作流程)               │
└──────────────────┬───────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌────────┐  ┌───────────┐  ┌──────────┐
│ web_   │  │ wechat-   │  │ ima-     │
│ search │  │ article-  │  │ skills   │
│ (6类   │  │ search    │  │ (知识库  │
│ 信息源)│  │ (微信搜索)│  │  写入)   │
└───┬────┘  └─────┬─────┘  └────┬─────┘
    │             │              │
    │    ┌────────┘              │
    ▼    ▼                       ▼
┌──────────────────┐    ┌───────────────┐
│ 日报 Markdown    │    │ IMA 知识库    │
│ (本地文件)       │    │ (云端)        │
└──────────────────┘    └───────────────┘
```
