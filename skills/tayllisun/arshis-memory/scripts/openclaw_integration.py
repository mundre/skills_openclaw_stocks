#!/usr/bin/env python3
"""
OpenClaw 工具集成
让 memory_store/memory_recall 工具调用自制记忆系统
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, List, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_CORE = os.path.join(SCRIPT_DIR, 'memory_core.py')
SMART_EXTRACT = os.path.join(SCRIPT_DIR, 'smart_extract.py')


def run_command(args: List[str]) -> Dict[str, Any]:
    """运行 Python 脚本并返回 JSON 结果"""
    result = subprocess.run(
        ['python3'] + args,
        capture_output=True,
        text=True,
        cwd=SCRIPT_DIR
    )
    
    try:
        return json.loads(result.stdout)
    except:
        return {
            'error': result.stderr,
            'output': result.stdout
        }


def memory_store(text: str, importance: float = 0.5, category: str = '其他') -> Dict[str, Any]:
    """
    存储记忆（对应 OpenClaw memory_store 工具）
    
    Args:
        text: 记忆内容
        importance: 重要性 (0-1)
        category: 分类（人物/事件/知识/偏好/地点/时间/其他）
    
    Returns:
        {'id': 'xxx', 'status': 'stored', 'text': '...'}
    """
    # 先用 LLM 提取结构化信息
    extract_result = run_command([SMART_EXTRACT, text])
    
    # 使用提取的结果（如果有）
    if 'category' in extract_result and not extract_result.get('error'):
        category = extract_result.get('category', category)
        importance = extract_result.get('importance', importance)
    
    # 存储记忆
    return run_command([MEMORY_CORE, 'store', text, str(importance), category])


def memory_recall(query: str, limit: int = 5, memory_range: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    检索记忆（对应 OpenClaw memory_recall 工具）
    
    Args:
        query: 搜索关键词
        limit: 返回数量
        memory_range: 记忆范围过滤 (core/working/peripheral/None)
    
    Returns:
        [{'id': 'xxx', 'text': '...', 'score': 0.8, ...}]
    """
    args = [MEMORY_CORE, 'recall', query, str(limit)]
    if memory_range:
        args.append(memory_range)
    
    return run_command(args)


def memory_list(limit: int = 20) -> List[Dict[str, Any]]:
    """列出所有记忆"""
    return run_command([MEMORY_CORE, 'list', str(limit)])


def memory_stats() -> Dict[str, Any]:
    """查看统计"""
    return run_command([MEMORY_CORE, 'stats'])


def memory_delete(memory_id: str) -> Dict[str, Any]:
    """删除记忆"""
    return run_command([MEMORY_CORE, 'delete', memory_id])


def lifecycle_stats() -> Dict[str, Any]:
    """查看生命周期统计"""
    result = subprocess.run(
        ['python3', os.path.join(SCRIPT_DIR, 'lifecycle.py'), 'stats'],
        capture_output=True,
        text=True
    )
    return {'output': result.stdout}


def lifecycle_update_all() -> Dict[str, Any]:
    """更新所有记忆的重要性"""
    result = subprocess.run(
        ['python3', os.path.join(SCRIPT_DIR, 'lifecycle.py'), 'update-all'],
        capture_output=True,
        text=True
    )
    return {'output': result.stdout}


# 命令行测试
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python openclaw_integration.py <command> [args]")
        print("Commands:")
        print("  store <text> [importance] [category]  - 存储记忆")
        print("  recall <query> [limit]                - 检索记忆")
        print("  list [limit]                          - 列出记忆")
        print("  stats                                 - 查看统计")
        print("  delete <id>                           - 删除记忆")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'store':
        text = sys.argv[2] if len(sys.argv) > 2 else ''
        importance = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
        category = sys.argv[4] if len(sys.argv) > 4 else '其他'
        result = memory_store(text, importance, category)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'recall':
        query = sys.argv[2] if len(sys.argv) > 2 else ''
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        result = memory_recall(query, limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'list':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        result = memory_list(limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'stats':
        result = memory_stats()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'delete':
        memory_id = sys.argv[2] if len(sys.argv) > 2 else ''
        result = memory_delete(memory_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'lifecycle-stats':
        result = lifecycle_stats()
        print(result['output'])
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)
