#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
system_design.py - 游戏系统策划设计模块

基于行业研究的完整系统策划方案
包含：系统框架/UI 设计/交互流程/系统循环/功能模块

数据来源：
- 2025 游戏 UI 设计
- UI/UX设计师岗位工作区别
- 2025 年 UI/UX 界面设计趋势
- 游戏系统策划和交互设计师区别
"""

import json
from typing import Dict, List, Optional


class SystemDesign:
    """游戏系统策划设计生成器"""
    
    # 核心系统库
    CORE_SYSTEMS = {
        "combat": {
            "name": "战斗系统",
            "subsystems": ["技能系统", "武器系统", "敌人 AI", "战斗 UI", "连招系统"],
            "priority": "核心",
            "complexity": "高"
        },
        "progression": {
            "name": "成长系统",
            "subsystems": ["等级系统", "属性系统", "技能树", "装备强化", "天赋系统"],
            "priority": "核心",
            "complexity": "高"
        },
        "economy": {
            "name": "经济系统",
            "subsystems": ["货币系统", "商城系统", "交易系统", "生产系统", "消耗系统"],
            "priority": "核心",
            "complexity": "高"
        },
        "social": {
            "name": "社交系统",
            "subsystems": ["好友系统", "公会系统", "聊天系统", "组队系统", "排行榜"],
            "priority": "重要",
            "complexity": "中"
        },
        "exploration": {
            "name": "探索系统",
            "subsystems": ["地图系统", "传送系统", "收集系统", "任务系统", "成就系统"],
            "priority": "重要",
            "complexity": "中"
        },
        "narrative": {
            "name": "叙事系统",
            "subsystems": ["任务系统", "对话系统", "过场动画", "剧情分支", "角色关系"],
            "priority": "重要",
            "complexity": "中"
        },
        "customization": {
            "name": "自定义系统",
            "subsystems": ["外观系统", "装备外观", "家园系统", "角色定制", "界面定制"],
            "priority": "次要",
            "complexity": "中"
        },
        "activity": {
            "name": "活动系统",
            "subsystems": ["日常活动", "周常活动", "限时活动", "赛季活动", "节日活动"],
            "priority": "重要",
            "complexity": "中"
        }
    }
    
    # UI 界面模板
    UI_TEMPLATES = {
        "main_menu": {
            "name": "主菜单",
            "elements": [
                {"name": "继续游戏", "type": "button", "priority": "高"},
                {"name": "新游戏", "type": "button", "priority": "高"},
                {"name": "加载游戏", "type": "button", "priority": "中"},
                {"name": "设置", "type": "button", "priority": "中"},
                {"name": "退出", "type": "button", "priority": "低"}
            ],
            "layout": "垂直居中",
            "background": "动态场景/静态图"
        },
        "game_hud": {
            "name": "游戏界面 HUD",
            "elements": [
                {"name": "血条", "type": "bar", "position": "左上", "priority": "高"},
                {"name": "蓝条/精力条", "type": "bar", "position": "左上", "priority": "高"},
                {"name": "Buff 图标", "type": "icon", "position": "左下", "priority": "中"},
                {"name": "金币/货币", "type": "text", "position": "右上", "priority": "高"},
                {"name": "小地图", "type": "map", "position": "右上", "priority": "中"},
                {"name": "技能栏", "type": "bar", "position": "下中", "priority": "高"},
                {"name": "快捷道具", "type": "slot", "position": "右下", "priority": "中"}
            ],
            "layout": "四角分布",
            "transparency": "半透明"
        },
        "inventory": {
            "name": "背包界面",
            "elements": [
                {"name": "装备栏", "type": "slot", "priority": "高"},
                {"name": "物品栏", "type": "grid", "priority": "高"},
                {"name": "分类筛选", "type": "tab", "priority": "中"},
                {"name": "物品详情", "type": "panel", "priority": "中"},
                {"name": "背包容量", "type": "text", "priority": "低"}
            ],
            "layout": "左右分栏",
            "grid_size": "5x8"
        },
        "character": {
            "name": "角色界面",
            "elements": [
                {"name": "角色模型", "type": "3d_model", "priority": "高"},
                {"name": "装备栏", "type": "slot", "priority": "高"},
                {"name": "属性面板", "type": "panel", "priority": "高"},
                {"name": "等级/经验", "type": "bar", "priority": "高"},
                {"name": "技能树", "type": "tree", "priority": "中"}
            ],
            "layout": "左模型右属性",
            "interaction": "可旋转模型"
        },
        "shop": {
            "name": "商城界面",
            "elements": [
                {"name": "商品分类", "type": "tab", "priority": "高"},
                {"name": "商品列表", "type": "grid", "priority": "高"},
                {"name": "商品详情", "type": "panel", "priority": "中"},
                {"name": "货币显示", "type": "text", "priority": "高"},
                {"name": "购买按钮", "type": "button", "priority": "高"},
                {"name": "限时标签", "type": "badge", "priority": "中"}
            ],
            "layout": "上分类下商品",
            "highlight": "推荐/限时商品"
        },
        "quest": {
            "name": "任务界面",
            "elements": [
                {"name": "任务列表", "type": "list", "priority": "高"},
                {"name": "任务详情", "type": "panel", "priority": "高"},
                {"name": "任务追踪", "type": "toggle", "priority": "中"},
                {"name": "任务分类", "type": "tab", "priority": "中"},
                {"name": "任务奖励", "type": "preview", "priority": "中"}
            ],
            "layout": "左列表右详情",
            "filter": "主线/支线/日常/周常"
        },
        "settings": {
            "name": "设置界面",
            "elements": [
                {"name": "图形设置", "type": "panel", "priority": "高"},
                {"name": "声音设置", "type": "panel", "priority": "高"},
                {"name": "操作设置", "type": "panel", "priority": "高"},
                {"name": "游戏性设置", "type": "panel", "priority": "中"},
                {"name": "键位绑定", "type": "mapping", "priority": "中"}
            ],
            "layout": "左侧导航右侧内容",
            "categories": ["游戏玩法", "镜头", "声音", "图像", "控制器", "键鼠"]
        },
        "gacha": {
            "name": "抽卡界面",
            "elements": [
                {"name": "卡池展示", "type": "banner", "priority": "高"},
                {"name": "抽卡按钮", "type": "button", "priority": "高"},
                {"name": "抽卡次数", "type": "text", "priority": "高"},
                {"name": "概率公示", "type": "link", "priority": "高"},
                {"name": "保底进度", "type": "bar", "priority": "高"},
                {"name": "抽卡记录", "type": "button", "priority": "中"}
            ],
            "layout": "中央卡池下方操作",
            "animation": "抽卡特效"
        }
    }
    
    # 交互流程模板
    INTERACTION_FLOWS = {
        "quest_accept": {
            "name": "接受任务流程",
            "steps": [
                {"step": 1, "action": "NPC 对话", "ui": "对话界面", "duration": "30-60 秒"},
                {"step": 2, "action": "任务说明", "ui": "任务详情", "duration": "15-30 秒"},
                {"step": 3, "action": "玩家选择", "ui": "接受/拒绝按钮", "duration": "5 秒"},
                {"step": 4, "action": "任务追踪", "ui": "任务栏更新", "duration": "即时"},
                {"step": 5, "action": "奖励预览", "ui": "奖励展示", "duration": "5 秒"}
            ],
            "feedback": ["音效", "UI 动画", "任务图标标记"]
        },
        "combat_encounter": {
            "name": "战斗遭遇流程",
            "steps": [
                {"step": 1, "action": "敌人出现", "ui": "战斗 UI 激活", "duration": "即时"},
                {"step": 2, "action": "锁定目标", "ui": "血条显示", "duration": "0.5 秒"},
                {"step": 3, "action": "战斗开始", "ui": "技能栏激活", "duration": "即时"},
                {"step": 4, "action": "战斗进行", "ui": "实时反馈", "duration": "30-180 秒"},
                {"step": 5, "action": "战斗结束", "ui": "战利品展示", "duration": "5-10 秒"}
            ],
            "feedback": ["受击反馈", "技能特效", "血条变化", "音效"]
        },
        "item_purchase": {
            "name": "物品购买流程",
            "steps": [
                {"step": 1, "action": "打开商城", "ui": "商城界面", "duration": "1 秒"},
                {"step": 2, "action": "浏览商品", "ui": "商品列表", "duration": "10-60 秒"},
                {"step": 3, "action": "查看详情", "ui": "商品详情弹窗", "duration": "5-15 秒"},
                {"step": 4, "action": "确认购买", "ui": "二次确认弹窗", "duration": "3 秒"},
                {"step": 5, "action": "获得物品", "ui": "获得动画", "duration": "3 秒"}
            ],
            "feedback": ["货币变化", "获得动画", "音效", "背包更新"]
        },
        "character_upgrade": {
            "name": "角色升级流程",
            "steps": [
                {"step": 1, "action": "获得经验", "ui": "经验条增长", "duration": "即时"},
                {"step": 2, "action": "升级提示", "ui": "升级弹窗", "duration": "3 秒"},
                {"step": 3, "action": "属性提升", "ui": "属性动画", "duration": "2 秒"},
                {"step": 4, "action": "技能点获得", "ui": "技能点提示", "duration": "2 秒"},
                {"step": 5, "action": "可分配提示", "ui": "红点标记", "duration": "持续"}
            ],
            "feedback": ["升级特效", "音效", "属性动画", "红点提示"]
        }
    }
    
    # 系统循环设计
    SYSTEM_LOOPS = {
        "core_loop": {
            "name": "核心循环",
            "duration": "3-5 分钟",
            "steps": ["遭遇敌人", "战斗", "获得奖励", "强化角色", "继续探索"],
            "motivation": "即时满足感"
        },
        "daily_loop": {
            "name": "日常循环",
            "duration": "30-60 分钟/天",
            "steps": ["登录签到", "完成日常任务", "领取奖励", "体力消耗", "下线"],
            "motivation": "稳定收益"
        },
        "weekly_loop": {
            "name": "周常循环",
            "duration": "2-4 小时/周",
            "steps": ["周常任务", "副本挑战", "排行榜竞争", "周常奖励", "重置"],
            "motivation": "阶段性目标"
        },
        "seasonal_loop": {
            "name": "赛季循环",
            "duration": "6-12 周",
            "steps": ["赛季开始", "通行证进度", "活动参与", "排名竞争", "赛季奖励"],
            "motivation": "长期目标 + 限定奖励"
        },
        "progression_loop": {
            "name": "成长循环",
            "duration": "整个游戏周期",
            "steps": ["角色成长", "装备收集", "内容解锁", "挑战高难", "追求极致"],
            "motivation": "长期成就感"
        }
    }
    
    def __init__(self):
        self.system_data = {}
    
    def generate_system_design(self, game_type: str, system_name: str) -> Dict:
        """
        生成系统设计方案
        
        Args:
            game_type: 游戏类型
            system_name: 系统名称
        
        Returns:
            完整系统设计方案
        """
        system_info = self.CORE_SYSTEMS.get(system_name, self.CORE_SYSTEMS["combat"])
        
        return {
            "game_type": game_type,
            "system": {
                "name": system_info["name"],
                "key": system_name,
                "priority": system_info["priority"],
                "complexity": system_info["complexity"],
                "subsystems": system_info["subsystems"]
            },
            "ui_design": self._generate_ui_design(system_name),
            "interaction_flow": self._generate_interaction_flow(system_name),
            "system_loop": self._generate_system_loop(game_type, system_name),
            "technical_requirements": self._generate_technical_requirements(system_name)
        }
    
    def _generate_ui_design(self, system_name: str) -> Dict:
        """生成 UI 设计方案"""
        # 根据系统名称匹配 UI 模板
        ui_map = {
            "combat": "game_hud",
            "progression": "character",
            "economy": "shop",
            "social": "main_menu",
            "exploration": "quest",
            "narrative": "quest",
            "customization": "character",
            "activity": "quest"
        }
        
        ui_template_key = ui_map.get(system_name, "main_menu")
        ui_template = self.UI_TEMPLATES[ui_template_key]
        
        return {
            "main_ui": ui_template,
            "related_uis": [
                self.UI_TEMPLATES[k] for k in list(self.UI_TEMPLATES.keys())[:3]
            ],
            "design_principles": [
                "清晰易读：关键信息突出显示",
                "操作便捷：常用功能一键可达",
                "视觉统一：保持整体风格一致",
                "反馈及时：操作即时反馈",
                "可定制性：允许玩家自定义布局"
            ]
        }
    
    def _generate_interaction_flow(self, system_name: str) -> Dict:
        """生成交互流程"""
        flow_map = {
            "combat": "combat_encounter",
            "progression": "character_upgrade",
            "economy": "item_purchase",
            "narrative": "quest_accept"
        }
        
        flow_key = flow_map.get(system_name, "quest_accept")
        flow = self.INTERACTION_FLOWS[flow_key]
        
        return {
            "primary_flow": flow,
            "edge_cases": [
                {"scenario": "网络中断", "handling": "本地缓存 + 重连提示"},
                {"scenario": "操作取消", "handling": "返回上一步/关闭界面"},
                {"scenario": "资源不足", "handling": "提示 + 快捷获取入口"},
                {"scenario": "CD 冷却", "handling": "倒计时显示 + 灰化按钮"}
            ],
            "feedback_requirements": [
                "视觉反馈：UI 动画/特效",
                "听觉反馈：音效/语音",
                "触觉反馈：震动（移动端）",
                "时间反馈：加载进度/CD 显示"
            ]
        }
    
    def _generate_system_loop(self, game_type: str, system_name: str) -> Dict:
        """生成系统循环"""
        return {
            "loops": [
                self.SYSTEM_LOOPS["core_loop"],
                self.SYSTEM_LOOPS["daily_loop"],
                self.SYSTEM_LOOPS["weekly_loop"]
            ],
            "retention_design": [
                {"type": "短期", "mechanism": "即时反馈/连续登录奖励", "target": "D1 留存"},
                {"type": "中期", "mechanism": "7 日目标/通行证进度", "target": "D7 留存"},
                {"type": "长期", "mechanism": "赛季目标/收集养成", "target": "D30 留存"}
            ],
            "monetization_points": self._get_monetization_points(system_name)
        }
    
    def _get_monetization_points(self, system_name: str) -> List[str]:
        """获取付费点"""
        monetization_map = {
            "combat": ["技能解锁", "武器抽取", "战斗增益"],
            "progression": ["经验加成", "属性点重置", "快速升级"],
            "economy": ["货币礼包", "限时折扣", "月卡特权"],
            "social": ["外观展示", "公会特权", "聊天表情"],
            "customization": ["皮肤外观", "家园装饰", "角色定制"]
        }
        return monetization_map.get(system_name, ["资源礼包", "特权卡"])
    
    def _generate_technical_requirements(self, system_name: str) -> Dict:
        """生成技术需求"""
        return {
            "frontend": {
                "ui_framework": "Unity UGUI/UE UMG",
                "animation": "DOTween/UE Animation",
                "resolution_support": "多分辨率适配"
            },
            "backend": {
                "data_sync": "实时/延迟双模式",
                "anti_cheat": "服务器验证",
                "logging": "行为日志记录"
            },
            "performance": {
                "load_time": "<2 秒",
                "frame_rate": "稳定 60FPS",
                "memory": "<200MB (UI 相关)"
            },
            "testing": {
                "functional": "功能测试",
                "compatibility": "多设备兼容",
                "usability": "用户体验测试"
            }
        }
    
    def generate_system_report(self, game_type: str, system_name: str) -> str:
        """
        生成完整系统策划报告
        
        Args:
            game_type: 游戏类型
            system_name: 系统名称
        
        Returns:
            完整报告（Markdown 格式）
        """
        system_design = self.generate_system_design(game_type, system_name)
        
        report = f"""# 游戏系统策划报告

