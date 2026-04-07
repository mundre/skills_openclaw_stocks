#!/usr/bin/env python3
"""
招标文件解析脚本
输入：招标文件PDF路径或粘贴的文字
输出：招标概览结构化数据（JSON/飞书卡片）
"""

import sys
import json

def parse_bid_document(text):
    """
    解析招标文件文本，提取关键信息
    这里使用规则+关键词匹配，实际可调用LLM API
    """
    result = {
        "项目信息": {
            "项目名称": "（待解析）",
            "招标人": "（待解析）",
            "工程地点": "（待解析）",
            "投资金额": "（待解析）"
        },
        "资质门槛": {
            "企业资质": "（待解析）",
            "项目经理资格": "（待解析）",
            "安全生产许可证": "是/否",
            "类似业绩要求": "（待解析）"
        },
        "评标办法": {
            "评标方法": "（待解析）",
            "技术分权重": "（待解析）%",
            "商务分权重": "（待解析）%",
            "价格分权重": "（待解析）%"
        },
        "关键时间": {
            "投标截止": "（待解析）",
            "开标时间": "（待解析）",
            "工期要求": "（待解析）"
        }
    }
    return result

def main():
    input_text = sys.argv[1] if len(sys.argv) > 1 else ""
    if not input_text:
        print("Error: No input text provided")
        sys.exit(1)
    
    parsed = parse_bid_document(input_text)
    print(json.dumps(parsed, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
