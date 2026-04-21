#!/usr/bin/env python3
"""cn-qrcode-generator - 二维码生成工具"""
import sys, os, base64, ssl, urllib.request, urllib.parse

def generate_qrcode(text, size=300, margin=4, format='png'):
    """生成二维码
    
    使用qrserver.com API，无需安装依赖
    SSL双层降级：优先标准验证，失败后回退到不验证
    """
    encoded_text = urllib.parse.quote(text)
    url = f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&margin={margin}&format={format}&data={encoded_text}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    # 方案1：标准SSL验证
    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=15)
        data = response.read()
        return {
            "success": True,
            "data": f"data:image/{format};base64,{base64.b64encode(data).decode()}",
            "url": url
        }
    except Exception as e:
        error_str = str(e)
        if 'SSL' not in error_str:
            return {"success": False, "error": error_str}
        # SSL错误，降级到不验证
        pass
    
    # 方案2：SSL不验证（降级）
    try:
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=15, context=ctx)
        data = response.read()
        return {
            "success": True,
            "data": f"data:image/{format};base64,{base64.b64encode(data).decode()}",
            "url": url,
            "note": "SSL verification bypassed"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == '__main__':
    text = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    result = generate_qrcode(text)
    if result["success"]:
        print(f"✅ 二维码生成成功!")
        print(f"   Base64长度: {len(result['data'])} 字符")
    else:
        print(f"❌ 生成失败: {result['error']}")
