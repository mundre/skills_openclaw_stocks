---
name: melo-tts-metadata-creator
description: |-
  一个专为 **MeloTTS** 训练/微调设计的 metadata.list 生成工具。
  自动生成 MeloTTS 训练/微调所需的 metadata.list 文件（官方最新标准）。
  支持 .wav + 对应 .txt 转录，或自动调用 Whisper 转录。
  单音色/多音色均可，一键生成 UTF-8 无 BOM 格式。
metadata:
  openclaw:
    requires:
      bins:
        - python
---

# melo-tts-metadata-creator

**功能**：支持**单音色**与**多音色**两种模式，特别适配 **wav 文件和 txt 转录文件位于两个不同目录**，且每个子目录代表一个说话人的场景。
* 支持 wav 和 txt 分离存放（目录结构完全一致）
* 自动按第一级子目录名称提取 speaker（多音色模式）
* 支持 `--speaker` 参数强制使用统一说话人（单音色模式）
* 内置 Whisper 自动转录功能（无 txt 时自动生成）
* Whisper 模型下载到 `./models/` 目录（便于管理）
* 模型下载失败或转录失败时优雅跳过，继续处理其他文件
* 生成完全符合 MeloTTS 官方最新标准的 `metadata.list`

## 支持的模型（推荐顺序）
1. **openai/whisper-base** → Whisper是一个预训练的自动语音识别（ASR）和语音翻译模型。

## 执行步骤
1. **解析目录**：自动识别 --wav_dir 和 --txt_dir，支持多级子目录结构。每个第一级子目录将被视为一个独立说话人（speaker）。若传入 --speaker 参数，则强制使用统一说话人名称（单音色模式）。
2. **默认目标**：若未指定 --output 参数，默认在当前工作目录生成 metadata.list 文件。强烈建议显式指定输出路径，以便后续训练使用。
3. **调用命令**：使用以下兼容性命令启动脚本（优先使用 python3，失败则回退 python）。脚本会自动检测是否安装 Whisper 依赖，并在必要时提示安装。

   ```bash
   (python3 scripts/generate_metadata_list.py --wav_dir "<音频目录>" --txt_dir "<文本目录>" [--speaker <姓名>] [--lang {ZH,EN}] [--output <路径>] [--recursive] [--use_whisper]) || (python scripts/generate_metadata_list.py --wav_dir "<音频目录>" --txt_dir "<文本目录>" [--speaker <姓名>] [--lang {ZH,EN}] [--output <路径>] [--recursive] [--use_whisper])

