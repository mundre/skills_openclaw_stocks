#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - GDC 演讲精华与关卡设计知识库
基于 2024-2026 GDC/CGDC/IGDC 演讲精华
"""

from typing import Dict, Any, List


class GDCKnowledge:
    """GDC 演讲精华知识库"""
    
    def __init__(self):
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict[str, Any]:
        """加载 GDC 知识"""
        return {
            'gdc_2024_2025_highlights': self._gdc_highlights(),
            'level_design_principles': self._level_design(),
            'narrative_design': self._narrative_design(),
            'indie_success_patterns': self._indie_success(),
            'live_service_patterns': self._live_service()
        }
    
    def _gdc_highlights(self) -> Dict[str, Any]:
        """GDC 2024-2025 演讲精华"""
        return {
            'name': 'GDC 2024-2025 演讲精华',
            'key_sessions': [
                {
                    'game': '塞尔达传说：王国之泪',
                    'session': '王国之选：物理与声音的进化',
                    'key_insights': [
                        '将世界中以非物理形式运行的事物全部去除，让一切都遵循物理法则',
                        '不是创作有趣的内容，而是构建让有趣的事发生的机制',
                        '构建「海拉鲁世界内的发声规则」，保证任何地方都能实现自然音效',
                        '游戏设计师和美术创作者必须在充分了解目标的前提下通力合作'
                    ]
                },
                {
                    'game': '超级马力欧兄弟惊奇',
                    'session': '2D 与明天：在古典横版冒险中发掘新乐趣',
                    'key_insights': [
                        '2D 和 3D 马力欧都离不开「操作马力欧的动作游戏」核心',
                        '但两者玩法设计方式截然不同',
                        '在古典框架中寻找创新点'
                    ]
                },
                {
                    'topic': 'Demo 营销',
                    'session': 'Demo 如何重构 Steam 生态',
                    'speaker': 'Chris Zukowski',
                    'key_insights': [
                        'Demo 已不仅是试玩工具，而是撬动 Steam 算法的核心支点',
                        '《Parcel Simulator》Demo 发布后一周半愿望单从 7000→17000',
                        '《Minami Lane》《Nomad Idle》发布可玩版本后愿望单指数级增长',
                        '每个 Demo 已变成「流量核弹」'
                    ]
                },
                {
                    'topic': '独立游戏主机发行',
                    'speaker': '阿狗社产品总监 Leo',
                    'key_insights': [
                        'Steam 竞争加剧，PS/NS平台游戏数量少、流量扶持大',
                        '主机移植需提前完成本地化（中日英三语）、手柄支持、引擎升级',
                        '5 人团队平均 7-9 周即可完成移植',
                        '三点心得：读完文档/勇敢尝试/不懂就问'
                    ]
                },
                {
                    'topic': '游戏叙事设计',
                    'speaker': 'Charlene Putney (博德之门 3 叙事设计师)',
                    'key_insights': [
                        '「金种子」理论：内容要真实，能够牵动玩家情感',
                        '「五五开设计法」：设计有意义的选择，结合身体动作/内心挣扎/善恶观念/后果',
                        '使用 Twine 工具搭建分支，设置关键节点',
                        '相信自己，避免迎合大众，勇敢展现独特风格'
                    ]
                }
            ]
        }
    
    def _level_design(self) -> Dict[str, Any]:
        """关卡设计核心原则"""
        return {
            'name': '关卡设计核心原则与方法论',
            'five_core_principles': {
                'progression': {
                    'name': '渐进性 (Progression)',
                    'principles': [
                        '递进难度：难度逐步增加，玩家掌握技能后接受更高挑战',
                        '逐步引导：初期教学关卡为主，逐步引导玩家掌握规则'
                    ],
                    'examples': ['从简单敌人到复杂行为模式', '从单一机制到多机制组合']
                },
                'challenge_reward': {
                    'name': '挑战与回报 (Challenge and Reward)',
                    'principles': [
                        '挑战设置：过高导致沮丧，过低导致无聊',
                        '回报机制：不仅是物质奖励，还包括剧情/成长/成就等软性奖励'
                    ],
                    'examples': ['敌人/障碍/时间限制', '金币/装备/剧情推进/成就解锁']
                },
                'flow_pacing': {
                    'name': '流畅性与节奏 (Flow and Pacing)',
                    'principles': [
                        '游戏节奏把控：避免无聊或困惑',
                        '节奏变化：从探索→战斗→解谜→反思，增强趣味性'
                    ],
                    'examples': ['合理的敌人分布', '任务结构设计']
                },
                'replayability': {
                    'name': '可玩性和重玩性 (Replayability)',
                    'principles': [
                        '可玩性：多种通关方式，避免过于线性',
                        '重玩性：多结局/隐藏元素/支线任务/随机事件'
                    ],
                    'examples': ['多条路径', '隐藏要素', '随机事件']
                },
                'guidance_discovery': {
                    'name': '引导与自我发现 (Guidance and Discovery)',
                    'principles': [
                        '渐进式引导：通过环境/物体交互/元素揭示引导',
                        '隐性引导：颜色/光源/声音提示方向'
                    ],
                    'examples': ['特殊颜色提示', '光源引导', '声音提示']
                }
            },
            'ten_design_principles': {
                'name': '优秀关卡设计十大原则',
                'principles': [
                    '导航有趣：玩家始终知道该去哪里，使用连贯视觉语言',
                    '节奏控制：紧张→释放循环设计',
                    '目标分层：短期/中期/长期目标明确',
                    '空间结构：区域划分清晰，动线设计合理',
                    '规划 - 扰动模型：70% 预期验证 + 30% 预期颠覆',
                    '信息分层：视觉对比/听觉引导',
                    '心流设计：挑战与技能平衡',
                    '教学关设计：前三个房间教学核心机制',
                    '失败转化：将失败转化为持续动机',
                    '情感曲线：战斗 - 喘息 - 情感三段式节奏'
                ]
            },
            'level_planning_document': {
                'name': '关卡规划文档',
                'key_steps': [
                    '明确功能诉求：你想让谁做什么',
                    '定义目标群体：如「每日游戏时长 10-20 分钟的轻度活跃玩家」',
                    '设定转化目标：如「转化为每日 30-60 分钟的标准活跃玩家」',
                    '设计重点聚焦：避免方案拼凑感'
                ]
            }
        }
    
    def _narrative_design(self) -> Dict[str, Any]:
        """叙事设计"""
        return {
            'name': '游戏叙事设计',
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
            'tools': {
                'name': '叙事工具',
                'tools': [
                    'Twine - 搭建分支剧情',
                    '关键节点设置 - 确保故事丰富且连贯',
                    '晨间写作和呼吸练习 - 激发潜意识保持灵感'
                ]
            }
        }
    
    def _indie_success(self) -> Dict[str, Any]:
        """独立游戏成功模式"""
        return {
            'name': '独立游戏成功模式 2025-2026',
            'success_cases': [
                {
                    'game': '弓箭传说',
                    'studio': 'Habby',
                    'success_factors': [
                        '操作极其简单，只需手指滑动',
                        '每一局都做得足够有趣，体验拉满',
                        '被行业老兵称为「移动端史上的最爱」'
                    ]
                },
                {
                    'game': '卡皮巴拉 Go!',
                    'studio': 'Habby',
                    'achievement': '2025 年 App Store 年度游戏',
                    'success_factors': [
                        '简单易上手的操作',
                        '足够有趣的游戏体验',
                        '系列成功积累的经验'
                    ]
                },
                {
                    'game': '黑暗世界：因与果',
                    'studio': '上海月壤工作室',
                    'achievement': 'Steam 好评率 92%',
                    'success_factors': [
                        '风格独特，不易归类',
                        '第一人称心理恐怖',
                        '1984 年东德背景，潜入大脑搜寻证据'
                    ]
                },
                {
                    'game': '苏丹的游戏',
                    'studio': '成都双头龙工作室',
                    'success_factors': [
                        '140 万字剧情文本量',
                        '50 种解决方案',
                        '叙事驱动卡牌生存 RPG',
                        '权谋斗争复杂世界'
                    ]
                }
            ],
            'success_patterns': [
                '简单易上手的操作',
                '足够有趣的核心循环',
                '独特的艺术风格',
                '真实的情感共鸣',
                '持续的内容更新'
            ]
        }
    
    def _live_service(self) -> Dict[str, Any]:
        """长线运营游戏成功要素"""
        return {
            'name': '长线运营游戏成功要素',
            'success_cases': [
                {
                    'game': '原神',
                    'success_factors': [
                        '全球同步发行，统一运营节奏',
                        '持续高质量内容更新',
                        '文化输出典范',
                        '将中国神话推向全球'
                    ],
                    'achievements': [
                        '2025 年中国游戏出海代表',
                        '文化影响力巨大'
                    ]
                },
                {
                    'game': '黑神话：悟空',
                    'success_factors': [
                        '销量破 3000 万份',
                        '总收入约 100 亿',
                        'Steam 好评率 90%+',
                        '精准全球营销',
                        '中国文化国际传播'
                    ],
                    'achievements': [
                        '国产 3A 里程碑',
                        '国产单机黄金时代开启',
                        '带动 PS5 和装机热潮'
                    ],
                    'key_insights': [
                        '世界不是不接受中国故事，只是不接受「说不好」的中国故事',
                        '3000 万份销量不是终点，而是国产单机的起点',
                        '从单品爆款迈向可持续工业化'
                    ]
                }
            ],
            'china_game_advantages': [
                {
                    'name': '工业化能力',
                    'description': '高质量内容持续生产能力'
                },
                {
                    'name': '文化优势',
                    'description': '中国传统文化的国际传播力'
                },
                {
                    'name': '市场经验',
                    'description': '10 年+ 手游运营经验积累'
                }
            ],
            'live_service_key_metrics': [
                '日活/月活 (DAU/MAU)',
                '留存率 (1 日/7 日/30 日)',
                '付费率',
                'ARPU (每用户平均收入)',
                'LTV (用户生命周期价值)',
                '内容消耗速度',
                '社交活跃度'
            ]
        }
    
    def get_gdc_insights(self, topic: str) -> List[Dict[str, str]]:
        """
        获取 GDC 洞察
        
        Args:
            topic: 主题
        
        Returns:
            洞察列表
        """
        insights = []
        
        # 通用洞察
        insights.append({
            'category': 'GDC 精华',
            'insight': '不是创作有趣的内容，而是构建让有趣的事发生的机制',
            'source': '塞尔达传说：王国之泪',
            'importance': 'high'
        })
        
        insights.append({
            'category': 'Demo 营销',
            'insight': 'Demo 已变成「流量核弹」，能撬动 Steam 算法推荐',
            'source': 'GDC 2025 Chris Zukowski',
            'importance': 'high'
        })
        
        insights.append({
            'category': '叙事设计',
            'insight': '「金种子」理论：内容要真实，能够牵动玩家情感',
            'source': '博德之门 3 叙事设计师',
            'importance': 'medium'
        })
        
        return insights


def main():
    """命令行接口"""
    gdc = GDCKnowledge()
    
    print("=== GDC 演讲精华与关卡设计知识库 ===\n")
    print(f"共加载 {len(gdc.knowledge)} 个知识模块:\n")
    
    for key, value in gdc.knowledge.items():
        print(f"• {value.get('name', key)}")
    
    print("\n使用示例:")
    print("python gdc_knowledge.py highlights  - 查看 GDC 精华")
    print("python gdc_knowledge.py level       - 查看关卡设计")


if __name__ == '__main__':
    main()
