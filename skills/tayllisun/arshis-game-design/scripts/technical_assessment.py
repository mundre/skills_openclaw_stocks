#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
technical_assessment.py - 游戏技术评估模块

基于行业研究的技术选型和评估方案
包含：引擎选择/服务器架构/性能优化/技术风险评估

数据来源：
- Unity 2025 技术内容回顾
- UE vs Unity 技术选型分析
- Unity 性能优化方案
"""

import json
from typing import Dict, List, Optional


class TechnicalAssessment:
    """游戏技术评估生成器"""
    
    # 引擎对比数据
    ENGINE_COMPARISON = {
        "unity": {
            "name": "Unity",
            "version": "Unity 6 (2025 LTS)",
            "strengths": [
                "移动端优化成熟",
                "学习曲线平缓",
                "Asset Store 生态丰富",
                "2D/3D 通吃",
                "国内团队使用率高 (70%+)",
                "招聘容易"
            ],
            "weaknesses": [
                "高端画面表现略逊 UE",
                "源码不开放",
                "大项目性能管理复杂"
            ],
            "best_for": ["手游", "独立游戏", "2D 游戏", "跨平台", "AR/VR"],
            "performance": {
                "mobile": "优秀",
                "pc": "良好",
                "console": "良好",
                "drawcall_optimization": "成熟方案",
                "memory_management": "需手动优化"
            },
            "cost": {
                "personal": "免费 (<$100K 收入)",
                "pro": "$2040/年/席位",
                "enterprise": "定制"
            }
        },
        "ue": {
            "name": "Unreal Engine",
            "version": "UE 5.4 (2025)",
            "strengths": [
                "画面表现顶级",
                "内置功能丰富",
                "源码开放",
                "Nanite/Lumen 等先进技术",
                "3A 级项目首选"
            ],
            "weaknesses": [
                "移动端包体较大",
                "学习曲线陡峭",
                "蓝图为王但 C++ 门槛高",
                "国内团队使用率低 (20%)"
            ],
            "best_for": ["3A 大作", "PC/主机", "FPS", "开放世界", "影视级画面"],
            "performance": {
                "mobile": "良好 (需优化)",
                "pc": "优秀",
                "console": "优秀",
                "drawcall_optimization": "自动优化优秀",
                "memory_management": "自动管理优秀"
            },
            "cost": {
                "royalty": "收入超$1M 后 5% 分成",
                "custom": "可谈买断"
            }
        },
        "cocos": {
            "name": "Cocos Creator",
            "version": "Cocos 3.8 (2025)",
            "strengths": [
                "轻量级",
                "Web 友好",
                "小游戏首选",
                "国内支持好",
                "完全免费"
            ],
            "weaknesses": [
                "3D 能力较弱",
                "生态不如 Unity/UE",
                "高端画面受限"
            ],
            "best_for": ["小游戏", "2D 手游", "Web 游戏", "H5"],
            "performance": {
                "mobile": "优秀 (轻量)",
                "pc": "良好",
                "console": "不支持",
                "drawcall_optimization": "自动合批优秀",
                "memory_management": "轻量级"
            },
            "cost": {
                "license": "完全免费"
            }
        }
    }
    
    # 服务器架构模板
    SERVER_ARCHITECTURES = {
        "single_player": {
            "name": "单机/弱联网",
            "description": "本地运算 + 云端存档/验证",
            "components": [
                "客户端逻辑",
                "云端存档服务",
                "反作弊验证",
                "排行榜服务"
            ],
            "tech_stack": {
                "backend": "Node.js/Python",
                "database": "MongoDB/Redis",
                "hosting": "AWS/Aliyun"
            },
            "cost": "低 ($500-2000/月)",
            "scalability": "低",
            "best_for": ["单机游戏", "弱联网游戏", "休闲游戏"]
        },
        "authoritative": {
            "name": "服务器权威",
            "description": "所有关键逻辑在服务器运算",
            "components": [
                "游戏服务器集群",
                "匹配服务",
                "玩家数据服务",
                "反作弊系统",
                "日志分析"
            ],
            "tech_stack": {
                "backend": "Go/C++/Java",
                "database": "MySQL/PostgreSQL + Redis",
                "hosting": "AWS/Aliyun/TencentCloud",
                "networking": "UDP/TCP 自定义"
            },
            "cost": "中 ($5000-20000/月)",
            "scalability": "高",
            "best_for": ["FPS", "MOBA", "竞技游戏", "强 PVP"]
        },
        "mmo": {
            "name": "MMO 架构",
            "description": "多服务器分区/分线",
            "components": [
                "网关服务器",
                "场景服务器集群",
                "数据库集群",
                "匹配/组队服务",
                "聊天服务",
                "交易系统",
                "反作弊系统"
            ],
            "tech_stack": {
                "backend": "C++/Go/Java",
                "database": "MySQL 集群 + Redis 集群 + MongoDB",
                "hosting": "多云架构",
                "networking": "自定义 TCP/UDP",
                "message_queue": "Kafka/RabbitMQ"
            },
            "cost": "高 ($20000-100000+/月)",
            "scalability": "极高",
            "best_for": ["MMORPG", "大型社交游戏", "开放世界"]
        },
        "hybrid": {
            "name": "混合架构",
            "description": "客户端运算 + 服务器验证",
            "components": [
                "游戏服务器",
                "验证服务",
                "玩家数据服务",
                "匹配服务",
                "反作弊"
            ],
            "tech_stack": {
                "backend": "Node.js/Go/Python",
                "database": "MySQL + Redis",
                "hosting": "AWS/Aliyun",
                "networking": "HTTP/WebSocket"
            },
            "cost": "中低 ($2000-10000/月)",
            "scalability": "中",
            "best_for": ["卡牌 RPG", "SLG", "中度联网游戏"]
        }
    }
    
    # 性能优化清单
    PERFORMANCE_CHECKLIST = {
        "rendering": [
            {"item": "Draw Call 优化", "target": "<100/帧", "impact": "高"},
            {"item": "三角形数量", "target": "<50K/帧", "impact": "高"},
            {"item": "Overdraw", "target": "<3x", "impact": "中"},
            {"item": "Shader 复杂度", "target": "移动端<100 指令", "impact": "高"},
            {"item": "光照优化", "target": "烘焙 + 实时混合", "impact": "中"}
        ],
        "cpu": [
            {"item": "Update 调用", "target": "避免每帧 Update", "impact": "高"},
            {"item": "GC 优化", "target": "避免运行时 GC", "impact": "高"},
            {"item": "物理计算", "target": "LOD+ 休眠", "impact": "中"},
            {"item": "AI 计算", "target": "分帧处理", "impact": "中"}
        ],
        "memory": [
            {"item": "内存占用", "target": "iOS<500MB, Android<800MB", "impact": "高"},
            {"item": "纹理压缩", "target": "ASTC/ETC2", "impact": "高"},
            {"item": "对象池", "target": "高频对象复用", "impact": "中"},
            {"item": "资源加载", "target": "异步加载+ 预加载", "impact": "中"}
        ],
        "network": [
            {"item": "带宽占用", "target": "<50KB/s/玩家", "impact": "高"},
            {"item": "延迟", "target": "<100ms (国内)", "impact": "高"},
            {"item": "同步频率", "target": "10-20Hz", "impact": "中"},
            {"item": "数据压缩", "target": "Protobuf/MessagePack", "impact": "中"}
        ]
    }
    
    # 团队规模建议
    TEAM_SIZE_RECOMMENDATIONS = {
        "indie": {
            "size": "1-10 人",
            "timeline": "6-18 个月",
            "budget": "50-500 万",
            "recommended_engine": "Unity/Cocos",
            "recommended_arch": "single_player/hybrid"
        },
        "mid": {
            "size": "10-50 人",
            "timeline": "12-36 个月",
            "budget": "500-3000 万",
            "recommended_engine": "Unity/UE",
            "recommended_arch": "hybrid/authoritative"
        },
        "aaa": {
            "size": "50-200+ 人",
            "timeline": "24-60 个月",
            "budget": "3000 万 -3 亿+",
            "recommended_engine": "UE/Unity",
            "recommended_arch": "mmo/authoritative"
        }
    }
    
    def __init__(self):
        self.tech_data = {}
    
    def generate_engine_recommendation(self, game_type: str, team_size: str, platform: str) -> Dict:
        """
        生成引擎推荐
        
        Args:
            game_type: 游戏类型
            team_size: 团队规模 (indie/mid/aaa)
            platform: 目标平台 (mobile/pc/console/cross)
        
        Returns:
            引擎推荐报告
        """
        recommendations = []
        
        for engine_key, engine_info in self.ENGINE_COMPARISON.items():
            score = self._calculate_engine_score(engine_key, game_type, team_size, platform)
            recommendations.append({
                "engine": engine_info["name"],
                "key": engine_key,
                "score": score,
                "match_reasons": self._get_match_reasons(engine_key, game_type, platform),
                "concerns": self._get_concerns(engine_key, game_type, platform),
                "cost_info": engine_info["cost"],
                "strengths": engine_info["strengths"][:3],
                "weaknesses": engine_info["weaknesses"][:2]
            })
        
        # 按分数排序
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "game_type": game_type,
            "team_size": team_size,
            "platform": platform,
            "recommendations": recommendations,
            "top_choice": recommendations[0] if recommendations else None
        }
    
    def _calculate_engine_score(self, engine_key: str, game_type: str, team_size: str, platform: str) -> int:
        """计算引擎匹配分数"""
        score = 50  # 基础分
        
        # 平台匹配
        platform_match = {
            "unity": {"mobile": 20, "pc": 10, "console": 10, "cross": 20},
            "ue": {"mobile": 5, "pc": 20, "console": 20, "cross": 15},
            "cocos": {"mobile": 20, "pc": 10, "console": 0, "cross": 15}
        }
        score += platform_match.get(engine_key, {}).get(platform, 0)
        
        # 游戏类型匹配
        type_match = {
            "unity": ["rpg", "casual", "moba", "fps"],
            "ue": ["fps", "rpg", "openworld"],
            "cocos": ["casual", "2d", "card"]
        }
        if game_type in type_match.get(engine_key, []):
            score += 15
        
        # 团队规模匹配
        team_match = {
            "unity": {"indie": 10, "mid": 10, "aaa": 5},
            "ue": {"indie": 0, "mid": 5, "aaa": 15},
            "cocos": {"indie": 15, "mid": 10, "aaa": 0}
        }
        score += team_match.get(engine_key, {}).get(team_size, 0)
        
        return min(score, 100)
    
    def _get_match_reasons(self, engine_key: str, game_type: str, platform: str) -> List[str]:
        """获取匹配原因"""
        reasons = []
        
        if engine_key == "unity":
            if platform == "mobile":
                reasons.append("移动端优化成熟，包体控制好")
            if game_type in ["rpg", "casual"]:
                reasons.append("该类型成功案例多，生态完善")
            reasons.append("国内团队使用率高，招聘容易")
        
        elif engine_key == "ue":
            if platform in ["pc", "console"]:
                reasons.append("PC/主机端画面表现顶级")
            if game_type in ["fps", "openworld"]:
                reasons.append("该类型 3A 级项目首选")
            reasons.append("源码开放，可深度定制")
        
        elif engine_key == "cocos":
            if platform == "mobile":
                reasons.append("轻量级，小游戏首选")
            reasons.append("完全免费，成本低")
            reasons.append("国内支持好，文档完善")
        
        return reasons[:3]
    
    def _get_concerns(self, engine_key: str, game_type: str, platform: str) -> List[str]:
        """获取关注点"""
        concerns = []
        
        if engine_key == "unity":
            concerns.append("大项目性能管理需提前规划")
            if platform == "pc":
                concerns.append("高端画面表现略逊于 UE")
        
        elif engine_key == "ue":
            if platform == "mobile":
                concerns.append("移动端包体较大，需优化")
            concerns.append("学习曲线陡峭，团队培训成本")
        
        elif engine_key == "cocos":
            if game_type in ["3d", "openworld"]:
                concerns.append("3D 能力相对较弱")
            concerns.append("生态不如 Unity/UE 丰富")
        
        return concerns[:2]
    
    def generate_server_architecture(self, game_type: str, expected_players: str) -> Dict:
        """
        生成服务器架构方案
        
        Args:
            game_type: 游戏类型
            expected_players: 预期玩家数 (small/medium/large)
        
        Returns:
            服务器架构方案
        """
        player_map = {
            "small": "<1 万 DAU",
            "medium": "1-10 万 DAU",
            "large": ">10 万 DAU"
        }
        
        # 根据游戏类型推荐架构
        arch_map = {
            "rpg": "hybrid",
            "moba": "authoritative",
            "fps": "authoritative",
            "slg": "hybrid",
            "casual": "single_player",
            "mmorpg": "mmo"
        }
        
        recommended_arch = arch_map.get(game_type, "hybrid")
        arch_info = self.SERVER_ARCHITECTURES[recommended_arch]
        
        return {
            "game_type": game_type,
            "expected_players": player_map.get(expected_players, "未知"),
            "recommended_architecture": {
                "name": arch_info["name"],
                "description": arch_info["description"],
                "components": arch_info["components"],
                "tech_stack": arch_info["tech_stack"],
                "cost": arch_info["cost"],
                "scalability": arch_info["scalability"]
            },
            "alternative_architectures": [
                {
                    "name": self.SERVER_ARCHITECTURES[k]["name"],
                    "description": self.SERVER_ARCHITECTURES[k]["description"],
                    "when_to_use": self._get_alternative_use_case(k, recommended_arch)
                }
                for k in self.SERVER_ARCHITECTURES.keys()
                if k != recommended_arch
            ][:2]
        }
    
    def _get_alternative_use_case(self, arch_key: str, recommended: str) -> str:
        """获取替代架构使用场景"""
        use_cases = {
            "single_player": "单机为主，仅需云端存档和验证",
            "authoritative": "强 PVP 竞技，需要服务器权威",
            "mmo": "大型多人在线，需要分区分线",
            "hybrid": "中度联网，平衡性能和成本"
        }
        return use_cases.get(arch_key, "")
    
    def generate_performance_checklist(self, platform: str) -> Dict:
        """
        生成性能优化清单
        
        Args:
            platform: 目标平台
        
        Returns:
            性能优化清单
        """
        platform_targets = {
            "mobile": {
                "drawcall": "<100/帧",
                "triangles": "<50K/帧",
                "memory": "<500MB (iOS), <800MB (Android)",
                "fps": "稳定 60FPS",
                "loading": "冷启动<5 秒"
            },
            "pc": {
                "drawcall": "<200/帧",
                "triangles": "<200K/帧",
                "memory": "<2GB",
                "fps": "稳定 60-144FPS",
                "loading": "冷启动<10 秒"
            },
            "console": {
                "drawcall": "<300/帧",
                "triangles": "<500K/帧",
                "memory": "<4GB",
                "fps": "稳定 60FPS (30FPS for AAA)",
                "loading": "SSD<3 秒"
            }
        }
        
        targets = platform_targets.get(platform, platform_targets["mobile"])
        
        return {
            "platform": platform,
            "performance_targets": targets,
            "rendering_optimization": self.PERFORMANCE_CHECKLIST["rendering"],
            "cpu_optimization": self.PERFORMANCE_CHECKLIST["cpu"],
            "memory_optimization": self.PERFORMANCE_CHECKLIST["memory"],
            "network_optimization": self.PERFORMANCE_CHECKLIST["network"] if platform != "single" else []
        }
    
    def generate_technical_report(self, game_type: str, team_size: str, platform: str, expected_players: str) -> str:
        """
        生成完整技术评估报告
        
        Args:
            game_type: 游戏类型
            team_size: 团队规模
            platform: 目标平台
            expected_players: 预期玩家数
        
        Returns:
            完整报告（Markdown 格式）
        """
        engine_rec = self.generate_engine_recommendation(game_type, team_size, platform)
        server_arch = self.generate_server_architecture(game_type, expected_players)
        perf_checklist = self.generate_performance_checklist(platform)
        
        report = f"""# 游戏技术评估报告

