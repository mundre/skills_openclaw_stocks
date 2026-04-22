#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 长线运营游戏模板库
提供标准化的新内容设计模板
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime

# 模板目录
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class TemplateLibrary:
    """长线运营游戏模板库"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Any]:
        """加载所有模板"""
        return {
            'new_character': self._character_template(),
            'new_activity': self._activity_template(),
            'new_system': self._system_template(),
            'version_update': self._version_update_template(),
            'numeric_adjustment': self._numeric_adjustment_template()
        }
    
    def _character_template(self) -> Dict[str, Any]:
        """新角色设计模板"""
        return {
            'title': '新角色设计策划案',
            'version': '1.0',
            'sections': {
                '1_角色概述': {
                    'name': '角色名称',
                    'title': '角色称号',
                    'element': '元素属性（火/水/风/雷/草/冰/岩）',
                    'weapon': '武器类型（剑/弓/法器等）',
                    'rarity': '稀有度（4 星/5 星）',
                    'release_version': '上线版本（如 v2.5）',
                    'design_concept': '设计理念（100 字以内）'
                },
                '2_背景故事': {
                    'origin': '出身背景',
                    'affiliation': '所属势力',
                    'personality': '性格特点',
                    'appearance': '外貌描述',
                    'voice_actor': '配音演员（待定）',
                    'story_chapter': '传说任务章节'
                },
                '3_技能设计': {
                    'passive_talent_1': '固有天赋 1（名称 + 效果）',
                    'passive_talent_2': '固有天赋 2（名称 + 效果）',
                    'passive_talent_3': '固有天赋 3（名称 + 效果）',
                    'elemental_skill': '元素战技（E 技能）',
                    'elemental_burst': '元素爆发（Q 技能）',
                    'skill_mechanics': '技能机制详解',
                    'skill_combo': '技能连招推荐'
                },
                '4_数值设计': {
                    'base_stats': '基础属性（HP/攻击/防御/暴击等）',
                    'scaling': '成长曲线（1-90 级）',
                    'skill_damage': '技能伤害倍率',
                    'cooldown': '技能冷却时间',
                    'energy_cost': '元素能量消耗',
                    'constellation': '命之座效果（1-6 命）'
                },
                '5_获取方式': {
                    'gacha_banner': '卡池名称',
                    'banner_duration': '卡池持续时间',
                    'pity_system': '保底机制',
                    'alternative_source': '其他获取途径（活动/商店等）'
                },
                '6_美术需求': {
                    'character_model': '角色模型（3 视图 + 动作）',
                    'skill_effects': '技能特效',
                    'ui_elements': 'UI 元素（头像/立绘等）',
                    'promotional_art': '宣传图',
                    'animation': '动画需求（PV/演示等）'
                },
                '7_程序需求': {
                    'new_mechanics': '新机制实现',
                    'ai_behavior': 'AI 行为（如果是 NPC）',
                    'network_sync': '网络同步需求',
                    'performance': '性能优化要求'
                },
                '8_测试要点': {
                    'functional_test': '功能测试用例',
                    'balance_test': '平衡性测试',
                    'compatibility_test': '兼容性测试',
                    'exploit_test': '漏洞测试'
                },
                '9_运营计划': {
                    'marketing': '营销计划',
                    'community_event': '社区活动',
                    'merchandise': '周边商品',
                    'collaboration': '联动计划'
                },
                '10_世界观一致性检查': {
                    'element_system': '元素体系一致性',
                    'faction_relation': '势力关系一致性',
                    'timeline': '时间线一致性',
                    'character_relations': '角色关系一致性',
                    'conflict_check': '冲突检查结果'
                }
            },
            'attachments': [
                '角色三视图.png',
                '技能效果图.png',
                '数值配置表.csv',
                '动作列表.xlsx'
            ]
        }
    
    def _activity_template(self) -> Dict[str, Any]:
        """新活动策划模板"""
        return {
            'title': '新活动策划案',
            'version': '1.0',
            'sections': {
                '1_活动概述': {
                    'activity_name': '活动名称',
                    'activity_type': '活动类型（签到/挑战/剧情/收集等）',
                    'theme': '活动主题',
                    'target_audience': '目标用户（新玩家/老玩家/付费玩家等）',
                    'duration': '活动持续时间',
                    'release_version': '上线版本'
                },
                '2_活动玩法': {
                    'core_gameplay': '核心玩法描述',
                    'gameplay_loop': '玩法循环',
                    'entry_requirements': '参与条件',
                    'activity_rules': '活动规则',
                    'difficulty_levels': '难度分级'
                },
                '3_活动奖励': {
                    'participation_rewards': '参与奖励',
                    'completion_rewards': '完成奖励',
                    'ranking_rewards': '排名奖励',
                    'achievement_rewards': '成就奖励',
                    'reward_budget': '奖励预算（资源产出评估）'
                },
                '4_活动剧情': {
                    'story_background': '故事背景',
                    'story_chapters': '剧情章节',
                    'character_appearance': '登场角色',
                    'dialogue_script': '对话脚本',
                    'cutscene': '过场动画'
                },
                '5_数值设计': {
                    'enemy_stats': '敌人属性',
                    'player_power_requirement': '玩家战力要求',
                    'resource_consumption': '资源消耗',
                    'reward_distribution': '奖励产出曲线',
                    'difficulty_curve': '难度曲线'
                },
                '6_美术需求': {
                    'activity_ui': '活动 UI 界面',
                    'promotional_art': '宣传图',
                    'activity_icon': '活动图标',
                    'reward_icons': '奖励图标',
                    'special_effects': '特效需求'
                },
                '7_程序需求': {
                    'new_features': '新功能开发',
                    'data_tracking': '数据埋点',
                    'anti_cheat': '反作弊措施',
                    'server_load': '服务器负载评估'
                },
                '8_运营计划': {
                    'pre_heat': '预热计划',
                    'announcement': '公告计划',
                    'community_management': '社区运营',
                    'crisis_management': '危机公关预案'
                },
                '9_数据分析': {
                    'key_metrics': '核心指标（DAU/参与率/留存等）',
                    'success_criteria': '成功标准',
                    'ab_test': 'AB 测试方案'
                }
            }
        }
    
    def _system_template(self) -> Dict[str, Any]:
        """新系统上线模板"""
        return {
            'title': '新系统上线策划案',
            'version': '1.0',
            'sections': {
                '1_系统概述': {
                    'system_name': '系统名称',
                    'system_type': '系统类型（社交/养成/战斗等）',
                    'design_goal': '设计目标',
                    'target_users': '目标用户',
                    'release_version': '上线版本',
                    'priority': '优先级（P0/P1/P2）'
                },
                '2_核心玩法': {
                    'gameplay_description': '玩法描述',
                    'user_flow': '用户流程',
                    'core_loop': '核心循环',
                    'interaction_design': '交互设计'
                },
                '3_系统规则': {
                    'entry_conditions': '开启条件',
                    'operation_rules': '操作规则',
                    'restriction_rules': '限制规则',
                    'exception_handling': '异常处理'
                },
                '4_数值设计': {
                    'resource_input': '资源投入',
                    'resource_output': '资源产出',
                    'conversion_rate': '转化比例',
                    'balance_check': '平衡性检查'
                },
                '5_界面设计': {
                    'ui_layout': '界面布局',
                    'interaction_flow': '交互流程',
                    'icon_design': '图标设计',
                    'animation': '动效设计'
                },
                '6_技术实现': {
                    'architecture': '技术架构',
                    'dependencies': '依赖系统',
                    'performance': '性能要求',
                    'compatibility': '兼容性要求'
                },
                '7_测试计划': {
                    'test_scope': '测试范围',
                    'test_cases': '测试用例',
                    'performance_test': '性能测试',
                    'stress_test': '压力测试'
                },
                '8_上线计划': {
                    'release_timeline': '上线时间线',
                    'rollout_plan': '发布计划',
                    'rollback_plan': '回滚方案',
                    'monitoring': '监控方案'
                }
            }
        }
    
    def _version_update_template(self) -> Dict[str, Any]:
        """版本更新模板"""
        return {
            'title': '版本更新策划案',
            'version': '1.0',
            'sections': {
                '1_版本概述': {
                    'version_number': '版本号（如 v2.5）',
                    'release_date': '上线日期',
                    'update_size': '更新包大小',
                    'force_update': '是否强制更新',
                    'maintenance_time': '维护时间'
                },
                '2_更新内容': {
                    'new_characters': '新角色',
                    'new_activities': '新活动',
                    'new_systems': '新系统',
                    'new_areas': '新地图/区域',
                    'new_story': '新剧情'
                },
                '3_优化调整': {
                    'balance_changes': '平衡性调整',
                    'bug_fixes': 'BUG 修复',
                    'performance_optimization': '性能优化',
                    'ui_ux_improvement': 'UI/UX 优化'
                },
                '4_影响评估': {
                    'development_workload': '开发工作量',
                    'testing_workload': '测试工作量',
                    'server_impact': '服务器影响',
                    'client_impact': '客户端影响'
                },
                '5_公告计划': {
                    'pre_announcement': '预告公告',
                    'update_announcement': '更新公告',
                    'patch_notes': '更新说明',
                    'faq': '常见问题'
                }
            }
        }
    
    def _numeric_adjustment_template(self) -> Dict[str, Any]:
        """数值调整模板"""
        return {
            'title': '数值调整策划案',
            'version': '1.0',
            'sections': {
                '1_调整概述': {
                    'adjustment_reason': '调整原因',
                    'adjustment_goal': '调整目标',
                    'affected_content': '影响内容',
                    'priority': '优先级'
                },
                '2_数据分析': {
                    'current_state': '当前状态',
                    'problem_identification': '问题识别',
                    'data_support': '数据支撑',
                    'player_feedback': '玩家反馈'
                },
                '3_调整方案': {
                    'before_values': '调整前数值',
                    'after_values': '调整后数值',
                    'change_percentage': '变化幅度',
                    'rationale': '调整依据'
                },
                '4_影响评估': {
                    'gameplay_impact': '玩法影响',
                    'player_impact': '玩家影响',
                    'economy_impact': '经济影响',
                    'risk_assessment': '风险评估'
                },
                '5_测试计划': {
                    'simulation_test': '模拟测试',
                    'ptr_test': '测试服测试',
                    'monitoring_plan': '监控计划'
                },
                '6_公告方案': {
                    'announcement_content': '公告内容',
                    'communication_strategy': '沟通策略',
                    'feedback_collection': '反馈收集'
                }
            }
        }
    
    def get_template(self, template_type: str) -> Dict[str, Any]:
        """
        获取指定模板
        
        Args:
            template_type: 模板类型
                - new_character: 新角色
                - new_activity: 新活动
                - new_system: 新系统
                - version_update: 版本更新
                - numeric_adjustment: 数值调整
        
        Returns:
            模板内容
        """
        template_map = {
            'new_character': 'new_character',
            'new_activity': 'new_activity',
            'new_system': 'new_system',
            'version_update': 'version_update',
            'numeric_adjustment': 'numeric_adjustment',
            'character': 'new_character',
            'activity': 'new_activity',
            'system': 'new_system',
            'version': 'version_update',
            'numeric': 'numeric_adjustment'
        }
        
        key = template_map.get(template_type.lower(), template_type.lower())
        return self.templates.get(key, None)
    
    def list_templates(self) -> List[Dict[str, str]]:
        """列出所有可用模板"""
        return [
            {
                'id': 'new_character',
                'name': '新角色设计',
                'description': '完整的角色设计模板，包含背景/技能/数值/美术需求等',
                'sections': 10
            },
            {
                'id': 'new_activity',
                'name': '新活动策划',
                'description': '活动策划模板，包含玩法/奖励/剧情/运营等',
                'sections': 9
            },
            {
                'id': 'new_system',
                'name': '新系统设计',
                'description': '新系统上线模板，包含玩法/规则/技术/测试等',
                'sections': 8
            },
            {
                'id': 'version_update',
                'name': '版本更新',
                'description': '版本更新管理模板，包含更新内容/影响评估/公告等',
                'sections': 5
            },
            {
                'id': 'numeric_adjustment',
                'name': '数值调整',
                'description': '数值平衡调整模板，包含数据分析/调整方案/影响评估等',
                'sections': 6
            }
        ]
    
    def generate_from_template(self, template_type: str, 
                                fill_data: Dict[str, Any] = None) -> str:
        """
        从模板生成策划案
        
        Args:
            template_type: 模板类型
            fill_data: 填充数据（可选）
        
        Returns:
            生成的策划案 Markdown 内容
        """
        template = self.get_template(template_type)
        
        if not template:
            return f"错误：模板 {template_type} 不存在"
        
        # 生成 Markdown 格式
        markdown = f"# {template['title']}\n\n"
        markdown += f"**版本**: {template['version']}\n"
        markdown += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        markdown += "---\n\n"
        
        for section_name, section_content in template['sections'].items():
            markdown += f"## {section_name}\n\n"
            
            if isinstance(section_content, dict):
                for field_name, field_value in section_content.items():
                    # 如果有填充数据，使用填充数据
                    if fill_data and field_name in fill_data:
                        value = fill_data[field_name]
                    else:
                        value = f"[请填写{field_value}]"
                    
                    markdown += f"### {field_name}\n{value}\n\n"
            else:
                markdown += f"{section_content}\n\n"
        
        if 'attachments' in template:
            markdown += "## 附件\n\n"
            for attachment in template['attachments']:
                markdown += f"- {attachment}\n"
        
        return markdown


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python templates.py <command> [args]")
        print("Commands:")
        print("  list                     - 列出所有模板")
        print("  get <type>               - 获取模板")
        print("  generate <type> [data]   - 从模板生成")
        sys.exit(1)
    
    command = sys.argv[1]
    library = TemplateLibrary()
    
    if command == 'list':
        templates = library.list_templates()
        print(f"共 {len(templates)} 个模板:\n")
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
            print(json.dumps(template, ensure_ascii=False, indent=2))
        else:
            print(f"模板 {template_type} 不存在")
    
    elif command == 'generate':
        template_type = sys.argv[2] if len(sys.argv) > 2 else None
        if not template_type:
            print("Error: 需要提供模板类型")
            sys.exit(1)
        
        # 简单演示，实际应该从文件或参数读取填充数据
        markdown = library.generate_from_template(template_type)
        print(markdown[:2000])  # 只显示前 2000 字
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