**游戏类型**: {game_type.upper()}
**系统名称**: {system_design['system']['name']}
**优先级**: {system_design['system']['priority']}
**复杂度**: {system_design['system']['complexity']}
**生成时间**: 2026-04-15

---

## 一、系统概述

### 基本信息
- **系统名称**: {system_design['system']['name']}
- **优先级**: {system_design['system']['priority']}
- **复杂度**: {system_design['system']['complexity']}

### 子系统构成
| 子系统 | 说明 |
|---|---|
"""
        for subsystem in system_design['system']['subsystems']:
            report += f"| {subsystem} | 待细化 |\n"
        
        report += f"""
---

## 二、UI 设计方案

### 主界面设计
- **界面类型**: {system_design['ui_design']['main_ui']['name']}
- **布局方式**: {system_design['ui_design']['main_ui']['layout']}
- **核心元素**: {len(system_design['ui_design']['main_ui']['elements'])} 个

### 界面元素
| 元素名称 | 类型 | 位置 | 优先级 |
|---|---|---|---|
"""
        for elem in system_design['ui_design']['main_ui']['elements']:
            report += f"| {elem['name']} | {elem['type']} | {elem.get('position', 'N/A')} | {elem['priority']} |\n"
        
        report += f"""
### 设计原则
"""
        for principle in system_design['ui_design']['design_principles']:
            report += f"- {principle}\n"
        
        report += f"""
