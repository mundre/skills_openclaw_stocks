"""
Meta Social Insights Fetcher
用途：每週自動抓取 IG / FB / Threads 數據，輸出 Excel 供 agent 分析
執行：python fetch_insights.py
輸出：~/.openclaw/workspace/socialMediaManager/reports/weekly_insights_YYYY-MM-DD.xlsx
"""

import os
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 從環境變數讀取設定（不要硬寫 token）---
ACCESS_TOKEN    = os.environ.get('META_ACCESS_TOKEN')
CLIENT_ID       = os.environ.get('META_CLIENT_ID')
CLIENT_SECRET   = os.environ.get('META_CLIENT_SECRET')
IG_ACCOUNT_ID   = os.environ.get('META_IG_ACCOUNT_ID')
PAGE_ID         = os.environ.get('META_PAGE_ID')

API_VERSION     = 'v25.0'
BASE_URL        = f'https://graph.facebook.com/{API_VERSION}'
OUTPUT_DIR      = os.path.expanduser('~/.openclaw/workspace/socialMediaManager/reports')
THREADS_USER_ID = IG_ACCOUNT_ID  # Threads user ID 通常與 IG business account ID 相同

# --- 2. Token 自動刷新 ---
def refresh_access_token(token):
    url = f'{BASE_URL}/oauth/access_token'
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'fb_exchange_token': token
    }
    response = requests.get(url, params=params).json()
    new_token = response.get('access_token')
    if new_token:
        print(f'✅ Token 刷新成功')
        return new_token
    else:
        print(f'⚠️ Token 刷新失敗：{response}')
        return token

# --- 3. Instagram Reels 數據 ---
def get_ig_reels():
    url = f'{BASE_URL}/{IG_ACCOUNT_ID}/media'
    params = {
        'fields': 'id,caption,media_type,timestamp,permalink',
        'access_token': ACCESS_TOKEN,
        'limit': 20
    }
    response = requests.get(url, params=params).json()
    reels = [m for m in response.get('data', []) if m.get('media_type') == 'VIDEO']

    rows = []
    for reel in reels:
        metrics = 'reach,plays,ig_reels_avg_watch_time,ig_reels_video_view_total_time,likes,comments,saves,shares'
        ins_url = f'{BASE_URL}/{reel["id"]}/insights'
        ins_params = {'metric': metrics, 'access_token': ACCESS_TOKEN}
        ins = requests.get(ins_url, params=ins_params).json()
        data = {m['name']: m['values'][0]['value'] for m in ins.get('data', [])}

        plays = data.get('plays', 1) or 1
        likes = data.get('likes', 0)
        comments = data.get('comments', 0)
        saves = data.get('saves', 0)
        shares = data.get('shares', 0)
        reach = data.get('reach', 0)
        engagement = likes + comments + saves + shares
        engagement_rate = round(engagement / reach * 100, 2) if reach else 0

        rows.append({
            '平台': 'Instagram Reels',
            '發布時間': reel['timestamp'],
            '內容摘要': (reel.get('caption') or '')[:30],
            '連結': reel.get('permalink', ''),
            '觸及人數': reach,
            '播放次數': plays,
            '平均觀看時長(秒)': round(data.get('ig_reels_avg_watch_time', 0) / 1000, 2),
            '按讚數': likes,
            '留言數': comments,
            '收藏數': saves,
            '分享數': shares,
            '互動總數': engagement,
            '互動率(%)': engagement_rate,
        })
    return rows

# --- 4. Instagram 一般貼文（輪播/靜態圖）---
def get_ig_posts():
    url = f'{BASE_URL}/{IG_ACCOUNT_ID}/media'
    params = {
        'fields': 'id,caption,media_type,timestamp,permalink',
        'access_token': ACCESS_TOKEN,
        'limit': 20
    }
    response = requests.get(url, params=params).json()
    posts = [m for m in response.get('data', []) if m.get('media_type') in ('IMAGE', 'CAROUSEL_ALBUM')]

    rows = []
    for post in posts:
        metrics = 'reach,impressions,likes,comments,saves,shares'
        ins_url = f'{BASE_URL}/{post["id"]}/insights'
        ins_params = {'metric': metrics, 'access_token': ACCESS_TOKEN}
        ins = requests.get(ins_url, params=ins_params).json()
        data = {m['name']: m['values'][0]['value'] for m in ins.get('data', [])}

        reach = data.get('reach', 0)
        likes = data.get('likes', 0)
        comments = data.get('comments', 0)
        saves = data.get('saves', 0)
        shares = data.get('shares', 0)
        engagement = likes + comments + saves + shares
        engagement_rate = round(engagement / reach * 100, 2) if reach else 0

        rows.append({
            '平台': f'Instagram {post["media_type"]}',
            '發布時間': post['timestamp'],
            '內容摘要': (post.get('caption') or '')[:30],
            '連結': post.get('permalink', ''),
            '觸及人數': reach,
            '播放次數': data.get('impressions', 0),
            '平均觀看時長(秒)': '-',
            '按讚數': likes,
            '留言數': comments,
            '收藏數': saves,
            '分享數': shares,
            '互動總數': engagement,
            '互動率(%)': engagement_rate,
        })
    return rows

