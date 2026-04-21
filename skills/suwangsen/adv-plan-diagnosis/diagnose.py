#!/usr/bin/env python3
"""
广告计划诊断助手 - 双平台真实 API 版
支持巨量引擎 (Ocean Engine) 和 腾讯广告 (Tencent Ads)
使用报表 API + 规则引擎，不依赖已下线的诊断接口
"""

import argparse
import json
import sys
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

======================= 诊断规则引擎 =======================
def rule_based_diagnosis(metrics: Dict[str, Any], target_cost: float = 30.0) -> Dict[str, Any]:
cost = metrics.get("cost", 0)
impressions = metrics.get("impressions", 0)
clicks = metrics.get("clicks", 0)
conversion_cost = metrics.get("conversion_cost")

ctr = (clicks / impressions * 100) if impressions > 0 else 0

if cost < 10 and impressions < 1000:
return {
"status": "不起量",
"metrics": metrics,
"ctr": round(ctr, 2),
"reason": f"消耗{cost}元（<10元），展现{impressions}次（<1000），计划未获得足够曝光",
"suggestion": "1. 检查出价是否过低，建议提高10%-20%\n2. 检查定向是否过窄，适当放宽人群\n3. 确认素材是否审核通过",
"urgency": "中"
}

if conversion_cost is not None and conversion_cost > target_cost * 1.2:
return {
"status": "成本高",
"metrics": metrics,
"ctr": round(ctr, 2),
"reason": f"转化成本{conversion_cost}元，超出目标成本{target_cost}元的20%",
"suggestion": f"1. 适当降低出价5%-10%\n2. 优化落地页，提升转化率\n3. 若持续超标，建议暂停计划",
"urgency": "高"
}

if ctr > 2.0 and conversion_cost is not None and conversion_cost > target_cost * 0.8:
return {
"status": "素材可能疲劳",
"metrics": metrics,
"ctr": round(ctr, 2),
"reason": f"点击率{ctr}%尚可，但转化成本{conversion_cost}元偏高，素材可能老化",
"suggestion": "1. 准备新素材进行A/B测试\n2. 复制计划重新学习\n3. 适当控速，避免预算浪费",
"urgency": "中"
}

return {
"status": "正常",
"metrics": metrics,
"ctr": round(ctr, 2),
"reason": "各项指标均在合理范围内",
"suggestion": "1. 保持观察，关注趋势变化\n2. 定期检查素材新鲜度\n3. 可根据ROI适当调整出价",
"urgency": "低"
}

======================= 腾讯广告 API =======================
class TencentAdsAPI:
def init(self):
self.client_id = os.getenv('TENCENT_CLIENT_ID')
self.client_secret = os.getenv('TENCENT_CLIENT_SECRET')
self.refresh_token = os.getenv('TENCENT_REFRESH_TOKEN')
self.access_token = None
self.token_expire_at = None

def _request_access_token(self):
url = 'https://api.e.qq.com/oauth/token'
params = {
'client_id': self.client_id,
'client_secret': self.client_secret,
'grant_type': 'refresh_token',
'refresh_token': self.refresh_token
}
resp = requests.get(url, params=params)
resp.raise_for_status()
data = resp.json()
if data.get('code') != 0:
raise Exception(f"腾讯广告获取token失败: {data.get('message')}")
token_data = data['data']
self.access_token = token_data['access_token']
self.token_expire_at = datetime.now() + timedelta(seconds=token_data.get('expires_in', 7200))
return self.access_token

def get_access_token(self):
if self.access_token and datetime.now() < self.token_expire_at:
return self.access_token
return self._request_access_token()

def get_report(self, account_id: int, adgroup_id: int, start_date: str, end_date: str) -> Dict[str, Any]:
token = self.get_access_token()
url = 'https://api.e.qq.com/v1.1/daily_reports/get'
params = {
'access_token': token,
'account_id': account_id,
'level': 'REPORT_LEVEL_ADGROUP',
'date_range': json.dumps({'start_date': start_date, 'end_date': end_date}),
'filtering': json.dumps([{
'field': 'adgroup_id',
'operator': 'EQUALS',
'values': [str(adgroup_id)]
}]),
'fields': json.dumps([
'adgroup_id', 'cost', 'view_count', 'valid_click_count',
'conversions_count', 'conversions_rate'
]),
'page': 1,
'page_size': 10
}
resp = requests.get(url, params=params)
resp.raise_for_status()
data = resp.json()
if data.get('code') != 0:
raise Exception(f"腾讯广告获取报表失败: {data.get('message')}")
report_list = data.get('data', {}).get('list', [])
if not report_list:
return {"cost": 0, "impressions": 0, "clicks": 0, "conversion_cost": None}
report = report_list[0]
cost = report.get('cost', 0) / 100
conversions = report.get('conversions_count', 0)
conversion_cost = cost / conversions if conversions > 0 else None
return {
"cost": round(cost, 2),
"impressions": report.get('view_count', 0),
"clicks": report.get('valid_click_count', 0),
"conversion_cost": round(conversion_cost, 2) if conversion_cost else None
}

