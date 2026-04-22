#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 通用框架模块
支持任意游戏类型的策划案生成
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class UniversalFramework:
    """通用游戏策划框架"""
    
    def __init__(self):
        # 游戏类型知识库
        self.game_types = self._load_game_type_knowledge()
        
        # 通用模板框架
        self.universal_template = self._create_universal_template()
    
    def _load_game_type_knowledge(self) -> Dict[str, Any]:
        """加载游戏类型知识库"""
        return {
            'moba': {
                'name': 'MOBA',
                'full_name': 'Multiplayer Online Battle Arena',
                'examples': ['王者荣耀', 'LOL', 'DOTA2'],
                'core_elements': ['英雄', '装备', '地图', '匹配', '平衡'],
                'design_focus': '英雄技能设计/平衡性/团队协作',
                'key_metrics': ['胜率', '出场率', '禁用率', 'KDA']
            },
            'fps': {
                'name': 'FPS',
                'full_name': 'First-Person Shooter',
                'examples': ['CS:GO', 'Valorant', 'OW', 'Apex'],
                'core_elements': ['武器', '角色', '地图', '模式', '反作弊'],
                'design_focus': '武器平衡/地图设计/手感优化',
                'key_metrics': ['KD', '胜率', '爆头率', 'TTK']
            },
            'slg': {
                'name': 'SLG',
                'full_name': 'Simulation Game',
                'examples': ['率土之滨', 'ROK', 'COK', '三国志战略版'],
                'core_elements': ['建筑', '兵种', '资源', '联盟', '大地图'],
                'design_focus': '数值平衡/社交设计/付费设计',
                'key_metrics': ['留存率', '付费率', 'ARPU', '联盟活跃度']
            },
            'gacha': {
                'name': '二次元/卡牌',
                'full_name': 'Gacha Game',
                'examples': ['原神', '崩坏', 'FGO', '明日方舟'],
                'core_elements': ['角色', '武器', '圣遗物', '活动', '剧情'],
                'design_focus': '角色设计/抽卡设计/内容更新',
                'key_metrics': ['抽卡率', '角色持有率', '活跃度', '流水']
            },
            'mmorpg': {
                'name': 'MMORPG',
                'full_name': 'Massively Multiplayer Online RPG',
                'examples': ['魔兽世界', 'FF14', '逆水寒'],
                'core_elements': ['职业', '副本', 'PVP', '社交', '经济'],
                'design_focus': '职业平衡/副本设计/经济系统',
                'key_metrics': ['在线人数', '副本通关率', '金币产出']
            },
            'roguelike': {
                'name': 'Roguelike',
                'examples': ['杀戮尖塔', '哈迪斯', '死亡细胞'],
                'core_elements': ['关卡生成', '道具池', 'Build', 'Boss'],
                'design_focus': '随机性/平衡性/重复可玩性',
                'key_metrics': ['通关率', '平均局时长', '重复游玩率']
            },
            'simulation': {
                'name': '模拟经营',
                'examples': ['模拟城市', '开罗游戏', '星露谷物语'],
                'core_elements': ['设施', '经济循环', '顾客', '扩张'],
                'design_focus': '经济平衡/成长曲线/内容深度',
                'key_metrics': ['留存率', '付费率', '游戏时长']
            },
            'openworld': {
                'name': '开放世界',
                'examples': ['GTA', '荒野大镖客', '上古卷轴'],
                'core_elements': ['区域设计', '任务系统', '探索', 'NPC'],
                'design_focus': '世界构建/任务设计/沉浸感',
                'key_metrics': ['探索度', '任务完成率', '游戏时长']
            }
        }
    
    def _create_universal_template(self) -> Dict[str, Any]:
        """创建通用模板框架"""
        return {
            'title': '[游戏类型] [设计内容] 策划案',
            'version': '1.0',
            'sections': {
                '1_概述': {
                    'design_goal': '设计目标',
                    'target_audience': '目标用户',
                    'design_philosophy': '设计理念',
                    'release_version': '上线版本'
                },
                '2_核心设计': {
                    'core_mechanic': '核心机制',
                    'gameplay_loop': '玩法循环',
                    'unique_selling_point': '独特卖点'
                },
                '3_详细设计': {
                    'detailed_rules': '详细规则',
                    'formulas': '公式设计',
                    'parameters': '参数设计'
                },
                '4_数值设计': {
                    'base_values': '基础数值',
                    'scaling': '成长曲线',
                    'balance': '平衡性考虑'
                },
                '5_美术需求': {
                    'models': '模型需求',
                    'animations': '动画需求',
                    'vfx': '特效需求',
                    'ui': 'UI 需求'
                },
                '6_程序需求': {
                    'logic': '逻辑实现',
                    'sync': '同步需求',
                    'performance': '性能要求',
                    'anti_cheat': '反作弊'
                },
                '7_测试要点': {
                    'functional_test': '功能测试',
                    'balance_test': '平衡测试',
                    'performance_test': '性能测试',
                    'exploit_test': '漏洞测试'
                },
                '8_运营计划': {
                    'release_plan': '上线计划',
                    'marketing': '营销计划',
                    'community': '社区运营',
                    'data_tracking': '数据埋点'
                }
            }
        }
    
    def identify_game_type(self, description: str) -> Dict[str, Any]:
        """
        识别游戏类型
        
        Args:
            description: 游戏描述
        
        Returns:
            识别结果
        """
        description_lower = description.lower()
        
        # 关键词匹配
        type_keywords = {
            'moba': ['moba', '王者', 'lol', 'dota', '5v5', '推塔', '英雄'],
            'fps': ['fps', '射击', 'cs', 'valorant', 'ow', 'apex', '枪', '武器'],
            'slg': ['slg', '策略', '率土', 'rok', 'cok', '三国志', '国战', '联盟'],
            'gacha': ['二次元', '卡牌', '抽卡', '原神', '崩坏', 'fgo', '方舟'],
            'mmorpg': ['mmorpg', 'mmo', '魔兽', 'ff14', '逆水寒', '副本', '职业'],
            'roguelike': ['roguelike', '杀戮尖塔', '哈迪斯', '死亡细胞', '随机'],
            'simulation': ['模拟', '经营', '模拟城市', '开罗', '星露谷'],
            'openworld': ['开放世界', 'gta', '荒野大镖客', '上古卷轴', '探索']
        }
        
        # 计算匹配度
        type_scores = {}
        for game_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in description_lower)
            type_scores[game_type] = score
        
        # 返回最高匹配
        best_match = max(type_scores.items(), key=lambda x: x[1])
        
        if best_match[1] == 0:
            return {
                'identified': False,
                'type': 'unknown',
                'confidence': 0,
                'suggestion': '请明确指定游戏类型（MOBA/FPS/SLG/二次元/MMORPG 等）'
            }
        
        type_info = self.game_types.get(best_match[0], {})
        
        return {
            'identified': True,
            'type': best_match[0],
            'type_name': type_info.get('name', best_match[0]),
            'confidence': min(1.0, best_match[1] / 3),  # 3 个关键词以上认为高置信度
            'examples': type_info.get('examples', []),
            'core_elements': type_info.get('core_elements', []),
            'design_focus': type_info.get('design_focus', '')
        }
    
    def generate_universal_design(self, game_type: str, design_content: str,
                                   custom_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成通用设计案
        
        Args:
            game_type: 游戏类型
            design_content: 设计内容
            custom_params: 自定义参数
        
        Returns:
            生成的设计案
        """
        # 获取类型知识
        type_info = self.game_types.get(game_type.lower(), {})
        
        # 使用通用模板
        template = self._create_universal_template()
        
        # 适配类型特定内容
        adapted = self._adapt_template(template, game_type, design_content, 
                                       type_info, custom_params)
        
        return adapted
    
    def _adapt_template(self, template: Dict, game_type: str, 
                        design_content: str, type_info: Dict,
                        custom_params: Dict = None) -> Dict[str, Any]:
        """适配模板到特定类型"""
        adapted = {
            'title': f"{type_info.get('name', game_type)} - {design_content} 策划案",
            'version': '1.0',
            'game_type': game_type,
            'type_info': type_info,
            'sections': {}
        }
        
        # 复制通用章节
        for section_name, section_content in template['sections'].items():
            adapted['sections'][section_name] = section_content.copy()
        
        # 添加类型特定章节
        if custom_params:
            for key, value in custom_params.items():
                adapted['sections'][key] = value
        
        return adapted
    
    def get_design_guidelines(self, game_type: str, design_content: str) -> List[Dict[str, str]]:
        """
        获取设计指导原则
        
        Args:
            game_type: 游戏类型
            design_content: 设计内容
        
        Returns:
            指导原则列表
        """
        type_info = self.game_types.get(game_type.lower(), {})
        design_focus = type_info.get('design_focus', '')
        
        guidelines = [
            {
                'category': '设计目标',
                'guideline': f'明确{design_content}的设计目标和定位',
                'importance': 'high'
            },
            {
                'category': '类型适配',
                'guideline': f'{type_info.get("name", game_type)}游戏重点关注：{design_focus}',
                'importance': 'high'
            },
            {
                'category': '平衡性',
                'guideline': '确保设计内容的平衡性，避免过强或过弱',
                'importance': 'high'
            },
            {
                'category': '用户体验',
                'guideline': '考虑用户体验，设计应易于理解但有深度',
                'importance': 'medium'
            },
            {
                'category': '技术可行性',
                'guideline': '评估技术实现难度和性能影响',
                'importance': 'medium'
            },
            {
                'category': '数据追踪',
                'guideline': '设计数据埋点，便于后续分析和调整',
                'importance': 'medium'
            }
        ]
        
        # 添加类型特定指导
        key_metrics = type_info.get('key_metrics', [])
        if key_metrics:
            guidelines.append({
                'category': '核心指标',
                'guideline': f'关注以下指标：{", ".join(key_metrics)}',
                'importance': 'high'
            })
        
        return guidelines
    
    def list_supported_types(self) -> List[Dict[str, Any]]:
        """列出支持的游戏类型"""
        result = []
        for type_id, info in self.game_types.items():
            result.append({
                'id': type_id,
                'name': info.get('name', type_id),
                'full_name': info.get('full_name', ''),
                'examples': info.get('examples', []),
                'core_elements': info.get('core_elements', []),
                'design_focus': info.get('design_focus', '')
            })
        return result


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python universal_framework.py <command> [args]")
        print("Commands:")
        print("  list-types              - 列出支持的游戏类型")
        print("  identify <description>  - 识别游戏类型")
        print("  guidelines <type> <content> - 获取设计指导")
        sys.exit(1)
    
    command = sys.argv[1]
    framework = UniversalFramework()
    
    if command == 'list-types':
        types = framework.list_supported_types()
        print(f"支持的游戏类型（共{len(types)}种）:\n")
        for t in types:
            print(f"{t['id']}: {t['name']}")
            if t.get('full_name'):
                print(f"  全称：{t['full_name']}")
            print(f"  代表游戏：{', '.join(t['examples'])}")
            print(f"  核心要素：{', '.join(t['core_elements'])}")
            print(f"  设计重点：{t['design_focus']}\n")
    
    elif command == 'identify':
        description = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else ''
        if not description:
            print("Error: 需要提供游戏描述")
            sys.exit(1)
        
        result = framework.identify_game_type(description)
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'guidelines':
        if len(sys.argv) < 4:
            print("Error: 需要提供游戏类型和设计内容")
            sys.exit(1)
        
        game_type = sys.argv[2]
        design_content = sys.argv[3]
        
        guidelines = framework.get_design_guidelines(game_type, design_content)
        print(f"\n{game_type} - {design_content} 设计指导原则:\n")
        for g in guidelines:
            emoji = '❗' if g['importance'] == 'high' else '⚠️'
            print(f"{emoji} {g['category']}: {g['guideline']}")
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