---

## 三、交互流程

### 主要流程：{system_design['interaction_flow']['primary_flow']['name']}
| 步骤 | 动作 | UI 界面 | 时长 |
|---|---|---|---|
"""
        for step in system_design['interaction_flow']['primary_flow']['steps']:
            report += f"| {step['step']} | {step['action']} | {step['ui']} | {step['duration']} |\n"
        
        report += f"""
### 反馈要求
"""
        for feedback in system_design['interaction_flow']['feedback_requirements']:
            report += f"- {feedback}\n"
        
        report += f"""
### 边界情况处理
| 场景 | 处理方案 |
|---|---|
"""
        for edge in system_design['interaction_flow']['edge_cases']:
            report += f"| {edge['scenario']} | {edge['handling']} |\n"
        
        report += f"""
---

## 四、系统循环设计

### 核心循环
- **名称**: {system_design['system_loop']['loops'][0]['name']}
- **时长**: {system_design['system_loop']['loops'][0]['duration']}
- **步骤**: {' → '.join(system_design['system_loop']['loops'][0]['steps'])}
- **驱动力**: {system_design['system_loop']['loops'][0]['motivation']}

### 日常循环
- **名称**: {system_design['system_loop']['loops'][1]['name']}
- **时长**: {system_design['system_loop']['loops'][1]['duration']}
- **步骤**: {' → '.join(system_design['system_loop']['loops'][1]['steps'])}
- **驱动力**: {system_design['system_loop']['loops'][1]['motivation']}

