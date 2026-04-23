---
name: music-studio
version: 1.0.7
description: 面向大模型（LLM）的轻量音乐创作工作台，通过自然语言交互生成音乐/歌词/翻唱。**不依赖系统级模型配置**，Provider/模型由 config.json 管理，API Key 默认优先走环境变量，也可通过 `set-key` 显式保存。**当前版本正式支持 MiniMax 的歌词、`music-2.6` 文本生成音乐，以及“两阶段翻唱”链路：`music-cover` 前处理 + `music-2.6` 最终生成。**只有明确说「打开音乐工作室」才进入对话流程。
---

# Music Studio v1.0.7

面向大模型的音乐创作工作台，对话式引导交付结果。

> 当前版本正式支持 MiniMax：
> - **歌词生成**：`/v1/lyrics_generation`
> - **文本生成音乐**：`music-2.6`
> - **翻唱**：`music-cover` 前处理 → `music-2.6` 最终生成

## 对话式交互

**唤醒**：用户说「打开音乐工作室」→ 进入引导流程

### 流程说明

```
用户：打开音乐工作室
↓
小盆子：🎵 音乐工作室已就绪！
        请问想做什么？
        1️⃣ 生成音乐
        2️⃣ 写歌词
        3️⃣ 翻唱
        4️⃣ 查看音乐库
        5️⃣ 导出 / 清理
        6️⃣ 会话历史
```

### 翻唱实现说明（重要）

当前 MiniMax 翻唱链路不是“直接用 `music-cover` 产出音频”，而是：

1. `POST /v1/music_cover_preprocess`，模型使用 `music-cover`
2. 拿到 `cover_feature_id` 与自动提取歌词
3. `POST /v1/music_generation`，模型使用 `music-2.6`
4. 传入 `cover_feature_id`、`lyrics`、`prompt` 完成最终生成

因此，配置中的 `cover_model` 实际表示**翻唱前处理模型**；最终音频生成仍使用 `music_model`。

### 生成完成后（选项说明）

| 选项 | 说明 |
|------|------|
| A) 下载音频 | 下载 MP3 到 `output/` 目录 |
| B) 继续生成 | 基于当前结果继续创作（改风格/加歌词） |
| C) 查看音乐库 | 查看所有生成记录 |
| D) 退出 | 结束当前会话 |

### Meta 命令（任意 step 可用）

| 命令 | 说明 |
|------|------|
| 「上一步」/「返回」 | 回到上一步重新输入 |
| 「会话历史」/「6」 | 查看所有历史会话 |
| 数字序号 | 恢复对应历史会话 |
| 「取消」/「退出」 | 退出音乐工作室 |

### 快速入口（越过引导）

| 用户说 | 效果 |
|--------|------|
| 「查看音乐库」 | 直接列出所有记录 |
| 「导出所有」 | 导出全部内容 |
| 「下载第X条」 | 下载对应音频 |
| 「清理」 | 清理过期记录 |

### 发布结构说明

当前 GitHub 仓库是开发仓库；发布到 ClawHub 的 skill 内容来自 **当前 `music_studio/` 目录本体**。

因此：

- ClawHub 安装后的目录结构会是 skill 根目录扁平内容
- 以当前 `SKILL.md` 和同目录代码文件为发布内容基准
- 根 README / 开发辅助文件不会作为安装内容强依赖

## CLI 命令（直接执行）

```bash
python -m music_studio set-key      # 显式保存 API Key
python -m music_studio clear-key    # 删除本地保存的 API Key
python -m music_studio lyrics "<主题>" [--title "标题"] [--edit "歌词"]
python -m music_studio music "<描述>" [歌词] [--instrumental] [--optimizer] [--format url|hex]
python -m music_studio cover "<描述>" --audio <URL> [--lyrics "歌词"]
python -m music_studio library list | get <id> | lyrics <id> | url <id> | download <id>
python -m music_studio library export lyrics <id> | export all | clean | purge
python -m music_studio init / reset / help
```

## Key 策略

- **默认不保存 API Key 到磁盘**
- 优先使用环境变量：`MINIMAX_API_KEY`
- 如确有需要，可运行 `python -m music_studio set-key` 显式保存
- 可运行 `python -m music_studio clear-key` 移除本地保存 key
- 初始化与对话式 setup 都会做真实 API 校验，避免“假成功”

## Session 管理器

每次「打开音乐工作室」创建独立会话，数据保存在 `output/sessions/`：

```
output/sessions/
├── sessions.json           # 轻量索引（最新20条）
└── <uuid>.json             # 每个会话完整记录
```

- **会话历史**：说「6」或「会话历史」查看，输入序号恢复
- **自动清理**：超过 30 天未更新的会话自动删除
- **每次新会话**：打开即新建，不重复复用

## 项目结构

```
music_studio/
├── session_manager/
│   └── manager.py          # 会话历史管理（创建/恢复/清理）
├── conversation/
│   ├── __init__.py         # handle() 入口
│   ├── engine.py           # 主引擎 + 状态路由 + meta 命令拦截
│   ├── session.py          # 会话状态管理（委托 session_manager）
│   └── flows.py            # 各业务方向引导流程 + DONE后续
├── providers/
│   ├── base.py             # MusicAPIBase 抽象类
│   ├── minimax.py          # MiniMax 实现
│   └── __init__.py         # get_api_client() 工厂
├── scripts/                # CLI 命令实现
├── cli.py                  # 统一 CLI 入口
├── config.py               # 配置读写（支持自定义 output_dir）
├── api.py                  # API 工厂
└── library.py              # 输出记录管理
```

## Provider 扩展

新增 Provider 只需：
1. 在 `providers/` 下新建 `xxx.py`，继承 `MusicAPIBase`
2. 在 `providers/__init__.py` 的 `_PROVIDERS` 字典注册
3. 修改 `config.json` 中 `provider` 字段即可切换

## 输出说明

- **保存路径**: `output/`
- **索引文件**: `output/library.json`
- **会话目录**: `output/sessions/`
- **清理规则**: 会话默认保留 30 天，library 记录保留 30 天

## 版本历史

See [CHANGELOG.md](./CHANGELOG.md)
