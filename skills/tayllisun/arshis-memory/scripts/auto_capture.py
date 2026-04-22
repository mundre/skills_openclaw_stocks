#!/usr/bin/env python3
"""
Memory Auto-Capture - 自动记忆捕获和注入
用于 OpenClaw Hook 集成
"""

import os
import sys
import json
import time
from typing import Dict, Any, List, Optional
from openclaw_integration import memory_store, memory_recall

# 配置
CONFIG_FILE = os.path.expanduser('~/.openclaw/data/memory-custom-config.json')
AUTO_CAPTURE_ENABLED = True
AUTO_RECALL_ENABLED = True
CAPTURE_MIN_MESSAGES = 3  # 最少消息数触发捕获
RECALL_MIN_LENGTH = 20    # 最少字符数触发检索
RECALL_MIN_REPEATED = 0   # 重复检索间隔（轮次）


def load_config() -> Dict[str, Any]:
    """加载配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def should_capture(messages: List[Dict[str, str]]) -> bool:
    """
    判断是否应该捕获记忆
    
    Args:
        messages: 对话消息列表
    
    Returns:
        是否捕获
    """
    if not AUTO_CAPTURE_ENABLED:
        return False
    
    # 检查消息数量
    if len(messages) < CAPTURE_MIN_MESSAGES:
        return False
    
    # 检查是否有用户消息
    user_messages = [m for m in messages if m.get('role') == 'user']
    if len(user_messages) < 2:
        return False
    
    return True


def should_recall(prompt: str, session_history: List[Dict]) -> bool:
    """
    判断是否应该检索记忆
    
    Args:
        prompt: 当前提示
        session_history: 会话历史
    
    Returns:
        是否检索
    """
    if not AUTO_RECALL_ENABLED:
        return False
    
    # 检查提示长度
    if len(prompt) < RECALL_MIN_LENGTH:
        return False
    
    return True


def extract_memory_candidates(messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    从对话中提取候选记忆
    
    Args:
        messages: 对话消息列表
    
    Returns:
        候选记忆列表
    """
    candidates = []
    
    # 提取用户消息中的重要信息
    for msg in messages:
        if msg.get('role') == 'user':
            content = msg.get('content', '')
            
            # 简单规则：包含特定关键词的消息可能是重要记忆
            memory_keywords = [
                '记住', '记一下', '重要的是', '注意', '关键',
                '喜欢', '讨厌', '经常', '每天', '习惯',
                '是', '叫', '名字', '身份', '职业',
                '世界观', '设定', '背景', '故事'
            ]
            
            if any(kw in content for kw in memory_keywords):
                # 使用智能提取
                from smart_extract import SmartExtractor
                config = load_config()
                extractor = SmartExtractor(config)
                
                try:
                    result = extractor.extract(content)
                    candidates.append({
                        'text': content,
                        'category': result.get('category', '其他'),
                        'importance': result.get('importance', 0.5),
                        'keywords': result.get('keywords', [])
                    })
                except:
                    # 提取失败，使用默认值
                    candidates.append({
                        'text': content,
                        'category': '其他',
                        'importance': 0.5,
                        'keywords': []
                    })
    
    return candidates


def capture_memories(messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    捕获并存储记忆
    
    Args:
        messages: 对话消息列表
    
    Returns:
        存储的记忆列表
    """
    if not should_capture(messages):
        return []
    
    candidates = extract_memory_candidates(messages)
    stored = []
    
    for candidate in candidates:
        try:
            result = memory_store(
                text=candidate['text'],
                importance=candidate.get('importance', 0.5),
                category=candidate.get('category', '其他')
            )
            if result.get('status') == 'stored':
                stored.append(result)
        except Exception as e:
            print(f"存储记忆失败：{e}")
    
    return stored


def recall_memories(prompt: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    检索相关记忆
    
    Args:
        prompt: 查询提示
        limit: 返回数量
    
    Returns:
        记忆列表
    """
    if not should_recall(prompt, []):
        return []
    
    try:
        memories = memory_recall(prompt, limit=limit)
        return memories
    except Exception as e:
        print(f"检索记忆失败：{e}")
        return []


def inject_memories(memories: List[Dict[str, Any]]) -> str:
    """
    将记忆注入到提示中
    
    Args:
        memories: 记忆列表
    
    Returns:
        注入的记忆文本
    """
    if not memories:
        return ""
    
    injection_text = "\n\n【相关记忆】\n"
    for mem in memories:
        injection_text += f"- {mem.get('text', '')} (相关性：{mem.get('score', 0):.2f})\n"
    
    return injection_text


# Hook 接口函数

def before_agent_start(session_id: str, prompt: str, messages: List[Dict]) -> Dict[str, Any]:
    """
    Agent 开始前 Hook - 自动检索并注入记忆
    
    Args:
        session_id: 会话 ID
        prompt: 当前提示
        messages: 消息历史
    
    Returns:
        修改后的提示（包含注入的记忆）
    """
    memories = recall_memories(prompt, limit=3)
    injection = inject_memories(memories)
    
    return {
        'prompt': prompt + injection,
        'memories': memories
    }


def after_agent_reply(session_id: str, messages: List[Dict], reply: str) -> Dict[str, Any]:
    """
    Agent 回复后 Hook - 自动捕获记忆
    
    Args:
        session_id: 会话 ID
        messages: 完整消息历史
        reply: Agent 回复
    
    Returns:
        捕获的记忆列表
    """
    stored = capture_memories(messages)
    
    return {
        'stored_memories': stored
    }


# 命令行测试
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python auto_capture.py <command> [args]")
        print("Commands:")
        print("  test-capture  - 测试捕获功能")
        print("  test-recall   - 测试检索功能")
        print("  config        - 查看配置")
        sys.exit(1)
    
    command = sys.argv[1]
    config = load_config()
    
    if command == 'test-capture':
        # 模拟对话
        test_messages = [
            {'role': 'user', 'content': '你好'},
            {'role': 'assistant', 'content': '你好！有什么可以帮助你的吗？'},
            {'role': 'user', 'content': '记住我喜欢喝红茶'},
            {'role': 'assistant', 'content': '好的，我已经记住了。'},
            {'role': 'user', 'content': '每天都要喝一杯'},
        ]
        
        print("测试自动捕获...")
        stored = capture_memories(test_messages)
        print(f"捕获了 {len(stored)} 条记忆:")
        for mem in stored:
            print(f"  - {mem.get('text', '')[:50]}")
    
    elif command == 'test-recall':
        test_prompt = "公子喜欢什么饮料"
        print(f"测试自动检索：{test_prompt}")
        memories = recall_memories(test_prompt, limit=3)
        print(f"检索到 {len(memories)} 条记忆:")
        for mem in memories:
            print(f"  - {mem.get('text', '')[:50]} (score: {mem.get('score', 0):.2f})")
    
    elif command == 'config':
        print("当前配置:")
        print(json.dumps(config, indent=2, ensure_ascii=False))
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)
