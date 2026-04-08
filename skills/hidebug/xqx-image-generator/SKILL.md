---
name: xqx-image-generator
description: Use Ark (火山引擎豆包) to generate images(生成图片) from text via OpenAI-compatible API.
metadata:
  openclaw:
    requires:
      env:
        - ARK_API_KEY
    primaryEnv: ARK_API_KEY
---

# XQX Ark 文生图 Skill

使用火山引擎 Ark (豆包) OpenAI 兼容接口进行文生图。

## 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `ARK_API_KEY` | 是 | 火山 Ark API Key |
| `ARK_IMAGE_MODEL` | 否 | 模型/端点 ID；未设置时使用脚本内默认端点 doubao-seedream-5-0-260128 |

**获取方式**：由调用方在运行前注入环境变量（本机 shell、`export`、CI 密钥、Agent 配置等）。若你使用 OpenClaw 工作区内的 `TOOLS.md` 仅作为本机备忘，可自行在其中写 `export` 并 `source`，但须遵守下方安全说明。

**安全说明（必读）**：`ARK_API_KEY` 是敏感凭证。请勿把真实密钥写入可被他人访问的共享文档、Wiki 或提交到 Git；勿将含密钥的 `TOOLS.md` 放在多人协作仓库或公共同步盘中。优先使用本机私有配置、操作系统/密钥管理器或 CI 密钥注入；脚本只从进程环境变量读取，不会将密钥写回磁盘。

**本机 `TOOLS.md` 示例**（占位符仅作格式参考，请替换为你自己的密钥管理方式）：

```
export ARK_API_KEY="你的API Key"
export ARK_IMAGE_MODEL="你选择的图片模型"  # 可选，端点 ID
```

**当前 shell 手动设置示例**：

```
export ARK_API_KEY="你的API Key"
export ARK_IMAGE_MODEL="你选择的图片模型"  # 可选
```

## 依赖

仅使用 Python 标准库，无需安装额外依赖。

## 使用方式

```
python scripts/xqximage.py <prompt> [size]
```

### 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| prompt | ✅ | 图片描述 |
| size | 可选 | 尺寸：2K、4K、2560x1440 等，默认 2K |


### 尺寸选项

- `2K` - 默认
- `4K`
- `1456x816`、`2048x2048`、`2560x1440`、`1440x2560`、`2304x1728`、`1728x2304`

## 示例

```
# 基本用法
python scripts/xqximage.py "星际穿越，黑洞，电影大片，动感"

# 指定 4K 尺寸
python scripts/xqximage.py "可爱的猫咪" 4K

# 指定 16:9 比例
python scripts/xqximage.py "风景照" 2560x1440

```

## 输出说明

- 直接运行：输出图片 URL

## 文件结构

```
xqx-image-generator/
├── SKILL.md         # 本文件
├── requirements.txt # 依赖
└── scripts/
    ├── xqximage.py  # 主脚本
```

## API 参考

- **base_url**: `https://ark.cn-beijing.volces.com/api/v3`
- **接口**: OpenAI images.generate 兼容
- **参数**: prompt, size, watermark, response_format
