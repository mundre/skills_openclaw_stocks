"""
持仓诊断 v4 - 单文件完整版（无外部依赖）
"""
import json, os, requests, numpy as np, pandas as pd
from datetime import date

# ─── 持仓数据（从 _holdings_std.py 读取）──────────────────────────────
_BASE = os.path.dirname(os.path.abspath(__file__))
_std = os.path.join(_BASE, '_holdings_std.py')
_h = {}
exec(open(_std, encoding='utf-8').read(), _h)
HOLDINGS = _h.get('HOLDINGS', [])

# ─── 行情获取 ────────────────────────────────────────────────────────
def fetch_kline_tencent(code, days=80):
    prefix = 'sh' if code.startswith(('6','9','5')) else 'sz'
    end = pd.Timestamp.today()
    start = end - pd.Timedelta(days=days+30)
    url = (f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&'
           f'param={prefix}{code},day,{start.strftime("%Y-%m-%d")},{end.strftime("%Y-%m-%d")},320,qfq')
    try:
        r = requests.get(url, timeout=10)
        text = r.text[text.index('=')+1:]
        raw = eval(text)['data'][prefix+code]['qfqday']
        df = pd.DataFrame(raw, columns=['date','open','close','high','low','vol'])
        for c in ['open','close','high','low','vol']: df[c] = df[c].astype(float)
        return df
    except: return None

# ─── 指标计算 ───────────────────────────────────────────────────────
def add_indicators(df):
    close = df['close'].values.astype(float)
    high = df['high'].values.astype(float); low = df['low'].values.astype(float)
    vol = df['vol'].values.astype(float); n = len(close)
    ma = {5:np.full(n,np.nan),10:np.full(n,np.nan),20:np.full(n,np.nan),30:np.full(n,np.nan)}
    for i in range(n):
        for m,(k,v) in enumerate(ma.items()):
            if i>=k-1: ma[k][i]=np.mean(close[max(0,i-k+1):i+1])
    e12=pd.Series(close).ewm(span=12,adjust=False).mean()
    e26=pd.Series(close).ewm(span=26,adjust=False).mean()
    dif=(e12-e26).values; dea=dif.ewm(span=9,adjust=False).mean().values
    macd_bar=(dif-dea)*2
    def rsi(s,n):
        d=np.diff(np.insert(s,0,s[0])); g=np.where(d>0,d,0); l=np.where(d<0,-d,0)
        ag=pd.Series(g).rolling(n,min_periods=1).mean().values
        al=pd.Series(l).rolling(n,min_periods=1).mean().values
        return np.where(al==0,100,100-100/(1+ag/al))
    df=df.copy()
    df['ma5']=ma[5]; df['ma10']=ma[10]; df['ma20']=ma[20]; df['ma30']=ma[30]
    df['dif']=dif; df['dea']=dea; df['macd_bar']=macd_bar
    df['rsi6']=rsi(close,6); df['rsi14']=rsi(close,14); df['rsi20']=rsi(close,20)
    df['vol_ma5']=pd.Series(vol).rolling(5,min_periods=1).mean().values
    df['vol_ratio']=vol/np.maximum(df['vol_ma5'].values,1)
    df['pct_change']=df['close'].pct_change().values
    df['pct5']=((close/np.roll(close,5))-1)*100
    df['pct20']=((close/np.roll(close,20))-1)*100
    return df

# ─── 统一评分 v3.2 ──────────────────────────────────────────────────
def calc_unified_score(df):
    if df is None or len(df)<25: return {'final_score':0,'rsi':0}
    close=df['close'].values; macd=df['macd_bar'].values; dif=df['dif'].values; dea=df['dea'].values
    ma5=df['ma5'].values; ma10=df['ma10'].values; ma20=df['ma20'].values; ma30=df['ma30'].values
    rsi6=df['rsi6'].values; rsi14=df['rsi14'].values; rsi20=df['rsi20'].values
    vol_r=df['vol_ratio'].values; pct5=df['pct5'].values; pct20=df['pct20'].values
    i=-1
    macd_avg=np.nanmean(macd[:i]); macd_diff=macd[i]-macd_avg
    macd_score=min(25,max(0,int(12.5+macd_diff/abs(np.nanstd(macd[:i])+1e-9)*6.25)))
    bull_count=sum([ma5[i]>ma10[i],ma10[i]>ma20[i],ma20[i]>ma30[i],dif[i]>0,macd[i]>0])
    bull_score=min(20,bull_count*5)
    rsi=rsi14[i]; rsi6_val=rsi6[i]; rsi_trend=rsi6_val-np.nanmean(rsi6[max(0,i-4):i])
    if rsi<40: rsi_score=20
    elif rsi<50: rsi_score=16+(50-rsi)/10*4
    elif rsi<60: rsi_score=12+(60-rsi)/10*4
    elif rsi<70: rsi_score=8+(70-rsi)/10*4
    else: rsi_score=max(0,8-(rsi-70)/10*4)
    if rsi_trend>0 and rsi<65: rsi_score=min(20,rsi_score+2)
    vol_score=min(20,15+min(5,(vol_r[i]-1)*5))
    if pct5[i]>15: vol_score=max(0,vol_score-5)
    pct_ch=close[i]/close[max(0,i-4)]-1 if i>=4 else 0
    trend_score=15 if pct_ch>0.02 else 10 if pct_ch>0 else 5
    final=int(macd_score+bull_score+rsi_score+vol_score+trend_score)
    return {'final_score':final,'rsi':round(rsi,1)}

