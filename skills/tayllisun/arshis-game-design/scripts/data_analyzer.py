#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 数据分析模块
接入运营数据，提供平衡性分析和建议
"""

import os
import json
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class DataAnalyzer:
    """数据分析器"""
    
    def __init__(self, use_mock_data: bool = True):
        """
        初始化数据分析器
        
        Args:
            use_mock_data: 是否使用模拟数据（True=模拟，False=接入实际 API）
        """
        self.use_mock_data = use_mock_data
        self.data_cache = {}
    
    def analyze_character_balance(self, characters: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        分析角色平衡性
        
        Args:
            characters: 角色列表（可选，不提供则使用模拟数据）
        
        Returns:
            平衡性分析报告
        """
        if not characters:
            characters = self._get_mock_character_data()
        
        # 计算统计数据
        stats = self._calculate_character_stats(characters)
        
        # 识别不平衡角色
        imbalanced = self._identify_imbalanced_characters(characters, stats)
        
        # 生成调整建议
        suggestions = self._generate_balance_suggestions(imbalanced)
        
        return {
            'analysis_type': 'character_balance',
            'timestamp': datetime.now().isoformat(),
            'total_characters': len(characters),
            'statistics': stats,
            'imbalanced_characters': imbalanced,
            'suggestions': suggestions,
            'summary': self._generate_balance_summary(stats, imbalanced)
        }
    
    def analyze_activity_performance(self, activity_id: str = None) -> Dict[str, Any]:
        """
        分析活动表现
        
        Args:
            activity_id: 活动 ID
        
        Returns:
            活动分析报告
        """
        # 模拟活动数据
        activity_data = self._get_mock_activity_data(activity_id)
        
        # 分析参与率
        participation_analysis = self._analyze_participation(activity_data)
        
        # 分析奖励产出
        reward_analysis = self._analyze_rewards(activity_data)
        
        # 分析玩家反馈
        feedback_analysis = self._analyze_feedback(activity_data)
        
        return {
            'analysis_type': 'activity_performance',
            'activity_id': activity_id or 'mock_activity',
            'timestamp': datetime.now().isoformat(),
            'participation': participation_analysis,
            'rewards': reward_analysis,
            'feedback': feedback_analysis,
            'suggestions': self._generate_activity_suggestions(
                participation_analysis, reward_analysis, feedback_analysis
            )
        }
    
    def analyze_numeric_trends(self, data_type: str = 'character_stats') -> Dict[str, Any]:
        """
        分析数值趋势
        
        Args:
            data_type: 数据类型（character_stats/economy/combat）
        
        Returns:
            趋势分析报告
        """
        trends = self._calculate_numeric_trends(data_type)
        
        return {
            'analysis_type': 'numeric_trends',
            'data_type': data_type,
            'timestamp': datetime.now().isoformat(),
            'trends': trends,
            'outliers': self._identify_outliers(trends),
            'recommendations': self._generate_trend_recommendations(trends)
        }
    
    def _get_mock_character_data(self) -> List[Dict[str, Any]]:
        """获取模拟角色数据"""
        return [
            {
                'id': 'char_001',
                'name': '温迪',
                'element': '风',
                'rarity': 5,
                'usage_rate': 0.65,  # 使用率 65%
                'win_rate': 0.52,    # 胜率 52%
                'avg_damage': 15000,
                'support_rating': 0.85,  # 辅助评分
                'dps_rating': 0.45       # 输出评分
            },
            {
                'id': 'char_002',
                'name': '迪卢克',
                'element': '火',
                'rarity': 5,
                'usage_rate': 0.45,
                'win_rate': 0.48,
                'avg_damage': 18000,
                'support_rating': 0.30,
                'dps_rating': 0.75
            },
            {
                'id': 'char_003',
                'name': '刻晴',
                'element': '雷',
                'rarity': 5,
                'usage_rate': 0.38,
                'win_rate': 0.44,
                'avg_damage': 16000,
                'support_rating': 0.40,
                'dps_rating': 0.65
            },
            {
                'id': 'char_004',
                'name': '琴',
                'element': '风',
                'rarity': 5,
                'usage_rate': 0.25,
                'win_rate': 0.55,
                'avg_damage': 8000,
                'support_rating': 0.95,
                'dps_rating': 0.25
            },
            {
                'id': 'char_005',
                'name': '诺艾尔',
                'element': '岩',
                'rarity': 4,
                'usage_rate': 0.15,
                'win_rate': 0.42,
                'avg_damage': 12000,
                'support_rating': 0.60,
                'dps_rating': 0.50
            }
        ]
    
    def _get_mock_activity_data(self, activity_id: str) -> Dict[str, Any]:
        """获取模拟活动数据"""
        return {
            'activity_id': activity_id or 'activity_2025_spring',
            'name': '春季祭典',
            'duration_days': 14,
            'start_date': (datetime.now() - timedelta(days=30)).isoformat(),
            'metrics': {
                'dau': 500000,  # 日活跃用户
                'participation_rate': 0.68,  # 参与率 68%
                'completion_rate': 0.45,     # 完成率 45%
                'avg_playtime': 120,         # 平均游玩时间（分钟）
                'revenue': 2500000,          # 收入（元）
                'player_satisfaction': 0.78  # 玩家满意度
            },
            'rewards': {
                'total_distributed': 10000000,  # 总产出
                'currency_distributed': 5000000,  # 货币产出
                'item_distributed': 5000000       # 道具产出
            },
            'feedback': {
                'positive': 0.65,
                'neutral': 0.25,
                'negative': 0.10,
                'common_complaints': [
                    '活动难度过高',
                    '奖励不够吸引人',
                    '活动时间太短'
                ]
            }
        }
    
    def _calculate_character_stats(self, characters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算角色统计数据"""
        if not characters:
            return {}
        
        usage_rates = [c['usage_rate'] for c in characters]
        win_rates = [c['win_rate'] for c in characters]
        damages = [c['avg_damage'] for c in characters]
        
        return {
            'avg_usage_rate': sum(usage_rates) / len(usage_rates),
            'avg_win_rate': sum(win_rates) / len(win_rates),
            'avg_damage': sum(damages) / len(damages),
            'max_usage': max(usage_rates),
            'min_usage': min(usage_rates),
            'max_win_rate': max(win_rates),
            'min_win_rate': min(win_rates),
            'usage_std_dev': self._calculate_std_dev(usage_rates),
            'win_rate_std_dev': self._calculate_std_dev(win_rates)
        }
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """计算标准差"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _identify_imbalanced_characters(self, characters: List[Dict], 
                                         stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别不平衡角色"""
        imbalanced = []
        
        for char in characters:
            issues = []
            
            # 检查使用率异常
            if char['usage_rate'] > stats['avg_usage_rate'] + 2 * stats['usage_std_dev']:
                issues.append({
                    'type': 'overused',
                    'severity': 'high',
                    'message': f'使用率过高 ({char["usage_rate"]*100:.1f}%)',
                    'suggestion': '考虑削弱或增加限制'
                })
            elif char['usage_rate'] < stats['avg_usage_rate'] - 2 * stats['usage_std_dev']:
                issues.append({
                    'type': 'underused',
                    'severity': 'medium',
                    'message': f'使用率过低 ({char["usage_rate"]*100:.1f}%)',
                    'suggestion': '考虑增强或重做'
                })
            
            # 检查胜率异常
            if char['win_rate'] > 0.60:
                issues.append({
                    'type': 'high_win_rate',
                    'severity': 'high',
                    'message': f'胜率过高 ({char["win_rate"]*100:.1f}%)',
                    'suggestion': '需要削弱'
                })
            elif char['win_rate'] < 0.40:
                issues.append({
                    'type': 'low_win_rate',
                    'severity': 'medium',
                    'message': f'胜率过低 ({char["win_rate"]*100:.1f}%)',
                    'suggestion': '需要增强'
                })
            
            # 检查伤害异常
            if char['avg_damage'] > stats['avg_damage'] * 1.5:
                issues.append({
                    'type': 'high_damage',
                    'severity': 'high',
                    'message': f'伤害过高 ({char["avg_damage"]:,.0f})',
                    'suggestion': '调整伤害倍率'
                })
            
            if issues:
                imbalanced.append({
                    'character_id': char['id'],
                    'character_name': char['name'],
                    'issues': issues,
                    'priority': 'high' if any(i['severity'] == 'high' for i in issues) else 'medium'
                })
        
        return imbalanced
    
    def _generate_balance_suggestions(self, imbalanced: List[Dict]) -> List[Dict[str, Any]]:
        """生成平衡性建议"""
        suggestions = []
        
        for char in imbalanced:
            for issue in char['issues']:
                suggestions.append({
                    'character': char['character_name'],
                    'issue': issue['message'],
                    'suggestion': issue['suggestion'],
                    'priority': issue['severity']
                })
        
        return suggestions
    
    def _generate_balance_summary(self, stats: Dict, imbalanced: List) -> str:
        """生成平衡性总结"""
        if not imbalanced:
            return "✅ 角色平衡性良好，无需调整"
        
        high_priority = sum(1 for c in imbalanced if c['priority'] == 'high')
        medium_priority = len(imbalanced) - high_priority
        
        return f"⚠️ 发现 {len(imbalanced)} 个不平衡角色 " \
               f"({high_priority} 高优先级，{medium_priority} 中优先级)"
    
    def _analyze_participation(self, activity_data: Dict) -> Dict[str, Any]:
        """分析活动参与率"""
        metrics = activity_data['metrics']
        
        # 评估参与率
        if metrics['participation_rate'] > 0.70:
            participation_rating = 'excellent'
        elif metrics['participation_rate'] > 0.50:
            participation_rating = 'good'
        elif metrics['participation_rate'] > 0.30:
            participation_rating = 'average'
        else:
            participation_rating = 'poor'
        
        return {
            'participation_rate': metrics['participation_rate'],
            'rating': participation_rating,
            'dau': metrics['dau'],
            'completion_rate': metrics['completion_rate'],
            'avg_playtime': metrics['avg_playtime']
        }
    
    def _analyze_rewards(self, activity_data: Dict) -> Dict[str, Any]:
        """分析活动奖励"""
        rewards = activity_data['rewards']
        metrics = activity_data['metrics']
        
        # 计算人均产出
        per_player_reward = rewards['total_distributed'] / (metrics['dau'] * metrics['participation_rate'])
        
        return {
            'total_distributed': rewards['total_distributed'],
            'per_player_reward': per_player_reward,
            'currency_ratio': rewards['currency_distributed'] / rewards['total_distributed'],
            'item_ratio': rewards['item_distributed'] / rewards['total_distributed']
        }
    
    def _analyze_feedback(self, activity_data: Dict) -> Dict[str, Any]:
        """分析玩家反馈"""
        feedback = activity_data['feedback']
        
        sentiment_score = (
            feedback['positive'] * 1.0 +
            feedback['neutral'] * 0.5 +
            feedback['negative'] * 0.0
        )
        
        return {
            'sentiment_score': sentiment_score,
            'positive_ratio': feedback['positive'],
            'negative_ratio': feedback['negative'],
            'common_complaints': feedback['common_complaints']
        }
    
    def _generate_activity_suggestions(self, participation: Dict, 
                                        rewards: Dict, feedback: Dict) -> List[Dict[str, Any]]:
        """生成活动优化建议"""
        suggestions = []
        
        # 参与率建议
        if participation['rating'] == 'poor':
            suggestions.append({
                'type': 'participation',
                'priority': 'high',
                'message': '参与率过低，建议降低活动门槛或增加奖励',
                'current': f"{participation['participation_rate']*100:.1f}%"
            })
        
        # 奖励建议
        if rewards['per_player_reward'] < 1000:
            suggestions.append({
                'type': 'rewards',
                'priority': 'medium',
                'message': '人均奖励偏低，建议增加奖励产出',
                'current': f"{rewards['per_player_reward']:,.0f}"
            })
        
        # 反馈建议
        if feedback['sentiment_score'] < 0.6:
            suggestions.append({
                'type': 'feedback',
                'priority': 'high',
                'message': '玩家满意度偏低，需要优化活动设计',
                'common_complaints': feedback['common_complaints']
            })
        
        return suggestions
    
    def _calculate_numeric_trends(self, data_type: str) -> Dict[str, Any]:
        """计算数值趋势"""
        # 模拟趋势数据
        return {
            'data_type': data_type,
            'time_range': 'last_30_days',
            'metrics': {
                'avg_character_power': {
                    'current': 15000,
                    'previous': 14500,
                    'change': 0.034  # +3.4%
                },
                'avg_clear_time': {
                    'current': 180,  # 秒
                    'previous': 185,
                    'change': -0.027  # -2.7%
                },
                'player_satisfaction': {
                    'current': 0.78,
                    'previous': 0.75,
                    'change': 0.040  # +4.0%
                }
            }
        }
    
    def _identify_outliers(self, trends: Dict) -> List[Dict[str, Any]]:
        """识别异常值"""
        outliers = []
        
        for metric_name, metric_data in trends.get('metrics', {}).items():
            change = metric_data.get('change', 0)
            
            if abs(change) > 0.10:  # 变化超过 10%
                outliers.append({
                    'metric': metric_name,
                    'change': change,
                    'severity': 'high' if abs(change) > 0.20 else 'medium',
                    'message': f'{metric_name} 变化 {change*100:+.1f}%'
                })
        
        return outliers
    
    def _generate_trend_recommendations(self, trends: Dict) -> List[Dict[str, Any]]:
        """生成趋势建议"""
        recommendations = []
        
        metrics = trends.get('metrics', {})
        
        # 角色强度增长过快
        if metrics.get('avg_character_power', {}).get('change', 0) > 0.05:
            recommendations.append({
                'type': 'power_creep',
                'priority': 'high',
                'message': '角色强度增长过快，存在数值膨胀风险',
                'suggestion': '控制新角色强度，避免数值膨胀'
            })
        
        # 通关时间过短
        if metrics.get('avg_clear_time', {}).get('current', 999) < 120:
            recommendations.append({
                'type': 'content_difficulty',
                'priority': 'medium',
                'message': '内容通关时间过短，玩家可能过快消耗内容',
                'suggestion': '增加内容难度或深度'
            })
        
        return recommendations


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python data_analyzer.py <command> [args]")
        print("Commands:")
        print("  character-balance  - 分析角色平衡性")
        print("  activity <id>      - 分析活动表现")
        print("  numeric-trends     - 分析数值趋势")
        sys.exit(1)
    
    command = sys.argv[1]
    analyzer = DataAnalyzer(use_mock_data=True)
    
    if command == 'character-balance':
        result = analyzer.analyze_character_balance()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'activity':
        activity_id = sys.argv[2] if len(sys.argv) > 2 else None
        result = analyzer.analyze_activity_performance(activity_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'numeric-trends':
        data_type = sys.argv[2] if len(sys.argv) > 2 else 'character_stats'
        result = analyzer.analyze_numeric_trends(data_type)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
