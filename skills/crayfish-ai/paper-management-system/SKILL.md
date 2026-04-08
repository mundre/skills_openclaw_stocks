---
name: paper-management-system
description: 文献管理系统 - 自动化PDF文献索引、搜索、AI提炼工具。当用户需要管理PDF文献、自动索引、搜索文献、提取元数据时激活。
metadata:
  {
    "openclaw":
      {
        "emoji": "📚",
        "tags": ["pdf", "papers", "research", "academic", "indexing"],
      },
  }
---

# Paper Management System

文献管理系统 - 自动化PDF文献管理工具

## 功能特性

- 📄 **自动索引**: 扫描PDF文件，提取元数据（标题、作者、DOI等）
- 🔍 **智能搜索**: 支持标题、作者、DOI、摘要等多字段搜索
- 🏷️ **自动重命名**: 按规范格式重命名PDF文件
- 📚 **全文提取**: 提取PDF文本内容便于检索
- 🤖 **AI提炼**: 自动提取研究背景、方法、结果、结论
- 🔔 **飞书通知**: 新文献入库自动通知（需配合 feishu-relay）
- 🔄 **定时任务**: 支持cron定时自动扫描

## 依赖项目

本项目的新文献通知功能需要配合 **feishu-relay** 使用：

🔗 **feishu-relay**: https://github.com/crayfish-ai/feishu-relay

feishu-relay 是一个飞书消息转发服务，提供统一的消息通知通道。

## 安装

```bash
git clone <repo-url>
cd paper-management-system
chmod +x auto_index.sh
```

## 使用方法

### 1. 初始化数据库
```bash
python3 paper_manager.py index
```

### 2. 搜索文献
```bash
python3 paper_manager.py search "关键词"
```

### 3. 自动重命名
```bash
python3 paper_manager.py rename
```

### 4. 查看状态
```bash
python3 paper_manager.py status
```

### 5. 设置定时任务
```bash
# 编辑crontab
crontab -e

# 添加每30分钟自动扫描
*/30 * * * * /path/to/paper-management-system/auto_index.sh
```

## 文件说明

| 文件 | 功能 |
|------|------|
| `paper_manager.py` | 核心管理模块（索引、搜索、重命名） |
| `auto_index.sh` | 自动化脚本（定时任务用） |
| `extract_fulltext.py` | PDF全文提取模块 |
| `ai_summarize.py` | AI智能提炼模块 |

## 数据库结构

SQLite数据库 `index.db` 包含以下字段：
- `file_hash`: MD5哈希（去重用）
- `filename`: 文件名
- `title`: 文献标题
- `authors`: 作者
- `doi`: DOI
- `year`: 年份
- `journal`: 期刊
- `abstract`: 摘要
- `full_text`: 全文内容
- `ai_summary`: AI提炼内容

## 配置

编辑脚本中的以下变量以适应你的环境：

```python
# paper_manager.py
DB_PATH = "/your/path/index.db"
PAPERS_DIR = "/your/path/papers"

# auto_index.sh
PAPERS_DIR="/your/path/papers"
DB_PATH="/your/path/index.db"
```

### 飞书通知配置（可选）

如需启用飞书通知，请确保已安装并配置 [feishu-relay](https://github.com/crayfish-ai/feishu-relay)，然后修改 `ai_summarize.py` 中的通知路径：

```python
# ai_summarize.py
cmd = f'/path/to/feishu-relay/bin/notify "{title}" "{message}"'
```

## 依赖

- Python 3.7+
- sqlite3
- PyPDF2（PDF解析）

## 相关项目

- [feishu-relay](https://github.com/crayfish-ai/feishu-relay) - 飞书统一通知服务

## License

MIT
