"""
A2A 云端服务 MVP - Flask 版本
包含完整的匹配通知、连接请求、消息中转、联系方式交换功能
运行: python a2a_server.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

app = Flask(__name__)
CORS(app)

# 数据存储目录
DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

# 内存数据库 (MVP)
users_db = {}
profiles_db = {}
matches_db = {}
notifications_db = {}
contacts_db = {}  # 连接请求
messages_db = {}  # 消息记录
contact_info_db = {}  # 联系方式交换记录

def generate_id(prefix='id'):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

def save_data():
    """保存数据到文件"""
    data = {
        'users': users_db,
        'profiles': profiles_db,
        'matches': matches_db,
        'notifications': notifications_db,
        'contacts': contacts_db,
        'messages': messages_db,
        'contact_info': contact_info_db
    }
    with open(DATA_DIR / 'a2a_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data():
    """从文件加载数据"""
    data_path = DATA_DIR / 'a2a_data.json'
    if data_path.exists():
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            globals()['users_db'] = data.get('users', {})
            globals()['profiles_db'] = data.get('profiles', {})
            globals()['matches_db'] = data.get('matches', {})
            globals()['notifications_db'] = data.get('notifications', {})
            globals()['contacts_db'] = data.get('contacts', {})
            globals()['messages_db'] = data.get('messages', {})
            globals()['contact_info_db'] = data.get('contact_info', {})

def get_user_id_from_token():
    """从 token 获取用户 ID"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token.startswith('token_'):
        return None
    return token.replace('token_', '')

def get_user_profile(user_id):
    """获取用户档案"""
    for pid, profile in profiles_db.items():
        if profile.get('user_id') == user_id:
            return profile
    return None

def get_user_name(user_id):
    """获取用户名称"""
    profile = get_user_profile(user_id)
    if profile:
        return profile.get('profile', {}).get('name', 'Unknown')
    return 'Unknown'

# 启动时加载数据
load_data()

# ============ 用户认证 ============

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.json
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'status': 'error', 'message': '邮箱和密码必填'}), 400
    
    # 检查邮箱是否已注册
    for uid, user in users_db.items():
        if user.get('email') == data['email']:
            return jsonify({'status': 'error', 'message': '邮箱已注册'}), 400
    
    user_id = generate_id('user')
    users_db[user_id] = {
        'id': user_id,
        'email': data['email'],
        'name': data.get('name', ''),
        'password': data['password'],  # MVP 不加密
        'contact_info': data.get('contact_info', {}),  # 联系方式
        'created_at': datetime.now().isoformat()
    }
    
    save_data()
    
    return jsonify({
        'status': 'success',
        'user': {
            'id': user_id,
            'email': data['email'],
            'name': data.get('name', '')
        },
        'token': f'token_{user_id}'
    })

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    
    for uid, user in users_db.items():
        if user.get('email') == data.get('email') and user.get('password') == data.get('password'):
            return jsonify({
                'status': 'success',
                'token': f'token_{uid}',
                'user': {
                    'id': uid,
                    'email': user['email'],
                    'name': user.get('name', '')
                }
            })
    
    return jsonify({'status': 'error', 'message': '邮箱或密码错误'}), 401

# ============ 档案管理 ============

@app.route('/api/v1/profiles', methods=['POST'])
def upload_profile():
    """上传/更新档案"""
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({'status': 'error', 'message': '未授权'}), 401
    
    data = request.json
    
    profile_id = generate_id('profile')
    data['id'] = profile_id
    data['user_id'] = user_id
    data['updated_at'] = datetime.now().isoformat()
    
    profiles_db[profile_id] = data
    
    # 触发匹配
    trigger_matching(user_id, data)
    
    save_data()
    
    return jsonify({
        'status': 'success',
        'profile_id': profile_id,
        'updated_at': data['updated_at']
    })

@app.route('/api/v1/profiles/me', methods=['GET'])
def get_my_profile():
    """获取我的档案"""
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({'status': 'error', 'message': '未授权'}), 401
    
    profile = get_user_profile(user_id)
    if profile:
        return jsonify({'status': 'success', 'profile': profile})
    
    return jsonify({'status': 'error', 'message': '档案不存在'}), 404

