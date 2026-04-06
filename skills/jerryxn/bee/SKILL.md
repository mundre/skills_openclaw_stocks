---
name: bee
version: 1.1.2
description: 抖音视频自动化工作流 - 下载、上传OSS、按角色批量插入飞书多维表格
author: openclaw
metadata:
  openclaw:
    emoji: 🎬
    requires:
      bins: [node, python3]
      env: [ALIYUN_OSS_ACCESS_KEY_ID, ALIYUN_OSS_ACCESS_KEY_SECRET, ALIYUN_OSS_ENDPOINT, ALIYUN_OSS_BUCKET]
    optional:
      env: [FEISHU_BITABLE_APP_TOKEN, FEISHU_BITABLE_TABLE_ID]
---

# 🎬 抖音视频工作流 (BEE)

自动化完成抖音视频处理全流程：下载无水印视频 → 上传阿里云OSS → 按角色批量插入飞书多维表格。

## ✨ 功能特性

- 🎬 **自动下载** - 获取抖音无水印视频（支持 v.douyin.com / douyin.com 链接）
- ☁️ **OSS上传** - 自动上传到阿里云对象存储，生成永久链接
- 📝 **批量插入** - 自动读取多维表格角色，每个角色插入一条记录
- 🏷️ **自动提取** - 从视频标题自动提取正文、话题标签（#号）
- 🔒 **安全设计** - 敏感信息通过环境变量读取
- ✅ **前置验证** - 运行前检查所有依赖和配置

## 🚀 快速开始

### 1. 安装依赖

```bash
pip3 install oss2 requests
clawhub install douyin-download
```

### 2. 配置环境变量

```bash
# 必需：阿里云OSS
export ALIYUN_OSS_ACCESS_KEY_ID="your_access_key_id"
export ALIYUN_OSS_ACCESS_KEY_SECRET="your_access_key_secret"
export ALIYUN_OSS_ENDPOINT="https://oss-cn-beijing.aliyuncs.com"
export ALIYUN_OSS_BUCKET="your_bucket_name"

# 可选：飞书多维表格
export FEISHU_BITABLE_APP_TOKEN="your_app_token"
export FEISHU_BITABLE_TABLE_ID="your_table_id"
```

### 3. 运行

```bash
python3 ~/.openclaw/workspace/skills/bee/scripts/workflow.py "https://v.douyin.com/xxxxx"
```

## 📋 工作流程

1. **验证阶段** - 检查环境变量、依赖、链接格式
2. **下载阶段** - 调用 douyin-download 获取视频信息 + 下载无水印视频
3. **上传阶段** - 上传到阿里云OSS，路径：`videos/douyin/YYYY/MM/video_id.mp4`
4. **记录阶段** - 读取多维表格"角色"字段所有选项，为每个角色创建一条记录

### 插入的字段

| 字段 | 来源 | 说明 |
|------|------|------|
| 热点词 | 视频标题 | 视频完整标题 |
| 大概描述 | 视频标题 | 视频完整标题 |
| 正文 | 标题提取 | 标题去掉 #话题标签 后的纯文本 |
| 话题 | 标题提取 | 从标题中提取的 #标签 |
| 视频原始地址 | 用户输入 | 原始抖音链接 |
| 阿里OSS地址 | 上传结果 | OSS永久链接 |
| 视频url | 上传结果 | 同上 |
| 状态 | 固定值 | "未制作" |
| 角色 | 表格字段 | 每个角色一条记录 |
| 素材审核状态 | 固定值 | "未审核" |
| 插入时间 | 当前时间 | 自动填充 |
| 锚点图地址 | 公式计算 | 表格公式按角色自动匹配 |

## 🔒 环境变量清单

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `ALIYUN_OSS_ACCESS_KEY_ID` | ✅ | 阿里云AccessKey ID |
| `ALIYUN_OSS_ACCESS_KEY_SECRET` | ✅ | 阿里云AccessKey Secret |
| `ALIYUN_OSS_ENDPOINT` | ✅ | OSS端点 |
| `ALIYUN_OSS_BUCKET` | ✅ | OSS Bucket名称 |
| `FEISHU_BITABLE_APP_TOKEN` | ❌ | 飞书多维表格 App Token |
| `FEISHU_BITABLE_TABLE_ID` | ❌ | 飞书多维表格 Table ID |

## 📊 输出示例

```
==================================================
🎬 抖音视频工作流启动
==================================================
视频链接: https://v.douyin.com/vE-E11wm18I/

📥 步骤1: 下载视频...
✅ 下载成功: 7617007615838565553.mp4 (2.2 MB)

☁️ 步骤2: 上传到阿里云OSS...
✅ 上传成功: videos/douyin/2026/04/7617007615838565553.mp4

📝 步骤3: 插入多维表格...
📋 角色列表: 小桃犟, 腿姐, 张伟杰, 张薇因 (共4个)
  ✅ [小桃犟] 记录已创建
  ✅ [腿姐] 记录已创建
  ✅ [张伟杰] 记录已创建
  ✅ [张薇因] 记录已创建

==================================================
✅ 工作流执行完成！
==================================================
📹 视频ID: 7617007615838565553
📁 本地文件: /tmp/douyin_workflow/7617007615838565553.mp4
☁️  OSS地址: https://openclawark.oss-cn-beijing.aliyuncs.com/videos/douyin/2026/04/7617007615838565553.mp4
```

## 🛠️ 故障排除

| 问题 | 解决 |
|------|------|
| 缺少环境变量 | 配置 `~/.bashrc` 中的 OSS 和飞书变量 |
| 缺少依赖 | `pip3 install oss2 requests` + 安装 Node.js |
| douyin-download 未找到 | `clawhub install douyin-download` |
| OSS上传失败 | 检查 AccessKey、Bucket、网络连接 |
| 下载超时 | 网络慢时大文件可能需要等待，超时300秒 |

## 📄 文件结构

```
~/.openclaw/workspace/skills/bee/
├── SKILL.md
├── _meta.json
└── scripts/
    └── workflow.py         # 主工作流脚本
```

## 🔄 更新日志

### v1.1.1 (2026-04-01)
- ✅ 补充「正文」和「话题」字段：从视频标题自动提取，正文去掉 #标签，话题单独提取
- ✅ 视频标题解析：下载时从视频信息中提取标题

### v1.1.0 (2026-04-01)
- ✅ 批量插入：自动读取多维表格角色字段，每个角色插入一条记录（原来只插1条）
- ✅ 补充字段：热点词、大概描述、素材审核状态
- ✅ 飞书凭证：从 openclaw.json 自动读取，无需额外配置
- ✅ 下载超时：从120秒提升到300秒

### v1.0.0 (2026-03-26)
- ✅ 初始版本：下载视频 → 上传OSS → 插入多维表格
- ✅ 安全的环境变量配置
- ✅ 前置验证和错误处理
