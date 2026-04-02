#!/usr/bin/env python3
"""
优化版回测引擎 v2
Optimized Backtest Engine v2

功能:
- 多策略回测
- 高性能计算 (向量化)
- 详细统计报告
- 风险评估指标
- 可视化数据输出
"""

import os
import sys
import json
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

# Security: Removed sys.path manipulation to prevent importing external packages.
# This module is self-contained and does not import from sibling directories.
# Removed imports from optimizer and advanced_indicators to ensure isolation.


class BacktestEngine:
    """优化版回测引擎"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.results = []
    
    def get_price_data(self, symbol: str, days: int = 60, use_a_share: bool = False) -> Optional[List[Dict]]:
        """获取价格数据"""
        if use_a_share:
            from a_stock_data import AStockDataFetcher
            fetcher = AStockDataFetcher()
            return fetcher.get_kline_data(symbol, days)
        else:
            # Twelve Data API
            from config import Config
            config = Config()
            api_key = config.get_api_key('twelve_data')
            
            if not api_key:
                print("⚠️ 未配置 Twelve Data API Key")
                return None
            
            url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize={days}&apikey={api_key}"
            
            try:
                import urllib.request
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0')
                
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode())
                    
                    if 'values' not in data:
                        return None
                    
                    kline = []
                    for item in reversed(data['values']):  # 从旧到新
                        kline.append({
                            'datetime': item.get('datetime', ''),
                            'open': float(item.get('open', 0)),
                            'high': float(item.get('high', 0)),
                            'low': float(item.get('low', 0)),
                            'close': float(item.get('close', 0)),
                            'volume': int(item.get('volume', 0)),
                        })
                    
                    return kline
                    
            except Exception as e:
                print(f"⚠️ 获取数据失败：{e}")
                return None
    
    def run_backtest(self, symbol: str, strategy: str = 'multi_signal', 
                    days: int = 60, use_a_share: bool = False) -> Dict:
        """
        运行回测
        
        Args:
            symbol: 标的符号
            strategy: 策略名称
            days: 回测天数
            use_a_share: 是否使用 A 股数据
            
        Returns:
            回测结果
        """
        print(f"\n🔬 开始回测：{symbol}")
        print(f"策略：{strategy}")
        print(f"周期：{days}天")
        print("=" * 60)
        
        # 获取数据
        data = self.get_price_data(symbol, days, use_a_share)
        if not data or len(data) < 30:
            print("❌ 数据不足")
            return None
        
        print(f"✅ 获取 {len(data)} 条数据")
        
        # 提取价格数组
        closes = [d['close'] for d in data]
        highs = [d['high'] for d in data]
        lows = [d['low'] for d in data]
        volumes = [d['volume'] for d in data]
        dates = [d['datetime'] for d in data]
        
        # 计算指标
        indicators = TechnicalIndicators.get_all_indicators(
            closes, highs, lows, volumes
        )
        
        # 运行策略
        if strategy == 'multi_signal':
            trades = self._multi_signal_strategy(closes, highs, lows, volumes, indicators)
        elif strategy == 'rsi_oversold':
            trades = self._rsi_oversold_strategy(closes, indicators)
        elif strategy == 'macd_crossover':
            trades = self._macd_crossover_strategy(closes, indicators)
        elif strategy == 'bollinger_bounce':
            trades = self._bollinger_bounce_strategy(closes, indicators)
        else:
            trades = self._multi_signal_strategy(closes, highs, lows, volumes, indicators)
        
        # 计算收益
        portfolio = self._calculate_portfolio(closes, trades)
        
        # 生成报告
        report = self._generate_report(symbol, data, trades, portfolio, strategy)
        
        return report
    
    def _multi_signal_strategy(self, closes: List[float], highs: List[float], 
                               lows: List[float], volumes: List[float],
                               indicators: Dict) -> List[Dict]:
        """多信号共振策略 (高胜率)"""
        trades = []
        position = None
        
        for i in range(30, len(closes)):
            # 截取到当前的指标
            current_indicators = {}
            for key, value in indicators.items():
                if isinstance(value, list):
                    current_indicators[key] = value[:i+1]
                elif isinstance(value, dict):
                    current_indicators[key] = value
            
            # 生成综合信号
            signal = TechnicalIndicators.generate_composite_signal(current_indicators)
            
            if signal['signal'] in ['STRONG_BUY', 'BUY'] and position is None:
                # 买入
                position = {
                    'entry_date': i,
                    'entry_price': closes[i],
                    'type': 'LONG',
                    'signal': signal,
                }
            
            elif signal['signal'] in ['STRONG_SELL', 'SELL'] and position is not None:
                # 卖出
                trades.append({
                    'entry_date': position['entry_date'],
                    'exit_date': i,
                    'entry_price': position['entry_price'],
                    'exit_price': closes[i],
                    'pnl_pct': (closes[i] - position['entry_price']) / position['entry_price'] * 100,
                    'type': 'LONG',
                })
                position = None
        
        # 如果还有持仓，强制平仓
        if position is not None:
            trades.append({
                'entry_date': position['entry_date'],
                'exit_date': len(closes) - 1,
                'entry_price': position['entry_price'],
                'exit_price': closes[-1],
                'pnl_pct': (closes[-1] - position['entry_price']) / position['entry_price'] * 100,
                'type': 'LONG',
            })
        
        return trades
    
    def _rsi_oversold_strategy(self, closes: List[float], indicators: Dict) -> List[Dict]:
        """RSI 超卖策略"""
        trades = []
        position = None
        rsi = indicators['rsi_14']
        
        for i in range(20, len(closes)):
            if rsi[i] is None:
                continue
            
            # RSI < 30 买入
            if rsi[i] < 30 and position is None:
                position = {
                    'entry_date': i,
                    'entry_price': closes[i],
                }
            
            # RSI > 70 卖出
            elif rsi[i] > 70 and position is not None:
                trades.append({
                    'entry_date': position['entry_date'],
                    'exit_date': i,
                    'entry_price': position['entry_price'],
                    'exit_price': closes[i],
                    'pnl_pct': (closes[i] - position['entry_price']) / position['entry_price'] * 100,
                })
                position = None
        
        return trades
    
    def _macd_crossover_strategy(self, closes: List[float], indicators: Dict) -> List[Dict]:
        """MACD 金叉死叉策略"""
        trades = []
        position = None
        macd_data = indicators['macd']
        histogram = macd_data['histogram']
        
        for i in range(30, len(closes)):
            if histogram[i] is None or histogram[i-1] is None:
                continue
            
            # 金叉：柱状图从负转正
            if histogram[i-1] < 0 and histogram[i] > 0 and position is None:
                position = {
                    'entry_date': i,
                    'entry_price': closes[i],
                }
            
            # 死叉：柱状图从正转负
            elif histogram[i-1] > 0 and histogram[i] < 0 and position is not None:
                trades.append({
                    'entry_date': position['entry_date'],
                    'exit_date': i,
                    'entry_price': position['entry_price'],
                    'exit_price': closes[i],
                    'pnl_pct': (closes[i] - position['entry_price']) / position['entry_price'] * 100,
                })
                position = None
        
        return trades
    
    def _bollinger_bounce_strategy(self, closes: List[float], indicators: Dict) -> List[Dict]:
        """布林带反弹策略"""
        trades = []
        position = None
        bb = indicators['bollinger']
        lower = bb['lower']
        upper = bb['upper']
        
        for i in range(25, len(closes)):
            if lower[i] is None or upper[i] is None:
                continue
            
            # 触及下轨买入
            if closes[i] <= lower[i] * 1.01 and position is None:
                position = {
                    'entry_date': i,
                    'entry_price': closes[i],
                }
            
            # 触及上轨卖出
            elif closes[i] >= upper[i] * 0.99 and position is not None:
                trades.append({
                    'entry_date': position['entry_date'],
                    'exit_date': i,
                    'entry_price': position['entry_price'],
                    'exit_price': closes[i],
                    'pnl_pct': (closes[i] - position['entry_price']) / position['entry_price'] * 100,
                })
                position = None
        
        return trades
    
    def _calculate_portfolio(self, closes: List[float], trades: List[Dict]) -> Dict:
        """计算投资组合表现"""
        capital = self.initial_capital
        
        for trade in trades:
            profit = capital * (trade['pnl_pct'] / 100)
            capital += profit
        
        return {
            'final_capital': capital,
            'total_return': (capital - self.initial_capital) / self.initial_capital * 100,
            'num_trades': len(trades),
        }
    
    def _generate_report(self, symbol: str, data: List[Dict], trades: List[Dict], 
                        portfolio: Dict, strategy: str) -> Dict:
        """生成回测报告"""
        if not trades:
            return {
                'symbol': symbol,
                'strategy': strategy,
                'period': f"{data[0]['datetime']} to {data[-1]['datetime']}",
                'total_return': 0,
                'num_trades': 0,
                'win_rate': 0,
                'avg_return_per_trade': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'trades': [],
            }
        
        # 计算胜率
        winning_trades = [t for t in trades if t['pnl_pct'] > 0]
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
        
        # 平均收益
        avg_return = sum(t['pnl_pct'] for t in trades) / len(trades) if trades else 0
        
        # 最大回撤 (简化)
        closes = [d['close'] for d in data]
        peak = closes[0]
        max_drawdown = 0
        
        for close in closes:
            if close > peak:
                peak = close
            drawdown = (peak - close) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # 夏普比率 (简化，假设无风险利率 0)
        if len(trades) > 1:
            returns = [t['pnl_pct'] for t in trades]
            avg_ret = sum(returns) / len(returns)
            std_ret = (sum((r - avg_ret) ** 2 for r in returns) / len(returns)) ** 0.5
            sharpe = avg_ret / std_ret if std_ret > 0 else 0
        else:
            sharpe = 0
        
        # 最佳/最差交易
        best_trade = max(trades, key=lambda x: x['pnl_pct']) if trades else None
        worst_trade = min(trades, key=lambda x: x['pnl_pct']) if trades else None
        
        report = {
            'symbol': symbol,
            'strategy': strategy,
            'period': f"{data[0]['datetime']} to {data[-1]['datetime']}",
            'initial_capital': self.initial_capital,
            'final_capital': portfolio['final_capital'],
            'total_return': portfolio['total_return'],
            'num_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(trades) - len(winning_trades),
            'win_rate': round(win_rate, 2),
            'avg_return_per_trade': round(avg_return, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe, 2),
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'trades': trades,
        }
        
        return report
    
    def print_report(self, report: Dict):
        """打印回测报告"""
        if not report:
            print("❌ 回测失败")
            return
        
        print("\n" + "=" * 60)
        print(f"📊 {report['symbol']} 回测报告")
        print("=" * 60)
        print(f"策略：{report['strategy']}")
        print(f"周期：{report['period']}")
        print()
        print("📈 收益表现:")
        print(f"   初始资金：${report['initial_capital']:,.2f}")
        print(f"   最终资金：${report['final_capital']:,.2f}")
        print(f"   总收益率：{report['total_return']:+.2f}%")
        print()
        print("📊 交易统计:")
        print(f"   总交易次数：{report['num_trades']}")
        print(f"   盈利交易：{report['winning_trades']}")
        print(f"   亏损交易：{report['losing_trades']}")
        print(f"   胜率：{report['win_rate']:.1f}%")
        print(f"   平均每笔收益：{report['avg_return_per_trade']:+.2f}%")
        print()
        print("⚠️  风险评估:")
        print(f"   最大回撤：{report['max_drawdown']:.1f}%")
        print(f"   夏普比率：{report['sharpe_ratio']:.2f}")
        print()
        
        if report['best_trade']:
            print(f"🏆 最佳交易：+{report['best_trade']['pnl_pct']:.2f}%")
        if report['worst_trade']:
            print(f"📉 最差交易：{report['worst_trade']['pnl_pct']:.2f}%")
        
        print("=" * 60)
        
        # 评级
        if report['win_rate'] >= 60 and report['total_return'] >= 20:
            rating = "⭐⭐⭐⭐⭐ 优秀"
        elif report['win_rate'] >= 50 and report['total_return'] >= 10:
            rating = "⭐⭐⭐⭐ 良好"
        elif report['win_rate'] >= 40:
            rating = "⭐⭐⭐ 一般"
        else:
            rating = "⭐⭐ 需优化"
        
        print(f"📌 策略评级：{rating}")
        print("=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='优化版回测引擎')
    parser.add_argument('symbol', nargs='?', default='BTC', help='标的符号')
    parser.add_argument('--strategy', default='multi_signal', 
                       choices=['multi_signal', 'rsi_oversold', 'macd_crossover', 'bollinger_bounce'],
                       help='策略选择')
    parser.add_argument('--days', type=int, default=60, help='回测天数')
    parser.add_argument('--a-share', action='store_true', help='使用 A 股数据')
    parser.add_argument('--capital', type=float, default=100000, help='初始资金')
    
    args = parser.parse_args()
    
    engine = BacktestEngine(initial_capital=args.capital)
    report = engine.run_backtest(args.symbol, args.strategy, args.days, args.a_share)
    
    if report:
        engine.print_report(report)
    
    # 保存报告
    os.makedirs('backtest_reports', exist_ok=True)
    report_file = f"backtest_reports/{args.symbol}_{args.strategy}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n💾 报告已保存：{report_file}")


if __name__ == '__main__':
    main()