**游戏类型**: {game_type.upper()}
**团队规模**: {team_size}
**目标平台**: {platform}
**预期玩家**: {server_arch['expected_players']}
**生成时间**: 2026-04-15

---

## 一、引擎推荐

### 🏆 首选引擎：{engine_rec['top_choice']['engine']}

**匹配分数**: {engine_rec['top_choice']['score']}/100

**推荐理由**:
"""
        for reason in engine_rec['top_choice']['match_reasons']:
            report += f"- ✅ {reason}\n"
        
        report += f"""
**核心优势**:
"""
        for strength in engine_rec['top_choice']['strengths']:
            report += f"- {strength}\n"
        
        report += f"""
**需关注**:
"""
        for concern in engine_rec['top_choice']['concerns']:
            report += f"- ⚠️ {concern}\n"
        
        report += f"""
**成本**: {engine_rec['top_choice']['cost_info']}

---

### 其他候选引擎

"""
        for i, rec in enumerate(engine_rec['recommendations'][1:], 2):
            report += f"""#### {i}. {rec['engine']} (分数：{rec['score']}/100)
- **优势**: {', '.join(rec['strengths'])}
- **劣势**: {', '.join(rec['weaknesses'])}
- **成本**: {rec['cost_info']}

"""
        
        report += f"""## 二、服务器架构方案

