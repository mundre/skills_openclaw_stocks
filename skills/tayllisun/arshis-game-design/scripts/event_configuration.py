#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
event_configuration.py - 游戏活动配置模块

基于行业研究的完整活动配置方案
包含：活动类型/奖励配置/时间安排/数值平衡

数据来源：
- Sensor Tower 2026 游戏报告
- 2026 游戏行业"主动权"之战
- 原神/崩铁/王者活动设计案例分析
"""

import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class EventConfiguration:
    """游戏活动配置生成器"""
    
    # 活动类型库
    EVENT_TYPES = {
        "daily_login": {
            "name": "每日签到",
            "frequency": "每日",
            "duration": "永久/月度",
            "participation": "登录即参与",
            "rewards": ["钻石", "体力", "金币", "材料"],
            "retention_lift": "+8-12% (7 日留存)"
        },
        "daily_mission": {
            "name": "每日任务",
            "frequency": "每日",
            "duration": "永久",
            "participation": "完成指定行为",
            "rewards": ["活跃度", "钻石", "材料"],
            "retention_lift": "+10-15% (7 日留存)"
        },
        "weekly_mission": {
            "name": "每周任务",
            "frequency": "每周",
            "duration": "永久",
            "participation": "完成周常目标",
            "rewards": ["钻石", "稀有材料", "抽卡券"],
            "retention_lift": "+5-8% (30 日留存)"
        },
        "limited_gacha": {
            "name": "限定卡池",
            "frequency": "版本更新",
            "duration": "2-3 周",
            "participation": "付费/免费抽卡",
            "rewards": ["限定角色", "限定武器"],
            "revenue_lift": "版本收入提升 200-400%"
        },
        "battle_pass": {
            "name": "战斗通行证",
            "frequency": "赛季制",
            "duration": "6-12 周",
            "participation": "免费线/付费线",
            "rewards": ["皮肤", "资源", "限定头像框"],
            "take_rate": "15-30%",
            "revenue_lift": "占总收入 20-30%"
        },
        "seasonal_event": {
            "name": "季节活动",
            "frequency": "节日/季节",
            "duration": "1-2 周",
            "participation": "活动任务/活动副本",
            "rewards": ["限定皮肤", "活动货币", "稀有材料"],
            "revenue_lift": "节日期间收入提升 50-100%"
        },
        "ranking_event": {
            "name": "排行榜活动",
            "frequency": "定期",
            "duration": "1-2 周",
            "participation": "PVP/PVE 挑战",
            "rewards": ["排名奖励", "称号", "稀有道具"],
            "engagement_lift": "日活提升 20-30%"
        },
        "collaboration": {
            "name": "联动活动",
            "frequency": "不定期",
            "duration": "2-4 周",
            "participation": "联动任务/联动卡池",
            "rewards": ["联动角色", "联动皮肤", "限定道具"],
            "revenue_lift": "联动期间收入提升 300-500%"
        }
    }
    
    # 奖励配置模板
    REWARD_TIERS = {
        "free": {
            "name": "免费奖励",
            "value_range": "低 - 中",
            "distribution": "广泛",
            "purpose": "保底体验，维持免费玩家留存"
        },
        "paid_basic": {
            "name": "付费基础档",
            "value_range": "中",
            "distribution": "月卡/通行证",
            "purpose": "转化付费，提供稳定收入"
        },
        "paid_premium": {
            "name": "付费高级档",
            "value_range": "高",
            "distribution": "648 档/限定",
            "purpose": "鲸鱼用户，提升 ARPU"
        }
    }
    
    # 时间安排模板
    SCHEDULING_TEMPLATES = {
        "daily_routine": {
            "name": "日常循环",
            "activities": [
                {"time": "每日 0 点", "event": "签到刷新/任务刷新"},
                {"time": "12:00-14:00", "event": "午间活跃高峰"},
                {"time": "20:00-23:00", "event": "晚间活跃高峰"},
                {"time": "23:59", "event": "每日任务截止"}
            ]
        },
        "weekly_routine": {
            "name": "周常循环",
            "activities": [
                {"time": "周一 0 点", "event": "周常任务刷新"},
                {"time": "周三", "event": "版本更新/活动开启"},
                {"time": "周五", "event": "周末活动预告"},
                {"time": "周日 23:59", "event": "周常任务截止"}
            ]
        },
        "version_cycle": {
            "name": "版本循环",
            "duration": "6-8 周",
            "phases": [
                {"phase": "版本初", "week": "1-2", "focus": "新内容体验/限定卡池"},
                {"phase": "版本中", "week": "3-5", "focus": "活动持续/长草期"},
                {"phase": "版本末", "week": "6-8", "focus": "版本收尾/预热下版本"}
            ]
        }
    }
    
    # 数值平衡公式
    BALANCE_FORMULAS = {
        "daily_currency": {
            "name": "每日货币产出",
            "formula": "免费玩家：50-100 钻石/天，月卡玩家：150-200 钻石/天",
            "monthly_total": "免费：1500-3000，月卡：4500-6000"
        },
        "gacha_pity": {
            "name": "抽卡保底",
            "formula": "小保底：70-90 抽，大保底：180 抽",
            "cost_estimate": "小保底：1120-1440 元，大保底：2240-2880 元"
        },
        "battle_pass_xp": {
            "name": "通行证经验",
            "formula": "每日任务：500-1000XP，每周任务：3000-5000XP",
            "completion_time": "活跃玩家：4-6 周满级，休闲玩家：8-10 周满级"
        }
    }
    
    def __init__(self):
        self.event_data = {}
    
    def generate_event_plan(self, game_type: str, event_type: str, duration: str) -> Dict:
        """
        生成活动配置方案
        
        Args:
            game_type: 游戏类型
            event_type: 活动类型
            duration: 活动时长
        
        Returns:
            完整活动配置方案
        """
        event_info = self.EVENT_TYPES.get(event_type, self.EVENT_TYPES["seasonal_event"])
        
        return {
            "game_type": game_type,
            "event": {
                "type": event_type,
                "name": event_info["name"],
                "frequency": event_info["frequency"],
                "duration": duration,
                "participation": event_info["participation"]
            },
            "schedule": self._generate_schedule(event_type, duration),
            "rewards": self._generate_rewards(event_type, game_type),
            "numerical_balance": self._generate_balance(event_type),
            "expected_metrics": self._generate_metrics(event_type)
        }
    
    def _generate_schedule(self, event_type: str, duration: str) -> Dict:
        """生成时间安排"""
        if "daily" in event_type:
            return self.SCHEDULING_TEMPLATES["daily_routine"]
        elif "weekly" in event_type:
            return self.SCHEDULING_TEMPLATES["weekly_routine"]
        elif "battle_pass" in event_type:
            return self.SCHEDULING_TEMPLATES["version_cycle"]
        else:
            return {
                "name": "活动周期",
                "duration": duration,
                "phases": [
                    {"phase": "预热期", "day": "1-2", "focus": "预告/预约"},
                    {"phase": "开启期", "day": "3-7", "focus": "活动高潮/付费高峰"},
                    {"phase": "持续期", "day": "8-12", "focus": "长尾参与"},
                    {"phase": "收尾期", "day": "13-14", "focus": "最后冲刺/奖励兑换"}
                ]
            }
    
    def _generate_rewards(self, event_type: str, game_type: str) -> Dict:
        """生成奖励配置"""
        event_info = self.EVENT_TYPES.get(event_type, self.EVENT_TYPES["seasonal_event"])
        
        return {
            "free_tier": {
                "name": "免费奖励",
                "rewards": self._get_specific_rewards(event_type, "free", game_type),
                "total_value": "约 500-1000 元等价资源",
                "purpose": event_info.get("rewards", ["资源"])[0]
            },
            "paid_tier": {
                "name": "付费奖励",
                "rewards": self._get_specific_rewards(event_type, "paid", game_type),
                "total_value": "约 2000-5000 元等价资源",
                "price_point": "68-328 元"
            },
            "whale_tier": {
                "name": "鲸鱼奖励",
                "rewards": self._get_specific_rewards(event_type, "whale", game_type),
                "total_value": "限定/稀有内容",
                "price_point": "648 元+"
            }
        }
    
    def _get_specific_rewards(self, event_type: str, tier: str, game_type: str) -> List[str]:
        """获取具体奖励"""
        reward_map = {
            "daily_login": {
                "free": ["钻石×50", "体力×30", "金币×5000"],
                "paid": ["钻石×100", "体力×60", "金币×10000"],
                "whale": ["限定头像框", "稀有材料"]
            },
            "limited_gacha": {
                "free": ["抽卡券×10", "钻石×1600"],
                "paid": ["抽卡券×50", "钻石×8000"],
                "whale": ["限定角色", "限定武器", "满命座"]
            },
            "battle_pass": {
                "free": ["资源包", "基础材料", "普通皮肤"],
                "paid": ["高级材料", "稀有皮肤", "限定头像框"],
                "whale": ["典藏版皮肤", "专属特效"]
            },
            "seasonal_event": {
                "free": ["活动货币", "材料包", "普通奖励"],
                "paid": ["限定皮肤", "稀有道具", "活动专属"],
                "whale": ["全套限定", "绝版内容"]
            }
        }
        
        return reward_map.get(event_type, {}).get(tier, ["资源"])
    
    def _generate_balance(self, event_type: str) -> Dict:
        """生成数值平衡"""
        return {
            "currency_output": self.BALANCE_FORMULAS["daily_currency"],
            "gacha_system": self.BALANCE_FORMULAS["gacha_pity"] if "gacha" in event_type else None,
            "progression": self.BALANCE_FORMULAS["battle_pass_xp"] if "battle_pass" in event_type else None,
            "difficulty_curve": {
                "easy": "免费玩家可完成 60-80%",
                "medium": "月卡玩家可完成 80-100%",
                "hard": "付费玩家可挑战 100%+"
            }
        }
    
    def _generate_metrics(self, event_type: str) -> Dict:
        """生成预期指标"""
        event_info = self.EVENT_TYPES.get(event_type, self.EVENT_TYPES["seasonal_event"])
        
        metrics = {
            "participation_rate": "活跃玩家的 60-80%",
            "completion_rate": "参与玩家的 40-60%",
            "revenue_lift": event_info.get("revenue_lift", "收入提升 20-50%"),
            "retention_lift": event_info.get("retention_lift", "留存提升 5-10%")
        }
        
        if "battle_pass" in event_type:
            metrics["take_rate"] = "15-30%"
        
        return metrics
    
    def generate_event_report(self, game_type: str, event_type: str, duration: str) -> str:
        """
        生成完整活动配置报告
        
        Args:
            game_type: 游戏类型
            event_type: 活动类型
            duration: 活动时长
        
        Returns:
            完整报告（Markdown 格式）
        """
        event_plan = self.generate_event_plan(game_type, event_type, duration)
        
        report = f"""# 游戏活动配置报告

