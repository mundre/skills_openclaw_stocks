import requests
import json
import os


# 从环境变量或配置文件读取账号密码
def get_credentials():
    # 优先从环境变量读取
    username = os.environ.get('LINGQUE_USERNAME')
    password = os.environ.get('LINGQUE_PASSWORD')
    
    if username and password:
        return username, password
    
    # 其次从配置文件读取
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('lingque_username'), config.get('lingque_password')
    
    return None, None


# 第一步：获取 access_token
def get_access_token(username, password):
    url = f"https://server.pinza.com.cn/pincloud-auth/chat/login"
    headers = {'Content-Type': 'application/json'}
    params = {
        "username": username,
        "password": password
    }
    print(params)
    response = requests.post(url, data=params)
    response_data = response.json()
    print(response_data)
    if response_data['code'] == "0":
        return response_data['data']
    else:
        print(f"获取 access_token 失败: {response_data['errmsg']}")
        return None
    

if __name__ == "__main__":
    import sys
    
    # 优先从命令行参数读取（兼容旧调用方式）
    if len(sys.argv) > 2:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        username, password = get_credentials()
        
    if not username or not password:
        print("错误：请配置灵雀AI账号密码")
        print("方法1：设置环境变量 LINGQUE_USERNAME 和 LINGQUE_PASSWORD")
        print("方法2：创建 config.json 文件，内容如下：")
        print('{"lingque_username": "手机号", "lingque_password": "密码"}')
        exit(1)
    
    print(username)
    print(password)
    access_token = get_access_token(username, password)
    print(access_token)