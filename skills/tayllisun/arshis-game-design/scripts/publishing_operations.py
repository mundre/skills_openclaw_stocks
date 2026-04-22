#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publishing_operations.py - 游戏发行运营策略模块

基于行业研究的完整发行运营方案
包含：上线节奏/买量策略/ROI 优化/留存提升/活动策划

数据来源：
- Sensor Tower 2026 游戏报告
- 2026 游戏行业"主动权"之战
- 2025 游戏市场 2562 亿报告
"""

import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class PublishingOperations:
    """游戏发行运营策略生成器"""
    
    # 上线节奏模板
    LAUNCH_PHASES = {
        "pre_launch": {
            "duration": "上线前 30-60 天",
            "goals": ["预约用户积累", "品牌曝光", "社区建设"],
            "kpis": {
                "pre_registration": "50-100 万预约",
                "social_followers": "10-30 万粉丝",
                "community_members": "5-10 万核心用户"
            }
        },
        "soft_launch": {
            "duration": "上线前 7-14 天",
            "goals": ["技术测试", "小范围验证", "口碑发酵"],
            "kpis": {
                "d1_retention": ">40%",
                "d7_retention": ">20%",
                "arpu": ">5 元"
            }
        },
        "hard_launch": {
            "duration": "上线后 0-7 天",
            "goals": ["冲榜", "最大化曝光", "用户爆发"],
            "kpis": {
                "daily_downloads": "10-50 万/天",
                "app_store_ranking": "免费榜前 10",
                "revenue": "首日 100-500 万"
            }
        },
        "growth": {
            "duration": "上线后 8-30 天",
            "goals": ["持续增长", "优化 ROI", "稳定留存"],
            "kpis": {
                "daily_downloads": "5-20 万/天",
                "roi": ">1.2",
                "d30_retention": ">10%"
            }
        },
        "maturity": {
            "duration": "上线后 31-180 天",
            "goals": ["稳定运营", "提升 LTV", "控制成本"],
            "kpis": {
                "daily_active_users": "稳定在峰值 60-80%",
                "arpu": "稳定增长",
                "churn_rate": "<5%/月"
            }
        }
    }
    
    # 买量渠道基准数据
    UA_CHANNELS = {
        "douyin": {
            "name": "抖音",
            "cpi_range": {"casual": "8-15 元", "midcore": "15-30 元", "hardcore": "30-60 元"},
            "roi_benchmark": {"d7": "0.8-1.2", "d30": "1.5-2.5"},
            "volume": "高",
            "best_for": ["休闲", "中度", "二次元"]
        },
        "tencent_ads": {
            "name": "腾讯广告 (微信/QQ)",
            "cpi_range": {"casual": "10-20 元", "midcore": "20-40 元", "hardcore": "40-80 元"},
            "roi_benchmark": {"d7": "0.9-1.3", "d30": "1.6-2.8"},
            "volume": "高",
            "best_for": ["SLG", "MMO", "棋牌"]
        },
        "xiaohongshu": {
            "name": "小红书",
            "cpi_range": {"casual": "12-25 元", "midcore": "25-50 元", "hardcore": "50-100 元"},
            "roi_benchmark": {"d7": "1.0-1.5", "d30": "2.0-3.5"},
            "volume": "中",
            "best_for": ["女性向", "二次元", "休闲"]
        },
        "bilibili": {
            "name": "B 站",
            "cpi_range": {"casual": "15-30 元", "midcore": "30-60 元", "hardcore": "60-120 元"},
            "roi_benchmark": {"d7": "1.0-1.6", "d30": "2.0-4.0"},
            "volume": "中",
            "best_for": ["二次元", "独立游戏", "硬核"]
        },
        "google_ads": {
            "name": "Google Ads (海外)",
            "cpi_range": {"casual": "$1-3", "midcore": "$3-8", "hardcore": "$8-20"},
            "roi_benchmark": {"d7": "0.7-1.2", "d30": "1.5-3.0"},
            "volume": "高",
            "best_for": ["全球发行", "休闲", "SLG"]
        },
        "facebook": {
            "name": "Facebook/Instagram (海外)",
            "cpi_range": {"casual": "$1-4", "midcore": "$4-10", "hardcore": "$10-25"},
            "roi_benchmark": {"d7": "0.8-1.3", "d30": "1.6-3.2"},
            "volume": "高",
            "best_for": ["欧美市场", "休闲", "社交"]
        }
    }
    
    # 留存提升策略
    RETENTION_STRATEGIES = {
        "d1_retention": [
            {"strategy": "新手引导优化", "impact": "+5-10%", "effort": "中"},
            {"strategy": "首充奖励", "impact": "+3-5%", "effort": "低"},
            {"strategy": "7 日签到", "impact": "+8-12%", "effort": "低"},
            {"strategy": "流失召回弹窗", "impact": "+2-4%", "effort": "低"}
        ],
        "d7_retention": [
            {"strategy": "成长目标系统", "impact": "+5-8%", "effort": "中"},
            {"strategy": "社交系统解锁", "impact": "+4-6%", "effort": "中"},
            {"strategy": "第一周活动", "impact": "+6-10%", "effort": "中"},
            {"strategy": "难度曲线调整", "impact": "+3-5%", "effort": "高"}
        ],
        "d30_retention": [
            {"strategy": "公会/社群系统", "impact": "+5-10%", "effort": "高"},
            {"strategy": "月度活动目标", "impact": "+4-7%", "effort": "中"},
            {"strategy": "PVP/排行榜", "impact": "+3-6%", "effort": "中"},
            {"strategy": "内容更新", "impact": "+5-8%", "effort": "高"}
        ]
    }
    
    def __init__(self):
        self.ops_data = {}
    
    def generate_launch_plan(self, game_type: str, budget: str = "中等") -> Dict:
        """
        生成完整上线计划
        
        Args:
            game_type: 游戏类型
            budget: 预算规模 (小/中等/大)
        
        Returns:
            完整上线计划
        """
        budget_config = {
            "小": {"multiplier": 0.5, "channels": 2, "timeline": "紧凑"},
            "中等": {"multiplier": 1.0, "channels": 4, "timeline": "标准"},
            "大": {"multiplier": 2.0, "channels": 6, "timeline": "充分"}
        }
        
        config = budget_config.get(budget, budget_config["中等"])
        
        launch_plan = {
            "game_type": game_type,
            "budget_level": budget,
            "phases": {},
            "channel_mix": [],
            "kpis": {},
            "risk_mitigation": []
        }
        
        # 各阶段计划
        for phase_name, phase_info in self.LAUNCH_PHASES.items():
            launch_plan["phases"][phase_name] = {
                "duration": phase_info["duration"],
                "goals": phase_info["goals"],
                "kpis": phase_info["kpis"],
                "budget_allocation": self._calculate_phase_budget(phase_name, config["multiplier"]),
                "key_activities": self._get_phase_activities(phase_name, game_type)
            }
        
        # 渠道组合
        launch_plan["channel_mix"] = self._suggest_channel_mix(game_type, config["channels"])
        
        # 整体 KPI
        launch_plan["kpis"] = self._calculate_overall_kpis(game_type, config["multiplier"])
        
        # 风险缓解
        launch_plan["risk_mitigation"] = self._identify_risks(game_type)
        
        return launch_plan
    
    def _calculate_phase_budget(self, phase: str, multiplier: float) -> Dict:
        """计算各阶段预算分配"""
        budget_map = {
            "pre_launch": {"percentage": "15%", "focus": "品牌曝光"},
            "soft_launch": {"percentage": "10%", "focus": "技术验证"},
            "hard_launch": {"percentage": "40%", "focus": "冲榜爆发"},
            "growth": {"percentage": "25%", "focus": "持续增长"},
            "maturity": {"percentage": "10%", "focus": "稳定运营"}
        }
        
        info = budget_map.get(phase, {})
        return {
            "allocation": info.get("percentage", "N/A"),
            "focus": info.get("focus", "N/A"),
            "adjusted": f"基准 x{multiplier}"
        }
    
    def _get_phase_activities(self, phase: str, game_type: str) -> List[str]:
        """获取各阶段关键活动"""
        activities_map = {
            "pre_launch": [
                "预约活动开启",
                "KOL/主播合作",
                "社交媒体运营",
                "社区建设 (Discord/QQ 群)",
                "预热视频发布"
            ],
            "soft_launch": [
                "小范围测试",
                "收集用户反馈",
                "优化新手引导",
                "调整付费点",
                "口碑发酵"
            ],
            "hard_launch": [
                "全渠道买量",
                "冲榜活动",
                "媒体 PR",
                "上线庆典活动",
                "首充/首发活动"
            ],
            "growth": [
                "持续买量优化",
                "A/B 测试",
                "留存活动",
                "内容更新",
                "社区运营"
            ],
            "maturity": [
                "稳定运营",
                "LTV 提升",
                "老用户召回",
                "版本更新",
                "成本控制"
            ]
        }
        return activities_map.get(phase, [])
    
    def _suggest_channel_mix(self, game_type: str, channel_count: int) -> List[Dict]:
        """建议渠道组合"""
        # 根据游戏类型排序渠道
        channel_priority = {
            "rpg": ["tencent_ads", "bilibili", "douyin", "google_ads"],
            "moba": ["douyin", "bilibili", "tencent_ads", "facebook"],
            "fps": ["douyin", "bilibili", "google_ads", "facebook"],
            "slg": ["tencent_ads", "google_ads", "facebook", "douyin"],
            "casual": ["douyin", "google_ads", "facebook", "xiaohongshu"],
            "otome": ["xiaohongshu", "bilibili", "douyin", "tencent_ads"]
        }
        
        priority = channel_priority.get(game_type, ["douyin", "tencent_ads", "bilibili", "google_ads"])
        
        channel_mix = []
        for channel_key in priority[:channel_count]:
            channel_info = self.UA_CHANNELS[channel_key]
            channel_mix.append({
                "channel": channel_info["name"],
                "key": channel_key,
                "cpi_range": channel_info["cpi_range"]["midcore"],
                "roi_benchmark": channel_info["roi_benchmark"],
                "volume": channel_info["volume"],
                "best_for": channel_info["best_for"],
                "budget_allocation": f"{max(10, 30 // channel_count)}-{min(40, 35 // channel_count + 10)}%"
            })
        
        return channel_mix
    
    def _calculate_overall_kpis(self, game_type: str, multiplier: float) -> Dict:
        """计算整体 KPI"""
        kpi_map = {
            "rpg": {"d1": "45%", "d7": "25%", "d30": "12%", "arpu": "80-150 元"},
            "moba": {"d1": "50%", "d7": "30%", "d30": "15%", "arpu": "50-100 元"},
            "fps": {"d1": "45%", "d7": "25%", "d30": "12%", "arpu": "40-80 元"},
            "slg": {"d1": "40%", "d7": "20%", "d30": "10%", "arpu": "150-300 元"},
            "casual": {"d1": "55%", "d7": "35%", "d30": "18%", "arpu": "10-30 元"},
            "otome": {"d1": "50%", "d7": "30%", "d30": "15%", "arpu": "100-200 元"}
        }
        
        base_kpis = kpi_map.get(game_type, kpi_map["rpg"])
        
        return {
            "d1_retention": base_kpis["d1"],
            "d7_retention": base_kpis["d7"],
            "d30_retention": base_kpis["d30"],
            "arpu_range": base_kpis["arpu"],
            "ltv_30": f"{float(base_kpis['arpu'].split('-')[0]) * 3:.0f}-{float(base_kpis['arpu'].split('-')[1].split('元')[0]) * 5:.0f}元",
            "paying_rate": "3-8%",
            "roi_target": "d7: 1.0+, d30: 2.0+"
        }
    
    def _identify_risks(self, game_type: str) -> List[Dict]:
        """识别风险并给出缓解方案"""
        risks = [
            {
                "risk": "买量成本过高",
                "probability": "中",
                "impact": "高",
                "mitigation": "多渠道测试，优化素材，提升自然量占比"
            },
            {
                "risk": "留存不达标",
                "probability": "中",
                "impact": "高",
                "mitigation": "软 launch 验证，快速迭代新手引导和前期体验"
            },
            {
                "risk": "付费率过低",
                "probability": "低",
                "impact": "中",
                "mitigation": "A/B 测试付费点，优化首充奖励，增加付费引导"
            },
            {
                "risk": "服务器不稳定",
                "probability": "低",
                "impact": "高",
                "mitigation": "压力测试，弹性扩容，应急预案"
            },
            {
                "risk": "竞品同期上线",
                "probability": "中",
                "impact": "中",
                "mitigation": "灵活调整上线时间，差异化定位"
            }
        ]
        return risks
    
    def generate_retention_plan(self, game_type: str) -> Dict:
        """
        生成留存提升方案
        
        Args:
            game_type: 游戏类型
        
        Returns:
            完整留存提升方案
        """
        return {
            "game_type": game_type,
            "d1_strategies": self.RETENTION_STRATEGIES["d1_retention"],
            "d7_strategies": self.RETENTION_STRATEGIES["d7_retention"],
            "d30_strategies": self.RETENTION_STRATEGIES["d30_retention"],
            "overall_target": {
                "d1": self._calculate_overall_kpis(game_type, 1.0)["d1_retention"],
                "d7": self._calculate_overall_kpis(game_type, 1.0)["d7_retention"],
                "d30": self._calculate_overall_kpis(game_type, 1.0)["d30_retention"]
            },
            "implementation_timeline": {
                "week1": ["新手引导优化", "7 日签到配置"],
                "week2": ["成长目标系统", "首充奖励调整"],
                "week3": ["社交系统解锁", "第一周活动策划"],
                "week4": ["公会系统", "月度活动目标"]
            }
        }
    
    def generate_operations_report(self, game_type: str, budget: str = "中等") -> str:
        """
        生成完整发行运营报告
        
        Args:
            game_type: 游戏类型
            budget: 预算规模
        
        Returns:
            完整报告（Markdown 格式）
        """
        launch_plan = self.generate_launch_plan(game_type, budget)
        retention_plan = self.generate_retention_plan(game_type)
        
        report = f"""# 游戏发行运营策略报告

