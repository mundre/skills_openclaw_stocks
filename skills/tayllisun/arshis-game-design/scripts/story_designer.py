#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 剧情结构设计系统
三幕剧/英雄之旅/救猫咪等经典结构
"""

import os
import json
import sys
from typing import Dict, Any, List
from datetime import datetime


class StoryDesigner:
    """剧情设计师"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), 'output', 'story')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_story_structure(self, structure_type: str = 'three_act') -> Dict[str, Any]:
        """
        生成剧情结构模板
        
        Args:
            structure_type: 结构类型（three_act/heros_journey/save_the_cat）
        
        Returns:
            剧情结构模板
        """
        structures = {
            'three_act': self._three_act_structure(),
            'heros_journey': self._heros_journey_structure(),
            'save_the_cat': self._save_the_cat_structure()
        }
        
        structure = structures.get(structure_type, structures['three_act'])
        
        # 保存为 markdown
        filename = f"story_structure_{structure_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(structure)
        
        return {
            'status': 'generated',
            'structure_type': structure_type,
            'filepath': filepath,
            'filename': filename
        }
    
    def _three_act_structure(self) -> str:
        """三幕剧结构"""
        return """# 三幕剧结构模板

## 第一幕：铺垫（25%）
### 1. 开场画面
[展示主角的日常生活]

### 2. 主题呈现
[暗示故事主题]

### 3. 铺垫
[介绍主角/世界观/关系]

### 4. 触发事件
[打破日常生活的事件]

### 5. 辩论
[主角犹豫是否接受冒险]

### 6. 进入第二幕
[主角决定踏上旅程]

---

## 第二幕：冲突（50%）
### 7. 副线故事
[引入爱情线/友情线]

### 8. 游戏时间
[主角探索新世界/学习新技能]

### 9. 中点
[重大转折/虚假胜利或失败]

### 10. 反派逼近
[反派势力增强]

### 11. 一切失去
[主角失去一切]

### 12. 灵魂黑夜
[主角最低谷时刻]

### 13. 进入第三幕
[主角找到解决方案]

---

## 第三幕：解决（25%）
### 14. 高潮
[最终对决]

### 15. 结局
[新的平衡建立]

### 16. 终场画面
[与开场呼应的画面]

---

_三幕剧结构 v1.0_
"""
    
    def _heros_journey_structure(self) -> str:
        """英雄之旅结构"""
        return """# 英雄之旅结构模板（12 阶段）

## 第一幕：出发
### 1. 平凡世界
[英雄的日常生活]

### 2. 冒险召唤
[收到冒险邀请]

### 3. 拒绝召唤
[英雄犹豫/拒绝]

### 4. 遇见导师
[导师出现并提供帮助]

### 5. 跨越门槛
[英雄正式踏上旅程]

---

## 第二幕：启蒙
### 6. 考验/盟友/敌人
[遇到考验/结交盟友/树立敌人]

### 7. 接近最深洞穴
[接近危险核心]

### 8. 严峻考验
[面对最大恐惧/死亡与重生]

### 9. 获得宝剑
[获得奖励/宝物/知识]

---

## 第三幕：返回
### 10. 返回之路
[带着宝物返回]

### 11. 复活
[最后一次考验]

### 12. 带着万能药返回
[返回平凡世界/带来改变]

---

_英雄之旅结构 v1.0_
"""
    
    def _save_the_cat_structure(self) -> str:
        """救猫咪结构（15 节拍）"""
        return """# 救猫咪结构模板（15 节拍）

## 第一幕
### 1. 开场画面（1%）
[展示主角现状]

### 2. 主题呈现（5%）
[暗示故事主题]

### 3. 铺垫（1-10%）
[介绍主角/世界观]

### 4. 催化剂（10%）
[触发事件]

### 5. 辩论（10-20%）
[主角犹豫]

### 6. 进入第二幕（20%）
[主角决定行动]

---

## 第二幕
### 7. 副线故事（22%）
[引入 B 故事]

### 8. 游戏时间（20-50%）
[主角探索/成长]

### 9. 中点（50%）
[重大转折]

### 10. 反派逼近（50-75%）
[反派增强/压力增大]

### 11. 一切失去（75%）
[主角失去一切]

### 12. 灵魂黑夜（75-80%）
[最低谷时刻]

### 13. 进入第三幕（80%）
[找到解决方案]

---

## 第三幕
### 14. 高潮（80-99%）
[最终对决]

### 15. 终场画面（100%）
[新的平衡]

---

_救猫咪结构 v1.0_
"""
    
    def generate_character_arc(self, arc_type: str = 'positive') -> Dict[str, Any]:
        """
        生成角色弧线模板
        
        Args:
            arc_type: 弧线类型（positive/negative/flat）
        
        Returns:
            角色弧线模板
        """
        arcs = {
            'positive': self._positive_arc(),
            'negative': self._negative_arc(),
            'flat': self._flat_arc()
        }
        
        arc = arcs.get(arc_type, arcs['positive'])
        
        return {
            'arc_type': arc_type,
            'template': arc
        }
    
    def _positive_arc(self) -> str:
        """正面角色弧线（成长）"""
        return """# 正面角色弧线（成长弧线）

## 起点
### 初始状态
- 主角的缺陷/谎言
- 舒适区生活
- 未意识到的需求

## 发展
### 觉醒
- 触发事件打破舒适区
- 开始意识到问题
- 抗拒改变

### 成长
- 学习新技能/观念
- 逐渐克服缺陷
- 付出代价

## 高潮
### 考验
- 面对最大恐惧
- 放弃旧观念
- 做出艰难选择

## 终点
### 新的平衡
- 克服缺陷
- 成为更好的自己
- 获得真正需要的

_正面弧线：从缺陷到成长_
"""
    
    def _negative_arc(self) -> str:
        """负面角色弧线（堕落）"""
        return """# 负面角色弧线（堕落弧线）

## 起点
### 初始状态
- 主角有道德底线
- 有想要保护的东西
- 面临压力

## 发展
### 妥协
- 第一次妥协底线
- 为达目的不择手段
- 逐渐迷失

### 堕落
- 完全抛弃底线
- 成为曾经讨厌的人
- 众叛亲离

## 终点
### 悲剧结局
- 失去一切
- 自我毁灭
- 或继续堕落

_负面弧线：从道德到堕落_
"""
    
    def _flat_arc(self) -> str:
        """平坦角色弧线（不变）"""
        return """# 平坦角色弧线（不变弧线）

## 起点
### 初始状态
- 主角已经掌握真理
- 坚定的信念
- 周围人质疑

## 发展
### 考验
- 世界挑战主角信念
- 诱惑主角放弃
- 主角坚持信念

### 影响
- 主角改变周围人
- 证明信念正确
- 付出代价

## 终点
### 胜利
- 信念被证明
- 改变世界/他人
- 主角本身不变

_平坦弧线：主角不变，改变世界_
"""
    
    def generate_narrative_rhythm(self, story_length: str = 'medium') -> Dict[str, Any]:
        """
        生成叙事节奏曲线
        
        Args:
            story_length: 故事长度（short/medium/long）
        
        Returns:
            节奏曲线设计
        """
        rhythm = {
            'tension_curve': [],
            'release_points': [],
            'pacing': {}
        }
        
        # 简化版本
        if story_length == 'short':
            rhythm['pacing'] = {
                'act1': '25%',
                'act2': '50%',
                'act3': '25%'
            }
        elif story_length == 'long':
            rhythm['pacing'] = {
                'act1': '20%',
                'act2': '60%',
                'act3': '20%'
            }
        else:
            rhythm['pacing'] = {
                'act1': '25%',
                'act2': '50%',
                'act3': '25%'
            }
        
        return {
            'story_length': story_length,
            'rhythm': rhythm,
            'tips': [
                '紧张 - 释放循环设计',
                '每 10-15 分钟一个小高潮',
                '每 30-45 分钟一个大高潮',
                '结尾前最黑暗时刻'
            ]
        }
    
    def generate_branch_narrative(self, branches: int = 3) -> Dict[str, Any]:
        """
        生成分支叙事模板
        
        Args:
            branches: 分支数量
        
        Returns:
            分支叙事树
        """
        branch_tree = {
            'root': '共同起点',
            'branches': [],
            'convergence_points': [],
            'endings': []
        }
        
        for i in range(branches):
            branch_tree['branches'].append({
                'id': f'branch_{i}',
                'name': f'分支{i+1}',
                'key_choice': f'关键选择{i+1}',
                'consequences': ['后果 A', '后果 B']
            })
        
        for i in range(branches):
            branch_tree['endings'].append({
                'id': f'ending_{i}',
                'name': f'结局{i+1}',
                'condition': f'通过分支{i+1}',
                'description': '结局描述'
            })
        
        return {
            'branches': branches,
            'tree': branch_tree,
            'tips': [
                '关键选择要有意义',
                '分支要有明显后果',
                '避免无效分支',
                '考虑开发成本'
            ]
        }


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python story_designer.py <command> [args]")
        print("Commands:")
        print("  structure [type]           - 生成剧情结构")
        print("  character_arc [type]       - 生成角色弧线")
        print("  rhythm [length]            - 生成叙事节奏")
        print("  branch [count]             - 生成分支叙事")
        sys.exit(1)
    
    command = sys.argv[1]
    designer = StoryDesigner()
    
    if command == 'structure':
        structure_type = sys.argv[2] if len(sys.argv) > 2 else 'three_act'
        result = designer.generate_story_structure(structure_type)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'character_arc':
        arc_type = sys.argv[2] if len(sys.argv) > 2 else 'positive'
        result = designer.generate_character_arc(arc_type)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'rhythm':
        story_length = sys.argv[2] if len(sys.argv) > 2 else 'medium'
        result = designer.generate_narrative_rhythm(story_length)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'branch':
        branches = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        result = designer.generate_branch_narrative(branches)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
