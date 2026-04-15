import requests
import json
import uuid

LAF_URL = "https://q3me0awfv7.sealosgzg.site/insight-ecom-gateway"
PAYMENT_URL = "https://afdian.com/order/create?plan_id=c27d1baa33c911f1a45652540025c377&product_type=0&remark=&affiliate_code="

def main(params):
    query = params.get("query", "")
    user_id = params.get("user_id", "")

    # ==================== 步骤1：生成/验证 user_id ====================
    if not user_id or user_id == "guest":
        new_id = "user_" + str(uuid.uuid4())[:8]
        return {
            "status": "need_register",
            "is_registered": False,
            "is_paid": False,
            "is_expired": False,
            "user_id": new_id,
            "payment_url": PAYMENT_URL,
            "payment_status": "未支付",
            "message": f"""📋 请先注册【灵犀神谕】账号

━━━━━━━━━━━━━━━
您的账号信息
━━━━━━━━━━━━━━━
👤 用户ID：{new_id}
📊 状态：未注册
💰 支付状态：未支付
━━━━━━━━━━━━━━━

请按以下步骤完成注册：

1️⃣ 点击下方链接支付（199元/年）
   → {PAYMENT_URL}

2️⃣ 支付时【留言/备注】栏填写：
   {new_id}

3️⃣ 支付成功后，回复：
   激活 {new_id}

—— 灵犀出品，必属精品"""
        }

    # ==================== 步骤2：调用 LAF 检查支付状态 ====================
    payload = {
        "action": "search",
        "query": query,
        "user_id": user_id
    }

    try:
        response = requests.post(LAF_URL, json=payload, timeout=10)
        res_data = response.json()

        status = res_data.get("status") or res_data.get("ec")

        if status == "success":
            return {
                "status": "success",
                "is_registered": True,
                "is_paid": True,
                "is_expired": False,
                "user_id": user_id,
                "payment_url": PAYMENT_URL,
                "payment_status": "已支付",
                "data": res_data.get("data"),
                "message": f"✅ 权限验证通过，以下是您的搜索结果：\n\n━━━━━━━━━━━━━━━\n您的账号信息\n━━━━━━━━━━━━━━━\n👤 用户ID：{user_id}\n📊 状态：已注册 ✅\n💰 支付状态：已支付 ✅\n━━━━━━━━━━━━━━━\n\n{res_data.get('data')}"
            }

        elif status == "expired":
            return {
                "status": "expired",
                "is_registered": True,
                "is_paid": True,
                "is_expired": True,
                "user_id": user_id,
                "payment_url": PAYMENT_URL,
                "payment_status": "已过期",
                "message": f"""🔄 您的权限已过期

━━━━━━━━━━━━━━━
您的账号信息
━━━━━━━━━━━━━━━
👤 用户ID：{user_id}
📊 状态：已注册（权限过期）
💰 支付状态：已过期
━━━━━━━━━━━━━━━

请按以下步骤续费：

1️⃣ 点击续费链接（199元/年）
   → {PAYMENT_URL}

2️⃣ 支付时【留言】填写：
   {user_id}

3️⃣ 支付成功后回复：
   激活 {user_id}

—— 灵犀出品，必属精品"""
            }

        elif status in ("need_pay", "need_pay未支付"):
            return {
                "status": "need_pay",
                "is_registered": True,
                "is_paid": False,
                "is_expired": False,
                "user_id": user_id,
                "payment_url": PAYMENT_URL,
                "payment_status": "未支付",
                "message": f"""💳 请完成支付以激活权限

━━━━━━━━━━━━━━━
您的账号信息
━━━━━━━━━━━━━━━
👤 用户ID：{user_id}
📊 状态：已注册（待激活）
💰 支付状态：未支付
━━━━━━━━━━━━━━━

请复制上方用户ID，粘贴到爱发电支付留言框：

1️⃣ 点击支付链接（199元/年）
   → {PAYMENT_URL}

2️⃣ 留言内容：
   {user_id}

3️⃣ 支付后回复本消息，24小时内开通

—— 灵犀出品，必属精品"""
            }

        else:
            return {
                "status": "error",
                "is_registered": False,
                "is_paid": False,
                "is_expired": False,
                "user_id": user_id,
                "payment_url": PAYMENT_URL,
                "payment_status": "未知",
                "message": res_data.get("message") or "系统繁忙，请联系 kinseyho16"
            }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "is_registered": False,
            "is_paid": False,
            "is_expired": False,
            "user_id": user_id,
            "payment_url": PAYMENT_URL,
            "payment_status": "连接超时",
            "message": "⏱️ 连接超时，请检查网络后重试"
        }
    except Exception as e:
        return {
            "status": "error",
            "is_registered": False,
            "is_paid": False,
            "is_expired": False,
            "user_id": user_id,
            "payment_url": PAYMENT_URL,
            "payment_status": "连接失败",
            "message": f"❌ 连接失败: {str(e)}"
        }