import sys
import json
import urllib.request
import urllib.error
import base64
import time
import random
from sm4_utils import sm4_encrypt

# 配置信息
PAY_TO = "42e458f3521e6d81bc69a41ccfddf91b2026040110491000100021027w6QbO4d3uHNtyIYyDdjI3AnEOylnBG8Bsrz00OLr4xqoppUgGqpTdEPCy7vVsdEo5KCNeZy"
SM4_KEY = base64.b64decode("jbIlAYC6Mg5IPyBmiltXig==")
AMOUNT = 1  # 0.01元，单位：分



def create_order(question: str) -> tuple:
    """创建订单"""
    # 生成订单号：时间戳 + 6位随机数
    order_no = time.strftime("%Y%m%d%H%M%S") + str(random.randint(100000, 999999))
    
    # 构建加密数据
    plain_dict = {
        "orderNo": order_no,
        "amount": str(AMOUNT),
        "payTo": PAY_TO
    }
    plain_text = json.dumps(plain_dict, separators=(',', ':'))
    encrypted_data = sm4_encrypt(plain_text, SM4_KEY)
    
    return order_no, AMOUNT, encrypted_data, PAY_TO

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("订单创建失败: 缺少写作需求参数")
        sys.exit(1)
    
    question = sys.argv[1]
    if not question.strip():
        print("订单创建失败: 写作需求不能为空")
        sys.exit(1)
    
    try:
        order_no, amount, encrypted_data, pay_to = create_order(question)
    except Exception as e:
        print(f"订单创建失败: {str(e)}")
        sys.exit(1)
    
    print(f"ORDER_NO={order_no}")
    print(f"AMOUNT={amount}")
    print(f"ENCRYPTED_DATA={encrypted_data}")
    print(f"PAY_TO={pay_to}")
