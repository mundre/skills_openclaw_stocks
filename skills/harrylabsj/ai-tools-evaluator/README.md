# AI Tools Evaluator V1

AI 工具对比评测助手 MVP

## 运行方式

```bash
cd /Users/jianghaidong/.openclaw/workspace/agents/code/ai-tools-evaluator
python3 evaluator.py
```

## 交互流程

1. 选择 2~5 个要对比的工具（输入编号，空格分隔）
2. 选择使用场景（1-6）
3. 选择预算区间（1-4）
4. 确认维度权重（直接回车用默认）
5. 查看生成的对比报告
6. 报告自动保存到 `ai_tools_report.md`

## 技术栈

- Python 3（标准库 + pyperclip 可选）
- 静态 JSON 数据（工具池 19 个工具，5 大类别）

## 工具池（19个）

- LLM大模型：ChatGPT, Claude, Gemini, DeepSeek, 通义千问, 零一万物
- AI搜索：Perplexity, 秘塔AI, 玄紫AI
- AI写作：Claude写作版, 文心一言, 智谱清言
- AI代码：GitHub Copilot, Cursor, 腾飞AI
- AI图像：Midjourney, DALL-E 3, Stable Diffusion, 文心一格
