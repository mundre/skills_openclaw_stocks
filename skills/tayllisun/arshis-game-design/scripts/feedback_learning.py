#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 反馈学习模块
记录用户反馈，持续优化建议质量
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List


class FeedbackLearner:
    """反馈学习器"""
    
    def __init__(self, knowledge_dir: str = None):
        self.knowledge_dir = knowledge_dir or os.path.dirname(__file__)
        self.feedback_db = os.path.join(self.knowledge_dir, 'feedback_database.json')
        self.improvement_log = os.path.join(self.knowledge_dir, 'improvement_log.json')
        
        # 加载反馈数据库
        self.feedback_db_data = self._load_feedback_db()
        
        # 加载改进日志
        self.improvements = self._load_improvements()
    
    def _load_feedback_db(self) -> Dict[str, Any]:
        """加载反馈数据库"""
        if os.path.exists(self.feedback_db):
            with open(self.feedback_db, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            'feedbacks': [],
            'total_feedbacks': 0,
            'effective_suggestions': 0,
            'ineffective_suggestions': 0
        }
    
    def _load_improvements(self) -> Dict[str, Any]:
        """加载改进日志"""
        if os.path.exists(self.improvement_log):
            with open(self.improvement_log, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            'improvements': [],
            'total_improvements': 0
        }
    
    def record_suggestion_feedback(self, suggestion: Dict[str, Any], 
                                    feedback: str,
                                    effectiveness: str,
                                    context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        记录建议反馈
        
        Args:
            suggestion: 原始建议
            feedback: 用户反馈内容
            effectiveness: 有效性（effective/ineffective/partially_effective）
            context: 上下文信息
        
        Returns:
            记录结果
        """
        feedback_entry = {
            'id': f"fb_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'suggestion': suggestion,
            'feedback': feedback,
            'effectiveness': effectiveness,
            'context': context or {}
        }
        
        self.feedback_db_data['feedbacks'].append(feedback_entry)
        self.feedback_db_data['total_feedbacks'] += 1
        
        if effectiveness == 'effective':
            self.feedback_db_data['effective_suggestions'] += 1
        elif effectiveness == 'ineffective':
            self.feedback_db_data['ineffective_suggestions'] += 1
        
        # 保存反馈数据库
        self._save_feedback_db()
        
        # 分析反馈，生成改进建议
        improvement = self._analyze_feedback(feedback_entry)
        
        return {
            'feedback_id': feedback_entry['id'],
            'effectiveness': effectiveness,
            'improvement_generated': improvement is not None
        }
    
    def _analyze_feedback(self, feedback_entry: Dict) -> Dict[str, Any]:
        """分析反馈，生成改进建议"""
        effectiveness = feedback_entry['effectiveness']
        suggestion = feedback_entry['suggestion']
        
        improvement = None
        
        # 如果建议有效，记录成功模式
        if effectiveness == 'effective':
            improvement = {
                'type': 'success_pattern',
                'timestamp': datetime.now().isoformat(),
                'pattern': suggestion.get('category', 'unknown'),
                'description': '这个类型的建议被用户采纳',
                'action': '继续使用该类型的建议方法'
            }
        
        # 如果建议无效，记录需要改进的地方
        elif effectiveness == 'ineffective':
            improvement = {
                'type': 'improvement_needed',
                'timestamp': datetime.now().isoformat(),
                'category': suggestion.get('category', 'unknown'),
                'feedback': feedback_entry['feedback'],
                'action': '需要改进这个类型的建议方法'
            }
        
        if improvement:
            self.improvements['improvements'].append(improvement)
            self.improvements['total_improvements'] += 1
            self._save_improvements()
        
        return improvement
    
    def _save_feedback_db(self):
        """保存反馈数据库"""
        with open(self.feedback_db, 'w', encoding='utf-8') as f:
            json.dump(self.feedback_db_data, f, ensure_ascii=False, indent=2)
    
    def _save_improvements(self):
        """保存改进日志"""
        with open(self.improvement_log, 'w', encoding='utf-8') as f:
            json.dump(self.improvements, f, ensure_ascii=False, indent=2)
    
    def get_effectiveness_rate(self) -> Dict[str, Any]:
        """获取建议有效率"""
        total = self.feedback_db_data['total_feedbacks']
        effective = self.feedback_db_data['effective_suggestions']
        
        if total == 0:
            return {
                'total_feedbacks': 0,
                'effective_rate': 0,
                'message': '暂无反馈数据'
            }
        
        return {
            'total_feedbacks': total,
            'effective_suggestions': effective,
            'ineffective_suggestions': self.feedback_db_data['ineffective_suggestions'],
            'effective_rate': effective / total,
            'message': f'建议有效率：{effective / total * 100:.1f}%'
        }
    
    def get_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """获取改进建议"""
        # 分析最近的反馈
        recent_feedbacks = self.feedback_db_data['feedbacks'][-10:]
        
        if not recent_feedbacks:
            return []
        
        # 统计无效建议的类别
        ineffective_categories = {}
        
        for fb in recent_feedbacks:
            if fb['effectiveness'] == 'ineffective':
                category = fb['suggestion'].get('category', 'unknown')
                ineffective_categories[category] = ineffective_categories.get(category, 0) + 1
        
        # 生成改进建议
        improvements = []
        
        for category, count in ineffective_categories.items():
            if count >= 2:  # 同一类别有 2 个以上无效建议
                improvements.append({
                    'category': category,
                    'issue_count': count,
                    'suggestion': f'改进{category}类别的建议方法',
                    'priority': 'high' if count >= 3 else 'medium'
                })
        
        return improvements
    
    def optimize_suggestion_template(self, category: str) -> Dict[str, Any]:
        """
        优化建议模板
        
        Args:
            category: 建议类别
        
        Returns:
            优化结果
        """
        # 分析该类别的历史反馈
        category_feedbacks = [
            fb for fb in self.feedback_db_data['feedbacks']
            if fb['suggestion'].get('category') == category
        ]
        
        if not category_feedbacks:
            return {
                'status': 'no_data',
                'message': f'{category}类别暂无反馈数据'
            }
        
        # 统计有效和无效的模式
        effective_patterns = []
        ineffective_patterns = []
        
        for fb in category_feedbacks:
            if fb['effectiveness'] == 'effective':
                effective_patterns.append(fb['suggestion'])
            elif fb['effectiveness'] == 'ineffective':
                ineffective_patterns.append(fb['suggestion'])
        
        # 生成优化建议
        optimization = {
            'category': category,
            'total_feedbacks': len(category_feedbacks),
            'effective_count': len(effective_patterns),
            'ineffective_count': len(ineffective_patterns),
            'recommendations': []
        }
        
        # 如果有有效模式，建议继续使用
        if effective_patterns:
            optimization['recommendations'].append({
                'type': 'continue',
                'description': '继续使用以下有效模式',
                'patterns': effective_patterns[:3]
            })
        
        # 如果有无效模式，建议避免
        if ineffective_patterns:
            optimization['recommendations'].append({
                'type': 'avoid',
                'description': '避免使用以下无效模式',
                'patterns': ineffective_patterns[:3]
            })
        
        return optimization
    
    def get_learning_progress(self) -> Dict[str, Any]:
        """获取学习进度"""
        return {
            'feedback_stats': self.get_effectiveness_rate(),
            'improvement_count': self.improvements['total_improvements'],
            'recent_improvements': self.improvements['improvements'][-5:],
            'optimization_opportunities': len(self.get_improvement_suggestions())
        }


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python feedback_learning.py <command> [args]")
        print("Commands:")
        print("  record <json>              - 记录反馈")
        print("  stats                      - 查看统计")
        print("  improvements               - 查看改进建议")
        print("  optimize <category>        - 优化建议模板")
        print("  progress                   - 查看学习进度")
        sys.exit(1)
    
    command = sys.argv[1]
    learner = FeedbackLearner()
    
    if command == 'record':
        feedback_json = sys.argv[2] if len(sys.argv) > 2 else '{}'
        feedback_data = json.loads(feedback_json)
        
        result = learner.record_suggestion_feedback(
            suggestion=feedback_data.get('suggestion', {}),
            feedback=feedback_data.get('feedback', ''),
            effectiveness=feedback_data.get('effectiveness', 'unknown'),
            context=feedback_data.get('context')
        )
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'stats':
        stats = learner.get_effectiveness_rate()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    elif command == 'improvements':
        improvements = learner.get_improvement_suggestions()
        print(json.dumps(improvements, ensure_ascii=False, indent=2))
    
    elif command == 'optimize':
        category = sys.argv[2] if len(sys.argv) > 2 else 'general'
        result = learner.optimize_suggestion_template(category)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'progress':
        progress = learner.get_learning_progress()
        print(json.dumps(progress, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
