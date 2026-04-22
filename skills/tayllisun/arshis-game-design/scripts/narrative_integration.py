#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 叙事整合系统
整合世界观/剧情/关卡/玩法
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime


class NarrativeIntegrator:
    """叙事整合器"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), 'output', 'integration')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def integrate_worldview_gameplay(self, worldview: Dict[str, Any], 
                                      gameplay: Dict[str, Any]) -> Dict[str, Any]:
        """
        整合世界观与玩法
        
        Args:
            worldview: 世界观数据
            gameplay: 玩法数据
        
        Returns:
            整合方案
        """
        integration = {
            'worldview_elements': [],
            'gameplay_integration': [],
            'consistency_check': []
        }
        
        # 世界观要素指导关卡设计
        if 'geography' in worldview:
            for location in worldview['geography'].get('locations', []):
                integration['worldview_elements'].append({
                    'type': 'location',
                    'name': location.get('name', ''),
                    'gameplay_application': '可设计为关卡场景'
                })
        
        # 势力关系指导阵营系统
        if 'factions' in worldview:
            integration['gameplay_integration'].append({
                'type': 'faction_system',
                'source': '世界观势力',
                'implementation': '阵营声望系统'
            })
        
        # 力量体系指导职业/技能系统
        if 'power_system' in worldview:
            integration['gameplay_integration'].append({
                'type': 'class_system',
                'source': '世界观力量体系',
                'implementation': '职业/技能系统'
            })
        
        return {
            'status': 'integrated',
            'integration': integration,
            'tips': [
                '世界观指导关卡设计',
                '势力关系指导阵营系统',
                '力量体系指导职业系统',
                '文化背景指导 NPC 设计'
            ]
        }
    
    def integrate_story_mission(self, story: Dict[str, Any],
                                 mission: Dict[str, Any]) -> Dict[str, Any]:
        """
        整合剧情与任务
        
        Args:
            story: 剧情数据
            mission: 任务数据
        
        Returns:
            整合方案
        """
        integration = {
            'main_story_missions': [],
            'side_missions': [],
            'character_missions': []
        }
        
        # 主线剧情转化为任务链
        if 'main_story' in story:
            integration['main_story_missions'].append({
                'type': 'story_chain',
                'source': '主线剧情',
                'implementation': '任务链设计'
            })
        
        # 角色背景转化为传说任务
        if 'characters' in story:
            integration['character_missions'].append({
                'type': 'character_quest',
                'source': '角色背景',
                'implementation': '传说任务设计'
            })
        
        return {
            'status': 'integrated',
            'integration': integration,
            'tips': [
                '主线剧情转化为任务链',
                '角色背景转化为传说任务',
                '世界观探索转化为支线',
                '势力冲突转化为阵营任务'
            ]
        }
    
    def generate_integration_report(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成整合报告
        
        Args:
            project_data: 项目数据（包含世界观/剧情/玩法）
        
        Returns:
            整合报告
        """
        report = {
            'project_name': project_data.get('name', 'Unnamed Project'),
            'worldview_gameplay_integration': {},
            'story_mission_integration': {},
            'character_progression_integration': {},
            'consistency_score': 0,
            'recommendations': []
        }
        
        # 世界观 - 玩法整合
        if 'worldview' in project_data and 'gameplay' in project_data:
            report['worldview_gameplay_integration'] = self.integrate_worldview_gameplay(
                project_data['worldview'],
                project_data['gameplay']
            )
        
        # 剧情 - 任务整合
        if 'story' in project_data and 'mission' in project_data:
            report['story_mission_integration'] = self.integrate_story_mission(
                project_data['story'],
                project_data['mission']
            )
        
        # 一致性评分
        report['consistency_score'] = 85  # 简化评分
        
        # 建议
        report['recommendations'] = [
            '确保世界观指导玩法设计',
            '剧情与任务紧密结合',
            '角色成长与玩家成长同步',
            '定期检查一致性'
        ]
        
        # 保存报告
        filename = f"integration_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return {
            'status': 'generated',
            'filepath': filepath,
            'filename': filename,
            'report': report
        }


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python narrative_integration.py <command> [args]")
        print("Commands:")
        print("  report <json_file>         - 生成整合报告")
        sys.exit(1)
    
    command = sys.argv[1]
    integrator = NarrativeIntegrator()
    
    if command == 'report':
        json_file = sys.argv[2] if len(sys.argv) > 2 else None
        if not json_file:
            print("Error: 需要提供 JSON 文件")
            sys.exit(1)
        
        with open(json_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        result = integrator.generate_integration_report(project_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
