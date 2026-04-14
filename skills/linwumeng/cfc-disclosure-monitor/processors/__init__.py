"""
Phase 2 内容处理器基类
所有处理器需注册到 HANDLERS 列表，按优先级匹配
"""
import re
import hashlib
import importlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urljoin


def make_id(title: str, date: str) -> str:
    """从标题+日期生成稳定的内容目录名（MD5前8位）"""
    key = f"{title[:40]}|{date}"
    return hashlib.md5(key.encode()).hexdigest()[:8]


class ContentResult:
    def __init__(self, success: bool, content_type: str = "",
                 text: str = "", attachments: list = None, error: str = ""):
        self.success = success
        self.content_type = content_type   # html | pdf | image_article | vue_page | unknown
        self.text = text                   # 提取的纯文本
        self.attachments = attachments or []  # [{"filename": ..., "path": ..., "size": ...}]
        self.error = error

    def to_meta(self) -> dict:
        return {
            "success": self.success,
            "content_type": self.content_type,
            "text_length": len(self.text),
            "attachments": self.attachments,
            "error": self.error,
        }


class ContentHandler(ABC):
    """处理器基类"""

    @property
    def name(self) -> str:
        return self.__class__.__name__.replace("Handler", "").lower()

    @property
    def priority(self) -> int:
        """数字越小优先级越高，用于 URL 后缀匹配"""
        return 100

    def match_url(self, url: str) -> bool:
        """URL 级别快速过滤，返回 True 表示该处理器接管"""
        return False

    def match_content_type(self, content_type_hint: str) -> bool:
        """根据公告 category 或其他元信息判断是否接管"""
        return False

    async def fetch(self, announcement: dict, out_dir: Path,
                    page=None) -> ContentResult:
        """
        核心方法：获取内容
        announcement: {"title", "date", "url", "category", ...}
        out_dir: 内容输出目录（已创建，内容写入其下）
        page: playwright Page 对象（如已启动浏览器可复用）
        返回 ContentResult
        """
        raise NotImplementedError


# ── 全局处理器注册表 ──────────────────────────────────────────────────────────
# 按 priority 排序，低优先级先尝试
HANDLERS: list[ContentHandler] = []

def register_handler(cls):
    HANDLERS.append(cls())
    HANDLERS.sort(key=lambda h: h.priority)
    return cls

def get_handler(url: str, content_type_hint: str = "") -> ContentHandler:
    for h in HANDLERS:
        if h.match_url(url) or h.match_content_type(content_type_hint):
            return h
    return None


# ── 自动加载当前目录下的所有处理器 ─────────────────────────────────────────────
# 由 batch_content_fetcher.py 显式 import，本文件只负责基类和注册逻辑
