#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 策划案生成器
支持世界观/系统/数值/关卡/剧情等完整策划案生成

使用 OpenClaw 默认模型，无需单独配置 API Key
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, Optional
from datetime import datetime

# 不再硬编码 API Key 和模型
# 使用 OpenClaw 默认模型配置

# 策划案模板
TEMPLATES = {
    'worldview': {
        'title': '世界观策划案',
        'sections': [
            '1. 世界概述（名称/核心概念/故事背景）',
            '2. 世界架构（九重天/大陆/国家/城市）',
            '3. 历史年表（重大事件/时间线）',
            '4. 种族设定（主要种族/特点/文化）',
            '5. 势力架构（主要势力/关系图）',
            '6. 地理生态（气候/资源/异兽）',
            '7. 文化体系（宗教/语言/习俗）',
            '8. 魔法/科技体系（能量来源/规则）'
        ]
    },
    'system': {
        'title': '系统策划案',
        'sections': [
            '1. 系统概述（设计目标/核心玩法/用户流程）',
            '2. 功能设计（功能列表/详细规则/界面原型）',
            '3. 玩法规则（核心循环/操作方式/胜利条件）',
            '4. 数值设计（核心公式/参数配置/成长曲线）',
            '5. 接口定义（数据结构/API 接口）',
            '6. UI/UX设计（界面布局/交互流程）',
            '7. 程序需求（技术要点/依赖系统）',
            '8. 美术需求（风格/规格/数量清单）'
        ]
    },
    'numeric': {
        'title': '数值策划案',
        'sections': [
            '1. 数值框架（核心属性/次要属性）',
            '2. 成长曲线（升级经验/属性成长）',
            '3. 战斗公式（伤害计算/命中闪避）',
            '4. 经济系统（货币产出/消耗/通胀控制）',
            '5. 装备系统（品质/强化/镶嵌）',
            '6. 技能系统（技能伤害/冷却/消耗）',
            '7. 配置表模板（CSV 格式）',
            '8. 平衡性分析（职业对比/PVP/PVE）'
        ]
    },
    'level': {
        'title': '关卡策划案',
        'sections': [
            '1. 关卡概述（主题/目标/时长）',
            '2. 关卡流程（路线图/节奏设计）',
            '3. 敌人配置（类型/数量/刷新点）',
            '4. 掉落设计（装备/材料/概率）',
            '5. 机关谜题（类型/解法/奖励）',
            '6. BOSS 设计（技能/机制/攻略）',
            '7. 难度曲线（动态难度/适配等级）',
            '8. 场景需求（地图/建筑/特效）'
        ]
    },
    'story': {
        'title': '剧情策划案',
        'sections': [
            '1. 故事概述（主题/基调/核心冲突）',
            '2. 主线剧情（章节大纲/关键节点）',
            '3. 角色剧情（角色背景/成长弧线）',
            '4. 支线剧情（支线列表/触发条件）',
            '5. 对话文本（关键对话/分支选项）',
            '6. 演出设计（CG/动画/分镜）',
            '7. 任务设计（任务目标/流程/奖励）',
            '8. 世界观关联（与主线/设定的联系）'
        ]
    }
}


class GameDesignGenerator:
    """游戏策划案生成器 - 使用 OpenClaw 默认模型"""
    
    def __init__(self):
        # 不再需要 API Key 和模型配置
        # 使用 OpenClaw 默认模型
        pass
    
    def generate(self, doc_type: str, topic: str, details: str = '', 
                 word_count: int = 5000) -> str:
        """
        生成策划案
        
        Args:
            doc_type: 文档类型 (worldview/system/numeric/level/story)
            topic: 主题（如"战斗系统"、"九重天世界观"）
            details: 详细要求
            word_count: 目标字数
        
        Returns:
            生成的策划案
        """
        if doc_type not in TEMPLATES:
            return f"错误：不支持的文档类型 {doc_type}，支持：{list(TEMPLATES.keys())}"
        
        template = TEMPLATES[doc_type]
        
        # 构建提示词
        prompt = self._build_prompt(template, topic, details, word_count)
        
        # 使用 OpenClaw 默认模型生成
        response = self._call_openclaw_llm(prompt)
        
        return response
    
    def _call_openclaw_llm(self, prompt: str) -> str:
        """
        调用 OpenClaw 默认 LLM
        
        优势：
        - 无需单独配置 API Key
        - 自动使用 OpenClaw 默认模型（如 dashscope/qwen3.5-plus）
        - 支持模型切换（/model 命令）
        - 统一用量统计
        
        Args:
            prompt: 提示词
        
        Returns:
            LLM 生成结果
        """
        # 通过 OpenClaw 的 message 工具或 sessions_send 调用 LLM
        # 这里使用 subprocess 调用 openclaw 命令
        
        try:
            # 方法 1: 使用 openclaw 命令行工具（如果可用）
            # result = subprocess.run(
            #     ['openclaw', 'chat', '--prompt', prompt],
            #     capture_output=True, text=True, timeout=120
            # )
            # return result.stdout
            
            # 方法 2: 直接返回提示词，让 OpenClaw 处理（当前实现）
            # 实际使用时会通过 OpenClaw 的工具系统调用
            return self._generate_via_openclaw_tool(prompt)
            
        except Exception as e:
            return f"调用 OpenClaw LLM 失败：{e}"
    
    def _generate_via_openclaw_tool(self, prompt: str) -> str:
        """
        通过 OpenClaw 工具系统生成内容
        
        这是推荐方式，完全集成到 OpenClaw 生态
        """
        # 在实际 OpenClaw 插件中，这里会调用:
        # await this.context.callTool('llm', { prompt })
        
        # 当前作为独立脚本，返回提示词供 OpenClaw 处理
        return f"[OpenClaw LLM 调用]\n提示词：{prompt[:500]}...\n\n请调用 OpenClaw LLM 工具生成完整内容"


def main():
    """命令行接口"""
    if len(sys.argv) < 3:
        print("Usage: python generator.py <type> <topic> [details]")
        print("Types: worldview, system, numeric, level, story")
        print("Example: python generator.py system 战斗系统 包含三人小队和职业系统")
        sys.exit(1)
    
    doc_type = sys.argv[1]
    topic = sys.argv[2]
    details = sys.argv[3] if len(sys.argv) > 3 else ''
    
    generator = GameDesignGenerator()
    
    print(f"正在生成 {TEMPLATES.get(doc_type, {}).get('title', doc_type)}...")
    print(f"主题：{topic}")
    print("-" * 60)
    
    result = generator.generate(doc_type, topic, details, word_count=5000)
    
    print(result)
    
    # 保存到文件
    output_file = f"{doc_type}_{topic.replace(' ', '_')}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"\n已保存到：{output_file}")


if __name__ == '__main__':
    main()
