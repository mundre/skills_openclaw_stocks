#!/usr/bin/env python3
"""
Game-Design-Pro - 策划案评审器
提供完整性检查、一致性验证、风险识别、优化建议
"""

import os
import sys
import json
import requests
from typing import Dict, Any, List
from datetime import datetime

# 配置
SILICONFLOW_API_KEY = os.environ.get('SILICONFLOW_API_KEY', 'sk-moxcmniwcppdgdxvyriwxcsqapldaskxcdhhsagfyaujqzep')
SILICONFLOW_BASE_URL = 'https://api.siliconflow.cn/v1'
LLM_MODEL = 'Qwen/Qwen2.5-72B-Instruct'


class GameDesignReviewer:
    """游戏策划案评审器"""
    
    def __init__(self):
        self.api_key = SILICONFLOW_API_KEY
        self.base_url = SILICONFLOW_BASE_URL
        self.model = LLM_MODEL
    
    def review(self, content: str, doc_type: str = 'system') -> Dict[str, Any]:
        """
        评审策划案
        
        Args:
            content: 策划案内容
            doc_type: 文档类型
        
        Returns:
            评审报告
        """
        prompt = self._build_review_prompt(content, doc_type)
        response = self._call_llm(prompt)
        
        # 解析评审结果
        report = self._parse_report(response)
        return report
    
    def _build_review_prompt(self, content: str, doc_type: str) -> str:
        """构建评审提示词"""
        prompt = f"""你是一位资深游戏策划评审专家，有 10 年商业项目评审经验。

请评审以下游戏策划案，类型：{doc_type}

## 策划案内容：
{content[:15000]}  # 限制长度

## 评审维度：

### 1. 完整性检查（30 分）
- 是否包含所有必要章节
- 关键信息是否遗漏
- 是否有明确的验收标准

### 2. 一致性检查（25 分）
- 世界观设定是否自洽
- 数值系统是否平衡
- 系统设计是否闭环

### 3. 可行性分析（20 分）
- 技术实现难度
- 开发成本评估
- 时间周期合理性

### 4. 创新性评估（15 分）
- 玩法创新点
- 差异化竞争优势
- 市场定位清晰度

### 5. 风险识别（10 分）
- 技术风险
- 设计风险
- 商业风险

## 输出格式：
```markdown
## 策划案评审报告

### 综合评分：XX/100

### ✅ 优点（至少 3 条）
1. ...
2. ...
3. ...

### ⚠️ 问题与风险（按严重程度排序）
1. 【高风险】...
2. 【中风险】...
3. 【低风险】...

### 💡 优化建议（至少 5 条具体建议）
1. ...
2. ...
3. ...

### 📊 竞品对比
- 与 XXX 游戏对比：...

### 📋 修改优先级
- P0（必须修改）：...
- P1（建议修改）：...
- P2（可选优化）：...
```

请开始评审：
"""
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """调用 LLM API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': '你是一位资深游戏策划评审专家，擅长发现设计问题并提供建设性意见。'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.5,
            'max_tokens': 4096
        }
        
        response = requests.post(
            f'{self.base_url}/chat/completions',
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            return f"API 错误：{response.status_code}"
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def _parse_report(self, response: str) -> Dict[str, Any]:
        """解析评审报告（简化版）"""
        return {
            'raw_report': response,
            'timestamp': datetime.now().isoformat()
        }


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python reviewer.py <input_file> [doc_type]")
        print("Example: python reviewer.py combat_design.md system")
        sys.exit(1)
    
    input_file = sys.argv[1]
    doc_type = sys.argv[2] if len(sys.argv) > 2 else 'system'
    
    # 读取策划案
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    reviewer = GameDesignReviewer()
    
    print(f"正在评审 {input_file}...")
    print("-" * 60)
    
    report = reviewer.review(content, doc_type)
    
    print(report['raw_report'])
    
    # 保存评审报告
    output_file = f"review_{os.path.basename(input_file)}"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report['raw_report'])
    
    print(f"\n评审报告已保存到：{output_file}")


if __name__ == '__main__':
    main()