@app.route('/api/v1/profiles/<profile_id>', methods=['GET'])
def get_profile(profile_id):
    """获取公开档案"""
    profile = profiles_db.get(profile_id)
    if not profile:
        return jsonify({'status': 'error', 'message': '档案不存在'}), 404
    
    # 脱敏
    public_profile = {
        'id': profile['id'],
        'user_id': profile['user_id'],
        'profile': profile.get('profile', {}),
        'capabilities': profile.get('capabilities', []),
        'resources': profile.get('resources', []),
        'needs': profile.get('needs', []),
        'business': profile.get('business', {})
    }
    
    return jsonify({'status': 'success', 'profile': public_profile})

@app.route('/api/v1/profiles/contact-info', methods=['PUT'])
def update_contact_info():
    """更新联系方式（隐私设置）"""
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({'status': 'error', 'message': '未授权'}), 401
    
    data = request.json
    
    if user_id not in users_db:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    
    users_db[user_id]['contact_info'] = {
        'weixin': data.get('weixin', ''),
        'email': data.get('email', ''),
        'phone': data.get('phone', ''),
        'qq': data.get('qq', ''),
        'preferred': data.get('preferred', 'weixin'),  # 偏好联系方式
        'public': data.get('public', False)  # 是否公开
    }
    
    save_data()
    
    return jsonify({
        'status': 'success',
        'message': '联系方式已更新'
    })

# ============ 匹配服务 ============

def extract_keywords(text):
    """提取关键词"""
    import re
    text = text.lower()
    keywords = []
    gpu_pattern = r'(rtx\s*\d+|a\d+|h\d+|v\d+|gtx\s*\d+)'
    gpu_matches = re.findall(gpu_pattern, text, re.IGNORECASE)
    keywords.extend([g.lower().replace(' ', '') for g in gpu_matches])
    words = re.findall(r'[\u4e00-\u9fa5]+|[a-z]+|[0-9]+', text)
    keywords.extend(words)
    return list(set(keywords))

def keyword_match(text1, text2):
    """关键词匹配"""
    kw1 = set(extract_keywords(text1))
    kw2 = set(extract_keywords(text2))
    if kw1 & kw2:
        return True
    t1 = text1.lower().replace(' ', '')
    t2 = text2.lower().replace(' ', '')
    return t1 in t2 or t2 in t1

def calculate_match_score(profile_a, profile_b):
    """计算匹配分数"""
    score = 0.0
    matches = []
    
    # 能力-需求匹配
    for need in profile_a.get('needs', []):
        for cap in profile_b.get('capabilities', []):
            if keyword_match(need.get('skill', ''), cap.get('skill', '')):
                match_score = 0.4
                if need.get('priority') == 'high':
                    match_score *= 1.3
                score += match_score
                matches.append({
                    'type': 'need-capability',
                    'need': need['skill'],
                    'capability': cap['skill'],
                    'score': match_score
                })
    
    # 资源-需求匹配
    for need in profile_a.get('needs', []):
        for res in profile_b.get('resources', []):
            if keyword_match(need.get('skill', ''), res.get('name', '')):
                match_score = 0.35
                score += match_score
                matches.append({
                    'type': 'need-resource',
                    'need': need['skill'],
                    'resource': res['name'],
                    'score': match_score
                })
    
    return {
        'score': min(round(score, 2), 1.0),
        'percentage': f"{min(score, 1.0) * 100:.0f}%",
        'matches': matches
    }

def trigger_matching(user_id, new_profile):
    """触发匹配"""
    for pid, profile in profiles_db.items():
        if profile.get('user_id') == user_id:
            continue
        
        # 双向匹配
        result_a = calculate_match_score(new_profile, profile)
        result_b = calculate_match_score(profile, new_profile)
        
        if result_a['score'] >= 0.5:
            # 创建匹配记录
            match_id = generate_id('match')
            matches_db[match_id] = {
                'id': match_id,
                'user_a': user_id,
                'user_b': profile['user_id'],
                'score': result_a['percentage'],
                'matches': result_a['matches'],
                'status': 'new',  # new, contacted, accepted, declined
                'created_at': datetime.now().isoformat()
            }
            
            # 发送通知给 user_b
            create_match_notification(
                to_user=profile['user_id'],
                from_user=user_id,
                match_score=result_a['percentage'],
                matches=result_a['matches']
            )
        
        if result_b['score'] >= 0.5:
            # 反向匹配通知
            create_match_notification(
                to_user=user_id,
                from_user=profile['user_id'],
                match_score=result_b['percentage'],
                matches=result_b['matches']
            )

