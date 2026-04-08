"""
基础客户端 - 处理 MCP 协议通信
"""

import json
import urllib.request
import urllib.error
from typing import Any, Optional

DEFAULT_BASE_URL = 'https://mcp.jin10.com/mcp'


class Jin10Error(Exception):
    """基础错误类"""
    def __init__(self, message: str, code: Optional[int] = None, data: Any = None):
        super().__init__(message)
        self.code = code
        self.data = data


class BaseClient:
    """MCP 协议处理基础类"""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, api_token: str = None):
        import os
        self.base_url = base_url
        self.api_token = api_token or os.environ.get('JIN10_API_TOKEN', '')
        self.request_id = 1
        self.initialized = False
        self.session_id: Optional[str] = None

    def _build_request(self, method: str, params: dict = None) -> dict:
        """构建带 id 的 JSON-RPC 请求"""
        payload = {
            'jsonrpc': '2.0',
            'id': self.request_id,
            'method': method,
            'params': params or {},
        }
        self.request_id += 1
        return payload

    def _build_notify_request(self, method: str, params: dict = None) -> dict:
        """构建不带 id 的 JSON-RPC notification 请求"""
        return {
            'jsonrpc': '2.0',
            'method': method,
            'params': params or {},
        }

    def _do_request(self, payload: dict) -> dict:
        """发送 HTTP 请求"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'Authorization': f'Bearer {self.api_token}',
        }

        if self.session_id:
            headers['Mcp-Session-Id'] = self.session_id

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            self.base_url,
            data=data,
            headers=headers,
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                self.session_id = response.headers.get('Mcp-Session-Id', self.session_id)
                raw_data = response.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            raise Jin10Error(f'HTTP Error: {e.code} - {e.reason}')
        except urllib.error.URLError as e:
            raise Jin10Error(f'Network Error: {e.reason}')

        # Notification 请求（没有 id）可能返回空 body
        if 'id' not in payload:
            return {}

        # 处理 SSE 格式响应 (event: message\ndata: {...}\n\n)
        if 'event: message' in raw_data or raw_data.startswith('data:'):
            for line in raw_data.split('\n'):
                if line.startswith('data:'):
                    raw_data = line[5:].strip()
                    break

        # 空响应
        if not raw_data:
            return {}

        result = json.loads(raw_data)

        if 'error' in result:
            raise Jin10Error(
                f"MCP Error ({result['error'].get('code')}): {result['error'].get('message')}",
                code=result['error'].get('code'),
                data=result['error'].get('data')
            )

        return result.get('result', {})

    def request(self, method: str, params: dict = None) -> Any:
        """发送请求（自动初始化）"""
        if not self.initialized:
            self.initialize()
        return self._do_request(self._build_request(method, params))

    def notify(self, method: str, params: dict = None) -> None:
        """发送通知（无响应）"""
        self._do_request(self._build_notify_request(method, params))

    def initialize(self) -> None:
        """初始化 MCP 连接"""
        if self.initialized:
            return

        # 使用 _do_request 直接发送，避免通过 request() 递归调用 initialize()
        self._do_request(self._build_request('initialize', {
            'protocolVersion': '2025-11-25',
            'capabilities': {},
            'clientInfo': {
                'name': 'jin10-py-client',
                'version': '1.0.0',
            },
        }))

        self.notify('notifications/initialized')

        # 获取工具和资源列表
        try:
            self._do_request(self._build_request('tools/list', {}))
            self._do_request(self._build_request('resources/list', {}))
        except Exception:
            pass

        self.initialized = True

    def call_tool(self, name: str, arguments: dict = None) -> Any:
        """调用 MCP 工具"""
        if not self.initialized:
            self.initialize()

        result = self.request('tools/call', {
            'name': name,
            'arguments': arguments or {},
        })

        if not result:
            raise Jin10Error('No result returned from tool')

        if result.get('isError'):
            content = json.dumps(result.get('content', 'Unknown Error'))
            raise Jin10Error(f'Tool execution error: {content}')

        # 优先使用 structuredContent
        if result.get('structuredContent'):
            return result['structuredContent']

        if result.get('content') and isinstance(result['content'], list):
            for c in result['content']:
                if c.get('structuredContent'):
                    return c['structuredContent']
            return result['content']

        return result

    def read_resource(self, uri: str) -> Any:
        """读取 MCP 资源"""
        if not self.initialized:
            self.initialize()

        result = self.request('resources/read', {'uri': uri})

        if not result:
            return None

        contents = result.get('contents', [])
        if contents:
            content = contents[0]
            return content.get('structuredContent') or content.get('text')

        return result


class Jin10Client(BaseClient):
    """完整的 Jin10 客户端"""

    def __init__(self, api_token: str = None, base_url: str = DEFAULT_BASE_URL):
        super().__init__(base_url, api_token)
        self._quotes: Optional['QuotesClient'] = None
        self._flash: Optional['FlashClient'] = None
        self._news: Optional['NewsClient'] = None
        self._calendar: Optional['CalendarClient'] = None

    @property
    def quotes(self) -> 'QuotesClient':
        if self._quotes is None:
            self._quotes = QuotesClient(self.base_url, self.api_token)
            self._quotes.session_id = self.session_id
        return self._quotes

    @property
    def flash(self) -> 'FlashClient':
        if self._flash is None:
            self._flash = FlashClient(self.base_url, self.api_token)
            self._flash.session_id = self.session_id
        return self._flash

    @property
    def news(self) -> 'NewsClient':
        if self._news is None:
            self._news = NewsClient(self.base_url, self.api_token)
            self._news.session_id = self.session_id
        return self._news

    @property
    def calendar(self) -> 'CalendarClient':
        if self._calendar is None:
            self._calendar = CalendarClient(self.base_url, self.api_token)
            self._calendar.session_id = self.session_id
        return self._calendar


# 延迟导入子模块避免循环引用
from .quotes import QuotesClient
from .flash import FlashClient
from .news import NewsClient
from .calendar import CalendarClient
