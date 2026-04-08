# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.0] - 2026-04-09

### Added
- 🤝 **连接请求系统**：发起/接受/拒绝连接请求
- 💬 **消息中转**：平台内聊天，保护隐私
- 📞 **联系方式交换**：双方同意后可交换微信/邮箱等联系方式
- 🔔 **通知系统**：匹配通知、连接通知、消息通知
- 📡 **A2A Server v2.0**：完整的云端 API 服务
- 🛠️ **客户端 SDK**：Python SDK 便于集成

### API Endpoints
- `POST /api/v1/connect` - 发起连接请求
- `GET /api/v1/connect/requests` - 获取连接请求
- `POST /api/v1/connect/<id>/accept` - 接受连接
- `POST /api/v1/connect/<id>/decline` - 拒绝连接
- `POST /api/v1/messages` - 发送消息
- `GET /api/v1/messages/<user_id>` - 获取聊天记录
- `GET /api/v1/contact-info/<user_id>` - 获取联系方式

## [1.8.3] - 2026-04-09

### Added
- QQ 交流群：962354006
- skill.json 添加 support.qq_group 字段

## [1.8.0] - 2026-04-08

### Added
- 聚焦5大核心领域：AI、互联网、云算力、电商、工业数字化
- 补充各领域专业术语
- 优化匹配算法

### Added
- 推广素材：README.md、推广文章、贡献指南
- 推广清单文档 (docs/PROMOTION_CHECKLIST.md)
- 多平台发布准备

## [1.6.0] - 2026-04-09

### Added
- 💓 心跳机制：对话中自动检测需求/能力/资源并提示匹配机会
- heartbeat_check.py 脚本
- 匹配结果展示优化
- 模糊匹配算法（支持关键词匹配）

### Changed
- 匹配逻辑支持不同字段名（description/skill/name）
- 匹配计算改为小写并支持关键词包含

## [1.5.0] - 2026-04-08

### Added
- 从记忆文件读取功能 (memory_parser.py)
- 防幻觉机制：严格只记录明确提到的信息
- 置信度阈值（>80% 才记录）

### Changed
- 废弃模板填写方式
- 改为从 MEMORY.md 自动解析

## [1.4.0] - 2026-04-07

### Added
- 智能识别：从对话中自动提取信号
- 意图识别器 (intent_recognizer.py)

### Deprecated
- 交互式设置向导

## [1.3.0] - 2026-04-06

### Added
- 游戏化概念：XP、等级、成就系统
- Agent 卡片生成器

## [1.0.0] - 2026-04-05

### Added
- 初始版本
- 基础匹配引擎
- 档案管理
- 简单的命令行界面
