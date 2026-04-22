---
name: content-writer
description: Content creation assistant. Writes articles, blog posts, marketing copy, and technical documentation. Triggers: content writing, copywriting, blog post, technical writing.
metadata: {"openclaw": {"emoji": "✍️"}}
---

# Content Writer — 内容创作助手

## 功能说明

根据需求创作各类文本内容。

## 使用方法

### 1. 技术文档

```
用户: 为这个API写一份文档：
[API描述或代码]
```

文档结构：
- 概述
- 接口列表
- 请求/响应示例
- 错误码说明
- 最佳实践

### 2. 博客文章

```
用户: 写一篇关于"Python异步编程"的博客文章，1500字左右
```

文章结构：
- 引人入胜的开头
- 核心概念讲解
- 代码示例
- 实战应用
- 总结

### 3. 营销文案

```
用户: 为一款AI写作工具写营销文案，目标用户是内容创作者
```

文案要素：
- 痛点共鸣
- 产品价值
- 使用场景
- 行动号召

### 4. 工作报告

```
用户: 根据以下数据写一份周报：
[工作数据/任务列表]
```

报告结构：
- 本周完成
- 数据亮点
- 遇到问题
- 下周计划

## 写作风格

可指定风格：
- 正式/专业
- 轻松/口语化
- 技术/教程
- 营销/说服

## 示例输出

```
# Python异步编程完全指南

## 为什么需要异步？

在传统同步编程中，当程序执行I/O操作（如网络请求、文件读写）时，
整个程序会阻塞等待操作完成。这对于高并发场景是巨大的浪费...

[继续正文]

## 快速上手

```python
import asyncio

async def fetch_data():
    # 异步获取数据
    await asyncio.sleep(1)
    return "data"

# 运行异步函数
result = asyncio.run(fetch_data())
```

## 实战案例

假设我们需要同时获取100个API的数据...

[继续正文]

## 总结

异步编程通过非阻塞I/O大幅提升了程序的并发处理能力...
```

## 注意事项

- 保持内容原创性
- 引用数据注明来源
- 代码示例确保可运行
- 适配目标读者水平
