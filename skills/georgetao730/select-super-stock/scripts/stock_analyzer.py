#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优质股票筛选专家 - 主分析脚本 (v1.1)
基于双核心模型：长线稳步上涨型 + 历史低位反弹型
数据源：AKShare（优先）> 东方财富 HTTP API > 新浪财经 HTTP API
"""

import sys
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

try:
    import pandas as pd
    import akshare as ak
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False


@dataclass
class StockSignal:
    """股票信号"""
    symbol: str
    name: str
    category: str  # 长线稳步上涨型 / 历史低位反弹型 / 垃圾股规避 / 观察区
    score: int  # 0-100
    similar_stock: str  # 相似标的参考
    technical_analysis: Dict = field(default_factory=dict)
    fundamental_analysis: Dict = field(default_factory=dict)
    recommendation: str = ""
    strategy: str = ""
    risks: List[str] = field(default_factory=list)


def get_stock_name(symbol: str) -> str:
    """获取股票名称"""
    # 1. 尝试 AKShare
    if HAS_AKSHARE:
        try:
            stock_info = ak.stock_individual_info_em(symbol=symbol)
            if stock_info is not None and len(stock_info) > 0:
                for _, row in stock_info.iterrows():
                    if '股票简称' in str(row.get('item', '')):
                        return row.get('value', symbol)
        except Exception:
            pass
    
    # 2. 尝试东方财富 HTTP API
    try:
        url = f"http://push2.eastmoney.com/api/qt/stock/get?secid=1.{symbol}&fields=f58,f57"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get('data') and data['data'].get('f58'):
            return data['data']['f58']
    except Exception:
        pass
    
    return symbol


def fetch_kline_from_eastmoney(symbol: str, period: str = "101", count: int = 500) -> Optional[pd.DataFrame]:
    """
    从东方财富获取 K 线数据（HTTP API）
    
    period: 001=日线，002=周线，003=月线
    """
    try:
        # 东方财富 HTTP API
        if period == "weekly":
            klt = "002"
        elif period == "monthly":
            klt = "003"
        else:
            klt = "001"
        
        fqt = "1"  # 前复权
        
        url = f"http://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.{symbol}&klt={klt}&fqt={fqt}&beg=19900101&end=20991231&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get('data') is None or data['data'].get('klines') is None:
            return None
        
        klines = data['data']['klines']
        if len(klines) == 0:
            return None
        
        # 解析数据
        rows = []
        for line in klines[-count:]:
            parts = line.split(',')
            if len(parts) >= 11:
                rows.append({
                    'date': parts[0],
                    'open': float(parts[1]),
                    'close': float(parts[2]),
                    'high': float(parts[3]),
                    'low': float(parts[4]),
                    'volume': float(parts[5]),
                    'turnover': float(parts[6]) if parts[6] else 0,
                    'amplitude': float(parts[7]) if parts[7] else 0,
                    'pct_change': float(parts[8]) if parts[8] else 0,
                    'change': float(parts[9]) if parts[9] else 0,
                    'turnover_rate': float(parts[10]) if parts[10] else 0
                })
        
        return pd.DataFrame(rows)
    
    except Exception as e:
        print(f"东方财富数据获取失败：{e}")
        return None


def fetch_kline_from_sina(symbol: str, count: int = 500) -> Optional[pd.DataFrame]:
    """
    从新浪财经获取 K 线数据（HTTP API）
    
    支持日线数据
    """
    try:
        # 确定市场
        if symbol.startswith('6'):
            market = 'sh'
        else:
            market = 'sz'
        
        # 获取日线数据（最大 1024 条）
        url = f"http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={market}{symbol}&scale=240&datalen={count}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if not data or len(data) == 0:
            return None
        
        # 解析数据
        rows = []
        for item in data:
            rows.append({
                'date': item['day'],
                'open': float(item['open']),
                'close': float(item['close']),
                'high': float(item['high']),
                'low': float(item['low']),
                'volume': float(item['volume']),
                'turnover': 0,
                'amplitude': 0,
                'pct_change': 0,
                'change': 0,
                'turnover_rate': 0
            })
        
        df = pd.DataFrame(rows)
        
        # 计算涨跌幅
        df['pct_change'] = df['close'].pct_change() * 100
        df['change'] = df['close'].diff()
        
        return df
    
    except Exception as e:
        print(f"新浪财经数据获取失败：{e}")
        return None


def fetch_kline_data(symbol: str, period: str = "daily", count: int = 500) -> pd.DataFrame:
    """
    获取 K 线数据（多数据源 fallback）
    
    优先级：AKShare > 东方财富 > 新浪财经
    
    Args:
        symbol: 股票代码
        period: daily/weekly/monthly
        count: 数据条数
    
    Returns:
        DataFrame with columns: date, open, high, low, close, volume
    """
    df = pd.DataFrame()
    
    # 1. 尝试 AKShare
    if HAS_AKSHARE:
        try:
            print(f"  [1/3] 尝试 AKShare...")
            df = ak.stock_zh_a_hist(symbol=symbol, period=period, adjust="qfq")
            if df is not None and len(df) > 0:
                print(f"  ✓ AKShare 成功获取 {len(df)} 条数据")
                df = df.tail(count)
                df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 
                              'turnover', 'amplitude', 'pct_change', 'change', 'turnover_rate']
                return df.reset_index(drop=True)
        except Exception as e:
            print(f"  ✗ AKShare 失败：{e}")
    
    # 2. 尝试东方财富（支持日/周/月线）
    try:
        print(f"  [2/3] 尝试东方财富...")
        df = fetch_kline_from_eastmoney(symbol, period, count)
        if df is not None and len(df) > 0:
            print(f"  ✓ 东方财富成功获取 {len(df)} 条数据")
            return df.reset_index(drop=True)
    except Exception as e:
        print(f"  ✗ 东方财富失败：{e}")
    
    # 3. 尝试新浪财经（仅日线）
    if period == "daily":
        try:
            print(f"  [3/3] 尝试新浪财经...")
            df = fetch_kline_from_sina(symbol, count)
            if df is not None and len(df) > 0:
                print(f"  ✓ 新浪财经成功获取 {len(df)} 条数据")
                return df.reset_index(drop=True)
        except Exception as e:
            print(f"  ✗ 新浪财经失败：{e}")
    
    print(f"  ❌ 所有数据源均失败")
    return pd.DataFrame()


def calculate_ma(prices: pd.Series, periods: List[int] = [5, 10, 20, 60, 120, 250]) -> Dict[str, pd.Series]:
    """计算均线"""
    mas = {}
    for period in periods:
        mas[f'MA{period}'] = prices.rolling(window=period).mean()
    return mas


def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
    """计算 MACD"""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd = (dif - dea) * 2
    
    return {
        'DIF': dif,
        'DEA': dea,
        'MACD': macd
    }


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """计算 RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def check_model_a(df: pd.DataFrame, mas: Dict) -> Tuple[bool, int]:
    """
    检查是否符合模型 A：长线稳步上涨型
    
    Returns:
        (是否符合，评分)
    """
    if len(df) < 250:
        return False, 0
    
    score = 0
    current_price = df['close'].iloc[-1]
    
    # 1. 年线多头排列 (250 日均线向上)
    ma250_current = mas['MA250'].iloc[-1]
    ma250_prev = mas['MA250'].iloc[-30] if len(mas['MA250']) > 30 else ma250_current
    
    if current_price > ma250_current:
        score += 20  # 股价在年线上方
    
    if ma250_current > ma250_prev:
        score += 15  # 年线向上
    
    # 2. 均线多头排列
    ma_order = [
        mas['MA5'].iloc[-1],
        mas['MA10'].iloc[-1],
        mas['MA20'].iloc[-1],
        mas['MA60'].iloc[-1],
        mas['MA120'].iloc[-1],
        mas['MA250'].iloc[-1]
    ]
    
    if all(ma_order[i] >= ma_order[i+1] for i in range(len(ma_order)-1)):
        score += 25  # 完美多头排列
    
    # 3. MACD 零轴上方
    macd = calculate_macd(df['close'])
    if macd['DIF'].iloc[-1] > 0:
        score += 20  # DIF 在零轴上方
    
    # 4. 温和上涨（非暴涨）
    price_change_60d = (df['close'].iloc[-1] / df['close'].iloc[-60] - 1) * 100 if len(df) > 60 else 0
    if 5 < price_change_60d < 50:
        score += 20  # 60 日涨幅在 5%-50% 之间，稳步上涨
    
    return score >= 60, score


