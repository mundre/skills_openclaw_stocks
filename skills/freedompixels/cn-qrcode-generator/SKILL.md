---
name: cn-qrcode-generator
version: 1.0.0
description: |
  中文二维码生成器。输入URL或文本，一键生成高清PNG/SVG二维码。
  支持自定义颜色/尺寸/Logo，无需API Key，开箱即用。
  当用户说"生成二维码"、"二维码"、"qrcode"时触发。
  Keywords: 二维码, 生成二维码, 扫码, qrcode, qr.
metadata: {"openclaw": {"emoji": "📱"}}
---

# cn-qrcode-generator - 中文二维码生成器

生成PNG/SVG二维码，支持自定义颜色/尺寸/Logo。

## 核心功能
- 输入URL/文本，生成高清二维码
- 支持自定义颜色（前景/背景）
- 支持自定义尺寸（默认300px）
- 可叠加Logo图片
- 支持PNG/SVG格式

## 使用场景
- 内容创作者在文章/封面图嵌入二维码
- 生成可扫码的短链接
- 制作个人名片/社交媒体二维码

## API方案
- qrcode.monster（免费，无需注册，直接HTTP生成）
- qrserver.com（备选，稳定）

## 输出格式
```json
{
  "text": "https://example.com",
  "file": "/path/to/qrcode.png",
  "size": 300,
  "api": "qrcode.monster"
}
```

## 使用方式
```bash
python ~/.qclaw/skills/cn-qrcode-generator/generate.py "https://example.com" --output qr.png --size 300
```

## 依赖
- Python3
- requests

## 标签
cn, qrcode, qr, code, generator
