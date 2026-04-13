#!/usr/bin/env python3
"""
Stock Price Alert - 股价异动实时提醒脚本
实时监控持仓股票价格波动，触发邮件告警和Sonos语音播报
"""

import os
import sys
import time
import json
import datetime
import argparse
from dotenv import load_dotenv
import yfinance as yf

# Gmail API imports
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
import subprocess

# 加载环境变量
load_dotenv()

# =============================================================================
# 核心配置 - 请根据您的实际持仓修改此处
# =============================================================================
PORTFOLIO = {
    'AAPL': 15,      # 苹果公司
    'MSFT': 8,       # 微软
    'GOOGL': 5,      # 谷歌
    'TSLA': 12,      # 特斯拉
    'NVDA': 10       # 英伟达
}

# =============================================================================
# 告警配置（可通过 .env 覆盖）
# =============================================================================
ALERT_THRESHOLD = float(os.getenv('ALERT_THRESHOLD', 5.0))  # 涨跌幅告警阈值 %
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 300))      # 检查间隔（秒）
ALERT_COOLDOWN = int(os.getenv('ALERT_COOLDOWN', 3600))     # 重复告警静默期（秒）
SONOS_SPEAKER_NAME = os.getenv('SONOS_SPEAKER', 'Living Room')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', 'user@example.com')
ALERT_LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'alert_history.json')

# 全局变量 - 告警状态追踪
alert_history = {}
STOCK_NAMES = {
    'AAPL': '苹果公司',
    'MSFT': '微软',
    'GOOGL': '谷歌',
    'TSLA': '特斯拉',
    'NVDA': '英伟达',
    'AMZN': '亚马逊',
    'META': 'Meta',
    'BRK-B': '伯克希尔哈撒韦',
    'JPM': '摩根大通',
    'V': 'Visa'
}

# =============================================================================
# 工具函数
# =============================================================================

def load_alert_history():
    """加载告警历史记录"""
    global alert_history
    if os.path.exists(ALERT_LOG_FILE):
        try:
            with open(ALERT_LOG_FILE, 'r') as f:
                alert_history = json.load(f)
        except:
            alert_history = {}
    else:
        alert_history = {}

def save_alert_history():
    """保存告警历史记录"""
    os.makedirs(os.path.dirname(ALERT_LOG_FILE), exist_ok=True)
    with open(ALERT_LOG_FILE, 'w') as f:
        json.dump(alert_history, f, indent=2)

def can_alert(ticker: str) -> bool:
    """检查该股票是否在静默期内，可以发出告警"""
    if ticker not in alert_history:
        return True
    last_alert_time = alert_history[ticker]['timestamp']
    elapsed = time.time() - last_alert_time
    return elapsed >= ALERT_COOLDOWN

def record_alert(ticker: str, price: float, change_pct: float):
    """记录告警历史"""
    alert_history[ticker] = {
        'timestamp': time.time(),
        'datetime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'price': price,
        'change_pct': change_pct
    }
    save_alert_history()

# =============================================================================
# 行情获取与异动检测
# =============================================================================

def get_stock_prices() -> dict:
    """获取所有持仓股票的实时价格和涨跌幅"""
    tickers = yf.Tickers(list(PORTFOLIO.keys()))
    result = {}
    
    for ticker in PORTFOLIO.keys():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='2d')
            
            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                change_pct = ((current - prev_close) / prev_close) * 100
                
                result[ticker] = {
                    'ticker': ticker,
                    'name': STOCK_NAMES.get(ticker, ticker),
                    'current_price': current,
                    'prev_close': prev_close,
                    'change_pct': change_pct,
                    'change_amount': current - prev_close
                }
        except Exception as e:
            print(f"获取 {ticker} 行情数据失败: {e}")
            continue
    
    return result

def check_price_alerts(prices: dict, threshold: float = None) -> list:
    """检查价格异动，返回告警列表"""
    actual_threshold = threshold if threshold else ALERT_THRESHOLD
    alerts = []
    
    for ticker, data in prices.items():
        abs_change = abs(data['change_pct'])
        
        if abs_change >= actual_threshold and can_alert(ticker):
            alerts.append({
                **data,
                'alert_reason': f"单日涨跌幅 {data['change_pct']:+.2f}% 超过阈值 {actual_threshold}%",
                'severity': 'HIGH' if abs_change >= 10 else 'MEDIUM'
            })
    
    return alerts

# =============================================================================
# Gmail 邮件告警
# =============================================================================