**游戏类型**: {game_type.upper()}
**预算规模**: {budget}
**生成时间**: 2026-04-15

---

## 一、上线节奏规划

"""
        for phase_name, phase_info in launch_plan["phases"].items():
            report += f"""### {phase_name.replace('_', ' ').title()}
- **周期**: {phase_info['duration']}
- **目标**: {' → '.join(phase_info['goals'])}
- **预算分配**: {phase_info['budget_allocation']['allocation']} (重点：{phase_info['budget_allocation']['focus']})
- **核心 KPI**:
"""
            for kpi, value in phase_info['kpis'].items():
                report += f"  - {kpi}: {value}\n"
            
            report += f"- **关键活动**:\n"
            for activity in phase_info['key_activities'][:3]:
                report += f"  - {activity}\n"
            report += "\n"
        
        report += """## 二、买量渠道组合

| 渠道 | CPI 范围 | ROI 基准 (D7/D30) | 预算分配 | 适合类型 |
|---|---|---|---|---|
"""
        for channel in launch_plan["channel_mix"]:
            report += f"| {channel['channel']} | {channel['cpi_range']} | {channel['roi_benchmark']['d7']}/{channel['roi_benchmark']['d30']} | {channel['budget_allocation']} | {', '.join(channel['best_for'])} |\n"
        
        report += f"""
