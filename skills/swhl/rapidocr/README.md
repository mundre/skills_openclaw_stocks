# RapidOCR Skill

一个适配当前平台执行方式的本地 OCR Skill，用于识别本机图片中的文字。

## 当前能力

- 支持本地图片 OCR：`png`、`jpg`、`jpeg`、`webp`、`bmp`、`tif`、`tiff`
- 支持中文、英文、数字混合识别
- 支持从 **自然语言** 中自动提取图片绝对路径
- 支持识别 **远程图片 URL**，先自动下载到本机临时目录再 OCR
- 支持两种输出模式：**纯文本** / **JSON 结构化输出**
- 本地离线执行（依赖安装完成后，本地图片识别无需联网）

## 当前推荐调用方式

### 纯文本输出

```text
请识别图片里的文字，图片路径是 C:\Users\ma139\.maclaw\workspace\rapidocr_chinese_test.png
```

### JSON 输出

```text
请识别图片里的文字并返回json，图片路径是 C:\Users\ma139\.maclaw\workspace\rapidocr_chinese_test.png
```

或：

```text
请识别图片里的文字，图片路径是 C:\Users\ma139\.maclaw\workspace\rapidocr_chinese_test.png --json
```

### 远程图片 URL 自动下载后识别

```text
请识别这张图，图片链接是 https://www.modelscope.cn/models/RapidAI/RapidOCR/resolve/master/resources/test_files/test.png
```

Skill 会自动执行等价命令：

```bash
node "{baseDir}/run_rapidocr.js" "<用户原话>"
```

也就是说：

- 不需要额外注入 `img_path` 模板变量
- 不要求用户只传裸路径
- 可以直接把用户原话当作脚本唯一参数传入

## 输出形式

### 1. 默认纯文本

每行一条识别结果：

```text
今天天气不错
RapidOCR 中文测试
ABC123
```

### 2. JSON 结构化输出

返回字段：

- `text`：合并后的完整文本
- `lines`：逐行文本数组
- `boxes`：检测框坐标
- `scores`：每行置信度
- `source`：实际识别的本地文件路径

示例：

```json
{
  "text": "今天天气不错\nRapidOCR 中文测试\nABC123",
  "lines": ["今天天气不错", "RapidOCR 中文测试", "ABC123"],
  "boxes": [[[30.0, 38.0], [247.0, 38.0], [247.0, 76.0], [30.0, 77.0]]],
  "scores": [0.99965, 0.98901, 0.99894],
  "source": "C:\\Users\\ma139\\.maclaw\\workspace\\rapidocr_chinese_test.png"
}
```

## 依赖要求

建议环境：

- Python 3.8 - 3.11
- 已安装：

```bash
python -m pip install rapidocr onnxruntime
```

如果终端里 `rapidocr` 不在 PATH 中，也没关系；wrapper 会自动尝试常见 Python Scripts 目录。

## 脚本说明

实际入口脚本：

```text
{baseDir}/run_rapidocr.js
```

这个 wrapper 做了几件事：

1. 从自然语言、JSON、环境变量中提取图片路径或图片 URL
2. 自动检查本地图片路径是否存在
3. 若输入是 URL，自动下载到系统临时目录
4. 自动寻找 Python / RapidOCR 可执行环境
5. 调用 Python 中的 RapidOCR 库执行 OCR
6. 过滤 warning 和 info 日志，只保留识别结果
7. 按需输出纯文本或 JSON

## 当前行为约定

### 支持的输入形式

1. 裸路径

```text
C:\Users\ma139\.maclaw\workspace\rapidocr_chinese_test.png
```

1. 自然语言 + 路径

```text
帮我识别这张图，图片路径是 C:\Users\ma139\.maclaw\workspace\rapidocr_chinese_test.png
```

1. JSON 风格文本

```json
{"img_path":"C:\\Users\\ma139\\.maclaw\\workspace\\rapidocr_chinese_test.png"}
```

1. 自然语言 + 远程图片 URL

```text
请识别这张图，图片链接是 https://example.com/demo.png
```

### 当前不支持

- PDF 直接识别
- 非图片 URL
- 相对路径鲁棒处理仍较弱，推荐优先使用 **绝对路径**

## 状态

当前版本已完成以下验证：

- 本地直接执行 wrapper：成功
- 通过 `manage_skill run` 调用 Skill：成功
- 路径从自然语言中提取：成功
- JSON 输出：成功
- 输出仅保留 OCR 文本 / JSON：成功

## License

- RapidOCR upstream: Apache 2.0
