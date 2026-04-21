#!/usr/bin/env python3
"""
会议智能纪要助手
录音转文字 → 生成纪要 → 提取待办 → 同步飞书
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

import requests


def transcribe_audio(audio_path: str, provider: str = 'volcano') -> Dict:
    """
    音频转文字
    
    Args:
        audio_path: 音频文件路径
        provider: ASR提供商 (local/volcano/siliconflow)
        
    Returns:
        {
            'text': 完整转写文本,
            'segments': 分段结果（含时间戳、说话人）,
            'duration': 音频时长（秒）
        }
    """
    if not os.path.exists(audio_path):
        return {'error': f'音频文件不存在: {audio_path}'}
    
    # 检查文件格式
    ext = Path(audio_path).suffix.lower()
    if ext not in ['.mp3', '.wav', '.m4a', '.mp4', '.wma']:
        return {'error': f'不支持的音频格式: {ext}，请使用 MP3/WAV/M4A'}
    
    # 获取文件大小
    file_size = os.path.getsize(audio_path)
    if file_size > 500 * 1024 * 1024:  # 500MB
        return {'error': '音频文件过大（>500MB），请分段上传'}
    
    # 模拟转写结果（实际需接入ASR API）
    # 这里返回模拟数据，实际实现需要调用火山/硅基流动等API
    
    print(f"🎤 正在转写: {os.path.basename(audio_path)} ({file_size/1024/1024:.1f}MB)")
    print(f"   使用ASR: {provider}")
    
    # 模拟分段结果
    mock_segments = [
        {'speaker': '发言人A', 'text': '大家好，我们今天讨论一下Q2的产品规划。', 'start': 0, 'end': 5},
        {'speaker': '发言人B', 'text': '我先说一下技术方面的准备情况。', 'start': 6, 'end': 10},
        {'speaker': '发言人A', 'text': '好的，请讲。', 'start': 11, 'end': 12},
    ]
    
    full_text = '\n'.join([f"[{s['speaker']}] {s['text']}" for s in mock_segments])
    
    return {
        'text': full_text,
        'segments': mock_segments,
        'duration': 300,  # 5分钟模拟
        'provider': provider,
        'audio_file': audio_path
    }


def generate_minutes(transcription: Dict) -> Dict:
    """
    根据转写文本生成结构化纪要
    
    策略：
    1. 识别会议主题（首段内容）
    2. 提取关键讨论点（基于关键词密度）
    3. 识别决策结论（"决定"/"确认"/"通过"等）
    4. 提取待办事项（"TODO"/"待办"/"负责"等）
    """
    text = transcription.get('text', '')
    segments = transcription.get('segments', [])
    
    if not text:
        return {'error': '转写文本为空'}
    
    # 提取主题（简单启发式：第一段或含"会议"/"讨论"/"议题"的句子）
    lines = text.split('\n')
    topic = "会议讨论"
    for line in lines[:5]:
        if any(kw in line for kw in ['会议', '讨论', '议题', '规划', '复盘']):
            topic = line.strip()[:50]
            break
    
    # 提取关键讨论点（含关键词的句子）
    key_points = []
    keywords = ['进度', '问题', '风险', '方案', '计划', '目标', '预算', '资源']
    for line in lines:
        for kw in keywords:
            if kw in line and len(line) > 10:
                key_points.append(line.strip())
                break
    
    # 去重并限制数量
    key_points = list(dict.fromkeys(key_points))[:8]
    
    # 提取决策结论
    decisions = []
    decision_patterns = [
        r'(决定|确认|通过|同意|确定).*?(?:。|$)',
        r'.*?((?:采用|选择|定为).{2,20}?)(?:。|$)',
    ]
    for line in lines:
        for pattern in decision_patterns:
            matches = re.findall(pattern, line)
            decisions.extend(matches)
    decisions = list(dict.fromkeys(decisions))[:5]
    
    # 提取待办事项
    todos = extract_todos(text)
    
    # 生成纪要文本
    minutes_text = f"""# 会议纪要