## 三、整体 KPI 目标

| 指标 | 目标值 |
|---|---|
| **D1 留存** | {launch_plan['kpis']['d1_retention']} |
| **D7 留存** | {launch_plan['kpis']['d7_retention']} |
| **D30 留存** | {launch_plan['kpis']['d30_retention']} |
| **ARPU** | {launch_plan['kpis']['arpu_range']} |
| **LTV(30 天)** | {launch_plan['kpis']['ltv_30']} |
| **付费率** | {launch_plan['kpis']['paying_rate']} |
| **ROI 目标** | {launch_plan['kpis']['roi_target']} |

## 四、留存提升策略

### D1 留存提升
| 策略 | 预期提升 | 执行难度 |
|---|---|---|
"""
        for strategy in retention_plan["d1_strategies"]:
            report += f"| {strategy['strategy']} | {strategy['impact']} | {strategy['effort']} |\n"
        
        report += f"""
### D7 留存提升
| 策略 | 预期提升 | 执行难度 |
|---|---|---|
"""
        for strategy in retention_plan["d7_strategies"]:
            report += f"| {strategy['strategy']} | {strategy['impact']} | {strategy['effort']} |\n"
        
        report += f"""
### D30 留存提升
| 策略 | 预期提升 | 执行难度 |
|---|---|---|
"""
        for strategy in retention_plan["d30_strategies"]:
            report += f"| {strategy['strategy']} | {strategy['impact']} | {strategy['effort']} |\n"
        
        report += f"""