# --- 5. Facebook 粉專貼文數據 ---
def get_fb_posts():
    url = f'{BASE_URL}/{PAGE_ID}/posts'
    params = {
        'fields': 'id,message,created_time,permalink_url',
        'access_token': ACCESS_TOKEN,
        'limit': 20
    }
    response = requests.get(url, params=params).json()

    rows = []
    for post in response.get('data', []):
        ins_url = f'{BASE_URL}/{post["id"]}/insights'
        ins_params = {
            'metric': 'post_impressions_unique,post_engaged_users,post_reactions_like_total,post_clicks',
            'access_token': ACCESS_TOKEN
        }
        ins = requests.get(ins_url, params=ins_params).json()
        data = {m['name']: m['values'][0]['value'] for m in ins.get('data', [])}

        reach = data.get('post_impressions_unique', 0)
        engaged = data.get('post_engaged_users', 0)
        engagement_rate = round(engaged / reach * 100, 2) if reach else 0

        rows.append({
            '平台': 'Facebook',
            '發布時間': post['created_time'],
            '內容摘要': (post.get('message') or '')[:30],
            '連結': post.get('permalink_url', ''),
            '觸及人數': reach,
            '播放次數': '-',
            '平均觀看時長(秒)': '-',
            '按讚數': data.get('post_reactions_like_total', 0),
            '留言數': '-',
            '收藏數': '-',
            '分享數': '-',
            '互動總數': engaged,
            '互動率(%)': engagement_rate,
        })
    return rows

# --- 6. Threads 數據 ---
def get_threads_posts():
    url = f'{BASE_URL}/{THREADS_USER_ID}/threads'
    params = {
        'fields': 'id,text,timestamp,permalink',
        'access_token': ACCESS_TOKEN,
        'limit': 20
    }
    response = requests.get(url, params=params).json()

    rows = []
    for post in response.get('data', []):
        ins_url = f'{BASE_URL}/{post["id"]}/insights'
        ins_params = {
            'metric': 'views,likes,replies,reposts,quotes',
            'access_token': ACCESS_TOKEN
        }
        ins = requests.get(ins_url, params=ins_params).json()
        data = {m['name']: m['values'][0]['value'] for m in ins.get('data', [])}

        views = data.get('views', 0)
        likes = data.get('likes', 0)
        replies = data.get('replies', 0)
        reposts = data.get('reposts', 0)
        quotes = data.get('quotes', 0)
        engagement = likes + replies + reposts + quotes
        engagement_rate = round(engagement / views * 100, 2) if views else 0

        rows.append({
            '平台': 'Threads',
            '發布時間': post['timestamp'],
            '內容摘要': (post.get('text') or '')[:30],
            '連結': post.get('permalink', ''),
            '觸及人數': views,
            '播放次數': '-',
            '平均觀看時長(秒)': '-',
            '按讚數': likes,
            '留言數': replies,
            '收藏數': reposts,
            '分享數': quotes,
            '互動總數': engagement,
            '互動率(%)': engagement_rate,
        })
    return rows

# --- 7. 主程式 ---
def main():
    global ACCESS_TOKEN

    if not ACCESS_TOKEN:
        print('❌ 找不到 META_ACCESS_TOKEN，請執行：openclaw configure set META_ACCESS_TOKEN "你的token"')
        return

    # 自動刷新 token
    ACCESS_TOKEN = refresh_access_token(ACCESS_TOKEN)

    print('📥 抓取 Instagram Reels...')
    ig_reels = get_ig_reels()

    print('📥 抓取 Instagram 貼文...')
    ig_posts = get_ig_posts()

    print('📥 抓取 Facebook 貼文...')
    fb_posts = get_fb_posts()

    print('📥 抓取 Threads 貼文...')
    threads_posts = get_threads_posts()

    all_data = ig_reels + ig_posts + fb_posts + threads_posts

    if not all_data:
        print('⚠️ 沒有抓到任何數據，請確認帳號 ID 和 token 是否正確')
        return

    df = pd.DataFrame(all_data)
    df['發布時間'] = pd.to_datetime(df['發布時間']).dt.strftime('%Y-%m-%d %H:%M')
    df = df.sort_values('發布時間', ascending=False)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = datetime.now().strftime('%Y-%m-%d')
    output_path = os.path.join(OUTPUT_DIR, f'weekly_insights_{today}.xlsx')
    df.to_excel(output_path, index=False)

    print(f'✅ 報告已輸出：{output_path}')
    print(f'   共 {len(all_data)} 筆貼文數據')

if __name__ == '__main__':
    main()
