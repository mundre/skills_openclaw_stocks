---
name: novel-character-graph
description: 从小说文本中提取人物关系，生成可视化人物关系图谱。当用户要求为小说绘制人物关系图、生成人物关系网络图、制作小说人物图谱时使用此技能。支持悬停查看人物详情、搜索、缩放拖拽。可处理 GBK/UTF-8 编码的中文 txt 文件。
allowed-tools: Read, Exec, Write, Edit
---

# 小说人物关系图谱

从小说文本中提取人物，构建并生成交互式人物关系可视化图谱。

## 核心流程

### 第一步：环境准备

```bash
# 检查依赖
python3 -c "import jieba, networkx, matplotlib, d3" 2>/dev/null || pip install jieba networkx matplotlib
```

### 第二步：分析小说结构

1. 读取文件（自动检测编码，支持 GBK/UTF-8/GB18030）
2. 按章节分割（匹配 `第X章` / `第X节` / `第X集` 模式）
3. 统计总章节数、总字数

```python
import re

def split_chapters(text):
    """按章节分割小说文本"""
    chapter_starts = []
    for m in re.finditer(r'第[一二三四五六七八九十百千\d]+[章节集]', text):
        chapter_starts.append(m.start())
    chapter_starts.append(len(text))
    return [text[chapter_starts[i]:chapter_starts[i+1]] for i in range(len(chapter_starts)-1)]
```

### 第三步：人物提取

#### 方式 A：预设人物列表（推荐）
提供一个人物字典 `{人名: 分组}`，通过共现分析计算关系权重。

```python
CHARACTERS = {
    '昌凡': '主角', '项涛': '主角挚友', '冰雪': '主角爱人',
    '青龙': '超级神兽', '朱韶': '主角挚友', '酆都大帝': '鬼界',
    # ... 覆盖小说主要人物
}
```

#### 方式 B：从文本自动提取（辅助）
从对话引号中提取更多角色名，过滤后追加到人物列表。

```python
# 从引号中提取人名
additional = defaultdict(int)
for ch in chapters:
    for m in re.finditer(r'["""](.{2,4})["""]', ch):
        if freq >= 50 and name not in KNOWN_CHARS:
            additional[name] += 1
```

### 第四步：关系提取

#### 共现关系（自动）
统计每对人物在同一章节出现的次数，作为关系权重。

```python
links_dict = defaultdict(lambda: {'weight': 0, 'label': ''})
for ch in chapters:
    chars_in_ch = [c for c in characters if c in ch]
    for i, c1 in enumerate(chars_in_ch):
        for c2 in chars_in_ch[i+1:]:
            key = tuple(sorted([c1, c2]))
            links_dict[key]['weight'] += 1
```

#### 预设关系（精确）
为重要人物对预设关系标签，权重更高。

```python
KNOWN_RELS = {
    ('昌凡', '冰雪'): '结发夫妻',
    ('昌凡', '项涛'): '义弟/结义兄弟',
    ('昌凡', '朱韶'): '师徒',
    ('昌凡', '酆都大帝'): '生死大敌',
    # ...
}
```

### 第五步：生成 D3.js 可视化

生成单个 HTML 文件，内嵌 D3.js 力导向图，通过 HTTP 服务器提供访问。

```python
# 输出文件: novel-character-graph.html
# 数据文件: graph_data.json
```

核心 HTML 结构：
- **节点颜色**：按分组（主角=金色、爱人=粉色、七星宗=蓝色、魔界=红色、鬼界=灰色等）
- **节点大小**：按出场频率
- **连线颜色**：强关系=金色、中=橙色、弱=深蓝
- **交互**：悬停显示详情、搜索高亮、缩放拖拽

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body { background: #0a0a0f; font-family: sans-serif; }
        .node circle { cursor: pointer; }
        .node text { font-size: 9px; fill: #fff; text-shadow: 0 0 2px #000; pointer-events: none; }
        #tooltip { position: absolute; background: rgba(15,15,30,0.98); border: 1px solid #558; border-radius: 12px; padding: 16px; pointer-events: none; opacity: 0; transition: opacity 0.2s; width: 360px; }
    </style>
</head>
<body>
    <!-- D3.js force-directed graph -->
</body>
</html>
```

### 第六步：提供访问

```bash
python3 -m http.server 8888
# 访问 http://localhost:8888/novel-character-graph.html
```

## 分组颜色方案

| 分组 | 颜色 | 示例 |
|------|------|------|
| 主角 | #FFD700 | 金色 |
| 主角爱人 | #FF6B9D | 粉色 |
| 主角挚友 | #FF69B4 | 浅粉 |
| 七星宗兄弟 | #4FC3F7 | 浅蓝 |
| 七星宗 | #29B6F6 | 蓝色 |
| 七星宗反派 | #EF5350 | 红色 |
| 凡间 | #FF9800 | 橙色 |
| 修妖界 | #81C784 | 绿色 |
| 超级神兽 | #BA68C8 | 紫色 |
| 上界/仙界 | #E040FB | 亮紫 |
| 魔界 | #F44336 | 深红 |
| 鬼界 | #90A4AE | 灰色 |

## 注意事项

1. **编码问题**：中文小说常用 GBK 编码，读取时需指定 `encoding='gbk'` 或 `errors='ignore'`
2. **章节分割**：不同小说章节标题格式不同，可调整正则 `第[一二三四五六七八九十百千\d]+[章节集]`
3. **关系噪音**：自动共现关系可能包含不准确的关系，需用预设关系覆盖
4. **人物数量**：超过200人时图会密集，可设置出场频率阈值过滤
5. **JSON 嵌入**：大数据集直接嵌入 HTML 可能导致浏览器解析错误，应使用外部 JSON 文件 + fetch/XHR 加载

## 输出格式

- `graph_data.json` — 人物和关系的 JSON 数据
- `character-graph.html` — D3.js 交互式可视化 HTML 文件
- `python3 -m http.server 8888` — 提供本地访问的 HTTP 服务器

## 人物描述丰富

为每个重要角色添加 `rich_desc` 字段，包含：
- 性格特点
- 与主角的关系
- 主要事迹

示例：
```json
{
  "id": "昌凡",
  "name": "昌凡",
  "group": "主角",
  "freq": 528,
  "rich_desc": "主角，从凡间到上界的传奇人物。性格坚毅果敢，重情重义，有原则有担当。"
}
```
