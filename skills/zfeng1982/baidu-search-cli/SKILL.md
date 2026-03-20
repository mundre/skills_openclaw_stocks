---
name: baidu-search-CLI
metadata: { "openclaw": { "emoji": "🔍︎",  "requires": { "bins": ["shell"], "env":["BAIDU_API_KEY"]},"primaryEnv":"BAIDU_API_KEY" } }
---
# Baidu Search
通过百度AI搜索API搜索网络，但不需要安装python,直接改用CLI
## Usage
curl命令，发送的post json请参考当前目录下的search_request.json文件  
用户的系统如果是windows请用cmd命令行执行curl命令，不要用PowerShell 
从环境变量BAIDU_API_KEY中获取apikey  
apikey的获取方法：用户自行注册百度千帆，注册成功后进入下面地址获取：https://console.bce.baidu.com/ai-search/qianfan/ais/console/apiKey
```bash  

curl -X POST -H "Authorization: Bearer BAIDU_API_KEY" -H "X-Appbuilder-From: openclaw" -H "Content-Type: application/json" -d "@search_request.json" "https://qianfan.baidubce.com/v2/ai_search/web_search"
```
## Request Param  

BAIDU_API_KEY     desc:apikey  
下面几个参数是search_request.json的字段说明  
content:string    desc:Search query  
top_k:int         desc:返回的数据条数，默认为10条，最多50条  
gte:string        desc:消息的开始时间，格式为"YYYY-MM-DD"  
lt:string         desc:消息的结束时间，格式为"YYYY-MM-DD"