def create_match_notification(to_user, from_user, match_score, matches):
    """创建匹配通知"""
    from_name = get_user_name(from_user)
    
    notif_id = generate_id('notif')
    notifications_db[notif_id] = {
        'id': notif_id,
        'user_id': to_user,
        'type': 'match',
        'from_user': from_user,
        'from_name': from_name,
        'match_score': match_score,
        'message': f"🔔 发现匹配！{from_name} 与你的匹配度 {match_score}",
        'matches': matches,
        'read': False,
        'created_at': datetime.now().isoformat()
    }

@app.route('/api/v1/match', methods=['POST'])
def request_match():
    """请求匹配"""
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({'status': 'error', 'message': '未授权'}), 401
    
    data = request.json
    
    my_profile = get_user_profile(user_id)
    if not my_profile:
        return jsonify({'status': 'error', 'message': '请先上传档案'}), 400
    
    # 匹配所有其他档案
    results = []
    for pid, profile in profiles_db.items():
        if profile.get('user_id') == user_id:
            continue
        
        result = calculate_match_score(my_profile, profile)
        if result['score'] >= data.get('min_score', 0.5):
            results.append({
                'profile_id': pid,
                'user_id': profile['user_id'],
                'user_name': profile.get('profile', {}).get('name', 'Unknown'),
                'match_score': result['percentage'],
                'matches': result['matches']
            })
    
    # 按分数排序
    results.sort(key=lambda x: float(x['match_score'].rstrip('%')), reverse=True)
    
    return jsonify({
        'status': 'success',
        'matches': results[:10],
        'total': len(results)
    })

@app.route('/api/v1/match/notifications', methods=['GET'])
def get_notifications():
    """获取匹配通知"""
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({'status': 'error', 'message': '未授权'}), 401
    
    notifications = [
        n for n in notifications_db.values()
        if n.get('user_id') == user_id
    ]
    
    # 按时间排序
    notifications.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        'status': 'success',
        'notifications': notifications,
        'unread': len([n for n in notifications if not n.get('read')])
    })

@app.route('/api/v1/match/notifications/<notif_id>/read', methods=['POST'])
def mark_notification_read(notif_id):
    """标记通知为已读"""
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({'status': 'error', 'message': '未授权'}), 401
    
    if notif_id in notifications_db:
        notifications_db[notif_id]['read'] = True
        save_data()
    
    return jsonify({'status': 'success'})

# ============ 连接请求（核心沟通机制）============

@app.route('/api/v1/connect', methods=['POST'])
def send_connect_request():
    """
    发起连接请求
    
    Request:
    {
        "to_user": "user_xxx",
        "match_id": "match_xxx",  // 可选
        "message": "你好，想聊聊合作",
        "exchange_contact": true  // 是否请求交换联系方式
    }
    """
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({'status': 'error', 'message': '未授权'}), 401
    
    data = request.json
    to_user = data.get('to_user')
    
    if not to_user:
        return jsonify({'status': 'error', 'message': '缺少目标用户'}), 400
    
    if to_user == user_id:
        return jsonify({'status': 'error', 'message': '不能连接自己'}), 400
    
    # 检查是否已有待处理的连接
    for cid, conn in contacts_db.items():
        if (conn['from_user'] == user_id and conn['to_user'] == to_user and conn['status'] == 'pending'):
            return jsonify({'status': 'error', 'message': '已有待处理的连接请求'}), 400
    
    # 创建连接请求
    connect_id = generate_id('conn')
    from_name = get_user_name(user_id)
    
    contacts_db[connect_id] = {
        'id': connect_id,
        'from_user': user_id,
        'from_name': from_name,
        'to_user': to_user,
        'match_id': data.get('match_id'),
        'message': data.get('message', ''),
        'exchange_contact': data.get('exchange_contact', False),
        'status': 'pending',  # pending, accepted, declined, expired
        'created_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
    }
    
    # 发送通知给目标用户
    notif_id = generate_id('notif')
    notifications_db[notif_id] = {
        'id': notif_id,
        'user_id': to_user,
        'type': 'connect_request',
        'from_user': user_id,
        'from_name': from_name,
        'connect_id': connect_id,
        'message': f"🤝 {from_name} 想要连接你：{data.get('message', '')}",
        'read': False,
        'created_at': datetime.now().isoformat()
    }
    
    save_data()
    
    return jsonify({
        'status': 'success',
        'connect_id': connect_id,
        'message': '连接请求已发送'
    })

