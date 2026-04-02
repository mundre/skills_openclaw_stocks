#!/usr/bin/env python3
"""
OpenClaw Trading Assistant CLI
命令行交互界面

Usage:
    openclaw-trading-assistant [command] [options]
    
Commands:
    interactive, interact, cli    Start interactive mode / 交互模式
    support-resistance            Analyze support/resistance levels / 分析支撑阻力位
    signals                       Generate trading signals / 生成交易信号
    position                      Calculate position size / 计算仓位大小
    alerts                        Manage price alerts / 管理价格提醒
    monitor                       Real-time market monitoring / 实时监控
    backtest                      Strategy backtesting (v2 optimized) / 策略回测
    cost                          Position cost basis analysis / 持仓成本分析
    quant                         Quantitative cost analysis / 量化成本分析
    entry                         Quantitative entry alerts / 量化进场提示
    strategies                    Quantitative strategies demo / 量化策略演示
    a-share                       A-Share data query / A 股数据查询
    indicators                    Advanced technical indicators / 高级技术指标
    live                          Live trading interface / 实盘接口
    all                           Run all analysis / 运行所有分析
    version                       Show version / 显示版本
    help                          Show help / 显示帮助
"""

import sys
import os
from datetime import datetime

# Security: Removed sys.path manipulation.
# This CLI only imports from its own directory using standard Python imports.

from config import Config
from i18n import t
from support_resistance import SupportResistanceAnalyzer
from trading_signals import SignalGenerator
from position_calculator import PositionCalculator
from stop_loss_alerts import StopLossAlert
from realtime_monitor import MarketMonitor
from backtest_engine import BacktestEngine
from position_cost_analyzer import PositionCostAnalyzer
from quantitative_cost_analyzer import QuantitativeCostAnalyzer, print_report
from quantitative_entry_alert import QuantitativeEntryAlert
from quantitative_strategies import demo_strategies, MultiFactorStrategy, MeanReversionStrategy, MomentumBreakoutStrategy, GridTradingStrategy
from a_stock_data import AStockDataFetcher
from advanced_indicators import TechnicalIndicators
from backtest_engine_v2 import BacktestEngine
from live_trading_interface import LiveTradingInterface

VERSION = "2.0.0"


