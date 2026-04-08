"""
A2A Match 客户端 SDK
用于 QClaw 与 A2A 服务端交互
"""

import requests
import json
from typing import Dict, List, Optional
from pathlib import Path

class A2AClient:
    """A2A Match 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:5000/api/v1", token: str = None):
        self.base_url = base_url
        self.token = token
        self.user_id = None
        self.user_name = None
    
    def set_token(self, token: str):
        """设置认证 token"""
        self.token = token
        if token.startswith('token_'):
            self.user_id = token.replace('token_', '')
    
    def _headers(self) -> Dict:
        """获取请求头"""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """发送请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == 'GET':
                resp = requests.get(url, headers=self._headers())
            elif method == 'POST':
                resp = requests.post(url, headers=self._headers(), json=data)
            elif method == 'PUT':
                resp = requests.put(url, headers=self._headers(), json=data)
            else:
                return {'status': 'error', 'message': f'不支持的请求方法: {method}'}
            
            return resp.json()
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    # ============ 用户认证 ============
    
    def register(self, email: str, password: str, name: str = "") -> Dict:
        """用户注册"""
        result = self._request('POST', '/auth/register', {
            'email': email,
            'password': password,
            'name': name
        })
        if result.get('status') == 'success':
            self.set_token(result['token'])
            self.user_name = name
        return result
    
    def login(self, email: str, password: str) -> Dict:
        """用户登录"""
        result = self._request('POST', '/auth/login', {
            'email': email,
            'password': password
        })
        if result.get('status') == 'success':
            self.set_token(result['token'])
            self.user_name = result.get('user', {}).get('name', '')
        return result
    
    # ============ 档案管理 ============
    
    def upload_profile(self, profile: Dict) -> Dict:
        """上传档案"""
        return self._request('POST', '/profiles', profile)
    
    def get_my_profile(self) -> Dict:
        """获取我的档案"""
        return self._request('GET', '/profiles/me')
    
    def get_profile(self, profile_id: str) -> Dict:
        """获取公开档案"""
        return self._request('GET', f'/profiles/{profile_id}')
    
    def update_contact_info(self, weixin: str = "", email: str = "", 
                            phone: str = "", qq: str = "", 
                            preferred: str = "weixin", public: bool = False) -> Dict:
        """更新联系方式"""
        return self._request('PUT', '/profiles/contact-info', {
            'weixin': weixin,
            'email': email,
            'phone': phone,
            'qq': qq,
            'preferred': preferred,
            'public': public
        })
    
    # ============ 匹配服务 ============
    
    def request_match(self, min_score: float = 0.5) -> Dict:
        """请求匹配"""
        return self._request('POST', '/match', {'min_score': min_score})
    
    def get_match_notifications(self) -> Dict:
        """获取匹配通知"""
        return self._request('GET', '/match/notifications')
    
    def mark_notification_read(self, notif_id: str) -> Dict:
        """标记通知已读"""
        return self._request('POST', f'/match/notifications/{notif_id}/read')
    
    # ============ 连接请求 ============
    
    def send_connect_request(self, to_user: str, message: str = "", 
                             match_id: str = None, exchange_contact: bool = False) -> Dict:
        """发起连接请求"""
        return self._request('POST', '/connect', {
            'to_user': to_user,
            'message': message,
            'match_id': match_id,
            'exchange_contact': exchange_contact
        })
    
    def get_connect_requests(self) -> Dict:
        """获取连接请求"""
        return self._request('GET', '/connect/requests')
    
    def accept_connect(self, connect_id: str, message: str = "") -> Dict:
        """接受连接"""
        return self._request('POST', f'/connect/{connect_id}/accept', {
            'message': message
        })
    
    def decline_connect(self, connect_id: str, reason: str = "") -> Dict:
        """拒绝连接"""
        return self._request('POST', f'/connect/{connect_id}/decline', {
            'reason': reason
        })
    
    # ============ 消息中转 ============
    
    def send_message(self, to_user: str, content: str) -> Dict:
        """发送消息"""
        return self._request('POST', '/messages', {
            'to_user': to_user,
            'content': content
        })
    
    def get_messages(self, with_user: str) -> Dict:
        """获取聊天记录"""
        return self._request('GET', f'/messages/{with_user}')
    
    def get_conversations(self) -> Dict:
        """获取对话列表"""
        return self._request('GET', '/conversations')
    
    # ============ 联系方式交换 ============
    
    def get_contact_info(self, with_user: str) -> Dict:
        """获取对方联系方式"""
        return self._request('GET', f'/contact-info/{with_user}')
    
    def share_contact_info(self, to_user: str, contact_type: str, contact_value: str) -> Dict:
        """主动分享联系方式"""
        return self._request('POST', '/contact-info/share', {
            'to_user': to_user,
            'contact_type': contact_type,
            'contact_value': contact_value
        })
    
    # ============ 工具方法 ============
    
    def health_check(self) -> Dict:
        """健康检查"""
        return self._request('GET', '/health')
    
    def get_api_docs(self) -> Dict:
        """获取 API 文档"""
        return self._request('GET', '/docs')


# ============ 便捷函数 ============

_client: Optional[A2AClient] = None

def get_client(base_url: str = "http://localhost:5000/api/v1") -> A2AClient:
    """获取全局客户端实例"""
    global _client
    if _client is None:
        _client = A2AClient(base_url)
    return _client

def init_client(base_url: str, token: str = None):
    """初始化客户端"""
    global _client
    _client = A2AClient(base_url, token)
    return _client


# ============ 使用示例 ============

if __name__ == '__main__':
    # 创建客户端
    client = A2AClient()
    
    # 健康检查
    print("健康检查:", client.health_check())
    
    # 用户注册
    print("\n用户注册:")
    result = client.register(
        email="test@example.com",
        password="123456",
        name="测试用户"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 上传档案
    print("\n上传档案:")
    profile = {
        'profile': {
            'name': '测试用户',
            'location': '北京'
        },
        'capabilities': [
            {'skill': 'Python开发', 'level': 'expert'}
        ],
        'needs': [
            {'skill': 'GPU算力', 'priority': 'high'}
        ],
        'resources': [
            {'name': 'RTX 3080', 'type': 'GPU'}
        ]
    }
    result = client.upload_profile(profile)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 请求匹配
    print("\n请求匹配:")
    result = client.request_match()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 获取匹配通知
    print("\n获取匹配通知:")
    result = client.get_match_notifications()
    print(json.dumps(result, ensure_ascii=False, indent=2))
