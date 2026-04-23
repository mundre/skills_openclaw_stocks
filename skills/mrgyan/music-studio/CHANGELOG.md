# Changelog

## [1.0.7] — 2026-04-23

### Changed
- 补充说明 GitHub 开发仓库与 ClawHub 实际发布结构的差异：ClawHub 以 `music_studio/` 目录为发布内容基准，安装后目录结构为扁平化 skill 根目录。

## [1.0.6] — 2026-04-23

### Fixed
- MiniMax 翻唱链路改为：`music-cover` 负责前处理，`music-2.6` 负责最终生成，修复此前直接用 `music-cover` 生成导致失败的问题。
- 翻唱记录新增 `preprocess_model` 字段，并保留 `cover_feature_id` 与自动提取歌词，便于追溯实际调用链路。

## [1.0.5] — 2026-04-22

### Fixed
- 首次使用或重置后，说「打开音乐工作室」会先进入自动初始化问答，而不是直接落到未配置菜单。
- 修复菜单数字与会话历史恢复冲突；只有明确进入「会话历史」后，数字序号才表示恢复会话。
- 修复恢复会话时 state/step 被重置的问题；现在会按原流程位置恢复。
- 会话 30 天自动清理已真正接线。
- 统一聊天流程的交付产物：音乐/翻唱会稳定输出 mp3（如可下载）、`.url`、`.meta.txt`；歌词会输出 `.lyrics.txt`、`.tags.txt`（如有）、`.meta.txt`。
- CLI 侧的 library/download/export 兼容新的 sidecar 文件字段，减少聊天流与命令行流行为不一致。

## [1.0.4] — 2026-04-22

### Changed
- 补充介绍说明：当前版本暂时只正式支持 MiniMax 的 `music-2.6` / `music-cover`。

## [1.0.3] — 2026-04-22

### Changed
- 补充支持范围说明：当前版本暂时只正式支持 MiniMax 的 `music-2.6` / `music-cover`。

### Fixed
- 会话中直接回传音乐文件/歌词文件，不再只给 URL。
- 修正 lyrics 完成态的选项映射。

## [1.0.2] — 2026-04-22

### Fixed
- 默认初始化不再落盘 API Key；环境变量 `MINIMAX_API_KEY` 优先。
- 新增 `set-key` / `clear-key`，显式管理本地保存的 API Key。
- 修复 `init.py` 的 key 保存逻辑 bug。
- 修复所有 CLI 脚本中 `OUTPUT_DIR()` 混用问题。
- 统一时间戳为真实 ISO-8601 本地带时区时间。
- 修复会话和 library 过期清理逻辑中的时间比较问题。

## [1.0.1] — 2026-04-22

### Fixed
- 安全与质量修正的首次补丁发布。

## [1.0.0] — 2026-04-22

### Added
- Python 包架构
- 对话式引导流程
- API 直调
- Session 管理器
- 生成完成后的继续操作
