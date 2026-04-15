---
name: file-uploader
description: 将本地文件（图片、文档、视频等）上传到 tiaowulan.com.cn 并返回网络访问路径。触发场景：(1) 用户说"上传文件"、"上传图片"、"上传文档"，(2) 需要将本地文件转换为网络 URL，(3) 用户提供文件并要求生成可直接网页引用的链接。
---

# file-uploader - 文件上传技能

将本地文件上传到指定服务器，返回可直接在网页中使用的网络路径。

## 上传配置

首次使用需要配置 JWT Token 和 Device-ID：

- **JWT Token 获取地址**：https://www.szmpy.com（登录后获取）
- **Device-ID**：请联系管理员获取，微信18936039765

两种配置方式：

### 方式 1：命令行参数（一次性）
```
python scripts/upload.py <文件路径> --token 你的JWT_TOKEN --device-id 你的DEVICE_ID
```

### 方式 2：保存到配置文件（推荐）
```
python scripts/upload.py <文件路径> --token 你的JWT_TOKEN --device-id 你的DEVICE_ID --save-config
```
配置会保存在 `~/.qclaw/skills/file-uploader/config.json`，后续使用无需重复输入。

## 使用方法

在对话中，用户可以：
- "上传这个图片"
- "上传文件 xxx.jpg"
- "把桌面上的 document.pdf 上传一下"

你需要：
1. 确认用户要上传的文件路径
2. 如果没有配置 token/Device-ID，请求用户提供
3. 执行上传脚本
4. 返回得到的网络 URL

## 脚本用法

```bash
# 基本用法
python scripts/upload.py <文件路径>

# 首次配置（保存到配置文件）
python scripts/upload.py <文件路径> --token JWT_TOKEN --device-id DEVICE_ID --save-config

# 查看完整 API 响应
python scripts/upload.py <文件路径> --show-raw
```

## 输出格式

上传成功后返回：
```
SUCCESS
URL: https://xxx.com/uploads/xxx.jpg
```

JSON 格式也会输出（便于程序解析）：
```json
{"success": true, "url": "https://xxx.com/uploads/xxx.jpg", "raw": {...}}
```

## 支持的文件类型

无限制。上传脚本会根据文件扩展名自动识别 MIME 类型：
- 图片：jpg, png, gif, webp, svg, bmp 等
- 文档：pdf, doc, docx, xls, xlsx, ppt, pptx 等
- 视频：mp4, avi, mov, mkv, webm 等
- 音频：mp3, wav, flac, aac 等
- 其他：zip, rar, tar, gz 等

## 错误处理

常见错误：
- `File not found` - 文件路径不存在，检查路径是否正确
- `HTTP 401` - JWT token 无效或过期
- `HTTP 403` - Device-ID 不正确或无权限
- `HTTP 413` - 文件太大（服务器限制）
- `Connection failed` - 网络问题或 URL 错误