**游戏类型**: {game_type.upper()}
**活动类型**: {event_plan['event']['name']}
**活动时长**: {duration}
**生成时间**: 2026-04-15

---

## 一、活动概述

### 基本信息
- **活动名称**: {event_plan['event']['name']}
- **活动频率**: {event_plan['event']['frequency']}
- **活动时长**: {event_plan['event']['duration']}
- **参与方式**: {event_plan['event']['participation']}

---

## 二、时间安排

"""
        if "phases" in event_plan["schedule"]:
            report += """### 活动阶段
| 阶段 | 时间 | 重点 |
|---|---|---|
"""
            for phase in event_plan["schedule"]["phases"]:
                report += f"| {phase['phase']} | {phase.get('day', phase.get('week', 'N/A'))} | {phase['focus']} |\n"
        
        report += f"""
---

## 三、奖励配置

### 免费奖励
- **内容**: {', '.join(event_plan['rewards']['free_tier']['rewards'])}
- **总价值**: {event_plan['rewards']['free_tier']['total_value']}
- **目的**: {event_plan['rewards']['free_tier']['purpose']}

### 付费奖励
- **内容**: {', '.join(event_plan['rewards']['paid_tier']['rewards'])}
- **总价值**: {event_plan['rewards']['paid_tier']['total_value']}
- **价格档**: {event_plan['rewards']['paid_tier']['price_point']}

