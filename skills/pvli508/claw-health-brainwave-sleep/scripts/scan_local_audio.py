#!/usr/bin/env python3
"""
本地音频库扫描器 - 生成 manifest.json
支持新的命名格式: bw_{亚型}_{场景}_{时长}_{严重度}_{脑波类型}_v{版本}.mp3
"""

import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 本地音频库路径
AUDIO_LIBRARY_PATH = Path(r"C:\Users\龚文瀚\Desktop\sleepAudio")
OUTPUT_MANIFEST = Path(__file__).parent.parent / "audio_library" / "manifest.json"

AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.flac', '.m4a'}

# 亚型映射 - 按优先级匹配
SUBTYPE_PATTERNS = [
    ('anxiety_sleep', '焦虑性失眠'),
    ('sleep_maintain', '睡眠维持'),
    ('sleep_onset', '入睡困难'),
    ('early_wake', '早醒'),
    ('circadian', '昼夜节律紊乱'),
    ('light_sleep', '浅眠多梦'),
    ('general', '通用')
]

# 场景映射
SCENE_PATTERNS = [
    ('pre_sleep', '睡前'),
    ('pre', '睡前'),
    ('wake', '夜醒'),
    ('midnight_wake', '夜醒'),
    ('nap', '午休'),
    ('relax', '日间放松'),
    ('relaxation', '日间放松')
]

# 严重程度映射
SEVERITY_PATTERNS = [
    ('mild', '轻度'),
    ('mod', '中度'),
    ('sev', '重度')
]


def parse_filename(filename: str) -> dict:
    """根据新命名格式解析音频元数据"""
    name = Path(filename).stem
    
    result = {
        "filename": filename,
        "sleep_subtype": None,
        "sleep_subtype_code": None,
        "use_scene": None,
        "duration": None,
        "severity": None,
        "brainwave_type": None,
        "version": None,
        "category": "brainwave",
        "tags": []
    }
    
    # 提取时长
    match = re.search(r'(\d+)min', name)
    if match:
        result["duration"] = int(match.group(1))
    
    # 提取版本
    match = re.search(r'v(\d+)$', name)
    if match:
        result["version"] = 'v' + match.group(1)
    
    # 提取亚型
    for code, label in SUBTYPE_PATTERNS:
        if code in name:
            result["sleep_subtype_code"] = code
            result["sleep_subtype"] = label
            result["tags"].append(label)
            break
    
    # 提取场景
    for code, label in SCENE_PATTERNS:
        if code in name:
            result["use_scene"] = label
            result["tags"].append(label)
            break
    
    # 提取严重程度
    for code, label in SEVERITY_PATTERNS:
        # 避免匹配到 _sev_ 后面的内容
        if re.search(rf'_{code}_', name):
            result["severity"] = label
            result["tags"].append(label)
            break
    
    # 提取脑波类型 (最后的 _xxx_v1 部分)
    match = re.search(r'_(\w+)_v\d+$', name)
    if match:
        result["brainwave_type"] = match.group(1)
    
    # 生成唯一 ID
    result["audio_id"] = Path(filename).stem
    
    return result


def scan_audio_library(library_path: Path) -> list:
    """扫描音频库目录"""
    audio_files = []
    
    if not library_path.exists():
        logger.error(f"音频库目录不存在: {library_path}")
        return audio_files
    
    logger.info(f"正在扫描音频库: {library_path}")
    
    for file_path in sorted(library_path.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() in AUDIO_EXTENSIONS:
            metadata = parse_filename(file_path.name)
            metadata["file_path"] = str(file_path)
            metadata["file_size"] = file_path.stat().st_size
            metadata["file_ext"] = file_path.suffix
            
            audio_files.append(metadata)
            
            subtype = metadata.get("sleep_subtype") or "?"
            severity = metadata.get("severity") or "?"
            duration = metadata.get("duration") or "?"
            scene = metadata.get("use_scene") or "?"
            logger.info(f"  {file_path.name}")
            logger.info(f"    -> {subtype} / {severity} / {scene} / {duration}min")
    
    return audio_files


def generate_manifest(audio_files: list, output_path: Path):
    """生成 manifest.json"""
    manifest = {
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat(),
        "library_path": str(AUDIO_LIBRARY_PATH),
        "total_count": len(audio_files),
        "audio_files": audio_files,
        "statistics": {
            "by_subtype": {},
            "by_scene": {},
            "by_severity": {},
            "by_duration": {}
        }
    }
    
    # 统计
    for audio in audio_files:
        # 按亚型统计
        subtype = audio.get("sleep_subtype") or "其他"
        manifest["statistics"]["by_subtype"][subtype] = \
            manifest["statistics"]["by_subtype"].get(subtype, 0) + 1
        
        # 按场景统计
        scene = audio.get("use_scene") or "其他"
        manifest["statistics"]["by_scene"][scene] = \
            manifest["statistics"]["by_scene"].get(scene, 0) + 1
        
        # 按严重程度统计
        severity = audio.get("severity") or "未知"
        manifest["statistics"]["by_severity"][severity] = \
            manifest["statistics"]["by_severity"].get(severity, 0) + 1
        
        # 按时长统计
        duration = audio.get("duration") or 0
        if duration:
            manifest["statistics"]["by_duration"][duration] = \
                manifest["statistics"]["by_duration"].get(duration, 0) + 1
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Manifest 已生成: {output_path}")
    return manifest


def main():
    print("=" * 60)
    print("本地音频库扫描器")
    print(f"音频库路径: {AUDIO_LIBRARY_PATH}")
    print("=" * 60)
    
    audio_files = scan_audio_library(AUDIO_LIBRARY_PATH)
    
    if not audio_files:
        logger.warning("未找到任何音频文件")
        return
    
    print(f"\n共找到 {len(audio_files)} 个音频文件")
    
    manifest = generate_manifest(audio_files, OUTPUT_MANIFEST)
    
    print("\n" + "=" * 60)
    print("统计信息")
    print("=" * 60)
    
    print("\n按亚型:")
    for k, v in manifest["statistics"]["by_subtype"].items():
        print(f"  {k}: {v} 个")
    
    print("\n按场景:")
    for k, v in manifest["statistics"]["by_scene"].items():
        print(f"  {k}: {v} 个")
    
    print("\n按严重程度:")
    for k, v in manifest["statistics"]["by_severity"].items():
        print(f"  {k}: {v} 个")
    
    print("\n按时长:")
    for k, v in sorted(manifest["statistics"]["by_duration"].items()):
        print(f"  {k}分钟: {v} 个")
    
    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
