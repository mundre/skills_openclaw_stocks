# Knowledge Connector

Knowledge Connector 的价值，不是“帮你建一个图”，而是把散落在不同文档里的知识变成可搜索、可解释、可行动的知识图谱结果。

这次升级重点收敛到 5 件事：
- 更像向导的导入入口
- 更顺手的导入体验
- 真正的跨文档搜索
- 更容易检查关系的可视化
- 带下一步建议的图谱结果

## 它适合什么问题

- “把这个目录里的笔记都导进来”
- “这个概念到底在哪些文档里出现过”
- “哪些文档之间其实在讲同一件事”
- “围绕这个概念画一个能看懂的关系图”
- “图谱出来以后，我下一步该补什么、查什么、连什么”

## 现在的核心体验

### 1. 导入文档

```bash
kc import-wizard --dir notes/
kc import-docs --dir notes/
kc import-docs --files intro.md roadmap.md ideas.txt
```

导入后会告诉你：
- 预计会导入多少文件
- 支持哪些文件类型
- 导入了多少文档
- 抽出了多少概念
- 自动补了多少关系

### 2. 跨文档搜索

```bash
kc search "强化学习"
kc answer "哪些文档把规划和强化学习连起来了？"
kc query "transformer" --sources
kc query --ask "哪些文档同时提到了规划和强化学习？"
```

搜索结果不只给概念，还会给：
- 命中的来源文档
- 相关关系
- 下一步建议

`kc answer` 会把这些结果整理成更像答案页的输出，也可以保存成 HTML。

### 3. 概念子图

```bash
kc map --concept "人工智能" --depth 2
```

这个命令适合做“围绕一个主题看局部图谱”，比直接扔一整张大图更可操作。

### 4. 图谱可视化

```bash
kc visualize --format html --output graph.html
kc visualize --concept "机器学习" --depth 2 --output ml-graph.html
```

生成的 HTML 图现在会同时显示：
- 图谱本身
- 下一步建议
- 常用后续命令提示

## 为什么这条产品线值得继续做

因为用户装它，不是为了“又一个知识技能”，而是为了更快回答这些问题：
- 我的知识散在哪里
- 哪些概念其实互相关联
- 哪些文档值得一起看
- 下一步该补什么，而不是只把图存下来

## 安装

```bash
clawhub install knowledge-connector
```

## 一句话卖点

把分散文档变成可导入、可回答、可视化、可行动的知识图谱结果。
