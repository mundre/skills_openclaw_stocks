#!/usr/bin/env python3
"""
Session Memory - 会话级记忆管理
为每个会话维护独立的短期记忆
"""

import os
import sys
import json
import time
import hashlib
from typing import Dict, Any, List, Optional

SESSION_DIR = os.path.expanduser('~/.openclaw/data/memory-sessions')


class SessionMemory:
    """会话记忆管理器"""
    
    def __init__(self, session_id: str):
        """
        初始化会话记忆
        
        Args:
            session_id: 会话唯一标识
        """
        self.session_id = session_id
        self.session_file = os.path.join(SESSION_DIR, f'{session_id}.json')
        self.messages = []
        self.summary = ""
        self.created_at = int(time.time())
        self.updated_at = int(time.time())
        
        self._load()
    
    def _load(self):
        """加载会话记忆"""
        if os.path.exists(self.session_file):
            with open(self.session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.messages = data.get('messages', [])
                self.summary = data.get('summary', '')
                self.created_at = data.get('created_at', int(time.time()))
                self.updated_at = data.get('updated_at', int(time.time()))
    
    def _save(self):
        """保存会话记忆"""
        os.makedirs(SESSION_DIR, exist_ok=True)
        data = {
            'session_id': self.session_id,
            'messages': self.messages,
            'summary': self.summary,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_message(self, role: str, content: str):
        """
        添加消息到会话
        
        Args:
            role: 角色 (user/assistant)
            content: 消息内容
        """
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': int(time.time())
        })
        self.updated_at = int(time.time())
        self._save()
    
    def get_recent_messages(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取最近的消息
        
        Args:
            limit: 返回数量
        
        Returns:
            消息列表
        """
        return self.messages[-limit:]
    
    def update_summary(self, summary: str):
        """
        更新会话摘要
        
        Args:
            summary: 摘要内容
        """
        self.summary = summary
        self.updated_at = int(time.time())
        self._save()
    
    def get_context(self, max_messages: int = 50) -> str:
        """
        获取会话上下文（用于注入到提示）
        
        Args:
            max_messages: 最大消息数
        
        Returns:
            格式化的上下文字符串
        """
        context_parts = []
        
        # 添加摘要
        if self.summary:
            context_parts.append(f"[会话摘要]\n{self.summary}\n")
        
        # 添加最近消息
        recent = self.get_recent_messages(max_messages)
        if recent:
            context_parts.append("[最近对话]")
            for msg in recent:
                role = "用户" if msg['role'] == 'user' else "助手"
                content = msg['content'][:200]  # 截断过长内容
                context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def clear(self):
        """清空会话记忆"""
        self.messages = []
        self.summary = ""
        self.updated_at = int(time.time())
        self._save()
    
    def delete(self):
        """删除会话"""
        if os.path.exists(self.session_file):
            os.remove(self.session_file)


class SessionMemoryManager:
    """会话记忆管理器（全局）"""
    
    def __init__(self):
        self.sessions = {}
        self._load_sessions()
    
    def _load_sessions(self):
        """加载所有会话列表"""
        if os.path.exists(SESSION_DIR):
            for filename in os.listdir(SESSION_DIR):
                if filename.endswith('.json'):
                    session_id = filename[:-5]
                    self.sessions[session_id] = SessionMemory(session_id)
    
    def get_session(self, session_id: str) -> SessionMemory:
        """
        获取或创建会话
        
        Args:
            session_id: 会话 ID
        
        Returns:
            SessionMemory 实例
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionMemory(session_id)
        return self.sessions[session_id]
    
    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        列出所有会话
        
        Args:
            limit: 返回数量
        
        Returns:
            会话列表
        """
        session_list = []
        for session_id, session in self.sessions.items():
            session_list.append({
                'session_id': session_id,
                'message_count': len(session.messages),
                'summary': session.summary[:50] if session.summary else '',
                'created_at': session.created_at,
                'updated_at': session.updated_at
            })
        
        # 按更新时间排序
        session_list.sort(key=lambda x: x['updated_at'], reverse=True)
        return session_list[:limit]
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话 ID
        
        Returns:
            是否成功删除
        """
        if session_id in self.sessions:
            self.sessions[session_id].delete()
            del self.sessions[session_id]
            return True
        return False


# 命令行接口
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python session_memory.py <command> [args]")
        print("Commands:")
        print("  list              - 列出所有会话")
        print("  get <session_id>  - 获取会话详情")
        print("  delete <id>       - 删除会话")
        print("  clear <id>        - 清空会话")
        sys.exit(1)
    
    command = sys.argv[1]
    manager = SessionMemoryManager()
    
    if command == 'list':
        sessions = manager.list_sessions(20)
        print(f"共 {len(sessions)} 个会话:")
        for s in sessions:
            print(f"  {s['session_id'][:8]}... - {s['message_count']} 条消息 - {s['summary'][:30]}")
    
    elif command == 'get':
        session_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not session_id:
            print("Error: 需要 session_id")
            sys.exit(1)
        
        session = manager.get_session(session_id)
        print(f"会话：{session_id}")
        print(f"创建时间：{time.strftime('%Y-%m-%d %H:%M', time.localtime(session.created_at))}")
        print(f"消息数：{len(session.messages)}")
        print(f"摘要：{session.summary or '无'}")
        print("\n最近消息:")
        for msg in session.get_recent_messages(10):
            role = "用户" if msg['role'] == 'user' else "助手"
            print(f"  {role}: {msg['content'][:100]}")
    
    elif command == 'delete':
        session_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not session_id:
            print("Error: 需要 session_id")
            sys.exit(1)
        
        if manager.delete_session(session_id):
            print(f"已删除会话：{session_id}")
        else:
            print(f"会话不存在：{session_id}")
    
    elif command == 'clear':
        session_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not session_id:
            print("Error: 需要 session_id")
            sys.exit(1)
        
        session = manager.get_session(session_id)
        session.clear()
        print(f"已清空会话：{session_id}")
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)
