#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 智能整合生成器
整合心理学/社会学/市场/GDC/关卡设计知识库
"""

import os
import sys
import json
from typing import Dict, Any, List

# 导入知识库
try:
    from psychology_knowledge import GamePsychology
    from sociology_knowledge import GameSociology
    from market_analysis import MarketAnalysis
    from gdc_knowledge import GDCKnowledge
    from creative_engine import CreativeEngine
    KNOWLEDGE_AVAILABLE = True
except ImportError as e:
    print(f"警告：知识库导入失败：{e}")
    KNOWLEDGE_AVAILABLE = False


class IntelligentGenerator:
    """智能整合生成器"""
    
    def __init__(self):
        if KNOWLEDGE_AVAILABLE:
            self.psychology = GamePsychology()
            self.sociology = GameSociology()
            self.market = MarketAnalysis()
            self.gdc = GDCKnowledge()
            self.creative = CreativeEngine()
        else:
            self.psychology = None
            self.sociology = None
            self.market = None
            self.gdc = None
            self.creative = None
    
    def generate_with_knowledge(self, design_type: str, 
                                 design_content: str,
                                 game_type: str = None) -> Dict[str, Any]:
        """
        基于知识库生成智能建议
        
        Args:
            design_type: 设计类型（关卡/角色/系统等）
            design_content: 设计内容描述
            game_type: 游戏类型
        
        Returns:
            智能建议（包含知识库引用）
        """
        result = {
            'design_type': design_type,
            'design_content': design_content,
            'game_type': game_type,
            'insights': [],
            'principles': [],
            'case_studies': [],
            'suggestions': []
        }
        
        if not KNOWLEDGE_AVAILABLE:
            result['error'] = '知识库不可用'
            return result
        
        # 1. 心理学洞察
        if self.psychology:
            psych_insights = self.psychology.get_psychology_insights(design_content)
            result['insights'].extend(psych_insights)
        
        # 2. 社会学洞察
        if self.sociology:
            soc_insights = self.sociology.get_social_insights(design_content)
            result['insights'].extend(soc_insights)
        
        # 3. 市场洞察
        if self.market and game_type:
            market_insights = self.market.get_market_insights(game_type)
            result['insights'].extend(market_insights)
        
        # 4. GDC 精华
        if self.gdc:
            gdc_insights = self.gdc.get_gdc_insights(design_type)
            result['insights'].extend(gdc_insights)
            
            # 关卡设计原则
            if design_type == 'level' or '关卡' in design_content:
                level_design = self.gdc.knowledge.get('level_design_principles', {})
                result['principles'].append({
                    'category': '关卡设计五大原则',
                    'principles': level_design.get('five_core_principles', {})
                })
                result['principles'].append({
                    'category': '规划 - 扰动模型',
                    'formula': '70% 预期验证 + 30% 预期颠覆',
                    'description': '平衡玩家预期，既有满足感又有惊喜'
                })
        
        # 5. 创意建议
        if self.creative:
            creative_suggestions = self.creative.generate_creative_suggestions(
                design_content, game_type
            )
            result['suggestions'].extend(creative_suggestions)
        
        # 6. 成功案例
        if self.market:
            success_cases = self._get_success_cases(design_type, game_type)
            result['case_studies'] = success_cases
        
        return result
    
    def _get_success_cases(self, design_type: str, game_type: str) -> List[Dict[str, Any]]:
        """获取相关成功案例"""
        cases = []
        
        if not self.market:
            return cases
        
        # 长线运营游戏
        if game_type in ['gacha', 'mmorpg', 'moba', 'slg']:
            cases.append({
                'name': '原神',
                'type': '长线运营',
                'success_factors': [
                    '全球同步发行，统一运营节奏',
                    '持续高质量内容更新',
                    '文化输出典范'
                ],
                'key_metrics': {
                    '海外收入': '204.55 亿美元（2025 年）',
                    '市场地位': '中国游戏出海代表'
                }
            })
        
        # 单机游戏
        if game_type in ['action', 'rpg', 'adventure']:
            cases.append({
                'name': '黑神话：悟空',
                'type': '单机 3A',
                'success_factors': [
                    '销量破 3000 万份',
                    '总收入约 100 亿',
                    'Steam 好评率 90%+',
                    '精准全球营销',
                    '中国文化国际传播'
                ],
                'key_insight': '世界不是不接受中国故事，只是不接受「说不好」的中国故事'
            })
        
        # 独立游戏
        if game_type in ['indie', 'roguelike', 'puzzle']:
            cases.append({
                'name': '弓箭传说',
                'type': '独立游戏',
                'success_factors': [
                    '操作极其简单，只需手指滑动',
                    '每一局都做得足够有趣，体验拉满'
                ],
                'achievement': '被行业老兵称为「移动端史上的最爱」'
            })
        
        return cases
    
    def generate_level_design_suggestions(self) -> Dict[str, Any]:
        """生成关卡设计建议（基于 GDC 原则）"""
        if not self.gdc:
            return {'error': 'GDC 知识库不可用'}
        
        level_design = self.gdc.knowledge.get('level_design_principles', {})
        
        return {
            'five_principles': level_design.get('five_core_principles', {}),
            'ten_principles': level_design.get('ten_design_principles', {}).get('principles', []),
            'planning_disturbance': {
                'name': '规划 - 扰动模型',
                'formula': '70% 预期验证 + 30% 预期颠覆',
                'disturbance_elements': [
                    '内容（敌人类型）',
                    '持续时间',
                    '间隔',
                    '幅度'
                ],
                'example': '《Hades》死亡后解锁新剧情，将失败转化为持续动机'
            },
            'emotional_curve': {
                'name': '情感曲线',
                'pattern': '战斗 - 喘息 - 情感三段式节奏',
                'example': '《最后生还者》的节奏设计'
            },
            'guidance_methods': {
                'visual': '暖色调吸引注意力，冷色调暗示危险',
                'audio': '特定音效预示事件',
                'environment': '环境暗示（血迹/光线）',
                'ui': 'UI 提示明确下一步行动'
            }
        }
    
    def generate_narrative_suggestions(self) -> Dict[str, Any]:
        """生成叙事设计建议（基于 GDC 精华）"""
        if not self.gdc:
            return {'error': 'GDC 知识库不可用'}
        
        narrative = self.gdc.knowledge.get('narrative_design', {})
        
        return {
            'golden_seed_theory': {
                'name': '金种子理论',
                'description': '内容要真实，能够牵动玩家情感，从而打动人心',
                'application': '剧情/角色/主题都要有真实情感基础'
            },
            'fifty_fifty_design': {
                'name': '五五开设计法',
                'description': '设计有意义的游戏选择',
                'elements': [
                    '身体动作',
                    '内心挣扎',
                    '善恶观念',
                    '后果承担'
                ],
                'example': '《神界原罪 2》分解尸体获取能力的黑色幽默设计'
            },
            'tools': [
                'Twine - 搭建分支剧情',
                '关键节点设置 - 确保故事丰富且连贯',
                '晨间写作和呼吸练习 - 激发潜意识保持灵感'
            ],
            'principle': '相信自己，避免迎合大众，勇敢展现独特风格'
        }


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python intelligent_generator.py <command> [args]")
        print("Commands:")
        print("  level-design          - 生成关卡设计建议")
        print("  narrative             - 生成叙事设计建议")
        print("  generate <type> <content> [game_type] - 智能生成建议")
        sys.exit(1)
    
    command = sys.argv[1]
    generator = IntelligentGenerator()
    
    if command == 'level-design':
        result = generator.generate_level_design_suggestions()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'narrative':
        result = generator.generate_narrative_suggestions()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'generate':
        if len(sys.argv) < 4:
            print("Error: 需要提供设计类型和内容")
            sys.exit(1)
        
        design_type = sys.argv[2]
        design_content = sys.argv[3]
        game_type = sys.argv[4] if len(sys.argv) > 4 else None
        
        result = generator.generate_with_knowledge(design_type, design_content, game_type)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