### 推荐架构：{server_arch['recommended_architecture']['name']}

**描述**: {server_arch['recommended_architecture']['description']}

**核心组件**:
"""
        for component in server_arch['recommended_architecture']['components']:
            report += f"- {component}\n"
        
        report += f"""
**技术栈**:
"""
        for tech, value in server_arch['recommended_architecture']['tech_stack'].items():
            report += f"- **{tech}**: {value}\n"
        
        report += f"""
**成本估算**: {server_arch['recommended_architecture']['cost']}
**扩展性**: {server_arch['recommended_architecture']['scalability']}

---

## 三、性能优化目标

### 平台目标 ({platform})

| 指标 | 目标值 |
|---|---|
"""
        for metric, target in perf_checklist['performance_targets'].items():
            report += f"| **{metric}** | {target} |\n"
        
        report += f"""
### 渲染优化

| 项目 | 目标 | 影响 |
|---|---|---|
"""
        for item in perf_checklist['rendering_optimization']:
            report += f"| {item['item']} | {item['target']} | {item['impact']} |\n"
        
        report += f"""
### CPU 优化

| 项目 | 目标 | 影响 |
|---|---|---|
"""
        for item in perf_checklist['cpu_optimization']:
            report += f"| {item['item']} | {item['target']} | {item['impact']} |\n"
        
        report += f"""