======================= 巨量引擎 API =======================
class OceanEngineAPI:
def init(self):
self.app_id = os.getenv('OCEAN_ENGINE_APP_ID')
self.secret = os.getenv('OCEAN_ENGINE_SECRET')
self.refresh_token = os.getenv('OCEAN_ENGINE_REFRESH_TOKEN')
self.access_token = None
self.token_expire_at = None

def _request_access_token(self):
url = 'https://ad.oceanengine.com/open_api/oauth2/refresh_token/'
data = {
'app_id': self.app_id,
'secret': self.secret,
'refresh_token': self.refresh_token,
'grant_type': 'refresh_token'
}
resp = requests.post(url, data=data)
resp.raise_for_status()
result = resp.json()
if result.get('code') != 0:
raise Exception(f"巨量引擎获取token失败: {result.get('message')}")
token_data = result['data']
self.access_token = token_data['access_token']
if 'refresh_token' in token_data:
self.refresh_token = token_data['refresh_token']
self.token_expire_at = datetime.now() + timedelta(seconds=token_data.get('expires_in', 86400))
return self.access_token

def get_access_token(self):
if self.access_token and datetime.now() < self.token_expire_at:
return self.access_token
return self._request_access_token()

def get_report(self, advertiser_id: int, ad_id: int, start_date: str, end_date: str) -> Dict[str, Any]:
token = self.get_access_token()
url = 'https://ad.oceanengine.com/open_api/2/report/integrated/get/'
headers = {'Access-Token': token}
params = {
'advertiser_id': advertiser_id,
'start_date': start_date,
'end_date': end_date,
'group_by': json.dumps(['ad_id']),
'metrics': json.dumps(['stat_cost', 'show_cnt', 'click_cnt', 'convert_cost']),
'filtering': json.dumps([{
'field': 'ad_id',
'operator': 'IN',
'values': [str(ad_id)]
}]),
'page': 1,
'page_size': 10
}
resp = requests.get(url, headers=headers, params=params)
resp.raise_for_status()
data = resp.json()
if data.get('code') != 0:
raise Exception(f"巨量引擎获取报表失败: {data.get('message')}")
report_list = data.get('data', {}).get('list', [])
if not report_list:
return {"cost": 0, "impressions": 0, "clicks": 0, "conversion_cost": None}
report = report_list[0]
cost = report.get('stat_cost', 0) / 100
conversion_cost = report.get('convert_cost', 0) / 100 if report.get('convert_cost') else None
return {
"cost": round(cost, 2),
"impressions": report.get('show_cnt', 0),
"clicks": report.get('click_cnt', 0),
"conversion_cost": round(conversion_cost, 2) if conversion_cost else None
}

======================= 主函数 =======================
def main():
parser = argparse.ArgumentParser(description="广告计划诊断助手")
parser.add_argument("--platform", required=True, choices=["ocean_engine", "tencent_ads"],
help="广告平台: ocean_engine / tencent_ads")
parser.add_argument("--account_id", required=True, help="广告主ID/账户ID")
parser.add_argument("--adgroup_id", required=True, help="广告ID/计划ID")
parser.add_argument("--target_cost", type=float, default=30.0, help="目标转化成本（元）")
parser.add_argument("--days", type=int, default=1, help="查询最近几天的数据，默认1（今天）")
args = parser.parse_args()

end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=args.days)).strftime('%Y-%m-%d')

try:
if args.platform == "tencent_ads":
api = TencentAdsAPI()
metrics = api.get_report(int(args.account_id), int(args.adgroup_id), start_date, end_date)
elif args.platform == "ocean_engine":
api = OceanEngineAPI()
metrics = api.get_report(int(args.account_id), int(args.adgroup_id), start_date, end_date)
else:
raise ValueError(f"Unsupported platform: {args.platform}")

diagnosis = rule_based_diagnosis(metrics, args.target_cost)
diagnosis["query_period"] = f"{start_date} 至 {end_date}"
diagnosis["platform"] = args.platform

print(json.dumps(diagnosis, ensure_ascii=False, indent=2))

except Exception as e:
error_output = {"status": "error", "message": str(e)}
print(json.dumps(error_output, ensure_ascii=False, indent=2))
sys.exit(1)

if name == "main":
main()