#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - AI 对话式设计助手
问答式引导，降低使用门槛
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime


class ChatDesigner:
    """对话式设计助手"""
    
    def __init__(self):
        self.context = {
            'project_name': '',
            'game_type': '',
            'current_task': '',
            'preferences': {}
        }
        self.history = []
    
    def start_chat(self) -> Dict[str, Any]:
        """开始对话"""
        return {
            'status': 'started',
            'message': '欢迎使用 Arshis-Game-Design-Pro！我是您的游戏策划助手。请问您想设计什么类型的游戏？（RPG/MOBA/FPS/SLG/开放世界/二次元/独立游戏）',
            'suggestions': [
                '我想做一个 RPG 游戏',
                '我想做一个开放世界游戏',
                '我想做一个 MOBA 游戏',
                '帮我设计新手流程'
            ]
        }
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入
        
        Returns:
            回复
        """
        # 记录历史
        self.history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # 意图识别
        intent = self._recognize_intent(user_input)
        
        # 根据意图回复
        if intent['type'] == 'game_type':
            response = self._handle_game_type(intent)
        elif intent['type'] == 'design_request':
            response = self._handle_design_request(intent)
        elif intent['type'] == 'tutorial':
            response = self._handle_tutorial(intent)
        elif intent['type'] == 'analysis':
            response = self._handle_analysis(intent)
        else:
            response = self._handle_general(intent)
        
        # 记录回复
        self.history.append({
            'role': 'assistant',
            'content': response['message'],
            'timestamp': datetime.now().isoformat()
        })
        
        return response
    
    def _recognize_intent(self, text: str) -> Dict[str, Any]:
        """识别用户意图"""
        text_lower = text.lower()
        
        # 游戏类型识别
        game_types = {
            'rpg': ['rpg', '角色扮演', '角色'],
            'moba': ['moba', '竞技', '王者'],
            'fps': ['fps', '射击', 'cs'],
            'slg': ['slg', '策略', '率土'],
            'openworld': ['开放世界', '开放', '世界'],
            'gacha': ['二次元', '抽卡', '原神'],
            'indie': ['独立游戏', '独立', 'roguelike']
        }
        
        for game_type, keywords in game_types.items():
            if any(kw in text_lower for kw in keywords):
                return {'type': 'game_type', 'game_type': game_type}
        
        # 设计请求识别
        design_keywords = ['设计', '生成', '创建', '帮我', '新手', '教学', '关卡', '剧情', '世界观']
        if any(kw in text_lower for kw in design_keywords):
            return {'type': 'design_request'}
        
        # 教程请求识别
        tutorial_keywords = ['教程', '怎么用', '如何使用', '帮助']
        if any(kw in text_lower for kw in tutorial_keywords):
            return {'type': 'tutorial'}
        
        # 分析请求识别
        analysis_keywords = ['分析', '案例', '参考', '成功']
        if any(kw in text_lower for kw in analysis_keywords):
            return {'type': 'analysis'}
        
        return {'type': 'general'}
    
    def _handle_game_type(self, intent: Dict) -> Dict[str, Any]:
        """处理游戏类型选择"""
        game_type = intent.get('game_type', 'rpg')
        self.context['game_type'] = game_type
        
        return {
            'status': 'game_type_selected',
            'game_type': game_type,
            'message': f'好的，{self._get_game_type_name(game_type)}！接下来您想设计什么内容呢？',
            'suggestions': [
                '帮我设计新手流程',
                '帮我设计世界观',
                '帮我设计剧情结构',
                '生成配置表模板'
            ]
        }
    
    def _handle_design_request(self, intent: Dict) -> Dict[str, Any]:
        """处理设计请求"""
        text = intent.get('text', '')
        
        # 识别具体需求
        if '新手' in text or '教学' in text:
            return {
                'status': 'tutorial_request',
                'message': '好的，我来帮您设计新手教学流程！请问您想包含哪些玩法教学？（采集/锻造/制作/战斗/探索/社交）',
                'suggestions': [
                    '采集 + 锻造 + 制作 + 战斗',
                    '完整新手流程（所有玩法）',
                    '简化版（采集 + 战斗）'
                ]
            }
        
        elif '世界观' in text:
            return {
                'status': 'worldview_request',
                'message': '好的，我来帮您构建世界观！请问您的游戏是什么类型？（RPG/开放世界/MOBA/二次元）',
                'suggestions': [
                    'RPG 世界观',
                    '开放世界世界观',
                    '二次元世界观'
                ]
            }
        
        elif '剧情' in text or '故事' in text:
            return {
                'status': 'story_request',
                'message': '好的，我来帮您设计剧情结构！请问您想用哪种结构？（三幕剧/英雄之旅/救猫咪）',
                'suggestions': [
                    '三幕剧结构',
                    '英雄之旅结构',
                    '救猫咪结构'
                ]
            }
        
        elif '关卡' in text:
            return {
                'status': 'level_request',
                'message': '好的，我来帮您设计关卡！基于 GDC 精华和关卡设计原则...',
                'suggestions': [
                    '新手关卡',
                    'Boss 战设计',
                    '探索关卡'
                ]
            }
        
        else:
            return {
                'status': 'general_design',
                'message': '好的，我来帮您设计！请问具体想设计什么内容呢？',
                'suggestions': [
                    '新手流程',
                    '世界观',
                    '剧情结构',
                    '关卡设计'
                ]
            }
    
    def _handle_tutorial(self, intent: Dict) -> Dict[str, Any]:
        """处理教程请求"""
        return {
            'status': 'tutorial',
            'message': '''欢迎使用 Arshis-Game-Design-Pro！

我可以帮您：
1. 设计新手教学流程
2. 构建世界观
3. 设计剧情结构
4. 生成配置表/流程图
5. 提供智能建议

使用方法：
- 直接告诉我您想设计什么
- 我会引导您完成设计
- 生成完整文档和配置

现在，请问您想设计什么类型的游戏？''',
            'suggestions': [
                '我想做一个 RPG 游戏',
                '帮我设计新手流程',
                '查看案例分析'
            ]
        }
    
    def _handle_analysis(self, intent: Dict) -> Dict[str, Any]:
        """处理分析请求"""
        return {
            'status': 'analysis',
            'message': '''我可以为您提供游戏案例分析：

已分析的案例：
1. 原神 - 开放世界 + 二次元
2. 黑神话：悟空 - 单机 3A
3. 王者荣耀 - MOBA
4. CS:GO - FPS
5. 杀戮尖塔 - Roguelike

您想了解哪个游戏的分析？''',
            'suggestions': [
                '原神分析',
                '黑神话分析',
                '王者荣耀分析',
                'CS:GO 分析'
            ]
        }
    
    def _handle_general(self, intent: Dict) -> Dict[str, Any]:
        """处理一般请求"""
        return {
            'status': 'general',
            'message': '我不太理解您的意思，能详细说说您想设计什么吗？',
            'suggestions': [
                '帮我设计新手流程',
                '帮我设计世界观',
                '查看使用教程'
            ]
        }
    
    def _get_game_type_name(self, game_type: str) -> str:
        """获取游戏类型名称"""
        names = {
            'rpg': 'RPG 游戏',
            'moba': 'MOBA 游戏',
            'fps': 'FPS 游戏',
            'slg': 'SLG 游戏',
            'openworld': '开放世界游戏',
            'gacha': '二次元游戏',
            'indie': '独立游戏'
        }
        return names.get(game_type, '游戏')
    
    def get_context(self) -> Dict[str, Any]:
        """获取上下文"""
        return self.context
    
    def get_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.history


def main():
    """命令行接口"""
    chat = ChatDesigner()
    
    print("=== Arshis-Game-Design-Pro 对话式设计助手 ===\n")
    
    # 开始对话
    response = chat.start_chat()
    print(f"助手：{response['message']}\n")
    
    if response.get('suggestions'):
        print("建议：")
        for i, sug in enumerate(response['suggestions'], 1):
            print(f"  {i}. {sug}")
        print()
    
    # 对话循环
    while True:
        try:
            user_input = input("您：").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("助手：再见！祝您开发顺利！")
                break
            
            response = chat.process_input(user_input)
            print(f"\n助手：{response['message']}\n")
            
            if response.get('suggestions'):
                print("建议：")
                for i, sug in enumerate(response['suggestions'], 1):
                    print(f"  {i}. {sug}")
                print()
        
        except KeyboardInterrupt:
            print("\n助手：再见！")
            break
        except Exception as e:
            print(f"助手：出错了 - {e}")


if __name__ == '__main__':
    main()
