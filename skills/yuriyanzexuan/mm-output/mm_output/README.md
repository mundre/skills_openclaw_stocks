# MMOutput - Multi-modal Output Module

多模态输出模块，用于将 PosterGen 生成的 HTML 转换为 PDF、PNG 和 DOCX 格式。

## 功能特性

- **PDF 输出**: 使用无头浏览器 Chrome (Playwright) 将 HTML 打印为 PDF
- **PNG 输出**: 使用无头浏览器 Chrome 截取 HTML 页面为 PNG 图片
- **DOCX 输出**: 使用 python-docx 将 HTML 内容转换为 Word 文档

## 安装依赖

```bash
# 核心依赖
pip install playwright python-docx beautifulsoup4

# 安装 Chromium 浏览器
playwright install chromium
```

## 使用方式

### 1. 作为 Python 模块使用

```python
from mm_output import MMOutputGenerator

# 方式一：使用上下文管理器
with MMOutputGenerator() as gen:
    # HTML 转 PDF
    gen.html_to_pdf("input.html", "output.pdf")
    
    # HTML 转 PNG（整页截图）
    gen.html_to_png("input.html", "output.png", full_page=True)
    
    # HTML 转 DOCX
    gen.html_to_docx("input.html", "output.docx")

# 方式二：批量转换所有格式
with MMOutputGenerator() as gen:
    results = gen.convert_all("input.html", "./outputs/", base_name="poster")
    # results = {'pdf': 'outputs/poster.pdf', 'png': 'outputs/poster.png', 'docx': 'outputs/poster.docx'}
```

### 2. 命令行使用

```bash
# HTML 转 PDF
python -m mm_output.cli input.html --format pdf --output poster.pdf

# HTML 转 PNG（整页截图）
python -m mm_output.cli input.html --format png --output poster.png

# HTML 转 DOCX
python -m mm_output.cli input.html --format docx --output poster.docx

# 批量转换所有格式
python -m mm_output.cli input.html --format all --output-dir ./outputs/

# 指定 Chrome 路径
python -m mm_output.cli input.html --format pdf --chrome-path /usr/bin/google-chrome
```

### 3. 集成到 run.py 工作流

修改 `run.py` 在渲染 HTML 后自动转换为其他格式：

```python
from mm_output import convert_all

# ... 现有代码 ...

# Step 2: Render the parsed content to HTML
renderer_unit = PosterGenRendererUnit()
html_path = renderer_unit.render(...)

# Step 3: Multi-modal output generation (NEW)
if html_path:
    from mm_output import MMOutputGenerator
    
    mm_output_dir = Path(args.output_dir) / "mm_outputs"
    mm_output_dir.mkdir(parents=True, exist_ok=True)
    
    with MMOutputGenerator() as gen:
        # 根据参数决定输出哪些格式
        formats = []
        if args.output_pdf:
            formats.append("pdf")
        if args.output_png:
            formats.append("png")
        if args.output_docx:
            formats.append("docx")
        
        if formats:
            results = gen.convert_all(
                html_path, 
                mm_output_dir, 
                formats=formats,
                base_name=Path(html_path).stem
            )
            print(f"Multi-modal outputs saved to: {mm_output_dir}")
```

## API 参考

### MMOutputGenerator

主类，提供格式转换功能。

#### 构造函数

```python
gen = MMOutputGenerator(chrome_path=None)
```

- `chrome_path`: 可选，指定 Chrome/Chromium 可执行文件路径

#### 方法

**html_to_pdf(html_path, output_path, **options)**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page_size` | str | "A4" | 页面大小 (A4, Letter, Legal, etc.) |
| `margin` | dict | {"top": "1cm", ...} | 页边距 |
| `landscape` | bool | False | 横向布局 |
| `print_background` | bool | True | 打印背景图形 |

**html_to_png(html_path, output_path, **options)**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `full_page` | bool | True | 是否捕获完整页面 |
| `viewport_size` | tuple | (1200, 1600) | 视口尺寸 |
| `wait_time` | int | 2000 | 页面加载等待时间 (ms) |

**html_to_docx(html_path, output_path, **options)**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `include_images` | bool | True | 是否包含图片 |

**convert_all(html_path, output_dir, **options)**

批量转换所有格式。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `base_name` | str | None | 输出文件基础名 |
| `formats` | list | ["pdf", "png", "docx"] | 要生成的格式列表 |

## 文件结构

```
mm_output/
├── __init__.py      # 模块入口
├── converter.py     # 核心转换逻辑
├── cli.py           # 命令行接口
└── README.md        # 本文档
```

## 注意事项

1. **PDF/PNG 依赖 Chrome**: 确保已安装 Chromium 浏览器 (`playwright install chromium`)
2. **DOCX 转换限制**: DOCX 转换是尽力而为的，复杂布局可能无法完美保留
3. **图片路径**: 确保 HTML 中的图片路径是相对路径或绝对路径，网络图片可能无法正确加载
