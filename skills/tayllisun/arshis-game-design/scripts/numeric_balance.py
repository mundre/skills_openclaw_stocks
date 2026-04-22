#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 数值平衡工具
经济系统/战斗平衡/成长曲线可视化
"""

import os
import json
import math
from typing import Dict, Any, List
from datetime import datetime


class NumericBalancer:
    """数值平衡器"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), 'output', 'numeric')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def calculate_economy_balance(self, economy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算经济系统平衡
        
        Args:
            economy_data: 经济数据（产出/消耗）
        
        Returns:
            平衡分析报告
        """
        report = {
            'status': 'analyzed',
            'income_sources': [],
            'expense_sinks': [],
            'balance_score': 0,
            'inflation_risk': 'low',
            'recommendations': []
        }
        
        # 简化分析
        income = economy_data.get('total_income', 1000)
        expense = economy_data.get('total_expense', 800)
        
        # 计算盈余
        surplus = income - expense
        surplus_rate = surplus / income if income > 0 else 0
        
        report['income_sources'] = economy_data.get('income_sources', [])
        report['expense_sinks'] = economy_data.get('expense_sinks', [])
        
        # 平衡评分
        if 0.1 <= surplus_rate <= 0.3:
            report['balance_score'] = 90
            report['inflation_risk'] = 'low'
        elif 0.3 < surplus_rate <= 0.5:
            report['balance_score'] = 70
            report['inflation_risk'] = 'medium'
        elif surplus_rate > 0.5:
            report['balance_score'] = 50
            report['inflation_risk'] = 'high'
        else:
            report['balance_score'] = 60
            report['inflation_risk'] = 'deflation'
        
        # 建议
        if surplus_rate > 0.3:
            report['recommendations'].append('建议增加消耗途径，减少货币盈余')
        if surplus_rate < 0.1:
            report['recommendations'].append('建议增加产出途径，避免通货紧缩')
        
        # 保存报告
        filename = f"economy_balance_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return {
            'status': 'generated',
            'filepath': filepath,
            'report': report
        }
    
    def calculate_growth_curve(self, curve_type: str = 'exponential',
                                params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        计算成长曲线
        
        Args:
            curve_type: 曲线类型（exponential/linear/logarithmic）
            params: 参数
        
        Returns:
            成长曲线数据
        """
        if params is None:
            params = {
                'base_value': 100,
                'growth_rate': 1.1,
                'max_level': 100
            }
        
        curve_data = {
            'type': curve_type,
            'params': params,
            'levels': []
        }
        
        base = params.get('base_value', 100)
        rate = params.get('growth_rate', 1.1)
        max_level = params.get('max_level', 100)
        
        for level in range(1, max_level + 1):
            if curve_type == 'exponential':
                value = base * (rate ** (level - 1))
            elif curve_type == 'linear':
                value = base + (base * 0.1 * (level - 1))
            elif curve_type == 'logarithmic':
                value = base * math.log(level + 1) / math.log(2)
            else:
                value = base * (rate ** (level - 1))
            
            curve_data['levels'].append({
                'level': level,
                'value': round(value, 2)
            })
        
        # 保存曲线数据
        filename = f"growth_curve_{curve_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(curve_data, f, ensure_ascii=False, indent=2)
        
        return {
            'status': 'generated',
            'filepath': filepath,
            'curve': curve_data,
            'preview': curve_data['levels'][:10]  # 预览前 10 级
        }
    
    def compare_stats(self, stats_a: Dict[str, Any], 
                      stats_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        对比两组数值
        
        Args:
            stats_a: A 组数值
            stats_b: B 组数值
        
        Returns:
            对比报告
        """
        comparison = {
            'stats_a': stats_a,
            'stats_b': stats_b,
            'differences': {},
            'balance_score': 100
        }
        
        # 对比每个属性
        all_keys = set(stats_a.keys()) | set(stats_b.keys())
        
        for key in all_keys:
            value_a = stats_a.get(key, 0)
            value_b = stats_b.get(key, 0)
            
            diff = value_a - value_b
            diff_rate = diff / value_b if value_b != 0 else 0
            
            comparison['differences'][key] = {
                'value_a': value_a,
                'value_b': value_b,
                'diff': diff,
                'diff_rate': f"{diff_rate*100:.1f}%"
            }
        
        # 平衡评分
        max_diff_rate = max(
            abs(float(v['diff_rate'].replace('%', ''))) 
            for v in comparison['differences'].values()
        ) if comparison['differences'] else 0
        
        if max_diff_rate < 10:
            comparison['balance_score'] = 95
        elif max_diff_rate < 20:
            comparison['balance_score'] = 80
        elif max_diff_rate < 30:
            comparison['balance_score'] = 60
        else:
            comparison['balance_score'] = 40
        
        return comparison
    
    def generate_numeric_template(self, game_type: str = 'rpg') -> Dict[str, Any]:
        """
        生成数值模板
        
        Args:
            game_type: 游戏类型
        
        Returns:
            数值模板
        """
        templates = {
            'rpg': self._rpg_numeric_template(),
            'moba': self._moba_numeric_template(),
            'fps': self._fps_numeric_template()
        }
        
        template = templates.get(game_type, templates['rpg'])
        
        # 保存模板
        filename = f"numeric_template_{game_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        
        return {
            'status': 'generated',
            'filepath': filepath,
            'template': template
        }
    
    def _rpg_numeric_template(self) -> Dict[str, Any]:
        """RPG 数值模板"""
        return {
            'game_type': 'rpg',
            'base_stats': {
                'level_1': {
                    'hp': 100,
                    'attack': 10,
                    'defense': 5,
                    'crit_rate': 0.05,
                    'crit_damage': 1.5
                },
                'level_100': {
                    'hp': 10000,
                    'attack': 1000,
                    'defense': 500,
                    'crit_rate': 0.3,
                    'crit_damage': 2.0
                }
            },
            'growth_rates': {
                'hp': 1.15,
                'attack': 1.12,
                'defense': 1.10
            },
            'combat_formulas': {
                'damage': '(attack * skill_multiplier) - (enemy_defense * 0.5)',
                'crit': 'damage * crit_damage',
                'final': 'damage * (1 + damage_bonus)'
            }
        }
    
    def _moba_numeric_template(self) -> Dict[str, Any]:
        """MOBA 数值模板"""
        return {
            'game_type': 'moba',
            'base_stats': {
                'level_1': {
                    'hp': 3000,
                    'attack': 60,
                    'defense': 30,
                    'magic_resist': 30
                },
                'level_18': {
                    'hp': 6000,
                    'attack': 150,
                    'defense': 100,
                    'magic_resist': 100
                }
            },
            'growth_per_level': {
                'hp': 100,
                'attack': 3,
                'defense': 4
            }
        }
    
    def _fps_numeric_template(self) -> Dict[str, Any]:
        """FPS 数值模板"""
        return {
            'game_type': 'fps',
            'weapons': {
                'rifle': {
                    'damage': 30,
                    'fire_rate': 600,
                    'accuracy': 0.8,
                    'magazine': 30
                },
                'sniper': {
                    'damage': 100,
                    'fire_rate': 60,
                    'accuracy': 1.0,
                    'magazine': 5
                }
            },
            'time_to_kill': {
                'rifle_vs_no_armor': 0.4,
                'rifle_vs_armor': 0.6,
                'sniper_headshot': 0.0
            }
        }


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python numeric_balance.py <command> [args]")
        print("Commands:")
        print("  economy                  - 经济平衡分析")
        print("  growth <type>            - 成长曲线")
        print("  template <game_type>     - 数值模板")
        sys.exit(1)
    
    import sys as system_module
    command = system_module.argv[1]
    balancer = NumericBalancer()
    
    if command == 'economy':
        economy_data = {
            'total_income': 1000,
            'total_expense': 800,
            'income_sources': ['任务', '副本', '活动'],
            'expense_sinks': ['强化', '购买', '合成']
        }
        result = balancer.calculate_economy_balance(economy_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'growth':
        curve_type = system_module.argv[2] if len(system_module.argv) > 2 else 'exponential'
        result = balancer.calculate_growth_curve(curve_type)
        print(f"成长曲线已生成：{result['filepath']}")
        print(f"预览（前 10 级）:")
        for level_data in result['preview']:
            print(f"  {level_data['level']} 级：{level_data['value']}")
    
    elif command == 'template':
        game_type = system_module.argv[2] if len(system_module.argv) > 2 else 'rpg'
        result = balancer.generate_numeric_template(game_type)
        print(f"数值模板已生成：{result['filepath']}")
    
    else:
        print(f"未知命令：{command}")
        system_module.exit(1)


if __name__ == '__main__':
    main()
