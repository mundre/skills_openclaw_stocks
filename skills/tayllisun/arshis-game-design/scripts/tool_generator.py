#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 实用工具生成器
生成 Excel 配置表/Mermaid 流程图/数值计算工具等
"""

import os
import json
import sys
from typing import Dict, Any, List
from datetime import datetime


class ToolGenerator:
    """实用工具生成器"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_excel_config(self, config_type: str, 
                               game_type: str = None) -> Dict[str, Any]:
        """
        生成 Excel 配置表模板
        
        Args:
            config_type: 配置表类型（character/weapon/skill/enemy/item）
            game_type: 游戏类型
        
        Returns:
            配置表模板（CSV 格式）
        """
        templates = {
            'character': self._character_config_template(),
            'weapon': self._weapon_config_template(),
            'skill': self._skill_config_template(),
            'enemy': self._enemy_config_template(),
            'item': self._item_config_template()
        }
        
        template = templates.get(config_type, templates['character'])
        
        # 保存为 CSV
        filename = f"{config_type}_config_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return {
            'status': 'generated',
            'type': config_type,
            'filepath': filepath,
            'filename': filename,
            'preview': template[:500]
        }
    
    def _character_config_template(self) -> str:
        """角色配置表模板"""
        return """ID,Name,Rarity,Element,Weapon,HP_Base,HP_Growth,Attack_Base,Attack_Growth,Defense_Base,Defense_Growth,Crit_Rate,Crit_Damage,Elemental_Mastery,Skills,Passive_Talents,Constellations,Description
1001,温迪，5,风，弓，1000,50,80,8,60,6,0.05,1.5,200,"E:高天之歌，Q:风神之诗",3 个被动，6 命座，风神巴巴托斯
1002,迪卢克，5，火，双手剑，1200,60,100,10,70,7,0.05,1.5,200,"E:逆火之刃，Q:黎明",3 个被动，6 命座，晨曦酒庄主人
1003,刻晴，5，雷，单手剑，1100,55,90,9,65,6,0.05,1.5,200,"E:星斗归位，Q:天街巡游",3 个被动，6 命座，璃月七星
"""
    
    def _weapon_config_template(self) -> str:
        """武器配置表模板"""
        return """ID,Name,Rarity,Type,Base_Attack,Secondary_Stat,Stat_Value,Passive_Name,Passive_Effect,Refinement_Levels,Description
10001,天空之翼，5，弓，674,Crit_Damage,0.441,"回响长天的诗歌",暴击伤害提升，5,"风神巴巴托斯祝福的弓"
10002,和璞鸢，5，长柄武器，608,Attack,0.496,"昭理",攻击力提升，5,"璃月千岩军制式武器"
10003,风鹰剑，5，单手剑，674,Attack,0.413,"顺风而行",攻击力提升，5,"蒙德英雄的象征"
"""
    
    def _skill_config_template(self) -> str:
        """技能配置表模板"""
        return """ID,Name,Character_ID,Type,Cooldown,Energy_Cost,Duration,Damage_Scaling,Effect_Type,Effect_Value,Description
100101,高天之歌，1001,E,15,0,2,1.5,Damage,"造成风元素伤害"
100102,风神之诗，1001,Q,15,60,15,2.0,Damage+CC,"造成风元素伤害并牵引敌人"
100201,逆火之刃，1002,E,10,0,0,2.5,Damage,"造成火元素伤害"
100202,黎明，1002,Q,12,40,0,3.0,Damage,"造成火元素范围伤害"
"""
    
    def _enemy_config_template(self) -> str:
        """敌人配置表模板"""
        return """ID,Name,Type,Level,HP,Attack,Defense,Element,Weakness,Resistances,Skills,Drops,Spawn_Locations,Description
2001,丘丘人，Common,1,500,50,30,无，无，无，"普通攻击",["摩拉","经验书"],["蒙德","璃月"],"常见的魔物"
2002,丘丘暴徒，Common,1,800,70,40,无，无，无，"普通攻击，重击",["摩拉","经验书","武器突破素材"],["蒙德","璃月"],"强壮的丘丘人"
2003,风史莱姆，Elemental,1,600,60,35,风，火，风免疫，"风弹，风球",["摩拉","风元素素材"],["蒙德"],"风元素构成的史莱姆"
"""
    
    def _item_config_template(self) -> str:
        """物品配置表模板"""
        return """ID,Name,Type,Rarity,Effect,Effect_Value,Duration,Cooldown,Stack_Limit,Price,Description
3001,摩拉，Currency,3,"货币",1,0,0,99999,1,"提瓦特大陆的通用货币"
3002,经验书，Material,3,"角色经验",1000,0,0,9999,10,"提供角色经验"
3003,风神瞳，Collectible,4,"提升体力",0,0,0,1,0,"收集后可提升体力上限"
3004,治疗药水，Consumable,2,"恢复 HP",500,0,5,99,50,"恢复 500 点生命值"
"""
    
    def generate_mermaid_flowchart(self, flowchart_type: str,
                                    content: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成 Mermaid 流程图
        
        Args:
            flowchart_type: 流程图类型（game_loop/combat_loop/quest/system）
            content: 流程图内容
        
        Returns:
            Mermaid 代码
        """
        templates = {
            'game_loop': self._game_loop_flowchart(),
            'combat_loop': self._combat_loop_flowchart(),
            'quest_flow': self._quest_flow_flowchart(),
            'system_arch': self._system_arch_flowchart()
        }
        
        mermaid_code = templates.get(flowchart_type, templates['game_loop'])
        
        # 保存为 md 文件
        filename = f"{flowchart_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"```mermaid\n{mermaid_code}\n```\n")
        
        return {
            'status': 'generated',
            'type': flowchart_type,
            'filepath': filepath,
            'filename': filename,
            'mermaid_code': mermaid_code
        }
    
    def _game_loop_flowchart(self) -> str:
        """游戏主循环流程图"""
        return """graph TD
    A[玩家登录] --> B[加载存档]
    B --> C{选择模式}
    C -->|主线 | D[主线任务]
    C -->|支线 | E[支线任务]
    C -->|探索 | F[开放世界探索]
    D --> G[战斗系统]
    E --> G
    F --> G
    G --> H[获得奖励]
    H --> I[角色养成]
    I --> J{继续游戏？}
    J -->|是 | C
    J -->|否 | K[保存存档]
    K --> L[退出游戏]
"""
    
    def _combat_loop_flowchart(self) -> str:
        """战斗循环流程图"""
        return """graph TD
    A[进入战斗] --> B[选择角色]
    B --> C[选择技能]
    C --> D{技能类型}
    D -->|普通攻击 | E[造成物理伤害]
    D -->|元素技能 | F[造成元素伤害]
    D -->|元素爆发 | G[造成大量伤害]
    E --> H{敌人状态}
    F --> H
    G --> H
    H -->|存活 | I[敌人反击]
    H -->|击败 | J[获得战利品]
    I --> C
    J --> K[战斗结束]
"""
    
    def _quest_flow_flowchart(self) -> str:
        """任务流程流程图"""
        return """graph TD
    A[接受任务] --> B[阅读任务描述]
    B --> C{任务类型}
    C -->|讨伐 | D[击败指定敌人]
    C -->|收集 | E[收集指定物品]
    C -->|对话 | F[与 NPC 对话]
    C -->|探索 | G[到达指定地点]
    D --> H[完成任务]
    E --> H
    F --> H
    G --> H
    H --> I[领取奖励]
    I --> J[任务完成]
"""
    
    def _system_arch_flowchart(self) -> str:
        """系统架构流程图"""
        return """graph TB
    A[客户端] --> B[UI 层]
    A --> C[游戏逻辑层]
    A --> D[渲染层]
    B --> E[界面管理]
    B --> F[输入处理]
    C --> G[战斗系统]
    C --> H[任务系统]
    C --> I[养成系统]
    D --> J[3D 渲染]
    D --> K[特效渲染]
    G --> L[服务器]
    H --> L
    I --> L
    L --> M[数据库]
    L --> N[日志系统]
"""
    
    def generate_numeric_calculator(self, calculator_type: str,
                                     game_type: str = None) -> Dict[str, Any]:
        """
        生成数值计算工具
        
        Args:
            calculator_type: 计算器类型（damage/exp/cost/gacha）
            game_type: 游戏类型
        
        Returns:
            计算工具（Python 代码）
        """
        templates = {
            'damage': self._damage_calculator(),
            'exp': self._exp_calculator(),
            'cost': self._cost_calculator(),
            'gacha': self._gacha_calculator()
        }
        
        calculator_code = templates.get(calculator_type, templates['damage'])
        
        # 保存为 py 文件
        filename = f"{calculator_type}_calculator_{datetime.now().strftime('%Y%m%d%H%M%S')}.py"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(calculator_code)
        
        return {
            'status': 'generated',
            'type': calculator_type,
            'filepath': filepath,
            'filename': filename,
            'code_preview': calculator_code[:500]
        }
    
    def _damage_calculator(self) -> str:
        """伤害计算器"""
        return """#!/usr/bin/env python3
\"\"\"
伤害计算器
基于原神伤害公式
\"\"\"

def calculate_damage(base_attack, skill_multiplier, crit_rate, crit_damage, 
                     elemental_mastery, enemy_defense, resistance, reaction_multiplier=1.0):
    \"\"\"
    计算伤害
    
    Args:
        base_attack: 基础攻击力
        skill_multiplier: 技能倍率
        crit_rate: 暴击率
        crit_damage: 暴击伤害
        elemental_mastery: 元素精通
        enemy_defense: 敌人防御力
        resistance: 敌人抗性
        reaction_multiplier: 反应倍率
    
    Returns:
        期望伤害
    \"\"\"
    # 攻击力
    attack = base_attack * skill_multiplier
    
    # 暴击期望
    crit_expectation = 1 + crit_rate * crit_damage
    
    # 防御乘区（假设角色等级 90，敌人等级 90）
    defense_multiplier = 0.5
    
    # 抗性乘区
    resistance_multiplier = 1 - resistance
    
    # 元素精通加成（简化公式）
    mastery_multiplier = 1 + elemental_mastery / 2000
    
    # 期望伤害
    expected_damage = attack * crit_expectation * defense_multiplier * resistance_multiplier * mastery_multiplier * reaction_multiplier
    
    return expected_damage

if __name__ == '__main__':
    # 示例：计算胡桃 E 技能伤害
    damage = calculate_damage(
        base_attack=3000,
        skill_multiplier=2.0,
        crit_rate=0.7,
        crit_damage=1.5,
        elemental_mastery=200,
        enemy_defense=1000,
        resistance=0.1,
        reaction_multiplier=2.0  # 蒸发反应
    )
    print(f"期望伤害：{damage:.2f}")
"""
    
    def _exp_calculator(self) -> str:
        """经验计算器"""
        return """#!/usr/bin/env python3
\"\"\"
角色升级经验计算器
\"\"\"

def calculate_exp_to_level(current_level, target_level):
    \"\"\"
    计算从当前等级到目标等级所需经验
    
    Args:
        current_level: 当前等级
        target_level: 目标等级
    
    Returns:
        所需经验
    \"\"\"
    # 原神升级经验表（简化版）
    exp_table = {
        1: 0,
        20: 124000,
        40: 410000,
        50: 680000,
        60: 1080000,
        70: 1680000,
        80: 2540000,
        90: 4200000
    }
    
    # 计算所需经验
    current_exp = exp_table.get(current_level, 0)
    target_exp = exp_table.get(target_level, 4200000)
    
    return target_exp - current_exp

if __name__ == '__main__':
    exp = calculate_exp_to_level(1, 90)
    print(f"1 级到 90 级所需经验：{exp:,}")
"""
    
    def _cost_calculator(self) -> str:
        """成本计算器"""
        return """#!/usr/bin/env python3
\"\"\"
养成成本计算器
\"\"\"

def calculate_character_cost(target_level, talent_levels=(8,8,8)):
    \"\"\"
    计算角色养成成本
    
    Args:
        target_level: 目标等级
        talent_levels: 天赋等级 (E,Q, 被动)
    
    Returns:
        成本详情
    \"\"\"
    # 摩拉成本（简化）
    level_cost = {
        90: 2000000,
        80: 1700000,
        70: 1200000,
        60: 800000
    }
    
    talent_cost = sum([t * 100000 for t in talent_levels])
    
    total_mora = level_cost.get(target_level, 0) + talent_cost
    
    return {
        'level_cost': level_cost.get(target_level, 0),
        'talent_cost': talent_cost,
        'total_mora': total_mora,
        'total_mora_formatted': f"{total_mora:,}"
    }

if __name__ == '__main__':
    cost = calculate_character_cost(90, (9,9,9))
    print(f"90 级 999 养成成本：{cost['total_mora_formatted']} 摩拉")
"""
    
    def _gacha_calculator(self) -> str:
        """抽卡计算器"""
        return """#!/usr/bin/env python3
\"\"\"
抽卡期望计算器
基于原神抽卡规则
\"\"\"

def calculate_gacha_expectation(target_item, pity_count=0):
    \"\"\"
    计算抽卡期望
    
    Args:
        target_item: 目标物品（character/weapon）
        pity_count: 当前保底计数
    
    Returns:
        抽卡期望
    \"\"\"
    if target_item == 'character':
        base_rate = 0.006  # 0.6%
        soft_pity = 74
        hard_pity = 90
        guarantee_rate = 0.5  # 50% 保底
    elif target_item == 'weapon':
        base_rate = 0.007  # 0.7%
        soft_pity = 63
        hard_pity = 80
        guarantee_rate = 0.75  # 75% 保底
    else:
        return {'error': 'Unknown target item'}
    
    # 简化期望计算
    average_pulls = hard_pity * (2 - guarantee_rate)
    
    return {
        'target': target_item,
        'base_rate': f"{base_rate*100}%",
        'soft_pity': soft_pity,
        'hard_pity': hard_pity,
        'guarantee_rate': f"{guarantee_rate*100}%",
        'average_pulls': average_pulls,
        'average_stone': average_pulls * 160  # 160 原石/抽
    }

if __name__ == '__main__':
    char_exp = calculate_gacha_expectation('character')
    print(f"角色期望：{char_exp['average_pulls']:.1f} 抽，{char_exp['average_stone']:.0f} 原石")
    
    wep_exp = calculate_gacha_expectation('weapon')
    print(f"武器期望：{wep_exp['average_pulls']:.1f} 抽，{wep_exp['average_stone']:.0f} 原石")
"""
    
    def generate_all_tools(self, game_type: str = 'rpg') -> Dict[str, Any]:
        """
        生成所有实用工具
        
        Args:
            game_type: 游戏类型
        
        Returns:
            所有生成的工具
        """
        results = {
            'excel_configs': [],
            'flowcharts': [],
            'calculators': []
        }
        
        # 生成配置表
        for config_type in ['character', 'weapon', 'skill', 'enemy', 'item']:
            result = self.generate_excel_config(config_type, game_type)
            results['excel_configs'].append(result)
        
        # 生成流程图
        for flowchart_type in ['game_loop', 'combat_loop', 'quest_flow', 'system_arch']:
            result = self.generate_mermaid_flowchart(flowchart_type)
            results['flowcharts'].append(result)
        
        # 生成计算器
        for calculator_type in ['damage', 'exp', 'cost', 'gacha']:
            result = self.generate_numeric_calculator(calculator_type, game_type)
            results['calculators'].append(result)
        
        return results


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python tool_generator.py <command> [args]")
        print("Commands:")
        print("  excel <type>              - 生成 Excel 配置表")
        print("  flowchart <type>          - 生成流程图")
        print("  calculator <type>         - 生成计算器")
        print("  all [game_type]           - 生成所有工具")
        sys.exit(1)
    
    command = sys.argv[1]
    generator = ToolGenerator()
    
    if command == 'excel':
        config_type = sys.argv[2] if len(sys.argv) > 2 else 'character'
        result = generator.generate_excel_config(config_type)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'flowchart':
        flowchart_type = sys.argv[2] if len(sys.argv) > 2 else 'game_loop'
        result = generator.generate_mermaid_flowchart(flowchart_type)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'calculator':
        calculator_type = sys.argv[2] if len(sys.argv) > 2 else 'damage'
        result = generator.generate_numeric_calculator(calculator_type)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'all':
        game_type = sys.argv[2] if len(sys.argv) > 2 else 'rpg'
        results = generator.generate_all_tools(game_type)
        print(f"生成了 {len(results['excel_configs'])} 个配置表")
        print(f"生成了 {len(results['flowcharts'])} 个流程图")
        print(f"生成了 {len(results['calculators'])} 个计算器")
        print(f"输出目录：{generator.output_dir}")
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