### 留存设计
| 类型 | 机制 | 目标 |
|---|---|---|
"""
        for retention in system_design['system_loop']['retention_design']:
            report += f"| {retention['type']} | {retention['mechanism']} | {retention['target']} |\n"
        
        report += f"""
### 付费点设计
"""
        for point in system_design['system_loop']['monetization_points']:
            report += f"- {point}\n"
        
        report += f"""
---

## 五、技术需求

### 前端技术
- **UI 框架**: {system_design['technical_requirements']['frontend']['ui_framework']}
- **动画系统**: {system_design['technical_requirements']['frontend']['animation']}
- **分辨率**: {system_design['technical_requirements']['frontend']['resolution_support']}

### 后端技术
- **数据同步**: {system_design['technical_requirements']['backend']['data_sync']}
- **反作弊**: {system_design['technical_requirements']['backend']['anti_cheat']}
- **日志**: {system_design['technical_requirements']['backend']['logging']}

### 性能要求
| 指标 | 目标 |
|---|---|
"""
        for metric, target in system_design['technical_requirements']['performance'].items():
            report += f"| **{metric}** | {target} |\n"
        
        report += f"""
---

## 六、验收标准

### 功能验收
- [ ] 所有子系统功能正常
- [ ] UI 界面显示正确
- [ ] 交互流程顺畅
- [ ] 边界情况处理正确

### 性能验收
- [ ] 加载时间<2 秒
- [ ] 帧率稳定 60FPS
- [ ] 内存占用<200MB

### 体验验收
- [ ] 新手引导清晰
- [ ] 操作反馈及时
- [ ] 界面美观统一
- [ ] 用户测试通过

---

*本报告基于 2025 游戏 UI 设计、UI/UX设计师岗位工作区别、2025 年 UI/UX 界面设计趋势生成*
*数据来源：行业研究 + 实战经验*
"""
        
        return report


def main():
    """主函数"""
    import sys
    
    system = SystemDesign()
    
    if len(sys.argv) < 2:
        print("用法：python3 system_design.py [game_type] [system_name]")
        print("示例：python3 system_design.py rpg combat")
        print("\n支持的游戏类型：rpg, moba, fps, slg, casual, otome")
        print("支持的系统：combat, progression, economy, social, exploration, narrative, customization, activity")
        sys.exit(1)
    
    game_type = sys.argv[1]
    system_name = sys.argv[2] if len(sys.argv) > 2 else "combat"
    
    # 生成报告
    report = system.generate_system_report(game_type, system_name)
    print(report)


if __name__ == "__main__":
    main()
