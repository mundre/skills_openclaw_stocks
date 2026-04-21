---
name: clean-desktop-pro
description: 智能整理桌面文件，按类型分类整理，检测并清理重复文件，生成整理报告，提升电脑效率
allowed-tools:
  - file-system
  - shell
  - http
---

# 专业桌面整理（含重复文件清理）

## 概述
专业桌面整理工具，帮助用户自动整理桌面文件，按类型分类，检测并清理重复文件，生成详细的整理报告，提升电脑使用效率。

## 功能特点
- **智能分类**：按文件类型自动分类整理到对应文件夹
- **重复文件检测**：通过哈希值检测并清理重复文件
- **详细报告**：生成整理报告，包含处理文件数、移动文件数、删除重复文件数等信息
- **跨平台支持**：支持 Windows、macOS 和 Linux 系统


## 执行步骤

### 步骤 1：扫描桌面文件
- 扫描桌面目录下的所有文件
- 排除已分类文件夹中的文件
- 统计文件总数

### 步骤 2：检测重复文件
- 计算每个文件的 MD5 哈希值
- 对比哈希值，识别重复文件
- 统计重复文件数量

### 步骤 3：清理重复文件
- 删除重复文件
- 记录删除的文件数量

### 步骤 4：按类型分类整理
- 根据文件扩展名分类到对应文件夹：
  - Documents：文档文件（.doc, .docx, .txt, .pdf 等）
  - Images：图片文件（.jpg, .jpeg, .png, .gif 等）
  - Videos：视频文件（.mp4, .avi, .mov 等）
  - Audio：音频文件（.mp3, .wav, .flac 等）
  - Archives：压缩文件（.zip, .rar, .7z 等）
  - Executables：可执行文件（.exe, .msi, .app 等）
  - Others：其他文件

### 步骤 5：生成整理报告
- 生成 JSON 格式的整理报告
- 报告包含：时间戳、桌面路径、处理文件数、移动文件数、删除重复文件数、各分类文件数量
- 报告保存到桌面目录下的 "整理报告.json"

## 支持的文件类型

### 文档文件
- .doc, .docx, .txt, .pdf, .xls, .xlsx, .ppt, .pptx

### 图片文件
- .jpg, .jpeg, .png, .gif, .bmp, .svg

### 视频文件
- .mp4, .avi, .mov, .wmv, .flv

### 音频文件
- .mp3, .wav, .flac, .aac

### 压缩文件
- .zip, .rar, .7z, .tar, .gz

### 可执行文件
- .exe, .msi, .app, .dmg

## 输出报告示例

```json
{
  "timestamp": "2026-04-16T12:00:00",
  "desktop_path": "C:\\Users\\User\\Desktop",
  "files_processed": 50,
  "files_moved": 45,
  "duplicates_removed": 5,
  "categories": {
    "Documents": 15,
    "Images": 10,
    "Videos": 5,
    "Audio": 3,
    "Archives": 2,
    "Executables": 1,
    "Others": 9
  }
}
```

## 注意事项
- 运行前请确保桌面文件没有打开或被其他程序占用
- 重复文件检测会删除重复的文件，只保留一个副本
- 整理过程中会创建分类文件夹，请确保有足够的权限
- 建议在运行前备份重要文件，以防意外情况

## 系统要求
- Python 3.6 或更高版本
- 支持 Windows、macOS 和 Linux 系统
- 需要文件系统读写权限