### 内存优化

| 项目 | 目标 | 影响 |
|---|---|---|
"""
        for item in perf_checklist['memory_optimization']:
            report += f"| {item['item']} | {item['target']} | {item['impact']} |\n"
        
        report += f"""
---

## 四、团队配置建议

"""
        team_info = self.TEAM_SIZE_RECOMMENDATIONS.get(team_size, {})
        if team_info:
            report += f"""| 维度 | 建议 |
|---|---|
| **团队规模** | {team_info['size']} |
| **开发周期** | {team_info['timeline']} |
| **预算范围** | {team_info['budget']} |
| **推荐引擎** | {team_info['recommended_engine']} |
| **推荐架构** | {team_info['recommended_arch']} |

"""
        
        report += """---

*本报告基于 Unity 2025 技术内容回顾、UE vs Unity 技术选型分析、行业性能优化实践生成*
*数据来源：官方文档 + 行业研究 + 实战经验*
"""
        
        return report


def main():
    """主函数"""
    import sys
    
    tech = TechnicalAssessment()
    
    if len(sys.argv) < 2:
        print("用法：python3 technical_assessment.py [game_type] [team_size] [platform] [players]")
        print("示例：python3 technical_assessment.py rpg mid mobile medium")
        print("\n支持的游戏类型：rpg, moba, fps, slg, casual, mmorpg")
        print("团队规模：indie, mid, aaa")
        print("目标平台：mobile, pc, console, cross")
        print("预期玩家：small, medium, large")
        sys.exit(1)
    
    game_type = sys.argv[1]
    team_size = sys.argv[2] if len(sys.argv) > 2 else "mid"
    platform = sys.argv[3] if len(sys.argv) > 3 else "mobile"
    expected_players = sys.argv[4] if len(sys.argv) > 4 else "medium"
    
    # 生成报告
    report = tech.generate_technical_report(game_type, team_size, platform, expected_players)
    print(report)


if __name__ == "__main__":
    main()