def check_model_b(df: pd.DataFrame, mas: Dict) -> Tuple[bool, int]:
    """
    检查是否符合模型 B：历史低位反弹型
    
    Returns:
        (是否符合，评分)
    """
    if len(df) < 250:
        return False, 0
    
    score = 0
    current_price = df['close'].iloc[-1]
    
    # 1. 距离历史高点大幅回撤
    high_52w = df['high'].max()
    drawdown = (high_52w - current_price) / high_52w * 100
    
    if drawdown > 50:
        score += 30  # 回撤超过 50%
    elif drawdown > 30:
        score += 20  # 回撤超过 30%
    
    # 2. 底部企稳信号
    low_60d = df['low'].iloc[-60:].min() if len(df) > 60 else current_price
    if current_price > low_60d * 1.05:
        score += 20  # 从最低点反弹超过 5%
    
    # 3. MACD 底背离
    macd = calculate_macd(df['close'])
    macd_recent = macd['MACD'].iloc[-10:].mean()
    macd_prev = macd['MACD'].iloc[-30:-20].mean() if len(macd['MACD']) > 30 else macd_recent
    
    if macd_recent > macd_prev and macd_recent < 0:
        score += 25  # MACD 底背离
    
    # 4. 温和放量
    volume_recent = df['volume'].iloc[-10:].mean()
    volume_prev = df['volume'].iloc[-30:-10].mean() if len(df) > 30 else volume_recent
    
    if volume_recent > volume_prev * 1.2:
        score += 15  # 温和放量
    
    # 5. 股价在底部区域
    if current_price < df['high'].max() * 0.6:
        score += 10  # 处于历史低位
    
    return score >= 50, score


