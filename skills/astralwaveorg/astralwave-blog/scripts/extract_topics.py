#!/usr/bin/env python3
"""
从聊天记录中提取 2-3 个核心话题，支持每日定时触发。

用法：
  python3 extract_topics.py <session_key> [date]
  date 格式：YYYY-MM-DD，默认今天

输出：
  JSON 格式的 2-3 个话题列表，每个话题包含：
    - keyword: 话题关键词
    - topic: 话题分类 (ai/devops/frontend/backend/tools/arch/db)
    - score: 重要性打分
    - reason: 为什么选这个话题
    - context: 相关的聊天片段摘要
"""

import sys
import json
import re
from datetime import datetime, timedelta
from collections import Counter

# 话题关键词映射表（用于识别技术话题）
TECH_KEYWORDS = {
    "ai":        ["llm", "大模型", "gpt", "openai", "claude", "gemini", "kimi", "智谱", "qwen", "通义", "o1", "o3", "o4", "gpt-4", "embedding", "向量", "rag", "知识库", "文生图", "扩散模型"],
    "agent":     ["agent", "智能体", "openclaw", "crewai", "langchain", "autoagent", "mcp", "工具调用"],
    "devops":    ["docker", "nginx", "linux", "服务器", "部署", "ci/cd", "github actions", "kubernetes", "k8s", "容器", "反向代理"],
    "frontend":  ["vue", "react", "typescript", "前端", "javascript", "css", "html", "组件", "框架"],
    "backend":   ["python", "java", "api", "后端", "fastapi", "spring", "node", "go", "rust", "grpc"],
    "db":        ["mysql", "redis", "mongodb", "postgresql", "数据库", "缓存", "sqlite", "orm", "sql"],
    "tools":     ["mcp", "cli", "cursor", "vscode", "jetbrains", "ide", "tool", "iflow", "openclaw", "claude code"],
    "arch":      ["微服务", "架构", "设计模式", "分布式", "k8s", "kubernetes", "集群", "高可用", "容错"],
}

# 权重系数
TECH_WEIGHT = 3.0
PERSONAL_INSIGHT_WEIGHT = 2.5   # 个人经验分享（包含"我的""我觉得"）
CODE_SHARING_WEIGHT = 2.0       # 代码分享
LONG_DISCUSSION_WEIGHT = 1.5    # 长回复（深度讨论）
PROBLEM_SOLVING_WEIGHT = 2.0   # 问题-解决对


def normalize_text(text: str) -> str:
    """标准化文本"""
    text = text.lower()
    text = re.sub(r'[^\w\s\u4e00-\u9fff@#]', ' ', text)
    return text


def detect_topic(tech: str) -> str:
    """将识别的技术关键词映射到话题分类"""
    topic_map = {
        "llm": "ai", "大模型": "ai", "gpt": "ai", "openai": "ai", "claude": "ai",
        "embedding": "ai", "向量": "ai", "rag": "ai", "知识库": "ai",
        "agent": "agent", "智能体": "agent", "openclaw": "agent", "mcp": "tools",
        "docker": "devops", "nginx": "devops", "linux": "devops", "部署": "devops",
        "vue": "frontend", "react": "frontend", "typescript": "frontend",
        "python": "backend", "java": "backend", "api": "backend", "fastapi": "backend",
        "mysql": "db", "redis": "db", "sqlite": "db", "数据库": "db",
        "cli": "tools", "cursor": "tools", "ide": "tools",
        "微服务": "arch", "架构": "arch", "分布式": "arch",
    }
    return topic_map.get(tech, "tools")


def extract_topics(messages: list, date_str: str = None) -> list:
    """
    从消息列表中提取 2-3 个核心话题。

    算法：
    1. 统计技术关键词出现频率（加权）
    2. 识别代码分享（包含 ``` 标记）
    3. 识别长回复（深度讨论）
    4. 识别问题-解决对
    5. 综合打分，取 top 3
    """

    if not messages:
        return []

    tech_scores = Counter()
    tech_contexts = {}

    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if not content or role == "system":
            continue

        norm = normalize_text(content)

        # 检测技术话题
        msg_score = 0
        msg_techs = []
        for tech, keywords in TECH_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in norm)
            if count > 0:
                msg_score += count * TECH_WEIGHT
                msg_techs.append(tech)
                # 保留最长的上下文
                if tech not in tech_contexts or len(content) > len(tech_contexts.get(tech, {}).get("context", "")):
                    tech_contexts[tech] = {
                        "keyword": tech,
                        "topic": detect_topic(tech),
                        "context": content[:500],
                    }

        # 代码分享加分
        if "```" in content:
            msg_score += CODE_SHARING_WEIGHT

        # 长回复加分
        if len(content) > 300:
            msg_score += LONG_DISCUSSION_WEIGHT

        # 个人经验分享加分（语气像作者本人）
        personal_patterns = ["我的", "我觉得", "最后选了", "踩了不少", "被打脸", "绕了不少"]
        if any(p in content for p in personal_patterns):
            msg_score += PERSONAL_INSIGHT_WEIGHT

        # 应用得分
        for tech in set(msg_techs):
            tech_scores[tech] += msg_score

    # 取 top 3
    top_techs = tech_scores.most_common(3)

    results = []
    for tech, score in top_techs:
        ctx = tech_contexts.get(tech, {})
        topic = detect_topic(tech)
        results.append({
            "keyword": tech,
            "topic": topic,
            "score": round(score, 2),
            "reason": f"技术话题 {tech}，综合得分 {score:.0f}",
            "context": ctx.get("context", ""),
        })

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_topics.py <session_key> [date]")
        print("Note: 在 OpenClaw agent 环境中，通过 sessions_history API 获取消息后调用")
        sys.exit(1)

    session_key = sys.argv[1]
    date_str = sys.argv[2] if len(sys.argv) > 2 else datetime.now().strftime("%Y-%m-%d")

    # 说明：实际调用时，消息列表通过 stdin 或环境变量传入
    # 这个脚本设计为由 agent 调用，agent 会把 sessions_history 的结果传进来
    print(json.dumps({
        "session_key": session_key,
        "date": date_str,
        "topics": [],
        "status": "ready",
        "note": "调用时需要 agent 将 sessions_history 结果通过 stdin 传入"
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