# ─── 卖出评分 ────────────────────────────────────────────────────────
def calc_sell_score(df, buy_price, buy_date):
    if df is None or len(df)<5: return {'sell_score':0,'action':'HOLD','sell_signals':[]}
    close=df['close'].values; rsi14=df['rsi14'].values; rsi6=df['rsi6'].values
    macd=df['macd_bar'].values; vol_r=df['vol_ratio'].values; pct5=df['pct5'].values
    buy_p=float(buy_price); i=-1; score=0; signals=[]
    profit=(close[i]/buy_p-1)*100
    if profit<-10: score+=40; signals.append(('止损线-10%',20))
    elif profit<-5: score+=20; signals.append(('接近止损线-5%',10))
    if rsi14[i]>85: score+=25; signals.append(('RSI严重超买>85',25))
    elif rsi14[i]>75: score+=15; signals.append(('RSI超买>75',15))
    if rsi6[i]>90: score+=15; signals.append(('RSI6>90极热',15))
    if macd[i]<0 and macd[i-1]>=0: score+=20; signals.append(('MACD死叉',20))
    if vol_r[i]>3: score+=15; signals.append(('巨量异常>3倍',15))
    elif vol_r[i]>2: score+=8; signals.append(('放量过大>2倍',8))
    if pct5[i]>15: score+=10; signals.append(('5日涨幅>15%',10))
    if profit>15 and score<20: score+=5; signals.append(('盈利>15%注意止盈',5))
    if score>=40: action='SELL'; level='强烈建议离场'
    elif score>=25: action='WARNING'; level='考虑分批止盈'
    else: action='HOLD'; level='继续持有'
    return {'sell_score':min(100,score),'action':action,'level':level,'sell_signals':signals[:5],'profit':round(profit,2)}

# ─── 工具函数 ────────────────────────────────────────────────────────
def get_name(code):
    prefix='sz' if code.startswith(('0','3')) else 'sh'
    try:
        r=requests.get(f'https://qt.gtimg.cn/q={prefix}{code}',timeout=3)
        return r.content.split(b'~')[1].decode('gbk',errors='replace')
    except: return code

def get_price(code):
    prefix='sz' if code.startswith(('0','3')) else 'sh'
    try:
        r=requests.get(f'https://qt.gtimg.cn/q={prefix}{code}',timeout=3)
        return float(r.content.split(b'~')[3].decode('gbk'))
    except: return 0

# ─── 主逻辑 ─────────────────────────────────────────────────────────
results=[]
for h in HOLDINGS:
    code=h['code']; name=get_name(code)
    cur=get_price(code); bp=h['buy_price']
    profit_pct=(cur/bp-1)*100 if cur else 0
    days=(date.today()-date.fromisoformat(h['buy_date'])).days
    df=fetch_kline_tencent(code,80)
    buy_s=None; sell_s=None
    if df is not None and len(df)>=25:
        df1=add_indicators(df.copy())
        buy_s=calc_unified_score(df1)
        sell_s=calc_sell_score(df1,bp,h['buy_date'])
    bsv=buy_s['final_score'] if buy_s else 0
    ssv=sell_s['sell_score'] if sell_s else 0
    ov='SELL' if ssv>=40 else 'WARNING' if ssv>=25 else 'HOLD'
    sigs=[s[0] for s in (sell_s.get('sell_signals',[]) if sell_s else [])]
    results.append({'code':code,'name':name,'cur_price':cur,'buy_price':bp,
        'profit_pct':round(profit_pct,2),'days':days,'buy_score':bsv,
        'sell_score':ssv,'action':ov,'signals':sigs,
        'rsi':round(buy_s['rsi'],1) if buy_s else 0,'overall':ov})

total_profit=sum(r['profit_pct'] for r in results)
out={'date':str(date.today()),'positions':results,
     'summary':{'total_profit':round(total_profit,2),
                'avg_buy_score':round(sum(r['buy_score'] for r in results)/max(1,len(results)),1),
                'avg_sell_score':round(sum(r['sell_score'] for r in results)/max(1,len(results)),1),
                'sell_count':sum(1 for r in results if r['sell_score']>=40),
                'warning_count':sum(1 for r in results if 25<=r['sell_score']<40)}}
out_path=os.path.join(_BASE,'holdings_result.json')
with open(out_path,'w',encoding='utf-8') as f:
    json.dump(out,f,ensure_ascii=False,indent=2)
print(f"OK -> {out_path}")
print(f"持仓 {len(results)} 只，总盈亏 {total_profit:.2f}%")