### 鲸鱼奖励
- **内容**: {', '.join(event_plan['rewards']['whale_tier']['rewards'])}
- **总价值**: {event_plan['rewards']['whale_tier']['total_value']}
- **价格档**: {event_plan['rewards']['whale_tier']['price_point']}

---

## 四、数值平衡

"""
        if event_plan["numerical_balance"]["currency_output"]:
            report += f"""### 货币产出
- **公式**: {event_plan['numerical_balance']['currency_output']['formula']}
- **月度总计**: {event_plan['numerical_balance']['currency_output']['monthly_total']}

"""
        
        if event_plan["numerical_balance"]["gacha_system"]:
            report += f"""### 抽卡保底
- **小保底**: {event_plan['numerical_balance']['gacha_system']['formula']}
- **大保底**: {event_plan['numerical_balance']['gacha_system']['cost_estimate']}

"""
        
        report += f"""### 难度曲线
- **免费玩家**: {event_plan['numerical_balance']['difficulty_curve']['easy']}
- **月卡玩家**: {event_plan['numerical_balance']['difficulty_curve']['medium']}
- **付费玩家**: {event_plan['numerical_balance']['difficulty_curve']['hard']}

---

## 五、预期指标

| 指标 | 预期值 |
|---|---|
"""
        for metric, value in event_plan["expected_metrics"].items():
            report += f"| **{metric}** | {value} |\n"
        
        report += """