@app.route('/api/v1/connect/requests', methods=['GET'])
def get_connect_requests():
    """获取我的连接请求"""
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({'status': 'error', 'message': '未授权'}), 401
    
    # 我发出的请求
    sent = [
        c for c in contacts_db.values()
        if c['from_user'] == user_id
    ]
    
    # 我收到的请求
    received = [
        c for c in contacts_db.values()
        if c['to_user'] == user_id
    ]
    
    # 按时间排序
    sent.sort(key=lambda x: x['created_at'], reverse=True)
    received.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        'status': 'success',
        'sent': sent,
        'received': received
    })

@app.route('/api/v1/connect/<connect_id>/accept', methods=['POST'])
def accept_connect(connect_id):
    """接受连接请求"""
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({'status': 'error', 'message': '未授权'}), 401
    
    if connect_id not in contacts_db:
        return jsonify({'status': 'error', 'message': '连接请求不存在'}), 404
    
    conn = contacts_db[connect_id]
    
    if conn['to_user'] != user_id:
        return jsonify({'status': 'error', 'message': '无权操作'}), 403
    
    if conn['status'] != 'pending':
        return jsonify({'status': 'error', 'message': f"连接已{conn['status']}"}), 400
    
    data = request.json or {}
    
    # 更新状态
    conn['status'] = 'accepted'
    conn['accepted_at'] = datetime.now().isoformat()
    conn['reply_message'] = data.get('message', '')
    
    # 如果请求交换联系方式，创建交换记录
    if conn.get('exchange_contact'):
        exchange_id = generate_id('exchange')
        contact_info_db[exchange_id] = {
            'id': exchange_id,
            'connect_id': connect_id,
            'user_a': conn['from_user'],
            'user_b': conn['to_user'],
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
    
    # 发送通知给发起者
    to_name = get_user_name(user_id)
    notif_id = generate_id('notif')
    notifications_db[notif_id] = {
        'id': notif_id,
        'user_id': conn['from_user'],
        'type': 'connect_accepted',
        'from_user': user_id,
        'from_name': to_name,
        'connect_id': connect_id,
        'message': f"✅ {to_name} 接受了你的连接请求！",
        'read': False,
        'created_at': datetime.now().isoformat()
    }
    
    save_data()
    
    return jsonify({
        'status': 'success',
        'message': '已接受连接请求',
        'connect_id': connect_id
    })

@app.route('/api/v1/connect/<connect_id>/decline', methods=['POST'])
def decline_connect(connect_id):
    """拒绝连接请求"""
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({'status': 'error', 'message': '未授权'}), 401
    
    if connect_id not in contacts_db:
        return jsonify({'status': 'error', 'message': '连接请求不存在'}), 404
    
    conn = contacts_db[connect_id]
    
    if conn['to_user'] != user_id:
        return jsonify({'status': 'error', 'message': '无权操作'}), 403
    
    if conn['status'] != 'pending':
        return jsonify({'status': 'error', 'message': f"连接已{conn['status']}"}), 400
    
    data = request.json or {}
    
    # 更新状态
    conn['status'] = 'declined'
    conn['declined_at'] = datetime.now().isoformat()
    conn['decline_reason'] = data.get('reason', '')
    
    # 发送通知给发起者
    to_name = get_user_name(user_id)
    notif_id = generate_id('notif')
    notifications_db[notif_id] = {
        'id': notif_id,
        'user_id': conn['from_user'],
        'type': 'connect_declined',
        'from_user': user_id,
        'from_name': to_name,
        'connect_id': connect_id,
        'message': f"❌ {to_name} 婉拒了你的连接请求",
        'read': False,
        'created_at': datetime.now().isoformat()
    }
    
    save_data()
    
    return jsonify({
        'status': 'success',
        'message': '已拒绝连接请求'
    })

# ============ 消息中转 ============

@app.route('/api/v1/messages', methods=['POST'])
def send_message():
    """
    发送消息
    
    Request:
    {
        "to_user": "user_xxx",
        "content": "你好！"
    }
    """
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({'status': 'error', 'message': '未授权'}), 401
    
    data = request.json
    to_user = data.get('to_user')
    content = data.get('content')
    
    if not to_user or not content:
        return jsonify({'status': 'error', 'message': '缺少必要参数'}), 400
    
    # 检查是否有已接受的连接
    has_connection = False
    for cid, conn in contacts_db.items():
        if conn['status'] == 'accepted':
            if (conn['from_user'] == user_id and conn['to_user'] == to_user) or \
               (conn['from_user'] == to_user and conn['to_user'] == user_id):
                has_connection = True
                break
    
    if not has_connection:
        return jsonify({'status': 'error', 'message': '请先建立连接'}), 403
    
    # 创建消息
    msg_id = generate_id('msg')
    from_name = get_user_name(user_id)
    
    messages_db[msg_id] = {
        'id': msg_id,
        'from_user': user_id,
        'from_name': from_name,
        'to_user': to_user,
        'content': content,
        'read': False,
        'created_at': datetime.now().isoformat()
    }
    
    # 发送通知
    notif_id = generate_id('notif')
    notifications_db[notif_id] = {
        'id': notif_id,
        'user_id': to_user,
        'type': 'message',
        'from_user': user_id,
        'from_name': from_name,
        'message': f"💬 {from_name}: {content[:50]}...",
        'read': False,
        'created_at': datetime.now().isoformat()
    }
    
    save_data()
    
    return jsonify({
        'status': 'success',
        'message_id': msg_id
    })

@app.route('/api/v1/messages/<with_user>', methods=['GET'])
def get_messages(with_user):
    """获取与某人的聊天记录"""
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({'status': 'error', 'message': '未授权'}), 401
    
    # 获取双方消息
    messages = [
        m for m in messages_db.values()
        if (m['from_user'] == user_id and m['to_user'] == with_user) or
           (m['from_user'] == with_user and m['to_user'] == user_id)
    ]
    
    # 按时间排序
    messages.sort(key=lambda x: x['created_at'])
    
    # 标记为已读
    for m in messages:
        if m['to_user'] == user_id and not m['read']:
            m['read'] = True
    
    save_data()
    
    return jsonify({
        'status': 'success',
        'messages': messages,
        'with_user': with_user,
        'with_user_name': get_user_name(with_user)
    })

@app.route('/api/v1/conversations', methods=['GET'])
def get_conversations():
    """获取我的对话列表"""
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({'status': 'error', 'message': '未授权'}), 401
    
    # 找出所有对话过的用户
    user_set = set()
    for m in messages_db.values():
        if m['from_user'] == user_id:
            user_set.add(m['to_user'])
        if m['to_user'] == user_id:
            user_set.add(m['from_user'])
    
    # 获取每个用户的最新消息
    conversations = []
    for other_user in user_set:
        msgs = [
            m for m in messages_db.values()
            if (m['from_user'] == user_id and m['to_user'] == other_user) or
               (m['from_user'] == other_user and m['to_user'] == user_id)
        ]
        msgs.sort(key=lambda x: x['created_at'], reverse=True)
        
        unread = len([m for m in msgs if m['to_user'] == user_id and not m['read']])
        
        conversations.append({
            'user_id': other_user,
            'user_name': get_user_name(other_user),
            'last_message': msgs[0] if msgs else None,
            'unread': unread
        })
    
    # 按最新消息排序
    conversations.sort(
        key=lambda x: x['last_message']['created_at'] if x['last_message'] else '0',
        reverse=True
    )
    
    return jsonify({
        'status': 'success',
        'conversations': conversations
    })

# ============ 联系方式交换 ============

@app.route('/api/v1/contact-info/<with_user>', methods=['GET'])
def get_contact_info(with_user):
    """获取对方的联系方式（需要双方同意）"""
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({'status': 'error', 'message': '未授权'}), 401
    
    # 检查是否有交换记录
    for eid, exchange in contact_info_db.items():
        if exchange['status'] == 'active':
            if (exchange['user_a'] == user_id and exchange['user_b'] == with_user) or \
               (exchange['user_a'] == with_user and exchange['user_b'] == user_id):
                # 返回对方的联系方式
                other_user = with_user
                if other_user in users_db:
                    contact = users_db[other_user].get('contact_info', {})
                    return jsonify({
                        'status': 'success',
                        'contact_info': {
                            'weixin': contact.get('weixin', ''),
                            'email': contact.get('email', ''),
                            'phone': contact.get('phone', ''),
                            'qq': contact.get('qq', ''),
                            'preferred': contact.get('preferred', 'weixin')
                        },
                        'user_name': get_user_name(other_user)
                    })
    
    return jsonify({
        'status': 'error',
        'message': '暂无权限查看联系方式，请先发起连接请求并选择交换联系方式'
    }), 403

@app.route('/api/v1/contact-info/share', methods=['POST'])
def share_contact_info():
    """
    主动分享联系方式
    
    Request:
    {
        "to_user": "user_xxx",
        "contact_type": "weixin",  // weixin, email, phone, qq
        "contact_value": "your_weixin_id"
    }
    """
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({'status': 'error', 'message': '未授权'}), 401
    
    data = request.json
    to_user = data.get('to_user')
    
    if not to_user:
        return jsonify({'status': 'error', 'message': '缺少目标用户'}), 400
    
    # 发送通知
    from_name = get_user_name(user_id)
    notif_id = generate_id('notif')
    
    notifications_db[notif_id] = {
        'id': notif_id,
        'user_id': to_user,
        'type': 'contact_shared',
        'from_user': user_id,
        'from_name': from_name,
        'message': f"📞 {from_name} 向你分享了联系方式：{data.get('contact_type')} - {data.get('contact_value')}",
        'contact_info': {
            'type': data.get('contact_type'),
            'value': data.get('contact_value')
        },
        'read': False,
        'created_at': datetime.now().isoformat()
    }
    
    save_data()
    
    return jsonify({
        'status': 'success',
        'message': '联系方式已分享'
    })

# ============ 需求广播 ============

@app.route('/api/v1/broadcast/need', methods=['POST'])
def broadcast_need():
    """广播需求"""
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({'status': 'error', 'message': '未授权'}), 401
    
    data = request.json
    
    broadcast_id = generate_id('broadcast')
    
    return jsonify({
        'status': 'success',
        'broadcast_id': broadcast_id,
        'message': '需求已广播',
        'reach_estimate': len(profiles_db)
    })

# ============ 健康检查 ============

@app.route('/api/v1/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'service': 'A2A Match API',
        'version': '2.0.0',
        'features': ['matching', 'connect', 'messaging', 'contact_exchange'],
        'stats': {
            'users': len(users_db),
            'profiles': len(profiles_db),
            'matches': len(matches_db),
            'contacts': len(contacts_db),
            'messages': len(messages_db)
        }
    })

