"""
File Backup Organizer for OpenClaw
智能文件备份整理工具 - OpenClaw 版本

功能：
- 递归扫描文件夹及所有子文件夹
- 按文件类型自动分类（Word、Excel、PDF、图片等）
- 支持排除指定文件类型
- 生成详细的备份报告
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import List, Optional

# 文件类型映射
FILE_TYPE_MAP = {
    # Word 文档
    '.doc': 'Word文件', '.docx': 'Word文件', '.docm': 'Word文件',
    '.dotx': 'Word文件', '.dotm': 'Word文件', '.odt': 'Word文件', '.rtf': 'Word文件',
    
    # Excel 表格
    '.xls': 'Excel文件', '.xlsx': 'Excel文件', '.xlsm': 'Excel文件',
    '.xlsb': 'Excel文件', '.csv': 'Excel文件', '.ods': 'Excel文件',
    
    # 图片文件
    '.jpg': '图片文件', '.jpeg': '图片文件', '.png': '图片文件',
    '.gif': '图片文件', '.bmp': '图片文件', '.webp': '图片文件',
    '.tiff': '图片文件', '.svg': '图片文件', '.psd': '图片文件',
    
    # PDF 文件
    '.pdf': 'PDF文件',
    
    # PowerPoint 文件
    '.ppt': 'PPT文件', '.pptx': 'PPT文件', '.pptm': 'PPT文件', '.ppsx': 'PPT文件',
    
    # 文本文件
    '.txt': '文本文件', '.md': '文本文件', '.log': '文本文件',
    
    # 压缩文件
    '.zip': '压缩文件', '.rar': '压缩文件', '.7z': '压缩文件',
    
    # 视频文件
    '.mp4': '视频文件', '.avi': '视频文件', '.mkv': '视频文件', '.mov': '视频文件',
    
    # 音频文件
    '.mp3': '音频文件', '.wav': '音频文件', '.flac': '音频文件',
    
    # 代码文件
    '.py': '代码文件', '.js': '代码文件', '.html': '代码文件',
    '.css': '代码文件', '.java': '代码文件', '.cpp': '代码文件',
    '.php': '代码文件', '.json': '代码文件', '.xml': '代码文件',
}

# 可能受影响的文件类型
POTENTIALLY_AFFECTED_TYPES = {'.html', '.htm', '.css', '.js', '.php', '.json', '.xml'}


def get_file_type_folder(extension: str) -> str:
    """根据扩展名获取分类文件夹名"""
    ext_lower = extension.lower()
    return FILE_TYPE_MAP.get(ext_lower, f"{ext_lower[1:].upper()}文件" if ext_lower else "其他文件")


def ensure_unique_filename(dest_folder: str, filename: str) -> str:
    """确保文件名唯一，如有重名则添加序号"""
    dest_path = os.path.join(dest_folder, filename)
    if not os.path.exists(dest_path):
        return dest_path
    
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while True:
        new_filename = f"{name}({counter}){ext}"
        new_dest_path = os.path.join(dest_folder, new_filename)
        if not os.path.exists(new_dest_path):
            return new_dest_path
        counter += 1


def scan_files(source_dir: str, exclude_extensions: Optional[List[str]] = None):
    """递归扫描所有文件"""
    all_files = []
    excluded_files = []
    
    if exclude_extensions:
        exclude_extensions = {ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                             for ext in exclude_extensions}
    
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, source_dir)
            extension = os.path.splitext(file)[1].lower()
            
            file_info = {
                'full_path': full_path,
                'rel_path': rel_path,
                'filename': file,
                'extension': extension
            }
            
            # 检查是否被排除
            if exclude_extensions and extension in exclude_extensions:
                file_info['exclude_reason'] = f"扩展名 {extension} 在排除列表中"
                excluded_files.append(file_info)
            else:
                all_files.append(file_info)
    
    return all_files, excluded_files


def backup_files(source_path: str, exclude_extensions: Optional[List[str]] = None) -> dict:
    """
    备份并分类整理文件
    
    Args:
        source_path: 源文件夹路径
        exclude_extensions: 要排除的文件扩展名列表，如 ['.tmp', '.log']
    
    Returns:
        包含备份结果的字典
    """
    # 检查源文件夹
    if not os.path.exists(source_path):
        return {'success': False, 'error': f'源文件夹不存在: {source_path}'}
    
    # 设置备份文件夹路径
    source_name = os.path.basename(source_path)
    backup_dir = os.path.join(os.path.dirname(source_path), f"{source_name}_备份")
    
    # 扫描文件
    all_files, excluded_files = scan_files(source_path, exclude_extensions)
    total_files = len(all_files)
    
    if total_files == 0:
        return {'success': False, 'error': '没有需要备份的文件'}
    
    # 按类型分组
    files_by_type = defaultdict(list)
    potentially_affected_files = []
    
    for file_info in all_files:
        ext = file_info['extension']
        type_folder = get_file_type_folder(ext)
        files_by_type[type_folder].append(file_info)
        
        if ext in POTENTIALLY_AFFECTED_TYPES:
            potentially_affected_files.append(file_info)
    
    # 创建备份文件夹
    os.makedirs(backup_dir, exist_ok=True)
    
    # 复制文件
    copy_stats = defaultdict(lambda: {'count': 0, 'files': []})
    
    for type_folder, files in files_by_type.items():
        type_folder_path = os.path.join(backup_dir, type_folder)
        os.makedirs(type_folder_path, exist_ok=True)
        
        for file_info in files:
            dest_path = ensure_unique_filename(type_folder_path, file_info['filename'])
            try:
                shutil.copy2(file_info['full_path'], dest_path)
                copy_stats[type_folder]['count'] += 1
                copy_stats[type_folder]['files'].append(os.path.basename(dest_path))
            except Exception as e:
                print(f"复制失败: {file_info['full_path']} - {str(e)}")
    
    # 生成报告
    generate_reports(backup_dir, source_path, copy_stats, total_files, 
                    potentially_affected_files, excluded_files)
    
    return {
        'success': True,
        'source_path': source_path,
        'backup_dir': backup_dir,
        'total_files': total_files,
        'excluded_count': len(excluded_files),
        'categories': dict(copy_stats),
        'potentially_affected': len(potentially_affected_files)
    }


def organize_by_type(source_path: str) -> dict:
    """
    按文件类型自动分类（不包含排除功能）
    
    Args:
        source_path: 源文件夹路径
    
    Returns:
        包含分类结果的字典
    """
    return backup_files(source_path, exclude_extensions=None)


def generate_reports(backup_dir, source_dir, stats, total_files, 
                    potentially_affected_files, excluded_files):
    """生成报告文件"""
    # 备份清单
    report_path = os.path.join(backup_dir, "备份清单.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("文件备份清单\n")
        f.write("=" * 80 + "\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"源文件夹: {source_dir}\n")
        f.write(f"备份文件夹: {backup_dir}\n")
        f.write(f"备份文件数: {total_files}\n")
        if excluded_files:
            f.write(f"排除文件数: {len(excluded_files)}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("【分类统计】\n")
        f.write("-" * 80 + "\n")
        
        for type_folder, info in sorted(stats.items(), key=lambda x: x[1]['count'], reverse=True):
            f.write(f"\n[{type_folder}]: {info['count']} 个文件\n")
            f.write("-" * 80 + "\n")
            for filename in info['files']:
                f.write(f"  - {filename}\n")
        
        if potentially_affected_files:
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("【警告：可能因丢失目录结构而无法正常使用的文件】\n")
            f.write("=" * 80 + "\n")
            for file_info in potentially_affected_files:
                f.write(f"  ! {file_info['rel_path']}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("备份完成\n")
        f.write("=" * 80 + "\n")
    
    # 删除清单
    if excluded_files:
        delete_report_path = os.path.join(backup_dir, "删除清单.txt")
        with open(delete_report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("排除文件清单\n")
            f.write("=" * 80 + "\n")
            f.write(f"排除文件总数: {len(excluded_files)}\n")
            f.write("=" * 80 + "\n\n")
            
            for file_info in excluded_files:
                f.write(f"- {file_info['rel_path']}\n")
                f.write(f"  原因: {file_info.get('exclude_reason', '未知')}\n\n")