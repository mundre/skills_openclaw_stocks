#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 玩法教学引导系统
设计剧情与玩法融合的新手流程
"""

import os
import json
import sys
from typing import Dict, Any, List
from datetime import datetime


class GameplayTutorialDesigner:
    """玩法教学引导设计师"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), 'output', 'tutorial')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 常见玩法类型
        self.common_gameplays = {
            'gathering': {
                'name': '采集',
                'description': '学习采集基础资源',
                'duration': '10 分钟',
                'rewards': ['基础工具', '采集材料']
            },
            'crafting': {
                'name': '锻造',
                'description': '学习锻造武器/装备',
                'duration': '10 分钟',
                'rewards': ['第一把武器']
            },
            'making': {
                'name': '制作',
                'description': '学习制作药水/食物',
                'duration': '10 分钟',
                'rewards': ['基础药水', '食物']
            },
            'combat': {
                'name': '战斗',
                'description': '学习基础战斗系统',
                'duration': '15 分钟',
                'rewards': ['战斗首胜奖励', '经验值']
            },
            'exploration': {
                'name': '探索',
                'description': '学习探索系统',
                'duration': '10 分钟',
                'rewards': ['探索奖励', '地图解锁']
            },
            'social': {
                'name': '社交',
                'description': '学习社交系统',
                'duration': '5 分钟',
                'rewards': ['好友位', '公会介绍']
            },
            'quest': {
                'name': '任务',
                'description': '学习任务系统',
                'duration': '5 分钟',
                'rewards': ['任务奖励']
            },
            'inventory': {
                'name': '背包',
                'description': '学习背包管理',
                'duration': '5 分钟',
                'rewards': ['背包扩展']
            }
        }
    
    def generate_tutorial_flow(self, gameplays: List[str], 
                                game_type: str = 'rpg') -> Dict[str, Any]:
        """
        生成教学流程
        
        Args:
            gameplays: 玩法列表（gathering/crafting/making/combat 等）
            game_type: 游戏类型
        
        Returns:
            完整教学流程设计
        """
        tutorial_flow = {
            'game_type': game_type,
            'total_duration': '0 分钟',
            'stages': [],
            'flowchart': '',
            'config_table': []
        }
        
        total_minutes = 0
        prev_stage_id = None
        
        for i, gameplay_key in enumerate(gameplays):
            gameplay = self.common_gameplays.get(gameplay_key, {})
            
            stage = {
                'stage_id': f'tutorial_{i+1:03d}',
                'stage_name': f'{gameplay.get("name", gameplay_key)}教学',
                'gameplay_type': gameplay_key,
                'duration': gameplay.get('duration', '10 分钟'),
                'description': gameplay.get('description', ''),
                'rewards': gameplay.get('rewards', []),
                'prerequisite': prev_stage_id
            }
            
            # 设计剧情节点
            stage['story_node'] = self._design_story_node(gameplay_key, i)
            
            # 设计玩法教学
            stage['tutorial_steps'] = self._design_tutorial_steps(gameplay_key)
            
            # 设计关卡要素
            stage['level_elements'] = self._design_level_elements(gameplay_key)
            
            tutorial_flow['stages'].append(stage)
            
            # 解析时长
            minutes = int(gameplay.get('duration', '10 分钟').replace('分钟', ''))
            total_minutes += minutes
            prev_stage_id = stage['stage_id']
        
        tutorial_flow['total_duration'] = f'{total_minutes}分钟'
        
        # 生成流程图
        tutorial_flow['flowchart'] = self._generate_flowchart(tutorial_flow['stages'])
        
        # 生成配置表
        tutorial_flow['config_table'] = self._generate_config_table(tutorial_flow['stages'])
        
        # 保存为 markdown
        filename = f"tutorial_flow_{datetime.now().strftime('%Y%m%d%H%M%S')}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self._export_to_markdown(tutorial_flow))
        
        return {
            'status': 'generated',
            'filepath': filepath,
            'filename': filename,
            'flow': tutorial_flow
        }
    
    def _design_story_node(self, gameplay_key: str, stage_index: int) -> Dict[str, Any]:
        """设计剧情节点"""
        story_templates = {
            'gathering': {
                'title': '村庄的危机',
                'description': '村庄遭到袭击，需要收集材料修复防御工事',
                'npc': '村长',
                'dialogue': [
                    '年轻人，我们的村庄遭到了袭击...',
                    '请帮我去收集一些木材和石头，我们需要修复防御！',
                    '去村庄外的采集点，用你的工具采集材料吧！'
                ],
                'objective': '采集 10 个木材和 10 个石头'
            },
            'crafting': {
                'title': '武器的重要性',
                'description': '需要武器来对抗敌人',
                'npc': '铁匠',
                'dialogue': [
                    '你只有徒手可不行，需要一把武器！',
                    '我来教你锻造一把基础武器。',
                    '放入材料，选择武器图纸，然后开始锻造！'
                ],
                'objective': '锻造一把基础武器'
            },
            'making': {
                'title': '药水的力量',
                'description': '需要准备药水应对战斗',
                'npc': '药剂师',
                'dialogue': [
                    '战斗前需要准备药水。',
                    '我来教你制作基础治疗药水。',
                    '放入草药，选择配方，开始制作！'
                ],
                'objective': '制作 5 瓶治疗药水'
            },
            'combat': {
                'title': '敌人来袭',
                'description': '敌人来袭，需要战斗',
                'npc': '卫兵队长',
                'dialogue': [
                    '警报！敌人来袭！',
                    '拿起你的武器，我来教你战斗！',
                    '使用普通攻击，然后使用技能，注意闪避！'
                ],
                'objective': '击败 3 个敌人'
            },
            'exploration': {
                'title': '探索未知',
                'description': '探索村庄周边区域',
                'npc': '探险家',
                'dialogue': [
                    '这附近还有很多未知的区域。',
                    '去探索一下吧，可能会有发现！',
                    '打开地图，前往标记的区域！'
                ],
                'objective': '探索 3 个区域'
            },
            'social': {
                'title': '结识伙伴',
                'description': '学习社交系统',
                'npc': '公会接待员',
                'dialogue': [
                    '冒险的路上需要伙伴。',
                    '来加入公会吧！',
                    '添加好友，加入公会，一起冒险！'
                ],
                'objective': '添加 1 个好友，加入公会'
            },
            'quest': {
                'title': '冒险的开始',
                'description': '学习任务系统',
                'npc': '冒险家协会',
                'dialogue': [
                    '欢迎来到冒险家协会！',
                    '这里有各种任务等着你。',
                    '查看任务列表，接受任务，完成任务！'
                ],
                'objective': '接受并完成 1 个任务'
            },
            'inventory': {
                'title': '整理行囊',
                'description': '学习背包管理',
                'npc': '商人',
                'dialogue': [
                    '你的背包有点乱了吧？',
                    '来，我教你整理背包。',
                    '打开背包，分类物品，整理格子！'
                ],
                'objective': '整理背包，分类物品'
            }
        }
        
        return story_templates.get(gameplay_key, {
            'title': f'教学阶段{stage_index+1}',
            'description': '学习游戏功能',
            'npc': '引导 NPC',
            'dialogue': ['欢迎来到游戏！', '让我教你怎么玩。'],
            'objective': '完成教学'
        })
    
    def _design_tutorial_steps(self, gameplay_key: str) -> List[Dict[str, Any]]:
        """设计玩法教学步骤"""
        step_templates = {
            'gathering': [
                {'step': 1, 'action': '点击采集点', 'tip': '找到可采集的资源点'},
                {'step': 2, 'action': '开始采集', 'tip': '长按采集按钮'},
                {'step': 3, 'action': '获得材料', 'tip': '材料会自动放入背包'},
                {'step': 4, 'action': '检查背包', 'tip': '打开背包查看获得的材料'}
            ],
            'crafting': [
                {'step': 1, 'action': '进入锻造界面', 'tip': '找到铁匠或锻造台'},
                {'step': 2, 'action': '选择武器图纸', 'tip': '选择要锻造的武器'},
                {'step': 3, 'action': '放入材料', 'tip': '放入所需的材料'},
                {'step': 4, 'action': '开始锻造', 'tip': '点击锻造按钮'},
                {'step': 5, 'action': '获得武器', 'tip': '锻造成功，获得武器'}
            ],
            'making': [
                {'step': 1, 'action': '进入制作界面', 'tip': '找到工作台'},
                {'step': 2, 'action': '选择配方', 'tip': '选择要制作的物品'},
                {'step': 3, 'action': '放入材料', 'tip': '放入所需的材料'},
                {'step': 4, 'action': '开始制作', 'tip': '点击制作按钮'},
                {'step': 5, 'action': '获得物品', 'tip': '制作成功'}
            ],
            'combat': [
                {'step': 1, 'action': '锁定敌人', 'tip': '点击敌人锁定目标'},
                {'step': 2, 'action': '普通攻击', 'tip': '使用普通攻击消耗敌人血量'},
                {'step': 3, 'action': '使用技能', 'tip': '使用技能造成更多伤害'},
                {'step': 4, 'action': '闪避/格挡', 'tip': '躲避敌人攻击'},
                {'step': 5, 'action': '击败敌人', 'tip': '敌人血量归零，战斗胜利'}
            ],
            'exploration': [
                {'step': 1, 'action': '打开地图', 'tip': '查看未知区域'},
                {'step': 2, 'action': '前往目标', 'tip': '跟随导航前往'},
                {'step': 3, 'action': '发现新区域', 'tip': '解锁新区域'},
                {'step': 4, 'action': '收集探索奖励', 'tip': '获得宝箱奖励'}
            ],
            'social': [
                {'step': 1, 'action': '打开社交界面', 'tip': '找到好友/公会入口'},
                {'step': 2, 'action': '添加好友', 'tip': '搜索并添加好友'},
                {'step': 3, 'action': '加入公会', 'tip': '申请加入公会'},
                {'step': 4, 'action': '与好友互动', 'tip': '发送消息或赠送礼物'}
            ],
            'quest': [
                {'step': 1, 'action': '打开任务列表', 'tip': '查看可用任务'},
                {'step': 2, 'action': '接受任务', 'tip': '点击接受按钮'},
                {'step': 3, 'action': '完成任务目标', 'tip': '按照任务要求完成'},
                {'step': 4, 'action': '领取奖励', 'tip': '返回 NPC 处领取奖励'}
            ],
            'inventory': [
                {'step': 1, 'action': '打开背包', 'tip': '点击背包按钮'},
                {'step': 2, 'action': '查看物品', 'tip': '浏览背包中的物品'},
                {'step': 3, 'action': '分类整理', 'tip': '将物品分类摆放'},
                {'step': 4, 'action': '使用/出售', 'tip': '使用物品或出售多余物品'}
            ]
        }
        
        return step_templates.get(gameplay_key, [
            {'step': 1, 'action': '跟随引导', 'tip': '按照提示操作'}
        ])
    
    def _design_level_elements(self, gameplay_key: str) -> Dict[str, Any]:
        """设计关卡要素"""
        return {
            'environment': f'教学场景_{gameplay_key}',
            'npcs': ['引导 NPC', '相关 NPC'],
            'interactables': [f'{gameplay_key}_交互点'],
            'enemies': ['教学用敌人'] if gameplay_key == 'combat' else [],
            'rewards': ['首通奖励', '成就解锁'],
            'checkpoints': ['检查点 1', '检查点 2']
        }
    
    def _generate_flowchart(self, stages: List[Dict]) -> str:
        """生成流程图"""
        mermaid = "graph TD\n"
        
        mermaid += "    A[进入游戏] --> B[开场剧情]\n"
        
        prev_node = "B"
        for stage in stages:
            node_id = stage['stage_id']
            node_name = stage['stage_name'].replace('教学', '')
            mermaid += f"    {prev_node} --> C[{node_name}教学]\n"
            prev_node = f"C{node_id[-3:]}"
        
        mermaid += f"    {prev_node} --> Z[新手流程完成]\n"
        
        return mermaid
    
    def _generate_config_table(self, stages: List[Dict]) -> List[Dict]:
        """生成配置表"""
        config = []
        
        for stage in stages:
            config.append({
                'ID': stage['stage_id'],
                'Name': stage['stage_name'],
                'Type': stage['gameplay_type'],
                'Prerequisite': stage.get('prerequisite', 'none'),
                'Duration': stage['duration'],
                'Description': stage['description'],
                'Rewards': ','.join(stage['rewards'])
            })
        
        return config
    
    def _export_to_markdown(self, flow: Dict) -> str:
        """导出为 Markdown"""
        md = f"# 新手教学流程设计\n\n"
        md += f"**游戏类型**: {flow['game_type']}\n"
        md += f"**总时长**: {flow['total_duration']}\n\n"
        
        md += "## 教学阶段\n\n"
        for stage in flow['stages']:
            md += f"### {stage['stage_name']}\n\n"
            md += f"**时长**: {stage['duration']}\n"
            md += f"**描述**: {stage['description']}\n\n"
            
            md += "**剧情节点**:\n"
            md += f"- 标题：{stage['story_node']['title']}\n"
            md += f"- NPC: {stage['story_node']['npc']}\n"
            md += f"- 目标：{stage['story_node']['objective']}\n\n"
            
            md += "**教学步骤**:\n"
            for step in stage['tutorial_steps']:
                md += f"{step['step']}. {step['action']} - {step['tip']}\n"
            md += "\n"
            
            md += f"**奖励**: {', '.join(stage['rewards'])}\n"
            md += "\n---\n\n"
        
        md += "## 流程图\n\n"
        md += f"```mermaid\n{flow['flowchart']}\n```\n\n"
        
        md += "## 配置表\n\n"
        md += "| ID | Name | Type | Prerequisite | Duration | Description | Rewards |\n"
        md += "|---|---|---|---|---|---|---|\n"
        for row in flow['config_table']:
            md += f"| {row['ID']} | {row['Name']} | {row['Type']} | {row['Prerequisite']} | {row['Duration']} | {row['Description']} | {row['Rewards']} |\n"
        
        return md


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python gameplay_tutorial.py <command> [args]")
        print("Commands:")
        print("  generate <gameplays...>    - 生成教学流程")
        print("  Example: python gameplay_tutorial.py generate gathering crafting making combat")
        sys.exit(1)
    
    command = sys.argv[1]
    designer = GameplayTutorialDesigner()
    
    if command == 'generate':
        gameplays = sys.argv[2:] if len(sys.argv) > 2 else ['gathering', 'crafting', 'making', 'combat']
        game_type = 'rpg'
        
        result = designer.generate_tutorial_flow(gameplays, game_type)
        print(f"教学流程已生成：{result['filepath']}")
        print(f"总时长：{result['flow']['total_duration']}")
        print(f"阶段数：{len(result['flow']['stages'])}")
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
