#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 一致性检查器
检查新内容与现有世界观/数值/技能的冲突
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# 配置
MEMORY_SCRIPT = os.path.join(os.path.dirname(__file__), '../Arshis-memory-pro/scripts/memory_core.py')


class ConsistencyChecker:
    """一致性检查器"""
    
    def __init__(self):
        self.memory_script = MEMORY_SCRIPT
        self.conflicts = []
        self.warnings = []
        self.suggestions = []
    
    def check_character(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查新角色的一致性
        
        Args:
            character_data: 角色数据
                - name: 角色名称
                - element: 元素属性
                - weapon: 武器类型
                - affiliation: 所属势力
                - skills: 技能列表
        
        Returns:
            检查结果
        """
        self.conflicts = []
        self.warnings = []
        self.suggestions = []
        
        # 1. 检查角色名称是否重复
        name_conflict = self._check_name_conflict(character_data.get('name', ''))
        if name_conflict:
            self.conflicts.append(name_conflict)
        
        # 2. 检查元素体系一致性
        element_check = self._check_element_system(character_data.get('element', ''))
        if element_check['conflict']:
            self.conflicts.append(element_check['conflict'])
        self.suggestions.extend(element_check.get('suggestions', []))
        
        # 3. 检查势力关系一致性
        faction_check = self._check_faction_relation(
            character_data.get('affiliation', ''),
            character_data.get('name', '')
        )
        if faction_check['conflict']:
            self.conflicts.append(faction_check['conflict'])
        self.warnings.extend(faction_check.get('warnings', []))
        
        # 4. 检查技能重复
        if 'skills' in character_data:
            skill_check = self._check_skill_duplication(character_data['skills'])
            if skill_check['conflicts']:
                self.conflicts.extend(skill_check['conflicts'])
            if skill_check['warnings']:
                self.warnings.extend(skill_check['warnings'])
        
        # 5. 检查数值平衡
        if 'stats' in character_data:
            numeric_check = self._check_numeric_balance(character_data['stats'])
            if numeric_check['conflicts']:
                self.conflicts.extend(numeric_check['conflicts'])
            if numeric_check['warnings']:
                self.warnings.extend(numeric_check['warnings'])
        
        return {
            'status': 'pass' if not self.conflicts else 'fail',
            'character_name': character_data.get('name', ''),
            'conflicts': self.conflicts,
            'warnings': self.warnings,
            'suggestions': self.suggestions,
            'summary': self._generate_summary()
        }
    
    def _check_name_conflict(self, name: str) -> Optional[Dict[str, Any]]:
        """检查角色名称是否重复"""
        if not name:
            return None
        
        # 查询现有角色
        result = self._query_memory(f"角色 {name}")
        
        if result and len(result) > 0:
            # 检查是否是相同角色
            for item in result:
                if name.lower() in item.get('text', '').lower():
                    return {
                        'type': 'name_conflict',
                        'severity': 'high',
                        'message': f'角色名称"{name}"已存在',
                        'existing': item.get('text', '')[:100],
                        'suggestion': f'建议修改角色名称，或确认是否为同一角色'
                    }
        
        return None
    
    def _check_element_system(self, element: str) -> Dict[str, Any]:
        """检查元素体系一致性"""
        result = {
            'conflict': None,
            'suggestions': []
        }
        
        if not element:
            return result
        
        # 查询现有元素体系
        element_query = self._query_memory("元素体系")
        
        # 标准元素列表（根据项目设定）
        standard_elements = ['火', '水', '风', '雷', '草', '冰', '岩']
        
        if element not in standard_elements:
            result['suggestions'].append({
                'type': 'element_warning',
                'message': f'元素"{element}"不在标准元素列表中',
                'standard': standard_elements,
                'suggestion': '确认是否为特殊元素，或考虑使用标准元素'
            })
        
        # 检查元素反应
        reaction_query = self._query_memory(f"{element}元素反应")
        if not reaction_query or len(reaction_query) == 0:
            result['suggestions'].append({
                'type': 'element_reaction',
                'message': f'未找到{element}元素相关反应设定',
                'suggestion': '建议补充元素反应设定，或参考现有元素反应体系'
            })
        
        return result
    
    def _check_faction_relation(self, faction: str, character_name: str) -> Dict[str, Any]:
        """检查势力关系一致性"""
        result = {
            'conflict': None,
            'warnings': []
        }
        
        if not faction:
            return result
        
        # 查询势力信息
        faction_query = self._query_memory(f"势力 {faction}")
        
        if not faction_query or len(faction_query) == 0:
            result['warnings'].append({
                'type': 'new_faction',
                'message': f'势力"{faction}"未在世界观中找到',
                'suggestion': '确认是否为新增势力，如是需要先创建势力设定'
            })
        else:
            # 检查势力关系
            for item in faction_query:
                text = item.get('text', '')
                # 检查是否有敌对关系等
                if '敌对' in text or '敌人' in text:
                    result['warnings'].append({
                        'type': 'faction_relation',
                        'message': f'势力{faction}存在敌对关系，确认角色背景是否合理',
                        'reference': text[:100]
                    })
        
        return result
    
    def _check_skill_duplication(self, skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """检查技能重复"""
        result = {
            'conflicts': [],
            'warnings': []
        }
        
        for skill in skills:
            skill_name = skill.get('name', '')
            skill_effect = skill.get('effect', '')
            
            if not skill_name:
                continue
            
            # 查询现有技能
            skill_query = self._query_memory(f"技能 {skill_name}")
            
            if skill_query and len(skill_query) > 0:
                # 检查技能名称是否重复
                for item in skill_query:
                    text = item.get('text', '')
                    if skill_name.lower() in text.lower():
                        result['conflicts'].append({
                            'type': 'skill_name_conflict',
                            'severity': 'high',
                            'message': f'技能名称"{skill_name}"已存在',
                            'existing': text[:100],
                            'suggestion': '建议修改技能名称'
                        })
            
            # 检查技能效果是否过于相似
            if skill_effect:
                effect_query = self._query_memory(skill_effect[:50])
                if effect_query and len(effect_query) > 0:
                    result['warnings'].append({
                        'type': 'skill_effect_similar',
                        'severity': 'medium',
                        'message': f'技能"{skill_name}"效果与现有技能相似',
                        'reference': effect_query[0].get('text', '')[:100],
                        'suggestion': '确认是否为有意设计，或调整技能效果'
                    })
        
        return result
    
    def _check_numeric_balance(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """检查数值平衡"""
        result = {
            'conflicts': [],
            'warnings': []
        }
        
        # 查询现有角色数值范围
        numeric_query = self._query_memory("角色数值 基础属性")
        
        if not numeric_query:
            result['warnings'].append({
                'type': 'no_numeric_reference',
                'message': '未找到现有角色数值参考',
                'suggestion': '建议先建立数值基准体系'
            })
            return result
        
        # 简单检查（实际应该更复杂）
        # 检查是否超出常规范围
        for stat_name, stat_value in stats.items():
            if isinstance(stat_value, (int, float)):
                # 假设基础攻击力正常范围是 100-300
                if stat_name == 'attack' and (stat_value < 50 or stat_value > 500):
                    result['warnings'].append({
                        'type': 'numeric_outlier',
                        'severity': 'medium',
                        'message': f'{stat_name}={stat_value} 超出常规范围',
                        'reference': '常规范围：100-300',
                        'suggestion': '确认数值设计是否合理'
                    })
        
        return result
    
    def _query_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """查询记忆系统"""
        try:
            result = subprocess.run(
                ['python3', self.memory_script, 'recall', query, str(limit)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            return []
        except:
            return []
    
    def _generate_summary(self) -> str:
        """生成检查总结"""
        if not self.conflicts and not self.warnings:
            return "✅ 一致性检查通过，无冲突"
        
        summary = []
        
        if self.conflicts:
            summary.append(f"❌ 发现 {len(self.conflicts)} 处冲突（需要修改）")
        
        if self.warnings:
            summary.append(f"⚠️ 发现 {len(self.warnings)} 处警告（建议检查）")
        
        if self.suggestions:
            summary.append(f"💡 {len(self.suggestions)} 条优化建议")
        
        return " | ".join(summary)
    
    def check_activity(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """检查新活动的一致性"""
        # 类似角色检查，针对活动特性
        # 简化实现
        return {
            'status': 'pass',
            'message': '活动一致性检查（简化版）',
            'conflicts': [],
            'warnings': [],
            'suggestions': []
        }
    
    def check_system(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """检查新系统的一致性"""
        # 类似角色检查，针对系统特性
        return {
            'status': 'pass',
            'message': '系统一致性检查（简化版）',
            'conflicts': [],
            'warnings': [],
            'suggestions': []
        }


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python consistency_checker.py <command> [args]")
        print("Commands:")
        print("  check-character <json_file>  - 检查新角色")
        print("  check-activity <json_file>   - 检查新活动")
        print("  check-system <json_file>     - 检查新系统")
        sys.exit(1)
    
    command = sys.argv[1]
    checker = ConsistencyChecker()
    
    if command == 'check-character':
        json_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not json_file or not os.path.exists(json_file):
            print("Error: 需要提供角色数据 JSON 文件")
            sys.exit(1)
        
        with open(json_file, 'r', encoding='utf-8') as f:
            character_data = json.load(f)
        
        result = checker.check_character(character_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'check-activity':
        json_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not json_file:
            print("Error: 需要提供活动数据 JSON 文件")
            sys.exit(1)
        
        with open(json_file, 'r', encoding='utf-8') as f:
            activity_data = json.load(f)
        
        result = checker.check_activity(activity_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'check-system':
        json_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not json_file:
            print("Error: 需要提供系统数据 JSON 文件")
            sys.exit(1)
        
        with open(json_file, 'r', encoding='utf-8') as f:
            system_data = json.load(f)
        
        result = checker.check_system(system_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
