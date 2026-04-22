#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - SLG 游戏模板库
率土之滨/ROK/COK 等 SLG 游戏专属模板
"""

from typing import Dict, Any, List
from datetime import datetime


class SLGTemplates:
    """SLG 游戏模板库"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Any]:
        """加载 SLG 专属模板"""
        return {
            'building_system': self._building_template(),
            'troop_system': self._troop_template(),
            'resource_system': self._resource_template(),
            'alliance_system': self._alliance_template(),
            'world_map': self._worldmap_template()
        }
    
    def _building_template(self) -> Dict[str, Any]:
        """建筑系统模板"""
        return {
            'title': 'SLG 建筑系统策划案',
            'version': '1.0',
            'sections': {
                '1_建筑概述': {
                    'system_goal': '系统设计目标',
                    'building_count': '建筑总数',
                    'building_categories': '建筑分类（军事/经济/科技/防御）',
                    'upgrade_system': '升级系统框架'
                },
                '2_主城建筑': {
                    'city_hall': '主城（等级/功能/前置）',
                    'resource_buildings': '资源建筑（农场/伐木场/铁矿/金矿）',
                    'military_buildings': '军事建筑（兵营/靶场/马厩）',
                    'tech_buildings': '科技建筑（研究所/学院）',
                    'defense_buildings': '防御建筑（城墙/箭塔/陷阱）'
                },
                '3_建筑属性': {
                    'hp': '生命值',
                    'defense': '防御值',
                    'construction_time': '建造时间',
                    'upgrade_cost': '升级消耗',
                    'prerequisites': '前置条件'
                },
                '4_建筑平衡': {
                    'progression_curve': '成长曲线',
                    'cost_efficiency': '性价比分析',
                    'time_gating': '时间限制',
                    'pay_to_win_balance': '付费平衡'
                },
                '5_美术需求': {
                    'building_models': '建筑模型',
                    'upgrade_stages': '升级阶段外观',
                    'destruction_effects': '破坏特效',
                    'ui_icons': 'UI 图标'
                },
                '6_程序需求': {
                    'building_logic': '建筑逻辑',
                    'queue_system': '建造队列',
                    'sync': '数据同步',
                    'performance': '性能优化'
                }
            }
        }
    
    def _troop_template(self) -> Dict[str, Any]:
        """兵种系统模板"""
        return {
            'title': 'SLG 兵种系统策划案',
            'version': '1.0',
            'sections': {
                '1_兵种概述': {
                    'system_goal': '系统设计目标',
                    'troop_types': '兵种类型（步兵/骑兵/弓兵/车兵）',
                    'troop_count': '兵种总数',
                    'counter_system': '克制系统框架'
                },
                '2_兵种属性': {
                    'attack': '攻击力',
                    'defense': '防御力',
                    'hp': '生命值',
                    'speed': '行军速度',
                    'load': '负重',
                    'training_cost': '训练消耗',
                    'training_time': '训练时间'
                },
                '3_兵种克制': {
                    'counter_matrix': '克制关系矩阵',
                    'counter_bonus': '克制加成',
                    'counter_penalty': '被克制惩罚',
                    'same_type_bonus': '同兵种加成'
                },
                '4_兵种升级': {
                    'tier_system': '阶位系统（T1/T2/T3...）',
                    'upgrade_requirements': '升级要求',
                    'upgrade_benefits': '升级收益',
                    'elite_troops': '精英兵种'
                },
                '5_英雄带兵': {
                    'troop_capacity': '带兵量',
                    'hero_bonuses': '英雄加成',
                    'hero_skills': '带兵技能',
                    'synergy': '英雄兵种协同'
                },
                '6_平衡设计': {
                    'troop_diversity': '兵种多样性',
                    'meta_analysis': '主流阵容分析',
                    'balance_adjustments': '平衡调整'
                },
                '7_美术需求': {
                    'troop_models': '兵种模型',
                    'attack_animations': '攻击动画',
                    'march_animations': '行军动画',
                    'ui_icons': 'UI 图标'
                },
                '8_程序需求': {
                    'combat_logic': '战斗逻辑',
                    'pathfinding': '寻路系统',
                    'sync': '战斗同步',
                    'performance': '大规模战斗优化'
                }
            }
        }
    
    def _resource_template(self) -> Dict[str, Any]:
        """资源系统模板"""
        return {
            'title': 'SLG 资源系统策划案',
            'version': '1.0',
            'sections': {
                '1_资源概述': {
                    'system_goal': '系统设计目标',
                    'resource_types': '资源类型（粮/木/铁/金）',
                    'resource_flow': '资源流向图',
                    'economy_type': '经济类型（免费/付费）'
                },
                '2_资源产出': {
                    'natural_production': '自然产出',
                    'building_production': '建筑产出',
                    'quest_rewards': '任务奖励',
                    'event_rewards': '活动奖励',
                    'purchase': '购买'
                },
                '3_资源消耗': {
                    'building_cost': '建筑消耗',
                    'troop_training': '征兵消耗',
                    'research_cost': '研究消耗',
                    'healing_cost': '治疗消耗',
                    'trade_cost': '交易消耗'
                },
                '4_资源平衡': {
                    'income_vs_expense': '收支平衡',
                    'resource_bottleneck': '资源瓶颈',
                    'inflation_control': '通胀控制',
                    'whale_balance': '大 R 平衡'
                },
                '5_交易系统': {
                    'market': '市场系统',
                    'trade_ratio': '交易比例',
                    'trade_tax': '交易税',
                    'alliance_help': '联盟援助'
                },
                '6_付费设计': {
                    'premium_currency': '付费货币',
                    'conversion_rate': '兑换比例',
                    'value_proposition': '付费价值',
                    'whale_spending': '大 R 消费点'
                },
                '7_数据分析': {
                    'resource_metrics': '资源指标',
                    'income_tracking': '收入追踪',
                    'spending_patterns': '消费模式',
                    'balance_dashboard': '平衡看板'
                }
            }
        }
    
    def _alliance_template(self) -> Dict[str, Any]:
        """联盟系统模板"""
        return {
            'title': 'SLG 联盟系统策划案',
            'version': '1.0',
            'sections': {
                '1_联盟概述': {
                    'system_goal': '系统设计目标',
                    'alliance_features': '联盟功能列表',
                    'social_design': '社交设计理念'
                },
                '2_联盟结构': {
                    'member_limit': '成员上限',
                    'ranks': '职位体系（盟主/副盟/官员/成员）',
                    'permissions': '权限体系',
                    'application': '加入流程'
                },
                '3_联盟功能': {
                    'alliance_tech': '联盟科技',
                    'alliance_shop': '联盟商店',
                    'alliance_gifts': '联盟礼物',
                    'help_system': '援助系统',
                    'language_chat': '聊天翻译'
                },
                '4_联盟战争': {
                    'territory_war': '领土战',
                    'fortress_war': '关卡战',
                    'alliance_tournament': '联盟赛事',
                    'reward_distribution': '奖励分配'
                },
                '5_联盟外交': {
                    'alliance_relations': '联盟关系（友好/敌对/中立）',
                    'non_aggression_pact': '互不侵犯条约',
                    'coalition': '联盟联盟',
                    'spy_system': '间谍系统'
                },
                '6_联盟管理': {
                    'activity_tracking': '活跃度追踪',
                    'kick_rules': '踢人规则',
                    'succession': '权力交接',
                    'disband': '解散规则'
                },
                '7_美术需求': {
                    'alliance_ui': '联盟 UI',
                    'alliance_banner': '联盟旗帜',
                    'territory_markers': '领土标记'
                },
                '8_程序需求': {
                    'alliance_logic': '联盟逻辑',
                    'chat_system': '聊天系统',
                    'sync': '数据同步',
                    'anti_abuse': '反滥用'
                }
            }
        }
    
    def _worldmap_template(self) -> Dict[str, Any]:
        """大地图设计模板"""
        return {
            'title': 'SLG 大地图设计策划案',
            'version': '1.0',
            'sections': {
                '1_地图概述': {
                    'map_name': '地图名称',
                    'map_size': '地图尺寸（格数）',
                    'server_capacity': '单服容量',
                    'season_design': '赛季设计'
                },
                '2_地图元素': {
                    'terrain_types': '地形类型（平原/山地/森林/河流）',
                    'resource_tiles': '资源地块',
                    'npc_cities': 'NPC 城市',
                    'passages': '关隘/渡口',
                    'special_locations': '特殊地点'
                },
                '3_领地系统': {
                    'territory_mechanic': '领地机制',
                    'expansion': '扩张规则',
                    'connection': '连接规则',
                    'occupation': '占领规则'
                },
                '4_行军系统': {
                    'movement_speed': '行军速度',
                    'terrain_impact': '地形影响',
                    'stamina_system': '体力系统',
                    'reinforcement': '增援规则'
                },
                '5_PVE 设计': {
                    'barbarian_camps': '蛮族营地',
                    'npc_cities_attack': 'NPC 城市攻打',
                    'boss_events': 'BOSS 事件',
                    'pve_rewards': 'PVE 奖励'
                },
                '6_PVP 设计': {
                    'player_city_attack': '玩家城市攻打',
                    'territory_war': '领土争夺',
                    'resource_raid': '资源掠夺',
                    'pvp_rewards': 'PVP 奖励'
                },
                '7_平衡设计': {
                    'spawn_balance': '出生点平衡',
                    'resource_balance': '资源分布平衡',
                    'pay_vs_free': '付费与免费平衡',
                    'new_vs_old': '新旧玩家平衡'
                },
                '8_美术需求': {
                    'map_art': '地图美术',
                    'terrain_art': '地形美术',
                    'minimap': '小地图',
                    'vfx': '行军/战斗特效'
                }
            }
        }
    
    def get_template(self, template_type: str) -> Dict[str, Any]:
        """获取指定模板"""
        template_map = {
            'building': 'building_system',
            'building_system': 'building_system',
            'troop': 'troop_system',
            'troop_system': 'troop_system',
            'resource': 'resource_system',
            'resource_system': 'resource_system',
            'alliance': 'alliance_system',
            'alliance_system': 'alliance_system',
            'map': 'world_map',
            'world_map': 'world_map'
        }
        
        key = template_map.get(template_type.lower(), template_type.lower())
        return self.templates.get(key, None)
    
    def list_templates(self) -> List[Dict[str, str]]:
        """列出所有 SLG 模板"""
        return [
            {
                'id': 'building_system',
                'name': '建筑系统',
                'description': 'SLG 建筑系统模板，包含主城/资源/军事/科技/防御建筑等',
                'sections': 6
            },
            {
                'id': 'troop_system',
                'name': '兵种系统',
                'description': 'SLG 兵种系统模板，包含属性/克制/升级/英雄带兵等',
                'sections': 8
            },
            {
                'id': 'resource_system',
                'name': '资源系统',
                'description': 'SLG 资源系统模板，包含产出/消耗/平衡/交易/付费等',
                'sections': 7
            },
            {
                'id': 'alliance_system',
                'name': '联盟系统',
                'description': 'SLG 联盟系统模板，包含结构/功能/战争/外交/管理等',
                'sections': 8
            },
            {
                'id': 'world_map',
                'name': '大地图设计',
                'description': 'SLG 大地图模板，包含元素/领地/行军/PVE/PVP/平衡等',
                'sections': 8
            }
        ]


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python templates_slg.py <command> [args]")
        print("Commands:")
        print("  list                     - 列出 SLG 模板")
        print("  get <type>               - 获取模板")
        sys.exit(1)
    
    command = sys.argv[1]
    library = SLGTemplates()
    
    if command == 'list':
        templates = library.list_templates()
        print(f"SLG 游戏模板库（共{len(templates)}个模板）:\n")
        for t in templates:
            print(f"{t['id']}: {t['name']}")
            print(f"  {t['description']}")
            print(f"  章节数：{t['sections']}\n")
    
    elif command == 'get':
        template_type = sys.argv[2] if len(sys.argv) > 2 else None
        if not template_type:
            print("Error: 需要提供模板类型")
            sys.exit(1)
        
        template = library.get_template(template_type)
        if template:
            import json
            print(json.dumps(template, ensure_ascii=False, indent=2))
        else:
            print(f"模板 {template_type} 不存在")
            print("可用模板:", list(library.templates.keys()))
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
