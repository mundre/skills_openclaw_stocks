# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.0] - 2026-04-01

### Added
- **Sherpa-ONNX 引擎集成**：新增 Sherpa-ONNX 作为首选 STT 引擎
- **自动 Fallback 机制**：Sherpa-ONNX 失败时自动切换到 Vosk
- **引擎策略配置**：支持 `sherpa`、`vosk`、`auto` 三种策略
- **中英文混合识别**：Sherpa-ONNX 原生支持中英文混合，准确率提升
- **多语言支持**：Sherpa-ONNX 支持中英日韩多语言识别
- **配置项扩展**：
  - `STT_ENGINE`: STT 引擎策略
  - `SHERPA_MODEL_DIR`: Sherpa-ONNX 模型目录
  - `SHERPA_MODEL_NAME`: Sherpa-ONNX 模型名称
  - `SHERPA_NUM_THREADS`: Sherpa-ONNX 线程数

### Changed
- **依赖更新**：
  - 新增 `sherpa-onnx>=1.10.0`（Sherpa-ONNX 引擎）
  - 移除 `funasr-onnx`（避免 CUDA/NVIDIA 依赖）
  - 移除 `librosa`, `scipy`（Sherpa-ONNX 不需要）
  - 保留 `numpy>=1.21.0`（Sherpa-ONNX 依赖）
- **默认引擎策略**：从 `sensevoice` 改为 `auto`（自动 fallback）
- **文档更新**：
  - 更新 `DESIGN.md`，添加 Sherpa-ONNX 设计说明
  - 更新 `README.md`，添加 Sherpa-ONNX 使用指南
  - 新增 STT 引擎对比表格

### Fixed
- 修复中英文混合识别准确率问题（通过 Sherpa-ONNX 解决）
- 修复 termux 环境依赖爆炸问题（移除 CUDA/NVIDIA 依赖）

### Compatibility
- 保持 Vosk 作为备份方案，向后兼容
- termux 环境下 Sherpa-ONNX 使用 CPU 推理（无 GPU 加速）
- 内存占用优化（int8 量化模型，600-800MB）

## [2.2.1] - 2026-03-31

### Added
- 新增 `SOUL.md` 配置最佳实践（动态频道识别）

### Changed
- 优化语音流程第 1 点为"重点注意"，强调严禁新开子会话
- 完善新手前置步骤文档
- 修复 `config.py` 环境变量验证问题 (`extra = "ignore"`)
- 优化飞书音频格式 (`.ogg` 容器)

## [2.1.5] - 2026-03-30

### Added
- 新增 Edge TTS 失败自动降级到 `pyttsx3`

### Changed
- 优化 TTS 错误处理逻辑

## [2.1.4] - 2026-03-29

### Fixed
- 修复 SKILL.md 格式问题
- 修复 ClawHub 发布配置

## [2.1.0] - 2026-03-28

### Changed
- 重构为纯 Skill 架构
- 移除插件依赖
- 简化配置流程

### Added
- 新增 `SKILL.md` 技能描述文件
- 新增 `DESIGN.md` 设计文档

## [2.0.0] - 2026-03-27

### Added
- 初始版本发布
- 支持 Vosk STT 引擎
- 支持 Edge TTS 引擎
- 支持飞书/Telegram 语音消息处理
- 支持自动语音回复

---

## 版本说明

- **主版本号 (Major)**：不兼容的 API 变更
- **次版本号 (Minor)**：向后兼容的功能新增
- **修订号 (Patch)**：向后兼容的问题修复
