#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 游戏社会学知识库
理解社交设计/社区动力学/网络效应
"""

from typing import Dict, Any, List


class GameSociology:
    """游戏社会学知识库"""
    
    def __init__(self):
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict[str, Any]:
        """加载社会学知识"""
        return {
            'social_design': self._social_design(),
            'community_dynamics': self._community_dynamics(),
            'network_effects': self._network_effects(),
            'guild_design': self._guild_design(),
            'viral_mechanics': self._viral_mechanics(),
            'player_ecosystem': self._player_ecosystem()
        }
    
    def _social_design(self) -> Dict[str, Any]:
        """社交设计"""
        return {
            'name': '游戏社交设计',
            'social_layers': {
                'name': '社交层次',
                'layers': [
                    {
                        'name': '浅层社交',
                        'description': '低门槛互动',
                        'examples': ['点赞', '送心', '访问好友', '排行榜']
                    },
                    {
                        'name': '中层社交',
                        'description': '需要一定投入的互动',
                        'examples': ['组队', '交易', '聊天', '公会']
                    },
                    {
                        'name': '深层社交',
                        'description': '强关系绑定',
                        'examples': ['师徒', '情缘', '固定队', '核心公会']
                    }
                ]
            },
            'social_hooks': {
                'name': '社交钩子',
                'hooks': [
                    '互惠（送体力/援助）',
                    '竞争（排行榜/PVP）',
                    '合作（组队/公会战）',
                    '展示（外观/成就）',
                    '归属（公会/阵营）'
                ]
            },
            'retention_impact': {
                'name': '对留存的影响',
                'data': [
                    '有好友的玩家留存 +30%',
                    '加入公会的玩家留存 +50%',
                    '有固定队的玩家留存 +80%',
                    '社交关系>3 个的玩家流失率<10%'
                ]
            }
        }
    
    def _community_dynamics(self) -> Dict[str, Any]:
        """社区动力学"""
        return {
            'name': '游戏社区动力学',
            'community_lifecycle': {
                'name': '社区生命周期',
                'stages': [
                    {
                        'name': '形成期',
                        'characteristics': '核心玩家聚集，规则建立',
                        'design_tips': '提供讨论空间，官方积极参与'
                    },
                    {
                        'name': '成长期',
                        'characteristics': '玩家快速增长，内容爆发',
                        'design_tips': 'UGC 激励，KOL 培养'
                    },
                    {
                        'name': '成熟期',
                        'characteristics': '稳定活跃，文化形成',
                        'design_tips': '维持活跃度，防止固化'
                    },
                    {
                        'name': '衰退期',
                        'characteristics': '活跃度下降，核心玩家流失',
                        'design_tips': '新版本/活动刺激，回流活动'
                    }
                ]
            },
            'player_roles': {
                'name': '玩家角色分类',
                'roles': [
                    {
                        'name': 'KOL/意见领袖',
                        'percentage': '1-3%',
                        'influence': '影响舆论，带动节奏',
                        'design': '官方合作，提前体验'
                    },
                    {
                        'name': '活跃玩家',
                        'percentage': '10-15%',
                        'influence': '社区中坚力量',
                        'design': '激励创作，提供展示'
                    },
                    {
                        'name': '普通玩家',
                        'percentage': '60-70%',
                        'influence': '沉默大多数',
                        'design': '降低参与门槛'
                    },
                    {
                        'name': '边缘玩家',
                        'percentage': '15-20%',
                        'influence': '潜在流失',
                        'design': '回流激励'
                    }
                ]
            },
            'toxic_behavior': {
                'name': '毒性行为管理',
                'types': [
                    '言语辱骂',
                    '故意送人头',
                    '诈骗/盗号',
                    '外挂/作弊',
                    '恶意举报'
                ],
                'prevention': [
                    '举报系统',
                    '信用系统',
                    '禁言/封禁',
                    '正向激励'
                ]
            }
        }
    
    def _network_effects(self) -> Dict[str, Any]:
        """网络效应"""
        return {
            'name': '游戏网络效应',
            'direct_network_effects': {
                'name': '直接网络效应',
                'description': '用户越多，产品价值越高',
                'examples': [
                    'MOBA - 匹配更快，对局质量更高',
                    'MMO - 世界更热闹，交易更活跃',
                    '社交游戏 - 好友越多越好玩'
                ]
            },
            'indirect_network_effects': {
                'name': '间接网络效应',
                'description': '用户越多，衍生内容越多',
                'examples': [
                    '攻略内容增多',
                    '同人创作增多',
                    '交易物品增多',
                    '社交机会增多'
                ]
            },
            'critical_mass': {
                'name': '临界质量',
                'description': '达到自持增长的用户数',
                'factors': [
                    '品类（MOBA 需要更多用户）',
                    '目标用户（硬核 vs 休闲）',
                    '地区（一线 vs 下沉）'
                ],
                'typical_values': {
                    'MOBA': '日活 100 万+',
                    'MMO': '单服 1 万+',
                    '卡牌': '日活 10 万+',
                    '独立游戏': '日活 1 万+'
                }
            },
            'churn_prevention': {
                'name': '防止流失螺旋',
                'description': '玩家流失导致体验下降，加速更多流失',
                'prevention': [
                    '机器人填充（保持匹配速度）',
                    '跨服匹配（扩大用户池）',
                    '回流激励（老玩家回归）',
                    '新手保护（新玩家体验）'
                ]
            }
        }
    
    def _guild_design(self) -> Dict[str, Any]:
        """公会设计"""
        return {
            'name': '公会/联盟设计',
            'guild_functions': {
                'name': '公会功能',
                'functions': [
                    '社交空间（聊天/活动）',
                    '互助系统（捐赠/援助）',
                    '集体目标（公会任务）',
                    '竞争内容（公会战）',
                    '资源共享（仓库/科技）'
                ]
            },
            'guild_progression': {
                'name': '公会成长',
                'stages': [
                    '创建（会长权力）',
                    '招募（成员增长）',
                    '升级（解锁功能）',
                    '扩张（更多成员）',
                    '争霸（公会排名）'
                ]
            },
            'guild_retention': {
                'name': '公会留存效应',
                'data': [
                    '加入公会的玩家留存 +50%',
                    '公会有好友的玩家留存 +70%',
                    '公会活跃的玩家留存 +90%',
                    '公会干部的玩家留存 +95%'
                ]
            },
            'guild_challenges': {
                'name': '公会设计挑战',
                'challenges': [
                    '小公会难以存活',
                    '大公会垄断资源',
                    '会长弃坑导致公会解散',
                    '成员活跃度不均'
                ],
                'solutions': [
                    '公会匹配/合并',
                    '分级奖励',
                    '副会长继承',
                    '活跃度考核'
                ]
            }
        }
    
    def _viral_mechanics(self) -> Dict[str, Any]:
        """病毒传播"""
        return {
            'name': '病毒传播机制',
            'viral_loops': {
                'name': '病毒循环',
                'loops': [
                    {
                        'name': '邀请循环',
                        'flow': '玩家 → 邀请好友 → 好友加入 → 获得奖励 → 继续邀请',
                        'examples': ['滴滴红包', '拼多多砍价', '游戏邀请码']
                    },
                    {
                        'name': '展示循环',
                        'flow': '玩家 → 分享成就 → 好友看到 → 产生兴趣 → 加入游戏',
                        'examples': ['王者荣耀分享', '原神抽卡分享']
                    },
                    {
                        'name': '合作循环',
                        'flow': '玩家 → 需要帮助 → 邀请好友 → 好友体验 → 加入游戏',
                        'examples': ['体力援助', '组队副本', '公会邀请']
                    }
                ]
            },
            'viral_coefficient': {
                'name': '病毒系数 (K 值)',
                'formula': 'K = 邀请数 × 转化率',
                'benchmark': {
                    'K > 1': '病毒增长',
                    'K = 1': '稳定增长',
                    'K < 1': '需要买量'
                },
                'typical_values': {
                    '优秀': 'K > 0.5',
                    '良好': 'K > 0.3',
                    '一般': 'K > 0.1'
                }
            },
            'sharing_triggers': {
                'name': '分享触发点',
                'triggers': [
                    '稀有掉落（我抽到了！）',
                    '高难度成就（我通关了！）',
                    '搞笑时刻（这操作太秀了）',
                    '社交炫耀（看我新皮肤）',
                    '求助（来个人帮我）'
                ]
            }
        }
    
    def _player_ecosystem(self) -> Dict[str, Any]:
        """玩家生态系统"""
        return {
            'name': '玩家生态系统设计',
            'ecosystem_roles': {
                'name': '生态角色',
                'roles': [
                    {
                        'name': '内容生产者',
                        'percentage': '5%',
                        'value': '创造攻略/视频/同人',
                        'design': '创作激励，展示平台'
                    },
                    {
                        'name': '内容消费者',
                        'percentage': '70%',
                        'value': '消费内容，提供活跃',
                        'design': '推荐系统，降低门槛'
                    },
                    {
                        'name': '社交节点',
                        'percentage': '10%',
                        'value': '连接其他玩家',
                        'design': '公会/组队激励'
                    },
                    {
                        'name': '经济参与者',
                        'percentage': '15%',
                        'value': '参与交易/市场',
                        'design': '交易系统，价格稳定'
                    }
                ]
            },
            'ecosystem_health': {
                'name': '生态健康指标',
                'metrics': [
                    '内容生产/消费比',
                    '社交网络密度',
                    '经济流动性',
                    '新老玩家比例',
                    '付费/免费玩家比例'
                ]
            },
            'ecosystem_risks': {
                'name': '生态风险',
                'risks': [
                    '内容生产者流失 → 内容枯竭',
                    '社交节点流失 → 关系断裂',
                    '经济失衡 → 通胀/通缩',
                    '新老玩家断层 → 社区老化'
                ]
            }
        }
    
    def get_social_insights(self, design_content: str) -> List[Dict[str, str]]:
        """
        根据设计内容提供社会学洞察
        
        Args:
            design_content: 设计内容描述
        
        Returns:
            社会学洞察列表
        """
        insights = []
        
        insights.append({
            'category': '社交设计',
            'insight': '设计浅层/中层/深层社交层次，让玩家逐步建立关系',
            'importance': 'high'
        })
        
        insights.append({
            'category': '社区建设',
            'insight': '培养 KOL 和活跃玩家，他们是社区的中坚力量',
            'importance': 'high'
        })
        
        insights.append({
            'category': '网络效应',
            'insight': '尽快达到临界质量，避免流失螺旋',
            'importance': 'medium'
        })
        
        insights.append({
            'category': '病毒传播',
            'insight': '设计分享触发点，提高 K 值',
            'importance': 'medium'
        })
        
        return insights


def main():
    """命令行接口"""
    sociology = GameSociology()
    
    print("=== 游戏社会学知识库 ===\n")
    print(f"共加载 {len(sociology.knowledge)} 个知识模块:\n")
    
    for key, value in sociology.knowledge.items():
        print(f"• {value.get('name', key)}")


if __name__ == '__main__':
    main()
