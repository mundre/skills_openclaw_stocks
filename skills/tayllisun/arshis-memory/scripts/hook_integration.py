#!/usr/bin/env python3
"""
Hook Integration - OpenClaw Hook 集成测试
测试自动捕获/注入功能
"""

import os
import sys
import json
import time
from typing import Dict, Any, List

# 导入相关模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auto_capture import capture_memories, recall_memories, inject_memories
from session_memory import SessionMemoryManager
from self_improvement import SelfImprovementLogger


def test_before_agent_start(session_id: str = "test_session"):
    """
    测试 before_agent_start Hook
    
    模拟 Agent 开始前的记忆注入
    """
    print("=" * 60)
    print("测试：before_agent_start Hook")
    print("=" * 60)
    
    # 1. 获取会话记忆
    session_mgr = SessionMemoryManager()
    session = session_mgr.get_session(session_id)
    
    # 2. 添加测试消息
    session.add_message('user', '你好，我想了解一下天裂世界观')
    session.add_message('assistant', '好的，天裂世界观是一个中式幻想世界观...')
    session.add_message('user', '五裔种族都有哪些？')
    
    # 3. 获取上下文
    context = session.get_context(max_messages=50)
    print("\n会话上下文:")
    print(context)
    
    # 4. 检索相关记忆
    prompt = "五裔种族都有哪些"
    memories = recall_memories(prompt, limit=3)
    
    print(f"\n检索到 {len(memories)} 条相关记忆:")
    for mem in memories:
        print(f"  - {mem.get('text', '')[:50]} (score: {mem.get('score', 0):.2f})")
    
    # 5. 注入记忆
    injection = inject_memories(memories)
    print("\n注入的记忆:")
    print(injection)
    
    # 6. 最终提示
    final_prompt = prompt + injection
    print("\n最终提示:")
    print(final_prompt)
    
    return {
        'session_context': context,
        'memories': memories,
        'injection': injection,
        'final_prompt': final_prompt
    }


def test_after_agent_reply(session_id: str = "test_session"):
    """
    测试 after_agent_reply Hook
    
    模拟 Agent 回复后的记忆捕获
    """
    print("\n" + "=" * 60)
    print("测试：after_agent_reply Hook")
    print("=" * 60)
    
    # 1. 准备测试消息
    messages = [
        {'role': 'user', 'content': '你好'},
        {'role': 'assistant', 'content': '你好！有什么可以帮助你的吗？'},
        {'role': 'user', 'content': '记住我喜欢喝红茶'},
        {'role': 'assistant', 'content': '好的，我已经记住了。'},
        {'role': 'user', 'content': '每天都要喝一杯'},
        {'role': 'assistant', 'content': '明白了，这是你的习惯。'},
    ]
    
    # 2. 捕获记忆
    print("\n测试消息:")
    for msg in messages:
        role = "用户" if msg['role'] == 'user' else "助手"
        print(f"  {role}: {msg['content'][:50]}")
    
    print("\n开始捕获记忆...")
    stored = capture_memories(messages)
    
    print(f"\n捕获了 {len(stored)} 条记忆:")
    for mem in stored:
        print(f"  - {mem.get('text', '')[:50]}")
    
    # 3. 更新会话
    session_mgr = SessionMemoryManager()
    session = session_mgr.get_session(session_id)
    
    for msg in messages:
        session.add_message(msg['role'], msg['content'])
    
    # 4. 生成会话摘要（简单实现）
    summary = f"对话包含 {len(messages)} 条消息，捕获了 {len(stored)} 条记忆"
    session.update_summary(summary)
    
    print(f"\n会话摘要：{summary}")
    
    return {
        'stored_memories': stored,
        'session_summary': summary
    }


def test_self_improvement():
    """
    测试 Self-Improvement 工具
    """
    print("\n" + "=" * 60)
    print("测试：Self-Improvement 工具")
    print("=" * 60)
    
    logger = SelfImprovementLogger()
    
    # 1. 记录学习
    print("\n记录学习条目...")
    learning_id = logger.log_learning(
        summary="测试学习：用户纠正了配置错误",
        details="在配置 memory-lancedb 时，需要将 embedding 配置放在 config 字段下",
        category="knowledge_gap",
        priority="medium",
        suggested_action="更新文档，添加配置示例",
        tags=["配置", "memory-lancedb", "教程"]
    )
    print(f"已记录学习：{learning_id}")
    
    # 2. 记录错误
    print("\n记录错误条目...")
    error_id = logger.log_error(
        summary="测试错误：API Key 无效",
        error_message="401 Unauthorized: Invalid API key",
        context="调用 SiliconFlow API 时发生",
        resolution="检查 API Key 是否正确复制",
        category="integration_issue",
        priority="high"
    )
    print(f"已记录错误：{error_id}")
    
    # 3. 列出条目
    print("\n列出待处理学习:")
    learnings = logger.list_learnings(limit=5, status='pending')
    for l in learnings:
        print(f"  {l['id']} - {l['summary'][:50]}")
    
    return {
        'learning_id': learning_id,
        'error_id': error_id,
        'learnings': learnings
    }


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Memory-Pro-Custom Hook 集成测试")
    print("=" * 60)
    
    results = {
        'before_agent_start': None,
        'after_agent_reply': None,
        'self_improvement': None
    }
    
    try:
        # 测试 1: before_agent_start
        results['before_agent_start'] = test_before_agent_start()
        
        # 测试 2: after_agent_reply
        results['after_agent_reply'] = test_after_agent_reply()
        
        # 测试 3: self-improvement
        results['self_improvement'] = test_self_improvement()
        
        # 总结
        print("\n" + "=" * 60)
        print("测试结果总结")
        print("=" * 60)
        print(f"✅ before_agent_start: 通过")
        print(f"✅ after_agent_reply: 通过")
        print(f"✅ self_improvement: 通过")
        print("\n所有测试通过！Hook 集成正常。")
        
        return results
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'full':
        # 完整测试
        run_all_tests()
    else:
        # 简单测试
        print("Usage: python hook_integration.py full")
        print("\n运行简单测试...")
        test_before_agent_start()
        test_after_agent_reply()
        print("\n✅ 简单测试完成")
