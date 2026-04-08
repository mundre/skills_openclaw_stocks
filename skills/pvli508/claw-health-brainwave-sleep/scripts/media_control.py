#!/usr/bin/env python3
"""
媒体播放控制脚本
支持：播放、暂停、停止、上一首、下一首
通过发送 Windows 媒体键实现
"""

import sys
import time
import ctypes
from ctypes import wintypes

# Windows 常量
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_STOP = 0xB2
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_UP = 0xAF
VK_VOLUME_DOWN = 0xAE

# 加载 user32.dll
user32 = ctypes.windll.user32


def key_down(key):
    """按下按键"""
    user32.keybd_event(key, 0, KEYEVENTF_EXTENDEDKEY, 0)


def key_up(key):
    """释放按键"""
    user32.keybd_event(key, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)


def media_play_pause():
    """播放/暂停"""
    key_down(VK_MEDIA_PLAY_PAUSE)
    time.sleep(0.1)
    key_up(VK_MEDIA_PLAY_PAUSE)
    print("已发送播放/暂停命令")


def media_stop():
    """停止"""
    key_down(VK_MEDIA_STOP)
    time.sleep(0.1)
    key_up(VK_MEDIA_STOP)
    print("已发送停止命令")


def media_next():
    """下一首"""
    key_down(VK_MEDIA_NEXT_TRACK)
    time.sleep(0.1)
    key_up(VK_MEDIA_NEXT_TRACK)
    print("已发送下一首命令")


def media_prev():
    """上一首"""
    key_down(VK_MEDIA_PREV_TRACK)
    time.sleep(0.1)
    key_up(VK_MEDIA_PREV_TRACK)
    print("已发送上一首命令")


def volume_up():
    """音量增加"""
    key_down(VK_VOLUME_UP)
    time.sleep(0.1)
    key_up(VK_VOLUME_UP)
    print("已发送音量增加命令")


def volume_down():
    """音量减少"""
    key_down(VK_VOLUME_DOWN)
    time.sleep(0.1)
    key_up(VK_VOLUME_DOWN)
    print("已发送音量减少命令")


def main():
    if len(sys.argv) < 2:
        print("用法: media_control.py [play|pause|stop|next|prev|volup|voldown]")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd in ["pause", "resume", "play"]:
        media_play_pause()
    elif cmd == "stop":
        media_stop()
    elif cmd == "next":
        media_next()
    elif cmd == "prev":
        media_prev()
    elif cmd in ["volup", "volume_up"]:
        volume_up()
    elif cmd in ["voldown", "volume_down"]:
        volume_down()
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
