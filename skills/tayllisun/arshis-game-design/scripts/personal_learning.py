#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 个性化学习模块
学习用户偏好，定制建议风格
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List


class PersonalLearning:
    """个性化学习器"""
    
    def __init__(self, knowledge_dir: str = None):
        self.knowledge_dir = knowledge_dir or os.path.dirname(__file__)
        self.preference_file = os.path.join(self.knowledge_dir, 'user_preferences.json')
        self.interaction_log = os.path.join(self.knowledge_dir, 'interaction_log.json')
        
        # 加载用户偏好
        self.preferences = self._load_preferences()
        
        # 加载交互日志
        self.interactions = self._load_interactions()
    
    def _load_preferences(self) -> Dict[str, Any]:
        """加载用户偏好"""
        if os.path.exists(self.preference_file):
            with open(self.preference_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认偏好
        return {
            'created_at': datetime.now().isoformat(),
            'design_style': {
                'complexity': 'balanced',  # simple/balanced/complex
                'innovation': 'balanced',  # conservative/balanced/innovative
                'detail_level': 'high'  # low/medium/high
            },
            'game_types': [],  # 常设计的游戏类型
            'preferred_features': [],  # 偏好功能
            'avoid_features': [],  # 避免功能
            'suggestion_style': 'detailed',  # brief/detailed/technical
            'last_updated': datetime.now().isoformat()
        }
    
    def _load_interactions(self) -> Dict[str, Any]:
        """加载交互日志"""
        if os.path.exists(self.interaction_log):
            with open(self.interaction_log, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            'total_interactions': 0,
            'interactions': [],
            'accepted_suggestions': 0,
            'rejected_suggestions': 0,
            'modified_suggestions': 0
        }
    
    def record_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        记录交互
        
        Args:
            interaction: 交互数据
                - type: 交互类型（suggestion/query/feedback）
                - content: 交互内容
                - result: 结果（accepted/rejected/modified）
                - feedback: 反馈内容
        
        Returns:
            记录结果
        """
        interaction_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': interaction.get('type', 'unknown'),
            'content': interaction.get('content', '')[:500],
            'result': interaction.get('result', 'unknown'),
            'feedback': interaction.get('feedback', '')
        }
        
        self.interactions['total_interactions'] += 1
        self.interactions['interactions'].append(interaction_entry)
        
        # 统计结果
        if interaction_entry['result'] == 'accepted':
            self.interactions['accepted_suggestions'] += 1
        elif interaction_entry['result'] == 'rejected':
            self.interactions['rejected_suggestions'] += 1
        elif interaction_entry['result'] == 'modified':
            self.interactions['modified_suggestions'] += 1
        
        # 保存交互日志
        self._save_interactions()
        
        # 分析交互，更新偏好
        self._analyze_interaction(interaction_entry)
        
        return {
            'status': 'recorded',
            'interaction_id': interaction_entry['timestamp'],
            'total_interactions': self.interactions['total_interactions']
        }
    
    def _analyze_interaction(self, interaction: Dict[str, Any]):
        """分析交互，更新偏好"""
        # 分析接受的建议类型
        if interaction['result'] == 'accepted':
            content = interaction['content']
            
            # 提取游戏类型
            game_types = ['rpg', 'moba', 'fps', 'slg', 'gacha', 'indie', 'roguelike']
            for game_type in game_types:
                if game_type in content.lower():
                    if game_type not in self.preferences['game_types']:
                        self.preferences['game_types'].append(game_type)
            
            # 提取偏好功能
            feature_keywords = {
                'open_world': ['开放世界', '探索', '自由'],
                'story': ['剧情', '叙事', '故事'],
                'combat': ['战斗', '动作', '技能'],
                'social': ['社交', '多人', '联机'],
                'strategy': ['策略', '战术', '规划']
            }
            
            for feature, keywords in feature_keywords.items():
                if any(kw in content for kw in keywords):
                    if feature not in self.preferences['preferred_features']:
                        self.preferences['preferred_features'].append(feature)
        
        # 更新最后更新时间
        self.preferences['last_updated'] = datetime.now().isoformat()
        
        # 保存偏好
        self._save_preferences()
    
    def _save_preferences(self):
        """保存用户偏好"""
        with open(self.preference_file, 'w', encoding='utf-8') as f:
            json.dump(self.preferences, f, ensure_ascii=False, indent=2)
    
    def _save_interactions(self):
        """保存交互日志"""
        with open(self.interaction_log, 'w', encoding='utf-8') as f:
            json.dump(self.interactions, f, ensure_ascii=False, indent=2)
    
    def get_personalized_suggestion(self, base_suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取个性化建议
        
        Args:
            base_suggestion: 基础建议
        
        Returns:
            个性化建议
        """
        personalized = base_suggestion.copy()
        
        # 根据偏好调整详细程度
        style = self.preferences.get('suggestion_style', 'detailed')
        if style == 'brief':
            # 简化建议
            personalized['detail_level'] = 'brief'
        elif style == 'technical':
            # 增加技术细节
            personalized['detail_level'] = 'technical'
        
        # 根据偏好游戏类型调整
        game_types = self.preferences.get('game_types', [])
        if game_types:
            personalized['preferred_game_types'] = game_types
        
        # 根据偏好功能调整
        preferred_features = self.preferences.get('preferred_features', [])
        if preferred_features:
            personalized['focus_features'] = preferred_features
        
        return personalized
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """获取学习统计"""
        total = self.interactions['total_interactions']
        accepted = self.interactions['accepted_suggestions']
        rejected = self.interactions['rejected_suggestions']
        modified = self.interactions['modified_suggestions']
        
        acceptance_rate = accepted / total if total > 0 else 0
        
        return {
            'total_interactions': total,
            'accepted_suggestions': accepted,
            'rejected_suggestions': rejected,
            'modified_suggestions': modified,
            'acceptance_rate': f"{acceptance_rate*100:.1f}%",
            'preferred_game_types': self.preferences.get('game_types', []),
            'preferred_features': self.preferences.get('preferred_features', []),
            'suggestion_style': self.preferences.get('suggestion_style', 'detailed')
        }
    
    def reset_preferences(self):
        """重置用户偏好"""
        self.preferences = self._load_preferences()
        self._save_preferences()
        
        return {
            'status': 'reset',
            'message': '用户偏好已重置'
        }
    
    def export_preferences(self) -> Dict[str, Any]:
        """导出用户偏好"""
        return {
            'preferences': self.preferences,
            'stats': self.get_learning_stats()
        }


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python personal_learning.py <command> [args]")
        print("Commands:")
        print("  record <json>              - 记录交互")
        print("  stats                      - 查看学习统计")
        print("  export                     - 导出偏好")
        print("  reset                      - 重置偏好")
        sys.exit(1)
    
    command = sys.argv[1]
    learner = PersonalLearning()
    
    if command == 'record':
        interaction_json = sys.argv[2] if len(sys.argv) > 2 else '{}'
        interaction_data = json.loads(interaction_json)
        
        result = learner.record_interaction(interaction_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'stats':
        stats = learner.get_learning_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    elif command == 'export':
        export = learner.export_preferences()
        print(json.dumps(export, ensure_ascii=False, indent=2))
    
    elif command == 'reset':
        result = learner.reset_preferences()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
