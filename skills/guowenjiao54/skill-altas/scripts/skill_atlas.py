# -*- coding: utf-8 -*-
"""
技能图谱 (Skill Atlas) - 按场景动态管理技能
"""
import json
import argparse
from pathlib import Path
import sys

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SKILLS_DIR = Path("D:/QClaw/resources/openclaw/config/skills")
CONFIG_PATH = Path(__file__).parent.parent / "config" / "scenes.json"

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_skill_status(skill_name):
    """获取技能状态"""
    skill_file = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_file.exists():
        return None
    
    try:
        content = skill_file.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        try:
            content = skill_file.read_text(encoding='gbk')
        except:
            return 'active'
    
    if 'disabled: true' in content.lower():
        return 'disabled'
    return 'active'

def set_skill_status(skill_name, disabled=True):
    """设置技能状态"""
    skill_file = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_file.exists():
        return False
    
    try:
        content = skill_file.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        try:
            content = skill_file.read_text(encoding='gbk')
        except:
            return False
    
    # 检查是否有 frontmatter
    if not content.startswith('---'):
        return False
    
    # 找到 frontmatter 结束位置
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False
    
    frontmatter = parts[1]
    body = parts[2]
    
    # 更新 disabled 状态
    lines = frontmatter.strip().split('\n')
    new_lines = []
    found_disabled = False
    
    for line in lines:
        if line.lower().startswith('disabled:'):
            found_disabled = True
            new_lines.append(f"disabled: {str(disabled).lower()}")
        else:
            new_lines.append(line)
    
    if not found_disabled and disabled:
        new_lines.append(f"disabled: true")
    
    new_frontmatter = '\n'.join(new_lines)
    new_content = f"---\n{new_frontmatter}\n---{body}"
    
    skill_file.write_text(new_content, encoding='utf-8')
    return True

def list_all_skills():
    """列出所有技能"""
    skills = []
    for skill_dir in SKILLS_DIR.iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                status = get_skill_status(skill_dir.name)
                skills.append({
                    'name': skill_dir.name,
                    'status': status
                })
    return sorted(skills, key=lambda x: x['name'])

def cmd_status():
    """显示当前状态"""
    config = load_config()
    skills = list_all_skills()
    
    active = [s for s in skills if s['status'] == 'active']
    disabled = [s for s in skills if s['status'] == 'disabled']
    
    print(f"[Skill Atlas - Status]")
    print(f"=" * 40)
    print(f"Active: {len(active)}")
    print(f"Disabled: {len(disabled)}")
    print()
    
    print("Active skills:")
    for s in active:
        core = " (core)" if s['name'] in config['core_skills'] else ""
        print(f"  + {s['name']}{core}")
    
    print()
    print("Disabled skills:")
    for s in disabled:
        print(f"  - {s['name']}")

def cmd_switch(scene):
    """切换场景"""
    config = load_config()
    
    if scene not in config['scenes']:
        print(f"[Error] Unknown scene: {scene}")
        print(f"Available: {', '.join(config['scenes'].keys())}")
        return
    
    scene_config = config['scenes'][scene]
    print(f"[Switch] Scene: {scene}")
    print(f"  {scene_config['description']}")
    
    # 先禁用所有非核心技能
    skills = list_all_skills()
    core_skills = config['core_skills']
    
    for s in skills:
        if s['name'] not in core_skills and s['status'] == 'active':
            set_skill_status(s['name'], disabled=True)
            print(f"  - Disable: {s['name']}")
    
    # 启用场景技能
    scene_skills = scene_config['skills']
    if scene_skills == 'all':
        for s in skills:
            if s['status'] == 'disabled':
                set_skill_status(s['name'], disabled=False)
                print(f"  + Enable: {s['name']}")
    else:
        for skill_name in scene_skills:
            if get_skill_status(skill_name) == 'disabled':
                set_skill_status(skill_name, disabled=False)
                print(f"  + Enable: {skill_name}")
    
    print()
    print(f"[Done] Switched to: {scene}")

def cmd_enable(skill_name):
    """启用技能"""
    if set_skill_status(skill_name, disabled=False):
        print(f"[OK] Enabled: {skill_name}")
    else:
        print(f"[Error] Failed: {skill_name}")

def cmd_disable(skill_name):
    """禁用技能"""
    config = load_config()
    if skill_name in config['core_skills']:
        print(f"[Error] Cannot disable core skill: {skill_name}")
        return
    
    if set_skill_status(skill_name, disabled=True):
        print(f"[OK] Disabled: {skill_name}")
    else:
        print(f"[Error] Failed: {skill_name}")

def cmd_list(scene):
    """列出场景技能"""
    config = load_config()
    
    if scene not in config['scenes']:
        print(f"[Error] Unknown scene: {scene}")
        return
    
    scene_config = config['scenes'][scene]
    print(f"[Scene] {scene}")
    print(f"  {scene_config['description']}")
    print()
    
    scene_skills = scene_config['skills']
    if scene_skills == 'all':
        print("  Contains all skills")
    else:
        print("  Skills:")
        for s in scene_skills:
            status = get_skill_status(s)
            icon = "+" if status == 'active' else "-"
            print(f"    {icon} {s}")

def main():
    parser = argparse.ArgumentParser(description='Skill Atlas - 技能图谱管理')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # status
    subparsers.add_parser('status', help='Show status')
    
    # switch
    switch_parser = subparsers.add_parser('switch', help='Switch scene')
    switch_parser.add_argument('scene', help='Scene name')
    
    # enable
    enable_parser = subparsers.add_parser('enable', help='Enable skill')
    enable_parser.add_argument('skill', help='Skill name')
    
    # disable
    disable_parser = subparsers.add_parser('disable', help='Disable skill')
    disable_parser.add_argument('skill', help='Skill name')
    
    # list
    list_parser = subparsers.add_parser('list', help='List scene skills')
    list_parser.add_argument('scene', help='Scene name')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        cmd_status()
    elif args.command == 'switch':
        cmd_switch(args.scene)
    elif args.command == 'enable':
        cmd_enable(args.skill)
    elif args.command == 'disable':
        cmd_disable(args.skill)
    elif args.command == 'list':
        cmd_list(args.scene)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
