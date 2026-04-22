#!/usr/bin/env python3
"""
Game-Design-Pro - 世界观管理器
管理世界观设定、角色档案、势力关系、时间线等
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime

# 配置
MEMORY_SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    '../Arshis-memory-pro/scripts/memory_core.py'
)


class WorldviewManager:
    """世界观管理器"""
    
    def __init__(self):
        self.memory_script = MEMORY_SCRIPT
    
    def store_worldview(self, category: str, content: str, 
                        importance: float = 0.9) -> Dict[str, Any]:
        """
        存储世界观设定
        
        Args:
            category: 分类 (worldview/character/faction/location/history)
            content: 设定内容
            importance: 重要性 (世界观默认 0.9，永久保存)
        
        Returns:
            存储结果
        """
        category_map = {
            'worldview': '知识',
            'character': '人物',
            'faction': '知识',
            'location': '知识',
            'history': '知识'
        }
        
        chinese_category = category_map.get(category, '知识')
        
        # 调用记忆存储
        result = self._run_memory_script(
            'store', content, str(importance), chinese_category
        )
        
        return result
    
    def query_worldview(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        查询世界观设定
        
        Args:
            query: 查询关键词
            limit: 返回数量
        
        Returns:
            相关设定列表
        """
        result = self._run_memory_script('recall', query, str(limit))
        
        if isinstance(result, list):
            return result
        return []
    
    def check_consistency(self, new_content: str) -> Dict[str, Any]:
        """
        检查新世界观设定与现有设定的一致性
        
        Args:
            new_content: 新设定内容
        
        Returns:
            一致性检查结果
        """
        # 提取关键词
        keywords = self._extract_keywords(new_content)
        
        # 查询相关设定
        related = []
        for kw in keywords:
            results = self.query_worldview(kw, limit=3)
            related.extend(results)
        
        # 分析一致性
        conflicts = []
        for item in related:
            conflict = self._check_conflict(new_content, item)
            if conflict:
                conflicts.append(conflict)
        
        return {
            'consistent': len(conflicts) == 0,
            'related_settings': related,
            'conflicts': conflicts,
            'suggestions': self._generate_suggestions(conflicts)
        }
    
    def _run_memory_script(self, command: str, *args) -> Any:
        """运行记忆脚本"""
        cmd = ['python3', self.memory_script, command] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        try:
            return json.loads(result.stdout)
        except:
            return {'error': result.stderr, 'output': result.stdout}
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词（简化版）"""
        # 实际应该用 NLP 提取，这里简化处理
        keywords = []
        
        # 提取人名（假设包含"是"、"叫"等）
        if '是' in content:
            for line in content.split('\n'):
                if '是' in line:
                    keywords.append(line.split('是')[0].strip()[:10])
        
        # 提取地名（假设包含"位于"、"在"等）
        if '位于' in content:
            keywords.append('地点')
        
        # 提取势力（假设包含"势力"、"组织"等）
        if '势力' in content or '组织' in content:
            keywords.append('势力')
        
        return list(set(keywords))[:5]
    
    def _check_conflict(self, new_content: str, existing: Dict) -> Optional[Dict]:
        """检查冲突（简化版）"""
        # 实际应该用 LLM 检查，这里简化处理
        if existing.get('text') and existing['text'] in new_content:
            return None  # 内容一致
        
        # 这里可以添加更复杂的冲突检测逻辑
        return None
    
    def _generate_suggestions(self, conflicts: List) -> List[str]:
        """生成修改建议"""
        if not conflicts:
            return ["设定与现有世界观一致，无需修改"]
        
        return [
            f"发现 {len(conflicts)} 处潜在冲突，建议检查相关设定",
            "建议与主策划确认冲突点",
            "建议更新世界观文档保持一致"
        ]


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python worldview_manager.py <command> [args]")
        print("Commands:")
        print("  store <category> <content>  - 存储设定")
        print("  query <keyword>             - 查询设定")
        print("  check <content>             - 一致性检查")
        sys.exit(1)
    
    command = sys.argv[1]
    manager = WorldviewManager()
    
    if command == 'store':
        category = sys.argv[2] if len(sys.argv) > 2 else 'worldview'
        content = sys.argv[3] if len(sys.argv) > 3 else ''
        if not content:
            print("Error: 需要设定内容")
            sys.exit(1)
        
        result = manager.store_worldview(category, content)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'query':
        keyword = sys.argv[2] if len(sys.argv) > 2 else ''
        if not keyword:
            print("Error: 需要关键词")
            sys.exit(1)
        
        results = manager.query_worldview(keyword)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    elif command == 'check':
        content = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else ''
        if not content:
            print("Error: 需要设定内容")
            sys.exit(1)
        
        result = manager.check_consistency(content)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