---

## 六、执行清单

### 活动前（提前 1-2 周）
- [ ] 活动配置完成
- [ ] 奖励配置测试
- [ ] 数值平衡验证
- [ ] 宣传物料准备
- [ ] 客服培训完成

### 活动中（每日）
- [ ] 数据监控（参与率/完成率/收入）
- [ ] 异常处理
- [ ] 玩家反馈收集
- [ ] 必要时调整

### 活动后（1 周内）
- [ ] 数据复盘
- [ ] 玩家反馈整理
- [ ] 经验总结
- [ ] 下次活动优化

---

*本报告基于 Sensor Tower 2026 游戏报告、2026 游戏行业"主动权"之战、原神/崩铁/王者活动设计案例生成*
*数据来源：行业研究 + 实战经验*
"""
        
        return report


def main():
    """主函数"""
    import sys
    
    event = EventConfiguration()
    
    if len(sys.argv) < 2:
        print("用法：python3 event_configuration.py [game_type] [event_type] [duration]")
        print("示例：python3 event_configuration.py rpg seasonal_event 2 周")
        print("\n支持的游戏类型：rpg, moba, fps, slg, casual, otome")
        print("支持的活动类型：daily_login, daily_mission, weekly_mission, limited_gacha, battle_pass, seasonal_event, ranking_event, collaboration")
        sys.exit(1)
    
    game_type = sys.argv[1]
    event_type = sys.argv[2] if len(sys.argv) > 2 else "seasonal_event"
    duration = sys.argv[3] if len(sys.argv) > 3 else "2 周"
    
    # 生成报告
    report = event.generate_event_report(game_type, event_type, duration)
    print(report)


if __name__ == "__main__":
    main()
