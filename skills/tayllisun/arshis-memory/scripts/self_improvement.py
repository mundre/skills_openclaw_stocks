#!/usr/bin/env python3
"""
Self-Improvement - 学习治理工具
记录经验教训，支持技能提取和审查
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

LEARNING_FILE = os.path.expanduser('~/.openclaw/workspace/.learnings/LEARNINGS.md')
ERROR_FILE = os.path.expanduser('~/.openclaw/workspace/.learnings/ERRORS.md')


class SelfImprovementLogger:
    """学习治理日志器"""
    
    def __init__(self):
        self.learning_file = LEARNING_FILE
        self.error_file = ERROR_FILE
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """确保文件存在"""
        os.makedirs(os.path.dirname(self.learning_file), exist_ok=True)
        for filepath in [self.learning_file, self.error_file]:
            if not os.path.exists(filepath):
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("# Learning Log\n\n记录经验教训、用户纠正、最佳实践。\n\n---\n\n")
    
    def _generate_id(self, prefix: str = 'LRN') -> str:
        """生成学习条目 ID"""
        date_str = datetime.now().strftime('%Y%m%d')
        # 简单计数
        if os.path.exists(self.learning_file):
            with open(self.learning_file, 'r', encoding='utf-8') as f:
                content = f.read()
                count = content.count(f'## [{prefix}-{date_str}-')
                return f'{prefix}-{date_str}-{count + 1:03d}'
        return f'{prefix}-{date_str}-001'
    
    def log_learning(self, summary: str, details: str = '', 
                     category: str = 'correction', priority: str = 'medium',
                     suggested_action: str = '', tags: List[str] = None) -> str:
        """
        记录学习条目
        
        Args:
            summary: 一句话摘要
            details: 详细上下文
            category: 分类 (correction/best_practice/knowledge_gap)
            priority: 优先级 (low/medium/high/critical)
            suggested_action: 建议行动
            tags: 标签列表
        
        Returns:
            学习条目 ID
        """
        learning_id = self._generate_id('LRN')
        timestamp = datetime.now().isoformat()
        tags_str = ', '.join(tags) if tags else ''
        
        entry = f"""## [{learning_id}] {category}

**Logged**: {timestamp}
**Priority**: {priority}
**Status**: pending

### Summary
{summary}

### Details
{details}

### Suggested Action
{suggested_action or '待补充'}

### Metadata
- Category: {category}
- Priority: {priority}
- Tags: {tags_str}

---

"""
        
        with open(self.learning_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        return learning_id
    
    def log_error(self, summary: str, error_message: str = '', 
                  context: str = '', resolution: str = '',
                  category: str = 'correction', priority: str = 'high') -> str:
        """
        记录错误条目
        
        Args:
            summary: 一句话摘要
            error_message: 错误信息
            context: 上下文
            resolution: 解决方案
            category: 分类 (correction/bug_fix/integration_issue)
            priority: 优先级
        
        Returns:
            错误条目 ID
        """
        error_id = self._generate_id('ERR')
        timestamp = datetime.now().isoformat()
        
        entry = f"""## [{error_id}] {category}

**Logged**: {timestamp}
**Priority**: {priority}
**Status**: {'resolved' if resolution else 'pending'}

### Summary
{summary}

### Error Message
```
{error_message}
```

### Context
{context}

### Resolution
{resolution or '待解决'}

---

"""
        
        with open(self.error_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        return error_id
    
    def list_learnings(self, limit: int = 10, status: str = 'pending') -> List[Dict[str, Any]]:
        """
        列出学习条目
        
        Args:
            limit: 返回数量
            status: 状态过滤 (pending/resolved)
        
        Returns:
            学习条目列表
        """
        learnings = []
        
        if os.path.exists(self.learning_file):
            with open(self.learning_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 简单解析（可以改进为更健壮的解析）
                entries = content.split('## [')[1:]
                for entry in entries[:limit]:
                    lines = entry.split('\n')
                    learning_id = lines[0].split(']')[0]
                    summary = ''
                    status_line = ''
                    
                    for line in lines:
                        if line.startswith('**Summary**'):
                            summary = lines[lines.index(line) + 1]
                        if line.startswith('**Status**'):
                            status_line = line.split(': ')[1] if ': ' in line else ''
                    
                    if status == 'all' or status.lower() in status_line.lower():
                        learnings.append({
                            'id': learning_id,
                            'summary': summary,
                            'status': status_line
                        })
        
        return learnings
    
    def mark_resolved(self, learning_id: str):
        """
        标记学习条目为已解决
        
        Args:
            learning_id: 学习条目 ID
        """
        if os.path.exists(self.learning_file):
            with open(self.learning_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换状态
            old_status = f'**ID**: {learning_id}'
            # 简单实现，可以改进为更精确的替换
            content = content.replace(
                f'[{learning_id}]',
                f'[{learning_id}] ✅'
            )
            
            with open(self.learning_file, 'w', encoding='utf-8') as f:
                f.write(content)


# 命令行接口
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python self_improvement.py <command> [args]")
        print("Commands:")
        print("  log-learning <summary> [details]  - 记录学习")
        print("  log-error <summary> [error_msg]   - 记录错误")
        print("  list [pending|resolved|all]       - 列出条目")
        print("  resolve <id>                      - 标记为已解决")
        sys.exit(1)
    
    command = sys.argv[1]
    logger = SelfImprovementLogger()
    
    if command == 'log-learning':
        summary = sys.argv[2] if len(sys.argv) > 2 else ''
        details = sys.argv[3] if len(sys.argv) > 3 else ''
        if not summary:
            print("Error: 需要 summary")
            sys.exit(1)
        
        learning_id = logger.log_learning(summary, details)
        print(f"已记录学习：{learning_id}")
    
    elif command == 'log-error':
        summary = sys.argv[2] if len(sys.argv) > 2 else ''
        error_msg = sys.argv[3] if len(sys.argv) > 3 else ''
        if not summary:
            print("Error: 需要 summary")
            sys.exit(1)
        
        error_id = logger.log_error(summary, error_msg)
        print(f"已记录错误：{error_id}")
    
    elif command == 'list':
        status = sys.argv[2] if len(sys.argv) > 2 else 'pending'
        learnings = logger.list_learnings(10, status)
        print(f"共 {len(learnings)} 条学习:")
        for l in learnings:
            print(f"  {l['id']} - {l['summary'][:50]} [{l['status']}]")
    
    elif command == 'resolve':
        learning_id = sys.argv[2] if len(sys.argv) > 2 else ''
        if not learning_id:
            print("Error: 需要 learning_id")
            sys.exit(1)
        
        logger.mark_resolved(learning_id)
        print(f"已标记为已解决：{learning_id}")
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)
