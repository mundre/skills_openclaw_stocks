# 小说人物关系图谱 - Skill

从小说文本中提取人物关系，生成交互式 D3.js 可视化图谱。

## 功能特性

- ✅ 自动检测文件编码（GBK/UTF-8/GB18030）
- ✅ 智能章节分割
- ✅ 人物共现关系提取
- ✅ 预设关系标签（夫妻、师徒、仇敌等）
- ✅ 分组着色（主角/爱人/挚友/七星宗/仙界/魔界/鬼界等）
- ✅ 交互式 D3.js 力导向图
- ✅ 悬停查看人物详情和关系
- ✅ 搜索高亮
- ✅ 缩放拖拽

## 快速开始

```bash
# 启动 HTTP 服务器
cd /path/to/novel
python3 -m http.server 8888

# 访问
open http://localhost:8888/character-graph.html
```

## 目录结构

```
novel-character-graph/
├── SKILL.md              # Skill 说明文档
├── _meta.json            # 元数据
├── scripts/
│   ├── extract_graph.py  # 人物关系提取脚本
│   └── generate_html.py  # HTML 生成脚本
├── examples/
│   └── example_characters.py  # 示例人物列表
└── README.md
```

## 使用方法

### 方式一：命令行

```bash
# 提取关系数据
python3 scripts/extract_graph.py /path/to/novel.txt

# 生成 HTML 可视化
python3 scripts/generate_html.py graph_data.json character-graph.html "小说名"
```

### 方式二：在 OpenClaw 中使用

当用户要求为小说绘制人物关系图时，此 Skill 将自动被触发，按照 SKILL.md 中的流程执行。

## 依赖

- Python 3.7+
- jieba（中文分词）
- d3.js v7（通过 CDN 加载，无需安装）

## 扩展使用

### 添加新人物

编辑 `examples/example_characters.py`，添加人物到 `CHARACTERS` 字典：

```python
CHARACTERS = {
    '新人物': '分组',  # 分组：主角/主角爱人/主角挚友/七星宗/上界/魔界/鬼界/其他
}
```

### 添加预设关系

编辑 `examples/example_characters.py`，添加关系到 `RELATIONSHIPS` 字典：

```python
RELATIONSHIPS = {
    ('人物A', '人物B'): '关系描述',
}
```
