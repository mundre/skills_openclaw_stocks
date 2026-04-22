#!/usr/bin/env python3
"""
Arshis-Game-Design-Pro - 版本管理器
支持策划案的版本保存、加载、对比、历史记录
"""

import os
import sys
import json
import hashlib
import difflib
from datetime import datetime
from typing import Dict, Any, List, Optional

# 配置
VERSIONS_DIR = os.path.expanduser('~/.openclaw/data/arshis-gdd-versions')


class VersionManager:
    """策划案版本管理器"""
    
    def __init__(self, project_name: str = 'default'):
        """
        初始化版本管理器
        
        Args:
            project_name: 项目名称，用于区分不同策划案
        """
        self.project_name = project_name
        self.versions_dir = os.path.join(VERSIONS_DIR, project_name)
        self.history_file = os.path.join(self.versions_dir, 'history.json')
        
        # 确保目录存在
        os.makedirs(self.versions_dir, exist_ok=True)
        
        # 加载历史记录
        self.history = self._load_history()
    
    def _load_history(self) -> Dict[str, Any]:
        """加载版本历史记录"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            'project': self.project_name,
            'created_at': datetime.now().isoformat(),
            'versions': [],
            'current_version': None
        }
    
    def _save_history(self):
        """保存版本历史记录"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def save_version(self, content: str, version: str, 
                     change_log: str = '', sections: Dict[str, str] = None) -> Dict[str, Any]:
        """
        保存策划案版本
        
        Args:
            content: 完整策划案内容
            version: 版本号（如 v1.0, v1.1）
            change_log: 修改日志
            sections: 分章节内容（可选）
        
        Returns:
            保存结果
        """
        # 计算内容哈希
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # 检查内容是否变化
        if self.history['current_version']:
            last_version = self.get_version(self.history['current_version'])
            if last_version and last_version.get('content_hash') == content_hash:
                return {
                    'status': 'unchanged',
                    'message': '内容未变化，无需保存新版本'
                }
        
        # 保存版本文件
        version_file = os.path.join(self.versions_dir, f'{version}.md')
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 保存分章节内容（如果有）
        if sections:
            sections_file = os.path.join(self.versions_dir, f'{version}_sections.json')
            with open(sections_file, 'w', encoding='utf-8') as f:
                json.dump(sections, f, ensure_ascii=False, indent=2)
        
        # 更新历史记录
        version_entry = {
            'version': version,
            'saved_at': datetime.now().isoformat(),
            'change_log': change_log,
            'content_hash': content_hash,
            'word_count': len(content),
            'sections': list(sections.keys()) if sections else [],
            'file': version_file
        }
        
        self.history['versions'].append(version_entry)
        self.history['current_version'] = version
        self._save_history()
        
        return {
            'status': 'saved',
            'version': version,
            'word_count': version_entry['word_count'],
            'sections': version_entry['sections'],
            'change_log': change_log
        }
    
    def get_version(self, version: str) -> Optional[Dict[str, Any]]:
        """
        获取指定版本内容
        
        Args:
            version: 版本号
        
        Returns:
            版本内容，不存在返回 None
        """
        version_file = os.path.join(self.versions_dir, f'{version}.md')
        
        if not os.path.exists(version_file):
            return None
        
        with open(version_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找版本元数据
        version_meta = None
        for v in self.history['versions']:
            if v['version'] == version:
                version_meta = v
                break
        
        return {
            'version': version,
            'content': content,
            'metadata': version_meta,
            'sections': self._load_sections(version) if version_meta else None
        }
    
    def _load_sections(self, version: str) -> Optional[Dict[str, str]]:
        """加载分章节内容"""
        sections_file = os.path.join(self.versions_dir, f'{version}_sections.json')
        
        if not os.path.exists(sections_file):
            return None
        
        with open(sections_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def compare_versions(self, version1: str, version2: str) -> Dict[str, Any]:
        """
        对比两个版本的差异
        
        Args:
            version1: 版本号 1
            version2: 版本号 2
        
        Returns:
            对比结果
        """
        v1_data = self.get_version(version1)
        v2_data = self.get_version(version2)
        
        if not v1_data or not v2_data:
            return {'error': '版本不存在'}
        
        # 使用 difflib 对比
        diff = difflib.unified_diff(
            v1_data['content'].splitlines(keepends=True),
            v2_data['content'].splitlines(keepends=True),
            fromfile=version1,
            tofile=version2,
            n=3
        )
        
        diff_text = ''.join(diff)
        
        # 分析差异
        added_lines = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        removed_lines = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        
        return {
            'version1': version1,
            'version2': version2,
            'diff_text': diff_text,
            'added_lines': added_lines,
            'removed_lines': removed_lines,
            'summary': f'+{added_lines} 行，-{removed_lines} 行'
        }
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """列出所有版本"""
        return self.history['versions']
    
    def get_history(self) -> Dict[str, Any]:
        """获取完整历史记录"""
        return self.history
    
    def modify_section(self, version: str, section_name: str, 
                       new_content: str, change_log: str = '') -> Dict[str, Any]:
        """
        修改特定章节
        
        Args:
            version: 当前版本号
            section_name: 章节名
            new_content: 新内容
            change_log: 修改日志
        
        Returns:
            修改结果
        """
        # 获取当前版本
        current = self.get_version(version)
        if not current:
            return {'error': f'版本 {version} 不存在'}
        
        # 加载分章节内容
        sections = current.get('sections') or {}
        
        # 更新章节
        old_content = sections.get(section_name, '')
        sections[section_name] = new_content
        
        # 生成新版本号
        version_parts = version.split('.')
        if len(version_parts) >= 2:
            major = version_parts[0]
            minor = int(version_parts[1]) + 1
            new_version = f'{major}.{minor}'
        else:
            new_version = f'{version}.1'
        
        # 重新组合完整内容（简化版：直接拼接章节）
        new_content_full = '\n\n'.join(sections.values())
        
        # 保存新版本
        result = self.save_version(
            content=new_content_full,
            version=new_version,
            change_log=change_log,
            sections=sections
        )
        
        result['old_version'] = version
        result['new_version'] = new_version
        result['modified_section'] = section_name
        result['old_content'] = old_content
        result['new_content'] = new_content
        
        return result


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python version_manager.py <command> [args]")
        print("Commands:")
        print("  list                     - 列出所有版本")
        print("  save <version> <file>    - 保存版本")
        print("  get <version>            - 获取版本内容")
        print("  compare <v1> <v2>        - 对比版本")
        print("  modify <ver> <section> <file> - 修改章节")
        sys.exit(1)
    
    command = sys.argv[1]
    manager = VersionManager('default')
    
    if command == 'list':
        versions = manager.list_versions()
        print(f"共 {len(versions)} 个版本:")
        for v in versions:
            print(f"  {v['version']} - {v['saved_at'][:10]} - {v['word_count']}字 - {v['change_log'][:30]}")
    
    elif command == 'save':
        version = sys.argv[2] if len(sys.argv) > 2 else 'v1.0'
        file = sys.argv[3] if len(sys.argv) > 3 else None
        
        if not file or not os.path.exists(file):
            print("Error: 需要提供文件路径")
            sys.exit(1)
        
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = manager.save_version(content, version, f'从 {file} 导入')
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'get':
        version = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not version:
            print("Error: 需要提供版本号")
            sys.exit(1)
        
        result = manager.get_version(version)
        if result:
            print(result['content'][:500])  # 只显示前 500 字
        else:
            print(f"版本 {version} 不存在")
    
    elif command == 'compare':
        v1 = sys.argv[2] if len(sys.argv) > 2 else None
        v2 = sys.argv[3] if len(sys.argv) > 3 else None
        
        if not v1 or not v2:
            print("Error: 需要提供两个版本号")
            sys.exit(1)
        
        result = manager.compare_versions(v1, v2)
        print(f"对比 {v1} → {v2}:")
        print(result['summary'])
        print("\n差异:")
        print(result['diff_text'][:1000])  # 只显示前 1000 字
    
    elif command == 'modify':
        version = sys.argv[2] if len(sys.argv) > 2 else 'v1.0'
        section = sys.argv[3] if len(sys.argv) > 3 else None
        file = sys.argv[4] if len(sys.argv) > 4 else None
        
        if not section or not file:
            print("Error: 需要提供章节名和文件路径")
            sys.exit(1)
        
        with open(file, 'r', encoding='utf-8') as f:
            new_content = f.read()
        
        result = manager.modify_section(version, section, new_content, f'修改 {section}')
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
