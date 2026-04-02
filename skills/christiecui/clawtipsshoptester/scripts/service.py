import sys
import json
import urllib.request
import urllib.error
import base64
import openai
from sm4_utils import sm4_decrypt

# 配置信息
SM4_KEY = base64.b64decode("jbIlAYC6Mg5IPyBmiltXig==")
# 可配置你的OpenAI API密钥或其他AI服务密钥
# OPENAI_API_KEY = "your-api-key"



def generate_ai_content(question: str) -> str:
    """调用AI生成内容"""
    try:
        # 示例：使用OpenAI API
        # openai.api_key = OPENAI_API_KEY
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{"role": "user", "content": question}]
        # )
        # return response.choices[0].message.content
        
        # 演示返回内容，实际使用时替换为真实AI调用
        return f"## AI写作结果\n\n**需求：** {question}\n\n这是为您生成的内容：\n\n（此处为AI生成的具体内容，实际部署时会替换为真实AI服务返回结果）\n\n✅ 内容已生成完毕，感谢使用AI写作助手！"
    
    except Exception as e:
        raise RuntimeError(f"AI生成失败: {str(e)}")

def ai_writer(question: str, order_no: str, credential: str) -> str:
    print(f"AI写作需求: {question}")
    
    if not credential:
        raise RuntimeError("缺少支付凭证")
    
    try:
        # 解密支付凭证
        decrypted = sm4_decrypt(credential, SM4_KEY)
        credential_data = json.loads(decrypted)
        
        pay_status = credential_data.get("payStatus", "FAIL")
        print(f"PAY_STATUS: {pay_status}")
        
        if pay_status != "SUCCESS":
            raise RuntimeError(f"支付未成功，状态：{pay_status}")
        
        # 验证订单信息
        if credential_data.get("orderNo") != order_no:
            raise RuntimeError("订单号不匹配")
        
        if int(credential_data.get("amount", "0")) != 1:
            raise RuntimeError("金额不匹配")
        
        # 生成AI内容
        content = generate_ai_content(question)
        return content
        
    except json.JSONDecodeError:
        raise RuntimeError("支付凭证格式错误")
    except Exception as e:
        raise RuntimeError(f"服务执行失败: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("PAY_STATUS: ERROR")
        print("ERROR_INFO: 缺少参数，用法: python service.py <写作需求> <订单号> <支付凭证>")
        sys.exit(1)
    
    question = sys.argv[1]
    order_no = sys.argv[2]
    credential = sys.argv[3]
    
    try:
        result = ai_writer(question, order_no, credential)
        print(result)
    except Exception as e:
        print(f"PAY_STATUS: ERROR")
        print(f"ERROR_INFO: {str(e)}")
        sys.exit(1)
