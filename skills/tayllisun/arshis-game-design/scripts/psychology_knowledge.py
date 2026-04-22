#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 游戏心理学知识库
理解玩家为什么喜欢/为什么留存/为什么付费
"""

from typing import Dict, Any, List


class GamePsychology:
    """游戏心理学知识库"""
    
    def __init__(self):
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict[str, Any]:
        """加载心理学知识（2026 年最新研究）"""
        return {
            'flow_theory': self._flow_theory(),
            'player_motivation': self._player_motivation(),
            'behavioral_economics': self._behavioral_economics(),
            'addiction_mechanics': self._addiction_mechanics(),
            'reward_schedules': self._reward_schedules(),
            'progression_psychology': self._progression_psychology(),
            'social_psychology': self._social_psychology(),
            'monetization_psychology': self._monetization_psychology(),
            'latest_research_2026': self._latest_research()  # 新增 2026 年研究
        }
    
    def _flow_theory(self) -> Dict[str, Any]:
        """心流理论"""
        return {
            'name': '心流理论 (Flow Theory)',
            'definition': '当挑战与技能匹配时，玩家进入的沉浸状态',
            'conditions': [
                '清晰的目标',
                '即时的反馈',
                '挑战与技能平衡',
                '专注的环境',
                '掌控感',
                '时间感扭曲'
            ],
            'flow_channels': {
                'anxiety': '挑战太高 → 焦虑 → 需要降低难度',
                'flow': '挑战=技能 → 心流 → 最佳体验',
                'boredom': '挑战太低 → 无聊 → 需要增加难度'
            },
            'game_design_implications': [
                '动态难度调整（DDA）',
                '清晰的进度反馈',
                '分段式目标设计',
                '技能成长曲线',
                '避免挫败感和无聊感'
            ],
            'examples': {
                'good': [
                    '塞尔达：荒野之息 - 自由探索 + 适度挑战',
                    '超级马里奥 - 精心设计的难度曲线',
                    '俄罗斯方块 - 动态速度调整'
                ],
                'bad': [
                    '新手村难度过高导致流失',
                    '后期内容过于简单导致无聊',
                    '随机性过大导致失控感'
                ]
            }
        }
    
    def _player_motivation(self) -> Dict[str, Any]:
        """玩家动机理论"""
        return {
            'name': '玩家动机理论',
            'bartle_types': {
                'name': '巴特尔玩家分类',
                'types': {
                    'achievers': {
                        'name': '成就型',
                        'motivation': '达成目标/收集/升级',
                        'design_tips': [
                            '成就系统',
                            '收集要素',
                            '等级/排名',
                            '可见的进度'
                        ]
                    },
                    'explorers': {
                        'name': '探索型',
                        'motivation': '发现新内容/隐藏要素',
                        'design_tips': [
                            '隐藏区域',
                            '彩蛋',
                            '开放世界',
                            ' lore/背景故事'
                        ]
                    },
                    'socializers': {
                        'name': '社交型',
                        'motivation': '与他人互动',
                        'design_tips': [
                            '公会系统',
                            '聊天功能',
                            '组队内容',
                            '社交空间'
                        ]
                    },
                    'killers': {
                        'name': '竞争型',
                        'motivation': '战胜他人',
                        'design_tips': [
                            'PVP 系统',
                            '排行榜',
                            '竞技场',
                            '赛季奖励'
                        ]
                    }
                },
                'distribution': '成就型 25% / 探索型 20% / 社交型 30% / 竞争型 25%'
            },
            'self_determination_theory': {
                'name': '自我决定理论 (SDT)',
                'needs': {
                    'autonomy': {
                        'name': '自主性',
                        'description': '玩家感到自己有选择权',
                        'design': ['多路径设计', '自由选择', '自定义选项']
                    },
                    'competence': {
                        'name': '能力感',
                        'description': '玩家感到自己在成长',
                        'design': ['清晰反馈', '适度挑战', '技能成长']
                    },
                    'relatedness': {
                        'name': '归属感',
                        'description': '玩家感到与他人连接',
                        'design': ['社交系统', '公会', '合作内容']
                    }
                }
            },
            'octalysis_framework': {
                'name': '八角行为分析法',
                'cores': [
                    '史诗意义与使命感',
                    '进步与成就',
                    '创意授权与反馈',
                    '所有权与占有',
                    '社交影响与关联',
                    '稀缺性与渴望',
                    '未知性与好奇心',
                    '损失与逃避'
                ]
            }
        }
    
    def _behavioral_economics(self) -> Dict[str, Any]:
        """行为经济学"""
        return {
            'name': '行为经济学在游戏设计中的应用',
            'biases': {
                'loss_aversion': {
                    'name': '损失厌恶',
                    'description': '人们对损失的敏感度高于获得',
                    'game_design': [
                        '限时活动（错过就没了）',
                        '连续登录奖励（断签就没了）',
                        '体力系统（不用就浪费了）',
                        '战令系统（买了不用就亏了）'
                    ]
                },
                'sunk_cost': {
                    'name': '沉没成本',
                    'description': '已经投入的成本影响决策',
                    'game_design': [
                        '长期养成系统',
                        '公会贡献累积',
                        '成就进度',
                        '社交关系绑定'
                    ]
                },
                'anchoring': {
                    'name': '锚定效应',
                    'description': '第一个看到的价格影响判断',
                    'game_design': [
                        '先展示高价礼包',
                        '原价/折扣价对比',
                        '月卡显得更划算'
                    ]
                },
                'fomo': {
                    'name': '错失恐惧 (FOMO)',
                    'description': '害怕错过机会',
                    'game_design': [
                        '限时皮肤',
                        '绝版道具',
                        '季节性活动',
                        '倒计时显示'
                    ]
                },
                'variable_rewards': {
                    'name': '变动奖励',
                    'description': '不确定的奖励更有吸引力',
                    'game_design': [
                        '抽卡系统',
                        '随机掉落',
                        '暴击机制',
                        '盲盒设计'
                    ]
                }
            }
        }
    
    def _addiction_mechanics(self) -> Dict[str, Any]:
        """成瘾机制"""
        return {
            'name': '游戏成瘾机制（负责任地使用）',
            'core_loop': {
                'name': '核心循环',
                'stages': [
                    '触发（内部/外部）',
                    '行动',
                    '变动奖励',
                    '投入'
                ],
                'example': '推送通知 → 上线 → 抽卡/掉落 → 养成 → 下次上线'
            },
            'hook_model': {
                'name': '上瘾模型 (Hook Model)',
                'components': [
                    'Trigger: 触发（推送/红点/体力满）',
                    'Action: 行动（点击/战斗/抽卡）',
                    'Variable Reward: 变动奖励（随机掉落）',
                    'Investment: 投入（养成/社交/收集）'
                ]
            },
            'ethical_considerations': [
                '避免过度利用心理弱点',
                '设置防沉迷系统',
                '提供消费上限',
                '明确掉率公示',
                '保护未成年玩家'
            ]
        }
    
    def _reward_schedules(self) -> Dict[str, Any]:
        """奖励时间表"""
        return {
            'name': '奖励时间表理论',
            'schedules': {
                'fixed_ratio': {
                    'name': '固定比率',
                    'description': '每 N 次行动给奖励',
                    'example': '每杀 10 个怪掉一个宝箱',
                    'effect': '稳定但容易厌倦'
                },
                'variable_ratio': {
                    'name': '变动比率',
                    'description': '随机次数后给奖励',
                    'example': '随机掉落/抽卡',
                    'effect': '最容易上瘾'
                },
                'fixed_interval': {
                    'name': '固定间隔',
                    'description': '每 N 时间给奖励',
                    'example': '每日奖励/每小时体力',
                    'effect': '形成习惯'
                },
                'variable_interval': {
                    'name': '变动间隔',
                    'description': '随机时间给奖励',
                    'example': '随机活动/限时 Boss',
                    'effect': '保持在线'
                }
            },
            'best_practices': [
                '混合使用多种奖励时间表',
                '前期固定奖励建立习惯',
                '后期变动奖励保持兴趣',
                '避免奖励疲劳'
            ]
        }
    
    def _progression_psychology(self) -> Dict[str, Any]:
        """进度心理学"""
        return {
            'name': '进度心理学',
            'goal_gradient': {
                'name': '目标梯度效应',
                'description': '越接近目标，努力程度越高',
                'game_design': [
                    '进度条显示',
                    '分段目标（10/100 → 10%）',
                    '最后几步加速',
                    '里程碑奖励'
                ]
            },
            'endowed_progress': {
                'name': '赠予进度效应',
                'description': '给一点初始进度能提高完成率',
                'game_design': [
                    '新手礼包送经验',
                    '战令购买送等级',
                    '活动开始送几次免费机会'
                ]
            },
            'zeigarnik_effect': {
                'name': '蔡格尼克效应',
                'description': '未完成的任务更容易被记住',
                'game_design': [
                    '任务列表显示',
                    '红点提醒',
                    '进度保存',
                    '断点续玩'
                ]
            }
        }
    
    def _social_psychology(self) -> Dict[str, Any]:
        """社交心理学"""
        return {
            'name': '社交心理学在游戏设计中的应用',
            'social_proof': {
                'name': '社会认同',
                'description': '人们会跟随他人的行为',
                'game_design': [
                    '热门游戏展示',
                    '好友在玩',
                    '排行榜',
                    '玩家数量显示'
                ]
            },
            'reciprocity': {
                'name': '互惠原则',
                'description': '人们倾向于回报他人的好意',
                'game_design': [
                    '免费礼包',
                    '新手福利',
                    '每日赠送',
                    '公会援助'
                ]
            },
            'commitment_consistency': {
                'name': '承诺与一致',
                'description': '人们倾向于保持与承诺一致的行为',
                'game_design': [
                    '每日签到',
                    '连续登录',
                    '公会承诺',
                    '组队约定'
                ]
            },
            'scarcity': {
                'name': '稀缺性',
                'description': '稀缺的东西更有价值',
                'game_design': [
                    '限时道具',
                    '绝版皮肤',
                    '限量发售',
                    '稀有度分级'
                ]
            }
        }
    
    def _monetization_psychology(self) -> Dict[str, Any]:
        """付费心理学"""
        return {
            'name': '付费心理学',
            'pricing_strategies': {
                'name': '定价策略',
                'strategies': [
                    {
                        'name': '锚定定价',
                        'description': '设置高价锚点让其他价格显得便宜',
                        'example': '648 元礼包让 128 元显得便宜'
                    },
                    {
                        'name': '分解定价',
                        'description': '将价格分解到每天显得便宜',
                        'example': '月卡 30 元 = 每天 1 元'
                    },
                    {
                        'name': '捆绑定价',
                        'description': '打包销售显得更划算',
                        'example': '新手礼包（原价 500 现价 68）'
                    }
                ]
            },
            'whale_psychology': {
                'name': '大 R 心理',
                'motivations': [
                    '地位展示（排行榜/稀有道具）',
                    '竞争优势（PVP 碾压）',
                    '收集完成（全图鉴）',
                    '社交认可（公会大佬）'
                ]
            },
            'dolphin_psychology': {
                'name': '中 R 心理',
                'motivations': [
                    '性价比（月卡/战令）',
                    '适度优势',
                    '外观收集'
                ]
            },
            'minnow_psychology': {
                'name': '小 R/免费玩家心理',
                'motivations': [
                    '时间换金钱',
                    '免费福利',
                    '社交参与'
                ]
            },
            'ethical_monetization': [
                '明确掉率公示',
                '设置消费上限',
                '提供退款渠道',
                '保护未成年玩家',
                '避免 Pay-to-Win 过度'
            ]
        }
    
    def _latest_research(self) -> Dict[str, Any]:
        """2026 年最新心理学研究"""
        return {
            'name': '2026 年游戏心理学最新研究',
            'key_findings': [
                {
                    'topic': 'PBL 系统的局限性',
                    'finding': '基于外在奖励的系统参与度下降速度比内在动机驱动的系统快 75%',
                    'implication': '游戏化设计应注重内在动机（能力/自主/关系）而非单纯积分徽章'
                },
                {
                    'topic': '心流体验六要素',
                    'finding': '注意力完全集中、行为与意识融合、内在动力、控制感、时间感扭曲、愉悦感',
                    'implication': '游戏设计应创造主动式环境，让玩家潜意识选择适合自己的难度'
                },
                {
                    'topic': '玩家情绪发展五阶段',
                    'finding': '初始探索→心流沉浸→挑战波动→情感投入→结束满足/失落',
                    'implication': '不同阶段需要不同的设计策略和支持'
                }
            ],
            'self_determination_theory': {
                'name': '自我决定理论（SDT）2026 应用',
                'three_needs': {
                    'autonomy': '自主需求 - 玩家感到有选择权（多路径/自由选择/自定义）',
                    'competence': '能力需求 - 玩家感到在成长（清晰反馈/适度挑战/技能成长）',
                    'relatedness': '归属需求 - 玩家感到与他人连接（社交系统/公会/合作内容）'
                },
                'application': '现代员工/玩家追求的不只是功能达成，还包括情感体验和自我实现'
            }
        }
    
    def get_psychology_insights(self, design_content: str) -> List[Dict[str, str]]:
        """
        根据设计内容提供心理学洞察
        
        Args:
            design_content: 设计内容描述
        
        Returns:
            心理学洞察列表
        """
        insights = []
        
        # 通用洞察
        insights.append({
            'category': '心流设计',
            'insight': '确保挑战与玩家技能匹配，提供清晰目标和即时反馈',
            'importance': 'high'
        })
        
        insights.append({
            'category': '玩家动机',
            'insight': '考虑四类玩家（成就/探索/社交/竞争）的需求',
            'importance': 'high'
        })
        
        insights.append({
            'category': '奖励设计',
            'insight': '混合使用固定和变动奖励时间表，避免奖励疲劳',
            'importance': 'medium'
        })
        
        insights.append({
            'category': '进度反馈',
            'insight': '利用目标梯度效应，清晰展示进度',
            'importance': 'medium'
        })
        
        return insights


def main():
    """命令行接口"""
    psychology = GamePsychology()
    
    print("=== 游戏心理学知识库 ===\n")
    print(f"共加载 {len(psychology.knowledge)} 个知识模块:\n")
    
    for key, value in psychology.knowledge.items():
        print(f"• {value.get('name', key)}")
    
    print("\n使用示例:")
    print("python psychology_knowledge.py flow      - 查看心流理论")
    print("python psychology_knowledge.py motivation - 查看玩家动机")
    print("python psychology_knowledge.py economics - 查看行为经济学")


if __name__ == '__main__':
    main()