def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("  OpenClaw Trading Assistant CLI")
    print(f"  Version: {VERSION}")
    print(f"  {t('timestamp')}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()


def print_help():
    """Print help message"""
    help_text = """
OpenClaw Trading Assistant CLI - Help

Commands:
  interactive, interact, cli    Start interactive mode / 交互模式
  support-resistance            Analyze support/resistance levels
  signals                       Generate trading signals
  position                      Calculate position size
  alerts                        Manage price alerts
  monitor                       Real-time market monitoring
  backtest                      Strategy backtesting
  all                           Run all analysis
  version                       Show version
  help                          Show this help

Examples:
  openclaw-trading-assistant
  openclaw-trading-assistant interactive
  openclaw-trading-assistant signals --symbol NVDA
  openclaw-trading-assistant position --symbol NVDA --price 175.64 --capital 10000
  openclaw-trading-assistant alerts check
  openclaw-trading-assistant monitor --watchlist AAPL GOOGL
  openclaw-trading-assistant backtest AAPL 2024-01-01 2024-12-31

Use --help after any command for detailed options.
"""
    print(help_text)


def run_support_resistance(args):
    """Run support/resistance analysis"""
    print(f"\n📊 {t('analyzing_support_resistance')}...")
    analyzer = SupportResistanceAnalyzer()
    
    if '--symbol' in args:
        idx = args.index('--symbol')
        symbol = args[idx + 1] if idx + 1 < len(args) else None
        if symbol:
            print(f"Symbol: {symbol}")
            # TODO: Add symbol-specific analysis
    else:
        # Analyze watchlist
        analyzer.analyze_watchlist()
    
    print("✅ Done!")


def run_signals(args):
    """Generate trading signals"""
    print(f"\n📈 {t('generating_signals')}...")
    generator = SignalGenerator()
    
    if '--symbol' in args:
        idx = args.index('--symbol')
        symbol = args[idx + 1] if idx + 1 < len(args) else None
        if symbol:
            print(f"Symbol: {symbol}")
            # TODO: Add symbol-specific signals
    else:
        # Generate for watchlist
        generator.generate_all()
    
    print("✅ Done!")


def run_position(args):
    """Calculate position size"""
    print(f"\n💰 {t('calculating_position')}...")
    calculator = PositionCalculator()
    
    # Parse arguments
    symbol = None
    price = None
    capital = None
    risk = None
    
    i = 0
    while i < len(args):
        if args[i] == '--symbol' and i + 1 < len(args):
            symbol = args[i + 1]
            i += 2
        elif args[i] == '--price' and i + 1 < len(args):
            price = float(args[i + 1])
            i += 2
        elif args[i] == '--capital' and i + 1 < len(args):
            capital = float(args[i + 1])
            i += 2
        elif args[i] == '--risk' and i + 1 < len(args):
            risk = float(args[i + 1])
            i += 2
        else:
            i += 1
    
    if symbol and price and capital:
        result = calculator.calculate(symbol, price, capital, risk)
        print(f"\n{t('symbol')}: {symbol}")
        print(f"{t('entry_price')}: ${price:.2f}")
        print(f"{t('total_capital')}: ${capital:.2f}")
        print(f"{t('position_size')}: {result.get('shares', 0)} shares")
        print(f"{t('position_value')}: ${result.get('position_value', 0):.2f}")
        print(f"{t('risk_amount')}: ${result.get('risk_amount', 0):.2f}")
    else:
        print("Missing required arguments: --symbol, --price, --capital")
        print("Example: openclaw-trading-assistant position --symbol NVDA --price 175.64 --capital 10000")


def run_alerts(args):
    """Manage price alerts"""
    print(f"\n🔔 {t('managing_alerts')}...")
    alerts = StopLossAlert()
    
    if not args or args[0] == 'check':
        alerts.check_all_alerts()
    elif args[0] == 'list':
        alerts.list_alerts()
    elif args[0] == 'create':
        # Parse create arguments
        symbol = None
        entry = None
        stop = None
        target = None
        
        i = 1
        while i < len(args):
            if args[i] == '--symbol' and i + 1 < len(args):
                symbol = args[i + 1]
                i += 2
            elif args[i] == '--entry' and i + 1 < len(args):
                entry = float(args[i + 1])
                i += 2
            elif args[i] == '--stop' and i + 1 < len(args):
                stop = float(args[i + 1])
                i += 2
            elif args[i] == '--target' and i + 1 < len(args):
                target = float(args[i + 1])
                i += 2
            else:
                i += 1
        
        if symbol and entry and stop:
            alerts.create_alert(symbol, entry, stop, target)
            print(f"✅ Alert created for {symbol}")
        else:
            print("Missing required arguments: --symbol, --entry, --stop")
            print("Example: openclaw-trading-assistant alerts create --symbol NVDA --entry 175 --stop 170 --target 185")
    else:
        print("Unknown alerts command. Use: check, list, create")


def run_monitor(args):
    """Run real-time monitor"""
    print("\n🔍 Real-time Market Monitor\n")
    monitor = MarketMonitor()
    
    if '--watchlist' in args:
        idx = args.index('--watchlist')
        watchlist = args[idx + 1:idx + 4] if idx + 1 < len(args) else []
        if watchlist:
            monitor.watchlist = [s.upper() for s in watchlist]
            print(f"Monitoring: {monitor.watchlist}")
            print("Use --run to start monitoring\n")
    
    if '--run' in args:
        interval = 60
        if '--interval' in args:
            idx = args.index('--interval')
            interval = int(args[idx + 1]) if idx + 1 < len(args) else 60
        monitor.run_monitor(interval)
    else:
        print("Usage: ta monitor --watchlist AAPL GOOGL --run --interval 60")


def run_backtest(args):
    """Run strategy backtest"""
    print("\n📈 Strategy Backtest\n")
    
    if len(args) < 3:
        print("Usage: ta backtest SYMBOL START_DATE END_DATE [--strategy sma_crossover|rsi_oversold]")
        print("Example: ta backtest AAPL 2024-01-01 2024-12-31 --strategy sma_crossover")
        return
    
    symbol = args[0]
    start_date = args[1]
    end_date = args[2]
    
    strategy = 'sma_crossover'
    if '--strategy' in args:
        idx = args.index('--strategy')
        strategy = args[idx + 1] if idx + 1 < len(args) else 'sma_crossover'
    
    engine = BacktestEngine()
    engine.run_backtest(symbol, start_date, end_date, strategy)


def run_cost(args):
    """Run position cost basis analysis"""
    print("\n💰 Position Cost Basis Analysis\n")
    
    if len(args) < 1:
        print("Usage: ta cost SYMBOL [--type crypto|stock]")
        print("Example: ta cost BTC --type crypto")
        print("         ta cost AAPL --type stock")
        return
    
    symbol = args[0]
    asset_type = 'crypto'
    
    if '--type' in args:
        idx = args.index('--type')
        asset_type = args[idx + 1] if idx + 1 < len(args) else 'crypto'
    
    analyzer = PositionCostAnalyzer()
    result = analyzer.calculate_cost_support_resistance(symbol, asset_type)
    
    if result:
        print(f"📊 {result['symbol']} 持仓成本分析")
        print("=" * 50)
        print(f"当前价格：${result['current_price']:,.2f}")
        print(f"平均持仓成本：${result['average_cost']:,.2f}")
        print(f"盈亏比例：{result['profit_ratio']:+.1f}%")
        print()
        print("支撑位:")
        for i, level in enumerate(result['support_levels'], 1):
            print(f"  S{i}: ${level:,.2f}")
        print("\n阻力位:")
        for i, level in enumerate(result['resistance_levels'], 1):
            print(f"  R{i}: ${level:,.2f}")
        print()
        print(f"🎯 信号：{result['signal']['action']}")
        print(f"   原因：{result['signal']['reason']}")
        print(f"   置信度：{result['signal']['confidence']:.0f}%")
        print("=" * 50)
    else:
        print("❌ 无法获取数据")


def run_quant(args):
    """Run quantitative cost analysis"""
    print("\n🔬 Quantitative Cost Analysis\n")
    
    if len(args) < 1:
        print("Usage: ta quant SYMBOL [--days 60]")
        print("Example: ta quant BTC --days 60")
        print("         ta quant AAPL --days 90")
        return
    
    symbol = args[0]
    days = 60
    
    if '--days' in args:
        idx = args.index('--days')
        days = int(args[idx + 1]) if idx + 1 < len(args) else 60
    
    analyzer = QuantitativeCostAnalyzer()
    result = analyzer.full_analysis(symbol, days)
    
    if result:
        print_report(result)
    else:
        print("❌ 分析失败")


def run_entry_alert(args):
    """Run quantitative entry alert"""
    print("\n🚨 Quantitative Entry Alert\n")
    
    alert_system = QuantitativeEntryAlert()
    
    if '--add' in args:
        idx = args.index('--add')
        symbol = args[idx + 1] if idx + 1 < len(args) else None
        if symbol:
            watchlist = alert_system.load_watchlist()
            if symbol not in watchlist:
                watchlist.append(symbol)
                alert_system.save_watchlist(watchlist)
                print(f"✅ 已添加 {symbol} 到监控列表")
            else:
                print(f"ℹ️  {symbol} 已在监控列表中")
        return
    
    if '--list' in args:
        watchlist = alert_system.load_watchlist()
        print(f"\n📋 监控列表 ({len(watchlist)}个):")
        for s in watchlist:
            print(f"   {s}")
        return
    
    if '--history' in args:
        if os.path.exists(alert_system.history_file):
            with open(alert_system.history_file, 'r') as f:
                history = json.load(f)
            print(f"\n📜 历史警报 ({len(history)}条):")
            for alert in history[-10:]:
                print(f"   {alert['timestamp'][:16]} {alert['symbol']} {alert['entry_signal']}")
        else:
            print("暂无历史警报")
        return
    
    symbol = args[0] if args else None
    use_a_share = '--a-share' in args
    continuous = '--continuous' in args
    interval = 300
    
    if '--interval' in args:
        idx = args.index('--interval')
        interval = int(args[idx + 1]) if idx + 1 < len(args) else 300
    
    symbols = [symbol] if symbol else None
    
    if continuous:
        alert_system.start_continuous_monitoring(symbols, interval, use_a_share)
    else:
        alerts = alert_system.monitor_all(symbols, use_a_share)
        if alerts:
            for alert in alerts:
                alert_system.print_alert_report(alert)


def run_strategies(args):
    """Run quantitative strategies demo"""
    print("\n📊 Quantitative Strategies Demo\n")
    demo_strategies()


def run_backtest(args):
    """Run optimized backtest engine"""
    print("\n🔬 Optimized Backtest Engine v2\n")
    
    symbol = args[0] if args else 'BTC'
    strategy = 'multi_signal'
    days = 60
    use_a_share = False
    
    if '--strategy' in args:
        idx = args.index('--strategy')
        strategy = args[idx + 1] if idx + 1 < len(args) else 'multi_signal'
    
    if '--days' in args:
        idx = args.index('--days')
        days = int(args[idx + 1]) if idx + 1 < len(args) else 60
    
    if '--a-share' in args:
        use_a_share = True
    
    engine = BacktestEngine()
    report = engine.run_backtest(symbol, strategy, days, use_a_share)
    
    if report:
        engine.print_report(report)


def run_indicators(args):
    """Show advanced technical indicators"""
    print("\n📈 Advanced Technical Indicators\n")
    
    symbol = args[0] if args else 'BTC'
    days = 60
    
    if '--days' in args:
        idx = args.index('--days')
        days = int(args[idx + 1]) if idx + 1 < len(args) else 60
    
    # 获取数据
    from a_stock_data import AStockDataFetcher
    fetcher = AStockDataFetcher()
    
    if symbol.startswith('sh') or symbol.startswith('sz') or symbol.isdigit():
        kline = fetcher.get_kline_data(symbol, days)
        use_a_share = True
    else:
        # 使用 Twelve Data 或其他
        kline = fetcher.get_kline_data(symbol, days)
        use_a_share = False
    
    if not kline:
        print("❌ 获取数据失败")
        return
    
    closes = [k['close'] for k in kline]
    highs = [k['high'] for k in kline]
    lows = [k['low'] for k in kline]
    volumes = [k['volume'] for k in kline]
    
    # 计算指标
    indicators = TechnicalIndicators.get_all_indicators(closes, highs, lows, volumes)
    
    print(f"📊 {symbol} 技术指标")
    print("=" * 60)
    
    # RSI
    rsi = indicators['rsi_14']
    if rsi and rsi[-1]:
        print(f"\nRSI (14): {rsi[-1]:.2f}")
        if rsi[-1] < 30:
            print("   状态：超卖 (买入信号)")
        elif rsi[-1] > 70:
            print("   状态：超买 (卖出信号)")
        else:
            print("   状态：中性")
    
    # MACD
    macd = indicators['macd']
    if macd and macd.get('current'):
        print(f"\nMACD:")
        print(f"   MACD 线：{macd['current']['macd']:.4f}")
        print(f"   信号线：{macd['current']['signal']:.4f}")
        print(f"   柱状图：{macd['current']['histogram']:.4f}")
    
    # 布林带
    bb = indicators['bollinger']
    if bb and bb.get('current'):
        print(f"\n布林带:")
        print(f"   上轨：${bb['current']['upper']:.2f}")
        print(f"   中轨：${bb['current']['middle']:.2f}")
        print(f"   下轨：${bb['current']['lower']:.2f}")
        print(f"   价格位置：{bb['current']['position']:.1f}%")
    
    # KDJ
    kdj = indicators['kdj']
    if kdj and kdj.get('current'):
        print(f"\nKDJ:")
        print(f"   K: {kdj['current']['k']:.2f}")
        print(f"   D: {kdj['current']['d']:.2f}")
        print(f"   J: {kdj['current']['j']:.2f}")
    
    # CCI
    cci = indicators['cci_20']
    if cci and cci[-1]:
        print(f"\nCCI (20): {cci[-1]:.2f}")
        if cci[-1] < -100:
            print("   状态：超卖")
        elif cci[-1] > 100:
            print("   状态：超买")
    
    # 综合信号
    print("\n" + "=" * 60)
    composite = TechnicalIndicators.generate_composite_signal(indicators)
    print(f"\n🎯 综合信号：{composite['signal']}")
    print(f"   置信度：{composite['confidence']:.1f}%")
    print(f"   原因：{composite['reason']}")
    print("=" * 60)


def run_live(args):
    """Live trading interface"""
    print("\n📡 Live Trading Interface\n")
    
    interface = LiveTradingInterface()
    interface.show_api_info()
    
    if '--test' in args:
        print("\n🧪 测试免注册接口...")
        
        print("\n1. Binance BTC 行情:")
        ticker = interface.get_binance_ticker('BTCUSDT')
        if ticker:
            print(f"   价格：${ticker['price']:,.2f}")
            print(f"   24h: {ticker['change_percent']:+.2f}%")
        
        print("\n2. CoinGecko BTC 价格:")
        price = interface.get_coingecko_price('bitcoin')
        if price:
            print(f"   价格：${price['price']:,.2f}")
            print(f"   24h: {price['change_24h']:+.2f}%")
        
        print("\n3. 新浪财经 贵州茅台:")
        quote = interface.get_sina_quote('sh600519')
        if quote:
            print(f"   {quote['name']}: ¥{quote['current']:.2f}")
            print(f"   涨跌：{quote['change_percent']:+.2f}%")
        
        print("\n✅ 测试完成")
    
    if '--config' in args:
        interface.setup_api_keys()


def run_a_share(args):
    """Query A-Share data"""
    print("\n🇨🇳 A-Share Data Query\n")
    
    fetcher = AStockDataFetcher()
    
    if '--status' in args:
        status = fetcher.get_market_status()
        print(f"📊 A 股市场状态")
        print(f"   交易时间：{'是' if status['is_trading'] else '否'}")
        print(f"   当前时间：{status['current_time']}")
        print(f"   {status['next_close']}")
        return
    
    if '--list' in args:
        stocks = fetcher.get_stock_list()
        print(f"\n📋 A 股股票列表 (部分)")
        for stock in stocks[:20]:
            print(f"   {stock['symbol']} - {stock['name']}")
        return
    
    symbol = args[0] if args else '600519'
    
    if '--kline' in args:
        days = 60
        if '--days' in args:
            idx = args.index('--days')
            days = int(args[idx + 1]) if idx + 1 < len(args) else 60
        
        kline = fetcher.get_kline_data(symbol, days)
        if kline:
            print(f"\n📈 {symbol} K 线数据 (近{days}天)")
            print(f"   共 {len(kline)} 条记录")
            if kline:
                latest = kline[-1]
                print(f"   最新：{latest['datetime']} O:{latest['open']} H:{latest['high']} L:{latest['low']} C:{latest['close']}")
        else:
            print("❌ 获取 K 线失败")
        return
    
    # 实时行情
    quote = fetcher.get_realtime_quote(symbol)
    if quote:
        print(f"\n📊 {quote['symbol']} - {quote['name']} 实时行情")
        print("=" * 50)
        print(f"   现价：¥{quote['current']:.2f}")
        print(f"   涨跌：{quote['change']:+.2f} ({quote['change_percent']:+.2f}%)")
        print(f"   今开：¥{quote['open']:.2f}")
        print(f"   昨收：¥{quote['close']:.2f}")
        print(f"   最高：¥{quote['high']:.2f}")
        print(f"   最低：¥{quote['low']:.2f}")
        print(f"   成交量：{quote['volume']:,} 手")
        print(f"   成交额：¥{quote['amount']/10000:.1f} 万")
        print(f"   时间：{quote['date']} {quote['time']}")
        print("=" * 50)
    else:
        print("❌ 获取行情失败")


def run_all(args):
    """Run all analysis"""
    print("\n🚀 Running all analysis...\n")
    run_support_resistance(args)
    print()
    run_signals(args)
    print()
    run_alerts(['check'])
    print("\n✅ All analysis complete!")


def interactive_mode():
    """Start interactive CLI mode"""
    print_banner()
    print("Welcome to OpenClaw Trading Assistant Interactive CLI")
    print("Type 'help' for available commands, 'exit' to quit\n")
    
    while True:
        try:
            user_input = input("ta> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye! 👋")
                break
            
            if user_input.lower() in ['help', 'h', '?']:
                print_help()
                continue
            
            if user_input.lower() in ['version', 'v']:
                print(f"OpenClaw Trading Assistant v{VERSION}")
                continue
            
            # Parse command
            parts = user_input.split()
            command = parts[0].lower()
            args = parts[1:]
            
            if command in ['interactive', 'interact', 'cli']:
                print("Already in interactive mode!")
            elif command in ['support', 'support-resistance', 'sr']:
                run_support_resistance(args)
            elif command in ['signals', 'signal', 'sig']:
                run_signals(args)
            elif command in ['position', 'pos', 'calc']:
                run_position(args)
            elif command in ['alerts', 'alert', 'alarm']:
                run_alerts(args)
            elif command in ['monitor', 'mon']:
                run_monitor(args)
            elif command in ['backtest', 'bt']:
                run_backtest(args)
            elif command in ['cost', 'costbasis']:
                run_cost(args)
            elif command in ['quant', 'quantitative']:
                run_quant(args)
            elif command in ['entry', 'entry-alert']:
                run_entry_alert(args)
            elif command in ['strategies', 'strategy', 'strat']:
                run_strategies(args)
            elif command in ['a-share', 'ashare', 'ash']:
                run_a_share(args)
            elif command in ['backtest', 'bt']:
                run_backtest(args)
            elif command in ['indicators', 'indicator', 'ind']:
                run_indicators(args)
            elif command in ['live', 'live-trading', 'trading']:
                run_live(args)
            elif command in ['all', 'full', 'analyze']:
                run_all(args)
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands")
        
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point"""
    args = sys.argv[1:]
    
    # No arguments: start interactive mode
    if not args:
        interactive_mode()
        return
    
    command = args[0].lower()
    command_args = args[1:]
    
    # Handle help
    if command in ['help', 'h', '-h', '--help']:
        print_help()
        return
    
    # Handle version
    if command in ['version', 'v', '-v', '--version']:
        print(f"OpenClaw Trading Assistant v{VERSION}")
        return
    
    # Handle interactive mode
    if command in ['interactive', 'interact', 'cli']:
        interactive_mode()
        return
    
    # Handle commands
    if command in ['support', 'support-resistance', 'sr']:
        run_support_resistance(command_args)
    elif command in ['signals', 'signal', 'sig']:
        run_signals(command_args)
    elif command in ['position', 'pos', 'calc']:
        run_position(command_args)
    elif command in ['alerts', 'alert', 'alarm']:
        run_alerts(command_args)
    elif command in ['monitor', 'mon']:
        run_monitor(command_args)
    elif command in ['backtest', 'bt']:
        run_backtest(command_args)
    elif command in ['cost', 'costbasis']:
        run_cost(command_args)
    elif command in ['quant', 'quantitative']:
        run_quant(command_args)
    elif command in ['entry', 'entry-alert']:
        run_entry_alert(command_args)
    elif command in ['strategies', 'strategy', 'strat']:
        run_strategies(command_args)
    elif command in ['a-share', 'ashare', 'ash']:
        run_a_share(command_args)
    elif command in ['all', 'full', 'analyze']:
        run_all(command_args)
    else:
        print(f"Unknown command: {command}")
        print("Type 'openclaw-trading-assistant help' for available commands")
        sys.exit(1)


if __name__ == '__main__':
    main()