def check_blacklist(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    检查是否属于黑名单股票（垃圾股）
    
    Returns:
        (是否规避，原因列表)
    """
    reasons = []
    
    if len(df) < 60:
        return False, []
    
    current_price = df['close'].iloc[-1]
    
    # 1. 暴涨暴跌
    price_changes = df['pct_change'].iloc[-30:] if 'pct_change' in df.columns else pd.Series()
    if len(price_changes) > 0:
        extreme_days = (price_changes.abs() > 9).sum()
        if extreme_days >= 3:
            reasons.append("近期多次出现涨跌停，波动极端")
    
    # 2. 高位巨量换手
    turnover_rate = df['turnover_rate'].iloc[-1] if 'turnover_rate' in df.columns else 0
    if turnover_rate > 20:
        reasons.append(f"单日换手率过高 ({turnover_rate:.1f}%)，警惕出货")
    
    # 3. 长上影线/下影线频繁
    recent_klines = df.tail(20)
    long_shadow_days = 0
    for _, row in recent_klines.iterrows():
        upper_shadow = (row['high'] - max(row['open'], row['close'])) / row['close']
        lower_shadow = (min(row['open'], row['close']) - row['low']) / row['close']
        if upper_shadow > 0.05 or lower_shadow > 0.05:
            long_shadow_days += 1
    
    if long_shadow_days >= 8:
        reasons.append("K 线频繁出现长影线，走势不连贯")
    
    # 4. 织布机走势（横盘震荡）
    price_range = (df['high'].iloc[-30:].max() - df['low'].iloc[-30:].min()) / df['close'].iloc[-30] * 100
    if price_range < 10:
        reasons.append("长期横盘震荡，疑似庄家控盘")
    
    return len(reasons) >= 2, reasons


def get_fundamental_data(symbol: str) -> Dict:
    """获取基本面数据"""
    data = {
        'pe_ratio': None,
        'pb_ratio': None,
        'roe': None,
        'dividend_yield': None,
        'market_cap': None,
        'revenue_growth': None,
        'profit_growth': None
    }
    
    try:
        # 获取个股信息
        info = ak.stock_individual_info_em(symbol=symbol)
        if info is not None:
            for _, row in info.iterrows():
                if '市盈率' in str(row['item']):
                    try:
                        data['pe_ratio'] = float(row['value'])
                    except:
                        pass
                elif '市净率' in str(row['item']):
                    try:
                        data['pb_ratio'] = float(row['value'])
                    except:
                        pass
                elif '总市值' in str(row['item']):
                    try:
                        data['market_cap'] = row['value']
                    except:
                        pass
    except Exception:
        pass
    
    return data


def analyze_stock(symbol: str, full: bool = False) -> StockSignal:
    """
    分析股票
    
    Args:
        symbol: 股票代码
        full: 是否完整分析
    
    Returns:
        StockSignal
    """
    # 获取股票名称
    name = get_stock_name(symbol)
    
    # 获取 K 线数据
    df_daily = fetch_kline_data(symbol, period="daily", count=500)
    df_weekly = fetch_kline_data(symbol, period="weekly", count=200) if full else pd.DataFrame()
    df_monthly = fetch_kline_data(symbol, period="monthly", count=100) if full else pd.DataFrame()
    
    if df_daily.empty:
        return StockSignal(
            symbol=symbol,
            name=name,
            category="观察区",
            score=0,
            similar_stock="N/A",
            recommendation="数据不足，无法分析"
        )
    
    # 计算技术指标
    mas = calculate_ma(df_daily['close'])
    macd = calculate_macd(df_daily['close'])
    rsi = calculate_rsi(df_daily['close'])
    
    # 模型判断
    is_model_a, score_a = check_model_a(df_daily, mas)
    is_model_b, score_b = check_model_b(df_daily, mas)
    is_blacklist, blacklist_reasons = check_blacklist(df_daily)
    
    # 确定分类
    if is_blacklist:
        category = "垃圾股规避"
        similar_stock = "类似中远海发"
        score = 0
    elif is_model_a:
        category = "长线稳步上涨型"
        similar_stock = "类似中国海油"
        score = min(score_a, 100)
    elif is_model_b:
        category = "历史低位反弹型"
        similar_stock = "类似万华化学"
        score = min(score_b, 100)
    else:
        category = "观察区"
        similar_stock = "N/A"
        score = max(score_a, score_b)
    
    # 技术面分析
    current_price = df_daily['close'].iloc[-1]
    technical_analysis = {
        'current_price': current_price,
        'ma250': mas['MA250'].iloc[-1] if len(mas['MA250']) > 0 else None,
        'ma60': mas['MA60'].iloc[-1] if len(mas['MA60']) > 0 else None,
        'macd_dif': macd['DIF'].iloc[-1],
        'rsi': rsi.iloc[-1],
        'price_change_60d': (current_price / df_daily['close'].iloc[-60] - 1) * 100 if len(df_daily) > 60 else 0
    }
    
    # 基本面分析
    fundamental = get_fundamental_data(symbol)
    
    # 生成建议
    if category == "长线稳步上涨型":
        recommendation = "适合中长期布局"
        strategy = f"建议分批建仓，依托{mas['MA250'].iloc[-1]:.2f}元（年线）作为防守位"
        risks = ["警惕短期涨幅过大回调", "关注行业政策变化"]
    elif category == "历史低位反弹型":
        recommendation = "处于建仓击球区"
        strategy = "可逐步建仓，关注右侧信号确认"
        risks = ["行业周期可能继续下行", "需耐心等待反转信号"]
    elif category == "垃圾股规避":
        recommendation = "坚决规避空仓"
        strategy = "不建议参与，风险极高"
        risks = blacklist_reasons
    else:
        recommendation = "等待右侧信号"
        strategy = "继续观察，等待更明确的信号"
        risks = ["方向不明确", "建议等待"]
    
    return StockSignal(
        symbol=symbol,
        name=name,
        category=category,
        score=score,
        similar_stock=similar_stock,
        technical_analysis=technical_analysis,
        fundamental_analysis=fundamental,
        recommendation=recommendation,
        strategy=strategy,
        risks=risks
    )


def format_output(signal: StockSignal) -> str:
    """格式化输出"""
    ta = signal.technical_analysis
    
    def safe_float(val, decimals=2):
        """安全格式化浮点数"""
        if val is None:
            return "N/A"
        try:
            return f"{float(val):.{decimals}f}"
        except:
            return str(val)
    
    output = f"""
### 📊 股票名称/代码：[{signal.name}({signal.symbol})]

**1. 资产定性分析**
* **分类归属**：{signal.category}
* **相似标的参考**：{signal.similar_stock}
* **综合评分**：{signal.score}/100

**2. 技术面解析 (Technical)**
* **当前价格**：{safe_float(ta.get('current_price'))}元
* **年线 (MA250)**：{safe_float(ta.get('ma250'))}元
* **60 日均线**：{safe_float(ta.get('ma60'))}元
* **MACD-DIF**：{safe_float(ta.get('macd_dif'), 4)}
* **RSI(14)**：{safe_float(ta.get('rsi'))}
* **60 日涨幅**：{safe_float(ta.get('price_change_60d', 0))}%

**3. 基本面与消息面 (Fundamental & News)**
* **市盈率 (PE)**：{signal.fundamental_analysis.get('pe_ratio', 'N/A')}
* **市净率 (PB)**：{signal.fundamental_analysis.get('pb_ratio', 'N/A')}
* **总市值**：{signal.fundamental_analysis.get('market_cap', 'N/A')}

**4. 综合投资建议 (Actionable Advice)**
* **结论**：{signal.recommendation}
* **操作策略**：{signal.strategy}
* **风险提示**：{"; ".join(signal.risks) if signal.risks else "无明显风险"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 风险提示：本分析仅供参考，不构成投资建议。股市有风险，入市需谨慎。
"""
    return output


def main():
    parser = argparse.ArgumentParser(description='优质股票筛选专家')
    parser.add_argument('--symbol', required=True, help='股票代码')
    parser.add_argument('--full', action='store_true', help='完整分析（包含周线/月线）')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')
    
    args = parser.parse_args()
    
    if not HAS_AKSHARE:
        print("❌ 未安装 AKShare！请运行：pip3 install akshare")
        sys.exit(1)
    
    # 分析股票
    signal = analyze_stock(args.symbol, full=args.full)
    
    # 输出结果
    if args.json:
        print(json.dumps({
            'symbol': signal.symbol,
            'name': signal.name,
            'category': signal.category,
            'score': signal.score,
            'similar_stock': signal.similar_stock,
            'recommendation': signal.recommendation,
            'strategy': signal.strategy,
            'risks': signal.risks
        }, ensure_ascii=False, indent=2))
    else:
        print(format_output(signal))


if __name__ == '__main__':
    main()
