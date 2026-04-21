# markitdown-zh 技能

📄 OpenClaw 等智能体文档转换技能，用于将各类文档转换为 Markdown 格式。基于微软 MarkItDown 库，支持 PDF、Word、PowerPoint、Excel、图像 (OCR)、音频 (转录)、HTML 和 YouTube 链接。

**文档和工具** 用于微软的 [MarkItDown](https://github.com/microsoft/markitdown) 库。

**原作者：** Karman Verma  
**中文作者：** 枫影

## 此技能是什么

此技能提供：
- ✅ MarkItDown 使用文档
- ✅ 批量转换脚本 (`scripts/batch_convert.py`)
- ✅ 使用示例和 API 参考

实际的文档转换由微软的 `markitdown` CLI 完成，需要通过 pipx 单独安装（不使用pip）。

## 安装

### 通过 ClawHub

```bash
clawhub install markitdown-zh
```

### 手动安装

安装 `markitdown` CLI：
```bash
sudo apt-get install pipx
# 使用pipx安装markitdown包 all表示支持所有格式
pipx install 'markitdown[all]'
# 将markitdown调用路径放入当前变量PATH内
pipx ensurepath
```

## 快速开始

```bash
# 转换 PDF 文件
markitdown document.pdf -o document.md

# 转换网页
markitdown https://example.com/docs -o docs.md

# 批量转换
python scripts/batch_convert.py docs/*.pdf -o markdown/
```

## 支持的格式

- **PDF** - 文本提取，结构保留
- **Word (.docx)** - 标题、列表、表格
- **PowerPoint** - 幻灯片、文本
- **Excel** - 表格、工作表
- **图像** - OCR + EXIF 元数据
- **音频** - 语音转录
- **HTML** - 结构保留
- **YouTube** - 视频转录

## 文件结构

```
markitdown-zh/
├── SKILL.md          # 主技能文档
├── README.md         # 此文件
├── _meta.json        # 元数据
├── scripts/
│   └── batch_convert.py  # 批量转换脚本
└── package.json      # 包信息
```

## 另请参阅

- [SKILL.md](SKILL.md) - 完整技能文档
- [USAGE-GUIDE.md](USAGE-GUIDE.md) - 详细使用指南
- [reference.md](reference.md) - API 参考
- [Microsoft MarkItDown](https://github.com/microsoft/markitdown) - 上游库

## 许可证

MIT
