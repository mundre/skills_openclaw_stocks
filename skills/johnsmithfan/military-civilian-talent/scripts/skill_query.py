#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
军地两用人才技能查询脚本

功能：
1. 按领域查询技能知识
2. 按难度级别提供指导
3. 相关技能推荐

用法：
    python skill_query.py --domain military --topic "打坦克" --level basic
"""

import argparse
import json
import sys

# 知识领域数据库
KNOWLEDGE_DOMAINS = {
    "military": {
        "name": "军事知识",
        "topics": ["打坦克", "打飞机", "进攻战斗", "防御战斗", "地形利用", "夜间战斗"],
        "reference": "military.md"
    },
    "agriculture": {
        "name": "农业知识",
        "topics": ["土壤改良", "种子选育", "肥料施用", "小麦种植", "水稻种植", "蔬菜种植"],
        "reference": "agriculture.md"
    },
    "rural-business": {
        "name": "农村副业",
        "topics": ["养猪", "养鸡", "养鱼", "果树种植", "药材种植", "粮食加工"],
        "reference": "rural-business.md"
    },
    "machinery": {
        "name": "机械知识",
        "topics": ["拖拉机维修", "电动机维修", "柴油机保养", "水泵使用", "农机操作"],
        "reference": "machinery.md"
    },
    "construction": {
        "name": "建筑知识",
        "topics": ["房屋建造", "基础施工", "墙体砌筑", "施工技术"],
        "reference": "construction.md"
    },
    "electrical": {
        "name": "电器知识",
        "topics": ["家电维修", "电路安装", "电器故障排除"],
        "reference": "electrical.md"
    },
    "photography": {
        "name": "摄影入门",
        "topics": ["相机使用", "曝光控制", "构图技巧", "光线运用"],
        "reference": "photography.md"
    },
    "cooking": {
        "name": "烹调技艺",
        "topics": ["红烧肉", "炒糖色", "家常菜", "腌制品", "刀工", "调味"],
        "reference": "cooking.md"
    },
    "accounting": {
        "name": "会计知识",
        "topics": ["基础会计", "记账方法", "凭证填制", "报表编制"],
        "reference": "accounting.md"
    },
    "management": {
        "name": "管理知识",
        "topics": ["计划管理", "组织管理", "生产管理", "质量管理"],
        "reference": "management.md"
    }
}

# 学习级别说明
LEVELS = {
    "basic": {
        "name": "初级",
        "description": "适合初学者，提供基础知识和入门指导"
    },
    "intermediate": {
        "name": "中级",
        "description": "适合有基础者，提供进阶技巧和实践指导"
    },
    "advanced": {
        "name": "高级",
        "description": "适合熟练者，提供专业知识和高级技巧"
    }
}


def query_knowledge(domain, topic, level="basic"):
    """
    查询知识
    """
    result = {
        "输入参数": {
            "领域": domain,
            "主题": topic,
            "级别": level
        },
        "查询结果": {
            "领域名称": "",
            "主题列表": [],
            "参考文件": "",
            "学习建议": []
        }
    }
    
    if domain in KNOWLEDGE_DOMAINS:
        domain_info = KNOWLEDGE_DOMAINS[domain]
        result["查询结果"]["领域名称"] = domain_info["name"]
        result["查询结果"]["主题列表"] = domain_info["topics"]
        result["查询结果"]["参考文件"] = domain_info["reference"]
        
        if level in LEVELS:
            result["查询结果"]["学习建议"] = [
                f"建议从{LEVELS[level]['name']}开始学习",
                LEVELS[level]["description"],
                "详细内容请参考对应的参考文件"
            ]
    else:
        result["查询结果"]["学习建议"] = [
            f"未找到领域: {domain}",
            "可用领域: " + ", ".join(KNOWLEDGE_DOMAINS.keys())
        ]
    
    return result


def list_domains():
    """
    列出所有知识领域
    """
    result = {
        "知识领域列表": []
    }
    
    for key, info in KNOWLEDGE_DOMAINS.items():
        result["知识领域列表"].append({
            "代码": key,
            "名称": info["name"],
            "主题数量": len(info["topics"]),
            "参考文件": info["reference"]
        })
    
    return result


def main():
    parser = argparse.ArgumentParser(description="军地两用人才技能查询工具")
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # 查询命令
    query_parser = subparsers.add_parser("query", help="查询知识")
    query_parser.add_argument("--domain", required=True, help="知识领域")
    query_parser.add_argument("--topic", help="具体主题")
    query_parser.add_argument("--level", choices=["basic", "intermediate", "advanced"], 
                             default="basic", help="学习级别")
    
    # 列表命令
    list_parser = subparsers.add_parser("list", help="列出知识领域")
    
    args = parser.parse_args()
    
    if args.command == "query":
        result = query_knowledge(args.domain, args.topic, args.level)
    elif args.command == "list":
        result = list_domains()
    else:
        parser.print_help()
        return
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
