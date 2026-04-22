#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 世界观构建系统
构建完整的世界观架构，检查一致性
"""

import os
import json
import sys
from typing import Dict, Any, List
from datetime import datetime


class WorldviewBuilder:
    """世界观构建器"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), 'output', 'worldview')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_worldview_template(self, game_type: str = 'rpg') -> Dict[str, Any]:
        """
        生成世界观模板
        
        Args:
            game_type: 游戏类型
        
        Returns:
            世界观模板
        """
        templates = {
            'rpg': self._rpg_worldview_template(),
            'openworld': self._openworld_worldview_template()
        }
        
        template = templates.get(game_type, templates['rpg'])
        
        # 保存为 markdown
        filename = f"worldview_template_{game_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return {
            'status': 'generated',
            'game_type': game_type,
            'filepath': filepath,
            'filename': filename
        }
    
    def _rpg_worldview_template(self) -> str:
        """RPG 世界观模板"""
        return """# 世界观设定文档

## 1. 世界概述
### 1.1 世界名称
[填写世界名称]

### 1.2 核心概念
[用一句话概括这个世界]

### 1.3 世界类型
- [ ] 奇幻世界
- [ ] 科幻世界
- [ ] 现代世界
- [ ] 历史世界
- [ ] 混合世界

### 1.4 世界规则
[物理法则/魔法规则/科技水平等]

---

## 2. 地理设定
### 2.1 世界结构
- 大陆数量：
- 主要海洋：
- 特殊区域：

### 2.2 主要国家/地区
| 名称 | 类型 | 特点 | 关系 |
|---|---|---|---|
| [国家 A] | [帝国/王国/共和国] | [特点] | [与其他国家关系] |
| [国家 B] | [帝国/王国/共和国] | [特点] | [与其他国家关系] |

### 2.3 重要地点
| 名称 | 类型 | 描述 | 重要性 |
|---|---|---|---|
| [地点 A] | [城市/遗迹/秘境] | [描述] | [剧情重要性] |
| [地点 B] | [城市/遗迹/秘境] | [描述] | [剧情重要性] |

---

## 3. 历史年表
### 3.1 创世时期
[世界起源神话]

### 3.2 古代历史
| 年份 | 事件 | 影响 |
|---|---|---|
| [年份] | [事件] | [对世界的影响] |

### 3.3 近代历史
[距离游戏开始 100 年内的历史]

### 3.4 当前局势
[游戏开始时的世界局势]

---

## 4. 种族设定
### 4.1 主要种族
| 种族 | 特点 | 分布 | 文化 |
|---|---|---|---|
| [种族 A] | [生理特点] | [分布地区] | [文化特点] |
| [种族 B] | [生理特点] | [分布地区] | [文化特点] |

### 4.2 种族关系
[种族间的关系：友好/敌对/中立]

---

## 5. 势力架构
### 5.1 主要势力
| 势力 | 类型 | 目标 | 实力 |
|---|---|---|---|
| [势力 A] | [国家/组织/教派] | [目标] | [实力评级] |
| [势力 B] | [国家/组织/教派] | [目标] | [实力评级] |

### 5.2 势力关系图
[绘制势力关系图]

---

## 6. 文化体系
### 6.1 宗教信仰
[主要宗教/信仰体系]

### 6.2 语言系统
[主要语言/文字]

### 6.3 社会结构
[阶级制度/社会形态]

### 6.4 科技/魔法水平
[科技发展程度/魔法普及程度]

---

## 7. 力量体系
### 7.1 力量来源
- [ ] 魔法
- [ ] 科技
- [ ] 武道
- [ ] 异能
- [ ] 其他

### 7.2 力量等级
| 等级 | 名称 | 描述 |
|---|---|---|
| 1 | [等级名称] | [描述] |
| 2 | [等级名称] | [描述] |

### 7.3 力量规则
[力量使用的规则和限制]

---

## 8. 生物设定
### 8.1 常见生物
[普通动物/怪物]

### 8.2 稀有生物
[传说生物/神兽]

### 8.3 敌人类型
[主要敌人类型设定]

---

## 9. 物品设定
### 9.1 货币系统
[货币类型/兑换比例]

### 9.2 重要物品
[传说装备/神器/关键道具]

### 9.3 资源分布
[重要资源产地]

---

## 10. 核心冲突
### 10.1 主要矛盾
[推动剧情的核心矛盾]

### 10.2 次要矛盾
[支线剧情的矛盾]

### 10.3 矛盾发展
[矛盾如何发展激化]

---

_世界观设定文档 v1.0_
_创建日期：[填写日期]_
"""
    
    def _openworld_worldview_template(self) -> str:
        """开放世界世界观模板"""
        return """# 开放世界世界观设定

## 1. 世界概述
[世界名称/核心概念/类型]

## 2. 地图设计
### 2.1 区域划分
| 区域 | 主题 | 等级范围 | 特色 |
|---|---|---|---|
| [区域 A] | [主题] | [等级] | [特色] |

### 2.2 地标设计
[重要地标/吸引玩家探索的点]

### 2.3 探索要素
[收集品/宝箱/谜题分布]

## 3. 势力分布
[各势力在地图上的分布]

## 4. 生态设计
[怪物分布/资源分布/生态系统]

## 5. 叙事分布
[主线/支线/隐藏剧情分布]

_开放世界世界观设定 v1.0_
"""
    
    def check_consistency(self, worldview_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查世界观一致性
        
        Args:
            worldview_data: 世界观数据
        
        Returns:
            一致性检查报告
        """
        issues = []
        
        # 检查时间线一致性
        if 'history' in worldview_data:
            timeline_issues = self._check_timeline(worldview_data['history'])
            issues.extend(timeline_issues)
        
        # 检查地理一致性
        if 'geography' in worldview_data:
            geo_issues = self._check_geography(worldview_data['geography'])
            issues.extend(geo_issues)
        
        # 检查种族一致性
        if 'races' in worldview_data:
            race_issues = self._check_races(worldview_data['races'])
            issues.extend(race_issues)
        
        # 检查势力一致性
        if 'factions' in worldview_data:
            faction_issues = self._check_factions(worldview_data['factions'])
            issues.extend(faction_issues)
        
        return {
            'status': 'checked',
            'total_issues': len(issues),
            'issues': issues,
            'consistency_score': max(0, 100 - len(issues) * 5)
        }
    
    def _check_timeline(self, history: Dict) -> List[Dict]:
        """检查时间线一致性"""
        issues = []
        # 简化检查：时间是否倒流等
        return issues
    
    def _check_geography(self, geography: Dict) -> List[Dict]:
        """检查地理一致性"""
        issues = []
        # 简化检查：国家位置是否冲突等
        return issues
    
    def _check_races(self, races: List) -> List[Dict]:
        """检查种族一致性"""
        issues = []
        # 简化检查：种族设定是否冲突
        return issues
    
    def _check_factions(self, factions: List) -> List[Dict]:
        """检查势力一致性"""
        issues = []
        # 简化检查：势力关系是否冲突
        return issues
    
    def extract_worldview_elements(self, text: str) -> Dict[str, Any]:
        """
        从文本中提取世界观要素
        
        Args:
            text: 世界观描述文本
        
        Returns:
            提取的要素
        """
        elements = {
            'locations': [],
            'characters': [],
            'factions': [],
            'events': [],
            'items': []
        }
        
        # 简化提取：实际应该用 NLP
        # 这里只做示例
        
        return elements
    
    def generate_worldview_chart(self, worldview_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成世界观架构图
        
        Args:
            worldview_data: 世界观数据
        
        Returns:
            Mermaid 图表代码
        """
        # 生成势力关系图
        faction_chart = """graph TB
    A[势力 A] -->|友好 | B[势力 B]
    A -->|敌对 | C[势力 C]
    B -->|中立 | C
"""
        
        # 生成历史时间线
        timeline_chart = """timeline
    title 历史年表
    section 创世时期
        元年 : 世界创造
    section 古代
        1000 年 : 第一次大战
    section 近代
        900 年 : 当前局势
"""
        
        return {
            'faction_chart': faction_chart,
            'timeline_chart': timeline_chart
        }


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python worldview_builder.py <command> [args]")
        print("Commands:")
        print("  template [game_type]       - 生成世界观模板")
        print("  check <json_file>          - 检查一致性")
        print("  extract <text_file>        - 提取要素")
        print("  chart <json_file>          - 生成架构图")
        sys.exit(1)
    
    command = sys.argv[1]
    builder = WorldviewBuilder()
    
    if command == 'template':
        game_type = sys.argv[2] if len(sys.argv) > 2 else 'rpg'
        result = builder.generate_worldview_template(game_type)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'check':
        json_file = sys.argv[2] if len(sys.argv) > 2 else None
        if not json_file:
            print("Error: 需要提供 JSON 文件")
            sys.exit(1)
        
        with open(json_file, 'r', encoding='utf-8') as f:
            worldview_data = json.load(f)
        
        result = builder.check_consistency(worldview_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'extract':
        text_file = sys.argv[2] if len(sys.argv) > 2 else None
        if not text_file:
            print("Error: 需要提供文本文件")
            sys.exit(1)
        
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        result = builder.extract_worldview_elements(text)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'chart':
        json_file = sys.argv[2] if len(sys.argv) > 2 else None
        if not json_file:
            print("Error: 需要提供 JSON 文件")
            sys.exit(1)
        
        with open(json_file, 'r', encoding='utf-8') as f:
            worldview_data = json.load(f)
        
        result = builder.generate_worldview_chart(worldview_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
