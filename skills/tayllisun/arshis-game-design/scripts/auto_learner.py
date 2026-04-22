#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 自动学习模块
定期搜索学习最新行业知识，自动更新知识库
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, List


class AutoLearner:
    """自动学习器"""
    
    def __init__(self, knowledge_dir: str = None):
        self.knowledge_dir = knowledge_dir or os.path.dirname(__file__)
        self.learning_log = os.path.join(self.knowledge_dir, 'auto_learning_log.json')
        self.case_library = os.path.join(self.knowledge_dir, 'case_library.json')
        
        # 加载学习历史
        self.learning_history = self._load_learning_history()
        
        # 加载案例库
        self.case_library_data = self._load_case_library()
    
    def _load_learning_history(self) -> Dict[str, Any]:
        """加载学习历史"""
        if os.path.exists(self.learning_log):
            with open(self.learning_log, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            'last_learning': None,
            'total_learnings': 0,
            'learning_topics': [],
            'knowledge_updates': []
        }
    
    def _load_case_library(self) -> Dict[str, Any]:
        """加载案例库"""
        if os.path.exists(self.case_library):
            with open(self.case_library, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            'success_cases': [],
            'failure_cases': [],
            'design_patterns': [],
            'total_cases': 0
        }
    
    def search_and_learn(self, query: str, category: str = 'general') -> Dict[str, Any]:
        """
        搜索并学习新知识
        
        Args:
            query: 搜索关键词
            category: 知识分类（gdc/market/psychology/sociology/level_design）
        
        Returns:
            学习结果
        """
        # 调用百度搜索
        search_results = self._baidu_search(query)
        
        # 提取关键洞察
        insights = self._extract_insights(search_results)
        
        # 更新知识库
        update_result = self._update_knowledge(category, insights)
        
        # 记录学习历史
        self._record_learning(query, category, insights, update_result)
        
        return {
            'query': query,
            'category': category,
            'insights_count': len(insights),
            'update_result': update_result
        }
    
    def _baidu_search(self, query: str) -> List[Dict[str, Any]]:
        """调用百度搜索"""
        try:
            # 调用 baidu-search 脚本
            search_script = os.path.join(
                os.path.dirname(self.knowledge_dir),
                'baidu-search',
                'scripts',
                'search.py'
            )
            
            # 获取 API Key
            api_key = os.environ.get('BAIDU_API_KEY', '')
            
            if not api_key:
                return []
            
            env = os.environ.copy()
            env['BAIDU_API_KEY'] = api_key
            
            result = subprocess.run(
                ['python3', search_script, json.dumps({
                    'query': query,
                    'count': 5
                })],
                capture_output=True,
                text=True,
                env=env,
                timeout=60
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            return []
            
        except Exception as e:
            print(f"搜索失败：{e}")
            return []
    
    def _extract_insights(self, search_results: List[Dict]) -> List[Dict[str, Any]]:
        """从搜索结果提取关键洞察"""
        insights = []
        
        for result in search_results[:5]:
            content = result.get('content', '')
            title = result.get('title', '')
            url = result.get('url', '')
            
            # 提取关键信息（简化版）
            if len(content) > 100:
                insights.append({
                    'title': title,
                    'url': url,
                    'summary': content[:500],
                    'extracted_at': datetime.now().isoformat()
                })
        
        return insights
    
    def _update_knowledge(self, category: str, insights: List[Dict]) -> Dict[str, Any]:
        """更新知识库"""
        # 根据分类更新不同知识库
        update_result = {
            'category': category,
            'insights_added': len(insights),
            'files_updated': []
        }
        
        # 这里可以实现具体的知识库更新逻辑
        # 简化版：记录更新
        
        update_file = os.path.join(self.knowledge_dir, 'knowledge_updates.json')
        
        if os.path.exists(update_file):
            with open(update_file, 'r', encoding='utf-8') as f:
                updates = json.load(f)
        else:
            updates = {'updates': []}
        
        updates['updates'].append({
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'insights_count': len(insights),
            'insights': insights[:3]  # 只保存前 3 个
        })
        
        with open(update_file, 'w', encoding='utf-8') as f:
            json.dump(updates, f, ensure_ascii=False, indent=2)
        
        update_result['files_updated'].append(update_file)
        
        return update_result
    
    def _record_learning(self, query: str, category: str, 
                         insights: List[Dict], update_result: Dict):
        """记录学习历史"""
        self.learning_history['last_learning'] = datetime.now().isoformat()
        self.learning_history['total_learnings'] += 1
        self.learning_history['learning_topics'].append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'category': category,
            'insights_count': len(insights)
        })
        
        # 保存学习历史
        with open(self.learning_log, 'w', encoding='utf-8') as f:
            json.dump(self.learning_history, f, ensure_ascii=False, indent=2)
    
    def add_case(self, case_type: str, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加案例到案例库
        
        Args:
            case_type: 案例类型（success/failure/pattern）
            case_data: 案例数据
        
        Returns:
            添加结果
        """
        if case_type == 'success':
            self.case_library_data['success_cases'].append(case_data)
        elif case_type == 'failure':
            self.case_library_data['failure_cases'].append(case_data)
        elif case_type == 'pattern':
            self.case_library_data['design_patterns'].append(case_data)
        
        self.case_library_data['total_cases'] += 1
        
        # 保存案例库
        with open(self.case_library, 'w', encoding='utf-8') as f:
            json.dump(self.case_library_data, f, ensure_ascii=False, indent=2)
        
        return {
            'status': 'added',
            'case_type': case_type,
            'total_cases': self.case_library_data['total_cases']
        }
    
    def get_similar_cases(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        获取相似案例
        
        Args:
            keywords: 关键词列表
        
        Returns:
            相似案例列表
        """
        similar_cases = []
        
        # 在成功案例中搜索
        for case in self.case_library_data.get('success_cases', []):
            case_text = json.dumps(case, ensure_ascii=False)
            if any(kw in case_text for kw in keywords):
                similar_cases.append(case)
        
        # 在失败案例中搜索
        for case in self.case_library_data.get('failure_cases', []):
            case_text = json.dumps(case, ensure_ascii=False)
            if any(kw in case_text for kw in keywords):
                similar_cases.append(case)
        
        return similar_cases[:5]  # 返回前 5 个
    
    def record_feedback(self, suggestion_id: str, feedback: str, 
                        effectiveness: str = 'unknown') -> Dict[str, Any]:
        """
        记录用户反馈
        
        Args:
            suggestion_id: 建议 ID
            feedback: 反馈内容
            effectiveness: 有效性（effective/ineffective/unknown）
        
        Returns:
            记录结果
        """
        feedback_log = os.path.join(self.knowledge_dir, 'feedback_log.json')
        
        if os.path.exists(feedback_log):
            with open(feedback_log, 'r', encoding='utf-8') as f:
                feedbacks = json.load(f)
        else:
            feedbacks = {'feedbacks': []}
        
        feedbacks['feedbacks'].append({
            'timestamp': datetime.now().isoformat(),
            'suggestion_id': suggestion_id,
            'feedback': feedback,
            'effectiveness': effectiveness
        })
        
        with open(feedback_log, 'w', encoding='utf-8') as f:
            json.dump(feedbacks, f, ensure_ascii=False, indent=2)
        
        return {
            'status': 'recorded',
            'suggestion_id': suggestion_id,
            'effectiveness': effectiveness
        }
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """获取学习统计"""
        return {
            'last_learning': self.learning_history.get('last_learning'),
            'total_learnings': self.learning_history.get('total_learnings', 0),
            'total_cases': self.case_library_data.get('total_cases', 0),
            'success_cases': len(self.case_library_data.get('success_cases', [])),
            'failure_cases': len(self.case_library_data.get('failure_cases', [])),
            'design_patterns': len(self.case_library_data.get('design_patterns', []))
        }
    
    def schedule_periodic_learning(self):
        """设置定期学习任务"""
        # 这个可以配置 cron 任务
        # 例如：每周学习一次最新 GDC 演讲
        # 每月学习一次市场趋势
        
        learning_schedule = {
            'weekly': [
                {'query': 'GDC 游戏开发者大会 演讲精华', 'category': 'gdc'},
                {'query': '游戏关卡设计 核心原则', 'category': 'level_design'}
            ],
            'monthly': [
                {'query': '游戏市场趋势 2026', 'category': 'market'},
                {'query': '游戏心理学 最新研究', 'category': 'psychology'}
            ]
        }
        
        schedule_file = os.path.join(self.knowledge_dir, 'learning_schedule.json')
        
        with open(schedule_file, 'w', encoding='utf-8') as f:
            json.dump(learning_schedule, f, ensure_ascii=False, indent=2)
        
        return learning_schedule


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python auto_learner.py <command> [args]")
        print("Commands:")
        print("  search <query> [category]  - 搜索并学习")
        print("  add-case <type> <json>     - 添加案例")
        print("  stats                      - 查看学习统计")
        print("  schedule                   - 设置学习计划")
        sys.exit(1)
    
    command = sys.argv[1]
    learner = AutoLearner()
    
    if command == 'search':
        query = sys.argv[2] if len(sys.argv) > 2 else '游戏设计'
        category = sys.argv[3] if len(sys.argv) > 3 else 'general'
        
        print(f"正在搜索学习：{query}")
        result = learner.search_and_learn(query, category)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'add-case':
        case_type = sys.argv[2] if len(sys.argv) > 2 else 'success'
        case_json = sys.argv[3] if len(sys.argv) > 3 else '{}'
        
        case_data = json.loads(case_json)
        result = learner.add_case(case_type, case_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'stats':
        stats = learner.get_learning_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    elif command == 'schedule':
        schedule = learner.schedule_periodic_learning()
        print(json.dumps(schedule, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