## 📋 基本信息
- **会议主题**: {topic}
- **会议时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- **音频时长**: {transcription.get('duration', 0)//60}分钟
- **转写引擎**: {transcription.get('provider', 'unknown')}

## 📝 会议内容

### 关键讨论点
{chr(10).join(['- ' + p for p in key_points]) if key_points else '- （未识别到明确讨论点）'}

### 决策结论
{chr(10).join(['✓ ' + d for d in decisions]) if decisions else '- （未识别到明确决策）'}

## ✅ 待办事项

{format_todos(todos) if todos else '无明确待办事项'}

## 📄 完整转写

<details>
<summary>点击查看完整转写文本</summary>

{text}

</details>

---
*由 cn-meeting-minutes 自动生成*
"""
    
    return {
        'topic': topic,
        'key_points': key_points,
        'decisions': decisions,
        'todos': todos,
        'minutes_text': minutes_text,
        'duration': transcription.get('duration', 0),
        'word_count': len(text)
    }


def extract_todos(text: str) -> List[Dict]:
    """
    从文本中提取待办事项
    
    识别模式：
    - "TODO: xxx"
    - "待办：xxx"
    - "xxx 负责 xxx"
    - "xxx 跟进 xxx"
    """
    todos = []
    lines = text.split('\n')
    
    todo_patterns = [
        r'(?:TODO|待办|待处理|待确认)[：:]\s*(.+)',
        r'(.{2,10})(?:负责|跟进|落实|确认|完成)(.{3,30})',
        r'(下周|明天|本周|月底前).*?(完成|确认|提交|评审)(.{2,20})',
    ]
    
    for line in lines:
        for pattern in todo_patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                if isinstance(match, tuple):
                    todo_text = ' '.join(match)
                else:
                    todo_text = match
                
                # 提取责任人（简单启发式）
                assignee = ''
                name_match = re.search(r'([\u4e00-\u9fa5]{2,4})(?:负责|跟进)', line)
                if name_match:
                    assignee = name_match.group(1)
                
                # 提取截止日期
                deadline = ''
                if '明天' in line:
                    deadline = '明天'
                elif '下周' in line:
                    deadline = '下周'
                elif '月底' in line:
                    deadline = '月底前'
                
                todos.append({
                    'task': todo_text.strip()[:100],
                    'assignee': assignee,
                    'deadline': deadline,
                    'source_line': line.strip()[:80]
                })
    
    # 去重
    seen = set()
    unique_todos = []
    for t in todos:
        key = t['task']
        if key not in seen:
            seen.add(key)
            unique_todos.append(t)
    
    return unique_todos[:10]  # 最多10条


def format_todos(todos: List[Dict]) -> str:
    """格式化待办列表为Markdown"""
    if not todos:
        return ''
    
    result = []
    for i, t in enumerate(todos, 1):
        assignee_str = f" @{t['assignee']}" if t['assignee'] else ''
        deadline_str = f" (截止: {t['deadline']})" if t['deadline'] else ''
        result.append(f"{i}. [ ] {t['task']}{assignee_str}{deadline_str}")
    
    return '\n'.join(result)


def save_to_feishu(minutes: Dict, folder_token: str = None) -> Dict:
    """保存纪要到飞书文档"""
    # 简化实现，实际需要调用飞书API
    return {
        'success': True,
        'message': '已生成飞书文档（模拟）',
        'doc_url': 'https://feishu.cn/docx/mock_meeting_minutes'
    }


def main():
    parser = argparse.ArgumentParser(description='会议智能纪要助手')
    parser.add_argument('audio_path', help='音频文件路径')
    parser.add_argument('--asr', choices=['local', 'volcano', 'siliconflow'],
                       default='volcano', help='ASR提供商')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--feishu', action='store_true', help='同步到飞书')
    
    args = parser.parse_args()
    
    # 1. 转写音频
    transcription = transcribe_audio(args.audio_path, args.asr)
    if 'error' in transcription:
        print(f"❌ {transcription['error']}")
        sys.exit(1)
    
    print(f"✅ 转写完成，共 {len(transcription['text'])} 字符")
    
    # 2. 生成纪要
    minutes = generate_minutes(transcription)
    
    print(f"\n📋 会议纪要预览:")
    print(f"   主题: {minutes['topic']}")
    print(f"   关键讨论点: {len(minutes['key_points'])} 条")
    print(f"   决策结论: {len(minutes['decisions'])} 条")
    print(f"   待办事项: {len(minutes['todos'])} 条")
    
    # 3. 保存到文件
    if args.output:
        output_path = args.output
    else:
        base_name = Path(args.audio_path).stem
        output_path = f"{base_name}_纪要.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(minutes['minutes_text'])
    
    print(f"\n💾 已保存到: {output_path}")
    
    # 4. 同步飞书（可选）
    if args.feishu:
        result = save_to_feishu(minutes)
        print(f"📤 {result['message']}")
    
    # 输出JSON结果
    result = {
        'success': True,
        'topic': minutes['topic'],
        'key_points_count': len(minutes['key_points']),
        'decisions_count': len(minutes['decisions']),
        'todos_count': len(minutes['todos']),
        'output_file': output_path
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