# ============ API 文档 ============

@app.route('/api/v1/docs', methods=['GET'])
def api_docs():
    """API 文档"""
    return jsonify({
        'title': 'A2A Match API',
        'version': '2.0.0',
        'endpoints': {
            'auth': {
                'POST /api/v1/auth/register': '用户注册',
                'POST /api/v1/auth/login': '用户登录'
            },
            'profiles': {
                'POST /api/v1/profiles': '上传/更新档案',
                'GET /api/v1/profiles/me': '获取我的档案',
                'GET /api/v1/profiles/<id>': '获取公开档案',
                'PUT /api/v1/profiles/contact-info': '更新联系方式'
            },
            'matching': {
                'POST /api/v1/match': '请求匹配',
                'GET /api/v1/match/notifications': '获取匹配通知',
                'POST /api/v1/match/notifications/<id>/read': '标记已读'
            },
            'connect': {
                'POST /api/v1/connect': '发起连接请求',
                'GET /api/v1/connect/requests': '获取连接请求',
                'POST /api/v1/connect/<id>/accept': '接受连接',
                'POST /api/v1/connect/<id>/decline': '拒绝连接'
            },
            'messaging': {
                'POST /api/v1/messages': '发送消息',
                'GET /api/v1/messages/<user_id>': '获取聊天记录',
                'GET /api/v1/conversations': '获取对话列表'
            },
            'contact_exchange': {
                'GET /api/v1/contact-info/<user_id>': '获取联系方式',
                'POST /api/v1/contact-info/share': '主动分享联系方式'
            }
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("A2A Match API v2.0.0")
    print("=" * 60)
    print("功能: 匹配通知 | 连接请求 | 消息中转 | 联系方式交换")
    print("=" * 60)
    print("API 文档: http://localhost:5000/api/v1/docs")
    print("健康检查: http://localhost:5000/api/v1/health")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