def send_email_alert(alert: dict) -> bool:
    """通过 Gmail 发送告警邮件"""
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    
    # 查找凭证文件
    token_paths = [
        "config/token.json",
        "../config/token.json",
        "../../../config/token.json",
        os.path.expanduser("~/.openclaw/workspace/config/token.json")
    ]
    
    creds = None
    for token_path in token_paths:
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
                break
            except:
                continue
    
    if not creds or not creds.valid:
        print(f"⚠️ Gmail 凭证未找到或无效，跳过邮件发送")
        return False
    
    try:
        service = build("gmail", "v1", credentials=creds)
        
        # 构建 HTML 邮件内容
        direction_icon = "📈" if alert['change_pct'] > 0 else "📉"
        severity_color = "#dc2626" if alert['severity'] == 'HIGH' else "#d97706"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: {severity_color}; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">
                        {direction_icon} 股价异动告警：{alert['name']} ({alert['ticker']})
                    </h1>
                </div>
                
                <div style="padding: 20px; background: #f9fafb; border-radius: 0 0 8px 8px;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                                <strong>告警时间：</strong>
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                                {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                                <strong>当前价格：</strong>
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                                <span style="font-size: 18px; font-weight: bold;">
                                    ${alert['current_price']:.2f}
                                </span>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                                <strong>涨跌幅：</strong>
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; color: {'#16a34a' if alert['change_pct'] >= 0 else '#dc2626'}; font-weight: bold;">
                                {alert['change_pct']:+.2f}%
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                                <strong>变动金额：</strong>
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                                ${alert['change_amount']:+.2f}
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                                <strong>告警级别：</strong>
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                                <span style="background: {severity_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;">
                                    {alert['severity']}
                                </span>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 12px;">
                                <strong>告警原因：</strong>
                            </td>
                            <td style="padding: 12px;">
                                {alert['alert_reason']}
                            </td>
                        </tr>
                    </table>
                    
                    <div style="margin-top: 20px; padding: 15px; background: #dbeafe; border-radius: 8px;">
                        <strong>💡 建议：</strong>
                        {'建议关注成交量变化，可考虑分批止盈。' if alert['change_pct'] > 0 else '建议评估基本面变化，可考虑补仓或止损。'}
                    </div>
                </div>
            </body>
        </html>
        """
        
        message = MIMEText(html, 'html')
        message['to'] = RECIPIENT_EMAIL
        message['subject'] = f"⚠️ 股价告警：{alert['ticker']} {alert['change_pct']:+.2f}% - {alert['name']}"
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        print(f"✅ 告警邮件已发送至 {RECIPIENT_EMAIL}")
        return True
        
    except HttpError as error:
        print(f"❌ 发送邮件失败: {error}")
        return False

# =============================================================================
# Sonos 语音播报
# =============================================================================

def sonos_announce_alert(alert: dict) -> bool:
    """通过 Sonos 扬声器语音播报告警"""
    direction = "上涨" if alert['change_pct'] > 0 else "下跌"
    
    announcement = f"""
    注意！股价异动提醒。
    {alert['name']}当前价格为 {alert['current_price']:.1f} 美元，
    较昨日收盘价{direction}了 {abs(alert['change_pct']):.1f} 个百分点，
    已触发预设的告警阈值，请您及时关注持仓变化。
    """
    
    try:
        # 使用 Sonos CLI 进行语音播报
        result = subprocess.run(
            ["sonos", SONOS_SPEAKER_NAME, "say", announcement, "--voice", "zh-CN-Wavenet-A"],
            check=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        print(f"✅ Sonos 语音播报已在 {SONOS_SPEAKER_NAME} 播放")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Sonos 播报失败: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print(f"❌ Sonos 播报超时")
        return False
    except FileNotFoundError:
        print(f"⚠️ Sonos CLI 未安装，跳过语音播报")
        return False

# =============================================================================
# 告警处理主逻辑
# =============================================================================

def process_alerts(alerts: list) -> tuple:
    """处理所有告警：发送邮件 + 语音播报"""
    email_success = 0
    sonos_success = 0
    
    for alert in alerts:
        print(f"\n🚨 检测到异动：{alert['ticker']} {alert['change_pct']:+.2f}%")
        print(f"   当前价格：${alert['current_price']:.2f}")
        print(f"   告警级别：{alert['severity']}")
        
        # 发送邮件
        if send_email_alert(alert):
            email_success += 1
        
        # Sonos 播报
        if sonos_announce_alert(alert):
            sonos_success += 1
        
        # 记录告警
        record_alert(alert['ticker'], alert['current_price'], alert['change_pct'])
    
    return email_success, sonos_success

# =============================================================================
# 运行模式
# =============================================================================

def run_monitor(custom_threshold=None):
    """常驻监控模式"""
    print(f"🔍 启动股价异动实时监控...")
    print(f"   监控股票：{', '.join(PORTFOLIO.keys())}")
    print(f"   告警阈值：{custom_threshold if custom_threshold else ALERT_THRESHOLD}%")
    print(f"   检查间隔：{CHECK_INTERVAL} 秒")
    print(f"   静默期：{ALERT_COOLDOWN} 秒")
    print("=" * 60)
    
    load_alert_history()
    
    while True:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n[{current_time}] 执行价格检查...")
        
        try:
            prices = get_stock_prices()
            
            if not prices:
                print("   ⚠️ 未能获取任何行情数据")
                time.sleep(CHECK_INTERVAL)
                continue
            
            # 显示当前状态
            for ticker, data in prices.items():
                indicator = "✓" if abs(data['change_pct']) < ALERT_THRESHOLD else "⚠"
                print(f"   {indicator} {ticker}: ${data['current_price']:.2f} ({data['change_pct']:+.2f}%)")
            
            # 检测并处理告警
            alerts = check_price_alerts(prices, custom_threshold)
            
            if alerts:
                email_ok, sonos_ok = process_alerts(alerts)
                print(f"\n   ✅ 处理完成：邮件 {email_ok}/{len(alerts)}，语音 {sonos_ok}/{len(alerts)}")
            else:
                print("   ✅ 无异常波动")
        
        except Exception as e:
            print(f"   ❌ 执行出错: {e}")
        
        time.sleep(CHECK_INTERVAL)

def run_check_once(custom_threshold=None):
    """单次检查模式（用于 cron）"""
    load_alert_history()
    
    prices = get_stock_prices()
    alerts = check_price_alerts(prices, custom_threshold)
    
    if alerts:
        process_alerts(alerts)
        print(f"检测到 {len(alerts)} 个价格异动告警")
        sys.exit(0)
    else:
        print("无异常波动")
        sys.exit(0)

def run_test_alert():
    """测试告警通知"""
    print("🧪 测试告警通知渠道...")
    
    test_alert = {
        'ticker': 'TEST',
        'name': '测试股票',
        'current_price': 100.0,
        'prev_close': 94.0,
        'change_pct': 6.38,
        'change_amount': 6.0,
        'alert_reason': '测试告警 - 验证通知渠道',
        'severity': 'MEDIUM'
    }
    
    print("\n📧 测试邮件发送...")
    email_ok = send_email_alert(test_alert)
    
    print("\n🔊 测试 Sonos 播报...")
    sonos_ok = sonos_announce_alert(test_alert)
    
    print(f"\n📊 测试结果：")
    print(f"   邮件：{'✅ 成功' if email_ok else '❌ 失败'}")
    print(f"   语音：{'✅ 成功' if sonos_ok else '❌ 失败'}")

def show_status():
    """显示当前配置和状态"""
    load_alert_history()
    
    print("=" * 60)
    print("📊 股价异动监控 - 状态报告")
    print("=" * 60)
    print(f"\n📌 监控配置：")
    print(f"   告警阈值：{ALERT_THRESHOLD}%")
    print(f"   检查间隔：{CHECK_INTERVAL} 秒")
    print(f"   静默期：{ALERT_COOLDOWN} 秒")
    print(f"   Sonos 音箱：{SONOS_SPEAKER_NAME}")
    print(f"   告警邮箱：{RECIPIENT_EMAIL}")
    
    print(f"\n💼 监控持仓：")
    for ticker, shares in PORTFOLIO.items():
        name = STOCK_NAMES.get(ticker, ticker)
        print(f"   {ticker} ({name}): {shares} 股")
    
    print(f"\n⏰ 最近告警记录：")
    if alert_history:
        for ticker, record in alert_history.items():
            print(f"   {ticker}: {record['datetime']} - ${record['price']:.2f} ({record['change_pct']:+.2f}%)")
    else:
        print(f"   暂无告警记录")
    print("=" * 60)

# =============================================================================
# 主入口
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='股价异动实时提醒工具')
    parser.add_argument('--monitor', action='store_true', help='启动常驻监控模式')
    parser.add_argument('--check-once', action='store_true', help='执行单次检查后退出')
    parser.add_argument('--threshold', type=float, help='自定义告警阈值（百分比）')
    parser.add_argument('--test-alert', action='store_true', help='测试告警通知渠道')
    parser.add_argument('--status', action='store_true', help='显示配置和状态')
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.test_alert:
        run_test_alert()
    elif args.monitor:
        run_monitor(args.threshold)
    elif args.check_once:
        run_check_once(args.threshold)
    else:
        parser.print_help()
        print("\n💡 示例：")
        print("  python stock_price_alert.py --monitor          # 启动实时监控")
        print("  python stock_price_alert.py --check-once       # 单次检查（用于cron）")
        print("  python stock_price_alert.py --test-alert       # 测试通知渠道")
        print("  python stock_price_alert.py --status           # 查看配置状态")

if __name__ == "__main__":
    main()
