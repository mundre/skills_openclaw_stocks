#!/usr/bin/env python3
"""
安装每日AI信号筛选的cron任务
"""
import subprocess
import sys
from pathlib import Path

def install_cron(time="09:00"):
    """安装每日定时任务"""
    hour, minute = time.split(':')
    
    skill_path = Path(__file__).parent.parent.absolute()
    script_path = skill_path / 'scripts' / 'run-signal-filter.py'
    
    # 构造cron命令
    cron_cmd = (
        f'{minute} {hour} * * * '
        f'cd {skill_path.parent} && '
        f'python3 {script_path} --cron'
    )
    
    # 获取现有crontab
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_crontab = result.stdout
    except subprocess.CalledProcessError:
        current_crontab = ''
    
    # 检查是否已安装
    if 'run-signal-filter' in current_crontab:
        print("[已安装] cron任务已存在")
        return True
    
    # 添加新任务
    new_crontab = current_crontab.rstrip() + '\n' + cron_cmd + '\n'
    
    try:
        subprocess.run(['crontab', '-'], input=new_crontab, text=True, check=True)
        print(f"[安装成功] 每日 {time} 自动执行AI信号筛选")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[安装失败] {e}")
        return False

def main():
    if len(sys.argv) > 1:
        time = sys.argv[1]
    else:
        time = "09:00"
    
    success = install_cron(time)
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
