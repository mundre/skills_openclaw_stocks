#!/usr/bin/env python3
"""
小说人物关系图谱提取脚本
用法: python3 extract_graph.py <小说文件路径> [输出目录]

示例:
  python3 extract_graph.py /path/to/novel.txt
  python3 extract_graph.py /path/to/novel.txt ./output/
"""

import re
import json
import sys
import os
from collections import defaultdict

def detect_encoding(content):
    """自动检测文件编码"""
    try:
        content.decode('utf-8')
        return 'utf-8'
    except UnicodeDecodeError:
        try:
            content.decode('gbk')
            return 'gbk'
        except UnicodeDecodeError:
            return 'gb18030'

def split_chapters(text):
    """按章节分割小说文本"""
    chapter_starts = []
    for m in re.finditer(r'第[一二三四五六七八九十百千\d]+[章节集部]', text):
        chapter_starts.append(m.start())
    chapter_starts.append(len(text))
    return [text[chapter_starts[i]:chapter_starts[i+1]] for i in range(len(chapter_starts)-1)]

def extract_characters_from_quotes(chapters, known_chars):
    """从对话引号中提取额外角色"""
    additional = defaultdict(int)
    for ch in chapters:
        for m in re.finditer(r'["""](.{2,4})["""]', ch):
            name = m.group(1)
            if 2 <= len(name) <= 4 and re.match(r'^[\u4e00-\u9fff]+$', name) and name not in known_chars:
                additional[name] += 1
    return {name: freq for name, freq in additional.items() if freq >= 30}

def build_graph(novel_path, output_dir='.', characters=None, relationships=None):
    """构建人物关系图"""
    # 读取文件
    with open(novel_path, 'rb') as f:
        content = f.read()
    
    encoding = detect_encoding(content)
    text = content.decode(encoding, errors='ignore')
    
    chapters = split_chapters(text)
    print(f"检测编码: {encoding}, 总章节: {len(chapters)}, 总字数: {len(text)}")
    
    # 提取额外角色
    if characters:
        extra = extract_characters_from_quotes(chapters, set(characters.keys()))
        for name, freq in extra.items():
            if name not in characters:
                characters[name] = '其他'
    
    if not characters:
        print("错误: 未提供人物列表！")
        return None
    
    char_ids = set(characters.keys())
    
    # 构建节点
    nodes = []
    for char, group in characters.items():
        freq = sum(1 for ch in chapters if char in ch)
        nodes.append({
            'id': char, 'name': char, 'group': group,
            'freq': freq, 'desc': '', 'rich_desc': f'{group}角色，共出场{freq}章。'
        })
    
    # 构建关系
    links_dict = defaultdict(lambda: {'weight': 0, 'label': ''})
    
    for ch in chapters:
        chars_in_ch = [c for c in char_ids if c in ch]
        for i, c1 in enumerate(chars_in_ch):
            for c2 in chars_in_ch[i+1:]:
                key = tuple(sorted([c1, c2]))
                links_dict[key]['weight'] += 1
    
    if relationships:
        for (c1, c2), label in relationships.items():
            key = tuple(sorted([c1, c2]))
            if key in links_dict:
                links_dict[key]['label'] = label
                links_dict[key]['weight'] += 30
    
    links = []
    for (c1, c2), data in links_dict.items():
        if c1 in char_ids and c2 in char_ids:
            label = data['label'] if data['label'] else f'同现{int(data["weight"])}章'
            links.append({'source': c1, 'target': c2, 'weight': data['weight'], 'label': label})
    
    links.sort(key=lambda x: -x['weight'])
    
    graph_data = {'nodes': nodes, 'links': links[:2000]}
    
    # 保存 JSON
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, 'graph_data.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)
    
    print(f"节点: {len(nodes)}, 关系: {len(links[:2000])}")
    print(f"数据已保存到: {json_path}")
    
    return graph_data

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    novel_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    
    if not os.path.exists(novel_path):
        print(f"文件不存在: {novel_path}")
        sys.exit(1)
    
    build_graph(novel_path, output_dir)
