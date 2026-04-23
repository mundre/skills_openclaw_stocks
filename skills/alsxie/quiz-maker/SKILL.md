---
name: quiz-maker
description: 出题工具。根据文档内容（docx、pdf、txt 等）生成选择题测试卷，并返回二维码供答题者扫码作答。触发词：出题、生成题目、创建测验、云端出题。
---

# quiz-maker - 出题技能

## 默认行为
**使用云端服务出题**，返回二维码图片。

## 调用流程

### 1. 提取文档内容
```bash
# docx
python3 -c "
from docx import Document
doc = Document('文件路径.docx')
for p in doc.paragraphs:
    if p.text.strip(): print(p.text)
for t in doc.tables:
    for row in t.rows: print(' | '.join(c.text.strip() for c in row.cells))
"

# pdf
python3 -c "
import PyPDF2
reader = PyPDF2.PdfReader('文件路径.pdf')
for page in reader.pages:
    t = page.extract_text()
    if t and t.strip(): print(t.strip())
"
```

### 2. 调用云端 API 出题
```bash
node ~/.openclaw/quiz-maker/quiz-create.js "<内容>" "<标题>" "<说明>"
```

### 3. 提取二维码并保存
```bash
# 从输出 JSON 中提取 qrImage 字段 base64，保存为 PNG
python3 -c "
import sys, base64, json
r = json.loads(sys.stdin.read())
b64 = r['qrImage'].replace('data:image/png;base64,', '')
open('输出路径.png', 'wb').write(base64.b64decode(b64))
"
```

### 4. 验证后发送
```bash
file 输出路径.png  # 确认为 PNG 再发送
```

## 注意事项
- 云端服务地址：`https://118.196.5.240:34100`
- 内容最少需要 50 字
- 二维码直接展示给用户即可

## 教训（踩坑记录）
- **不要自己发明 API 路径**：`create-with-qr` 返回的 JSON 里已有 `qrImage`（base64 PNG），直接用这个字段，不要另调 `/api/quiz/:id/qr` 等不存在的接口
- **先验证文件类型**：保存后用 `file` 命令确认是真正的 PNG 再发送