## 五、实施时间线

"""
        for week, tasks in retention_plan["implementation_timeline"].items():
            report += f"### {week.replace('week', '第').replace('1', '一').replace('2', '二').replace('3', '三').replace('4', '四')}周\n"
            for task in tasks:
                report += f"- {task}\n"
            report += "\n"
        
        report += """## 六、风险识别与缓解

| 风险 | 概率 | 影响 | 缓解方案 |
|---|---|---|---|
"""
        for risk in launch_plan["risk_mitigation"]:
            report += f"| {risk['risk']} | {risk['probability']} | {risk['impact']} | {risk['mitigation']} |\n"
        
        report += """
---

*本报告基于 Sensor Tower 2026 游戏报告、2026 游戏行业"主动权"之战、2025 游戏市场报告生成*
*数据来源：行业研究 + 实战经验*
"""
        
        return report


def main():
    """主函数"""
    import sys
    
    ops = PublishingOperations()
    
    if len(sys.argv) < 2:
        print("用法：python3 publishing_operations.py [game_type] [budget]")
        print("示例：python3 publishing_operations.py rpg 中等")
        print("\n支持的游戏类型：rpg, moba, fps, slg, casual, otome")
        print("预算规模：小，中等，大")
        sys.exit(1)
    
    game_type = sys.argv[1]
    budget = sys.argv[2] if len(sys.argv) > 2 else "中等"
    
    # 生成报告
    report = ops.generate_operations_report(game_type, budget)
    print(report)


if __name__ == "__main__":
    main()
