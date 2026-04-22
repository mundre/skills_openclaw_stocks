#!/usr/bin/env python3
"""
Smart Extraction - 智能记忆提取
使用 LLM 从原始文本中提取结构化记忆
"""

import os
import sys
import json
import requests
from typing import Dict, Any, Optional, List


class SmartExtractor:
    """智能提取器"""
    
    # 简单分类规则
    CATEGORY_KEYWORDS = {
        '人物': ['喜欢', '爱', '是', '叫', '名字', '身份', '职业'],
        '偏好': ['喜欢', '爱', '讨厌', '经常', '每天', '习惯'],
        '事件': ['发生', '遇到', '做了', '参加', '会议', '活动'],
        '知识': ['是', '有', '包括', '定义', '原理', '规则'],
        '地点': ['在', '地方', '位置', '地址', '城市'],
        '时间': ['时间', '时候', '年', '月', '日', '点']
    }
    
    def __init__(self, config: Dict[str, Any]):
        self.llm_config = config.get('llm', {})
        self.provider = self.llm_config.get('provider', 'siliconflow')
        self.api_key = self.llm_config.get('apiKey', os.environ.get('SILICONFLOW_API_KEY', 'sk-moxcmniwcppdgdxvyriwxcsqapldaskxcdhhsagfyaujqzep'))
        self.model = self.llm_config.get('model', 'Qwen/Qwen2.5-7B-Instruct')
        self.base_url = self.llm_config.get('baseURL', 'https://api.siliconflow.cn/v1')
    
    def extract(self, text: str) -> Dict[str, Any]:
        """
        从文本中提取结构化记忆
        
        返回：
        {
            "summary": "一句话摘要",
            "category": "分类（人物/事件/知识/偏好/其他）",
            "keywords": ["关键词 1", "关键词 2"],
            "importance": 0.5  # 重要性 0-1
        }
        """
        # 尝试用 LLM 提取，失败则 fallback 到规则提取
        try:
            return self._call_llm(text)
        except Exception as e:
            print(f"LLM 提取失败：{e}，使用规则提取 fallback")
            return self._rule_based_extract(text)
    
    def _call_llm(self, text: str) -> Dict[str, Any]:
        """调用 LLM API（SiliconFlow/Jina）"""
        prompt = f"""请从以下文本中提取关键信息，以 JSON 格式返回：

文本：{text[:2000]}

请提取：
1. summary: 一句话摘要（20 字以内）
2. category: 分类（从以下选择：人物、事件、知识、偏好、地点、时间、其他）
3. keywords: 3-5 个关键词
4. importance: 重要性评分（0-1 之间，0.5 为中等）

只返回 JSON，不要其他内容。格式：
{{
  "summary": "...",
  "category": "...",
  "keywords": ["...", "..."],
  "importance": 0.5
}}
"""
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': '你是一个记忆提取助手，负责从文本中提取结构化信息。只返回 JSON。'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3,
            'max_tokens': 300
        }
        
        response = requests.post(
            f'{self.base_url}/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f'LLM API error: {response.status_code} - {response.text}')
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        return self._parse_json(content)
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': '你是一个记忆提取助手，负责从文本中提取结构化信息。只返回 JSON。'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3,
            'max_tokens': 300
        }
        
        # DashScope 使用不同的端点
        url = f'{self.base_url}/chat/completions' if 'dashscope' in self.base_url else f'{self.base_url}/chat/completions'
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f'LLM API error: {response.status_code} - {response.text}')
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # 解析 JSON
        return self._parse_json(content)
    
    def _call_ollama(self, prompt: str) -> Dict[str, Any]:
        """调用本地 Ollama"""
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            'model': self.model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.3
            }
        }
        
        response = requests.post(
            f'{self.base_url}/api/generate',
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f'Ollama error: {response.status_code} - {response.text}')
        
        result = response.json()
        content = result.get('response', '')
        
        return self._parse_json(content)
    
    def _parse_json(self, content: str) -> Dict[str, Any]:
        """解析 JSON 响应"""
        # 清理可能的 markdown 标记
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        try:
            return json.loads(content)
        except:
            # 解析失败，返回默认值
            return {
                'summary': content[:50],
                'category': '其他',
                'keywords': [],
                'importance': 0.5
            }
    
    def _rule_based_extract(self, text: str) -> Dict[str, Any]:
        """基于规则的简化提取"""
        import re
        
        # 1. 摘要（取前 30 字）
        summary = text[:30] + '...' if len(text) > 30 else text
        
        # 2. 分类（关键词匹配）
        category = '其他'
        max_count = 0
        for cat, keywords in self.CATEGORY_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in text)
            if count > max_count:
                max_count = count
                category = cat
        
        # 3. 关键词（简单分词：按标点分割）
        words = re.split(r'[，。,.:;：；\s]+', text)
        # 过滤短词和停用词
        stopwords = ['的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个']
        keywords = [w for w in words if len(w) >= 2 and w not in stopwords][:5]
        
        # 4. 重要性（基于关键词）
        importance = 0.5
        if any(kw in text for kw in ['重要', '必须', '一定', '千万']):
            importance = 0.8
        elif any(kw in text for kw in ['可能', '也许', '大概']):
            importance = 0.3
        
        return {
            'summary': summary,
            'category': category,
            'keywords': keywords,
            'importance': importance
        }


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python smart_extract.py <text>")
        sys.exit(1)
    
    text = ' '.join(sys.argv[1:])
    
    # 从配置文件加载 LLM 配置
    config_file = os.path.expanduser('~/.openclaw/data/memory-custom-config.json')
    config = {}
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    # 默认 LLM 配置（如果没有配置）
    if 'llm' not in config:
        config['llm'] = {
            'provider': 'openai',
            'apiKey': os.environ.get('OPENAI_API_KEY', ''),
            'model': 'gpt-4o-mini',
            'baseURL': 'https://api.openai.com/v1'
        }
    
    extractor = SmartExtractor(config)
    
    try:
        result = extractor.extract(text)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({
            'error': str(e),
            'summary': text[:50],
            'category': '其他',
            'keywords': [],
            'importance': 0.5
        }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
