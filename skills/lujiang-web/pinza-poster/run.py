import requests
import json
import uuid

# 第一步：生成海报url
def generate_poster_url(token, record_data):
    url = f"https://server.pinza.com.cn/gpt/design/gemini"
    headers = {'token': token}
    files=[]
   
    response = requests.post(url, headers=headers, data=record_data, files=files)
    print(response)
    response_data = response.json()
    print(response_data)
    print("=" * 50)
    print("📌 请求URL：", response.url)
    print("\n📌 请求 Headers：")
    for k, v in response.headers.items():
        print(f"{k}: {v}")

    print("\n📌 请求体（发送给后台的真实参数）：")
    try:
        print(response.request.body.decode("utf-8"))  # FORM/中文正常显示
    except:
        print(response.request.body  or "无请求体")  # 无请求体或无法解码时显示提示信息

    print("=" * 50)
    if response_data['code'] == "0" :
        print("海报已生成")
        return response_data['data']['images'][0]['url']
    else:
        print(f"生成海报失败: {response_data['errmsg']}")
        return None
    


if __name__ == "__main__":
    import sys
    token = sys.argv[1]
    record_data = json.loads(sys.argv[2])
    record_data['groupId'] = str(uuid.uuid4())  # 添加唯一请求ID
    poster_url = generate_poster_url(token, record_data)