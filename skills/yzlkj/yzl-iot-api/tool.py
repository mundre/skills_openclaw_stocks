#!/usr/bin/env python3
"""云智联 IoT 设备管理工具"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from urllib.parse import urlencode

API_KEY = os.environ.get("YZLIOT_API_KEY", "")
BASE_URL = "https://open.yzlkj.com"

API_PATHS = {
    "ping": "/open/ping",
    "device_all": "/open/device/all",
    "device_list": "/open/device/list",
    "device": "/open/device/",
    "history": "/open/history",
    "command_send": "/open/command/send",
    "command_list": "/open/command/list",
    "command_detail": "/open/command/detail",
}

def make_request(endpoint, method="GET", data=None):
    if not API_KEY:
        return {"error": "请先设置环境变量 YZLIOT_API_KEY"}
    
    url = f"{BASE_URL}{endpoint}"
    headers = {"YZLIOT-APIKEY": API_KEY}
    
    if method == "POST":
        headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, headers=headers, data=json.dumps(data).encode("utf-8"), method=method)
    elif data:  # GET with Body (for history)
        headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, headers=headers, data=json.dumps(data).encode("utf-8"), method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}

def cmd_ping():
    result = make_request(API_PATHS["ping"])
    if result.get("code") == 0:
        return f"✅ 连接成功！服务器响应: {result.get('data')}"
    return f"❌ 错误: {result}"

def cmd_all():
    result = make_request(API_PATHS["device_all"])
    if result.get("code") != 0:
        return f"❌ 错误: {result}"
    
    items = result.get("data", {}).get("items", [])
    if not items:
        return "📭 未找到设备"
    
    output = [f"📋 设备列表 (共 {len(items)} 台)"]
    for i, dev in enumerate(items, 1):
        output.append(f"{i}. {dev.get('name', 'N/A')} - {dev.get('status', 'N/A')}")
    return "\n".join(output)

def cmd_list(skip=0, max_count=20):
    params = {"SkipCount": skip, "MaxResultCount": max_count}
    endpoint = API_PATHS["device_list"] + "?" + urlencode(params)
    result = make_request(endpoint)
    
    if result.get("code") != 0:
        return f"❌ 错误: {result}"
    
    items = result.get("data", {}).get("items", [])
    total = result.get("data", {}).get("totalCount", 0)
    
    if not items:
        return "📭 未找到设备"
    
    output = [f"📋 设备列表 (共 {total} 台)"]
    for i, dev in enumerate(items, 1):
        output.append(f"{i}. {dev.get('name', 'N/A')} - {dev.get('status', 'N/A')}")
    return "\n".join(output)

def cmd_device(device_id):
    if not device_id:
        return "❌ 请指定设备ID"
    
    endpoint = f"{API_PATHS['device']}{device_id}"
    result = make_request(endpoint)
    
    if result.get("code") != 0:
        return f"❌ 错误: {result}"
    
    dev = result.get("data", {})
    output = [f"📱 {dev.get('name', 'N/A')}", f"状态: {dev.get('status', 'N/A')}"]
    
    facilities = dev.get("facilitys", [])
    if facilities:
        output.append("📊 设施数据:")
        for f in facilities:
            output.append(f"  • {f.get('key', 'N/A')}: {f.get('value', 'N/A')}")
    
    return "\n".join(output)

def cmd_history(facility_id, days=5):
    """获取历史数据
    
    Args:
        facility_id: 设施ID（从 device 命令的设施数据中获取，key 为 id 字段）
        days: 查询天数（默认5天）
    """
    if not facility_id:
        return "❌ 请指定设施ID\n获取方法：先使用 device <设备ID> 查看设备详情，找到对应设施的 id 字段"
    
    # 计算时间范围
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    start_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
    end_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')
    
    # GET + Body 方式 (facilityId 在 query 参数中)
    body = {
        "startTime": start_str,
        "endTime": end_str,
        "maxCount": 500
    }
    
    # facilityId 作为 query 参数
    endpoint = f"{API_PATHS['history']}?facilityId={facility_id}"
    result = make_request(endpoint, method="GET", data=body)
    
    if result.get("code") != 0:
        return f"❌ 错误: {result}"
    
    data = result.get("data", {})
    if "statusCode" in data:
        return f"❌ API错误: statusCode={data.get('statusCode')}"
    
    values = data.get("values", [])
    if not values:
        return "📭 无历史数据"
    
    # 按日期分组统计
    from collections import defaultdict
    daily = defaultdict(list)
    for v in values:
        day = v['time'][:10]
        try:
            daily[day].append(float(v['value']))
        except:
            pass
    
    output = [f"📈 历史数据 (共 {len(values)} 条，近{days}天)", "=" * 40]
    
    for day in sorted(daily.keys()):
        nums = daily[day]
        avg = sum(nums) / len(nums)
        min_v = min(nums)
        max_v = max(nums)
        output.append(f"{day}: 最低{min_v:.1f} / 平均{avg:.1f} / 最高{max_v:.1f} ({len(nums)}条)")
    
    return "\n".join(output)

def cmd_device_history(device_id, days=5):
    """获取设备所有设施的历史数据
    
    Args:
        device_id: 设备ID
        days: 查询天数（默认5天）
    """
    if not device_id:
        return "❌ 请指定设备ID"
    
    # 先获取设备详情
    endpoint = f"{API_PATHS['device']}{device_id}"
    result = make_request(endpoint)
    
    if result.get("code") != 0:
        return f"❌ 获取设备详情失败: {result}"
    
    dev = result.get("data", {})
    facilities = dev.get("facilitys", [])
    
    if not facilities:
        return "❌ 该设备没有设施数据"
    
    # 计算时间范围
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    start_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
    end_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')
    
    body = {
        "startTime": start_str,
        "endTime": end_str,
        "maxCount": 500
    }
    
    output = [f"📈 {dev.get('name', device_id)} 近{days}天历史数据", "=" * 50]
    
    # 获取每个设施的历史数据
    for f in facilities:
        facility_id = f.get("id")
        facility_name = f.get("name", f.get("key", ""))
        
        if not facility_id:
            continue
        
        endpoint = f"{API_PATHS['history']}?facilityId={facility_id}"
        result = make_request(endpoint, method="GET", data=body)
        
        if result.get("code") != 0:
            continue
        
        data = result.get("data", {})
        values = data.get("values", [])
        
        if not values:
            continue
        
        # 统计
        from collections import defaultdict
        daily = defaultdict(list)
        for v in values:
            day = v['time'][:10]
            try:
                daily[day].append(float(v['value']))
            except:
                pass
        
        if daily:
            output.append(f"\n📊 {facility_name}:")
            for day in sorted(daily.keys()):
                nums = daily[day]
                avg = sum(nums) / len(nums)
                min_v = min(nums)
                max_v = max(nums)
                output.append(f"  {day}: {min_v:.1f} ~ {avg:.1f} ~ {max_v:.1f}")
    
    return "\n".join(output)

def cmd_send(device_id, cmd_type, args="{}", wait_confirm=True, wait_timeout=30):
    """发送控制指令
    
    Args:
        device_id: 设备ID
        cmd_type: 指令类型 (GetFac/SetFac/Upfs/Custom)
        args: 指令参数 (JSON 字符串或数组)
        wait_confirm: 是否等待确认
        wait_timeout: 等待超时时间(秒)
    """
    if not device_id:
        return "❌ 请指定设备ID"
    if not cmd_type:
        return "❌ 请指定指令类型"
    
    # args 可以是数组或对象
    try:
        if isinstance(args, str):
            # 尝试解析为JSON
            parsed = json.loads(args)
            # 如果是对象，转为数组格式
            if isinstance(parsed, dict):
                args_list = [json.dumps(parsed)]  # 转为 ["{\"key\":\"value\"}"]
            elif isinstance(parsed, list):
                args_list = parsed
            else:
                args_list = [str(parsed)]
        else:
            args_list = args
    except json.JSONDecodeError:
        # 如果不是JSON，直接作为字符串
        args_list = [args]
    
    body = {
        "deviceId": device_id,
        "type": cmd_type,
        "args": args_list,
        "waitConfirm": wait_confirm,
        "waitTimeout": wait_timeout
    }
    
    result = make_request(API_PATHS["command_send"], method="POST", data=body)
    
    if result.get("code") != 0:
        return f"❌ 发送失败: {result}"
    
    data = result.get("data", {})
    return f"✅ 指令已发送: {json.dumps(data, ensure_ascii=False)}"

def cmd_command_list(device_id, skip=0, max_count=20):
    """获取设备支持的指令列表
    
    Args:
        device_id: 设备ID
        skip: 跳过数量
        max_count: 最大数量
    """
    if not device_id:
        return "❌ 请指定设备ID"
    
    # 注意：文档显示是 DeviceId (大写D)
    params = {"DeviceId": device_id, "SkipCount": skip, "MaxResultCount": max_count}
    endpoint = API_PATHS["command_list"] + "?" + urlencode(params)
    result = make_request(endpoint)
    
    if result.get("code") != 0:
        return f"❌ 获取失败: {result}"
    
    items = result.get("data", {}).get("items", [])
    total = result.get("data", {}).get("totalCount", 0)
    
    if not items:
        return "📭 暂无指令记录"
    
    output = [f"📋 指令列表 (共 {total} 条)"]
    for i, cmd in enumerate(items, 1):
        output.append(f"{i}. {cmd.get('type', 'N/A')} | 状态: {cmd.get('status', 'N/A')}")
        output.append(f"   时间: {cmd.get('creationTime', 'N/A')}")
    
    return "\n".join(output)

def cmd_command_detail(command_id):
    """获取指令详情
    
    Args:
        command_id: 指令ID
    """
    if not command_id:
        return "❌ 请指定指令ID"
    
    endpoint = f"{API_PATHS['command_detail']}{command_id}"
    result = make_request(endpoint)
    
    if result.get("code") != 0:
        return f"❌ 获取失败: {result}"
    
    cmd = result.get("data", {})
    output = [f"📋 指令详情", "=" * 40]
    output.append(f"ID: {cmd.get('id', 'N/A')}")
    output.append(f"设备ID: {cmd.get('deviceId', 'N/A')}")
    output.append(f"类型: {cmd.get('type', 'N/A')}")
    output.append(f"状态: {cmd.get('status', 'N/A')}")
    output.append(f"创建时间: {cmd.get('creationTime', 'N/A')}")
    
    args = cmd.get('args', [])
    if args:
        output.append(f"参数: {args}")
    
    return "\n".join(output)

def main():
    if not API_KEY:
        print("❌ 请先设置环境变量 YZLIOT_API_KEY")
        print("")
        print("获取 API Key：")
        print("1. 打开微信小程序「云智联YZL」")
        print("2. 进入「我的」→「开放接口」")
        print("3. 复制您的 API Token")
        print("")
        print("设置方法：")
        print('  export YZLIOT_API_KEY="您的API密钥"')
        sys.exit(1)
    
    args = sys.argv[1:]
    
    # 不带参数时，默认获取所有设备数据
    if not args:
        print(cmd_all())
        return
    
    cmd = args[0].lower()
    
    if cmd == "ping":
        print(cmd_ping())
    elif cmd == "all":
        print(cmd_all())
    elif cmd == "list":
        print(cmd_list())
    elif cmd == "device":
        print(cmd_device(args[1] if len(args) > 1 else ""))
    elif cmd == "history":
        print(cmd_history(args[1] if len(args) > 1 else "", int(args[2]) if len(args) > 2 else 5))
    elif cmd == "device-history":
        # device-history <设备ID> [天数]
        device_id = args[1] if len(args) > 1 else ""
        days = int(args[2]) if len(args) > 2 else 5
        print(cmd_device_history(device_id, days))
    elif cmd == "send":
        # send <设备ID> <指令类型> [参数]
        device_id = args[1] if len(args) > 1 else ""
        cmd_type = args[2] if len(args) > 2 else ""
        cmd_args = args[3] if len(args) > 3 else "{}"
        print(cmd_send(device_id, cmd_type, cmd_args))
    elif cmd == "cmd-list":
        # cmd-list <设备ID>
        print(cmd_command_list(args[1] if len(args) > 1 else ""))
    elif cmd == "cmd-detail":
        # cmd-detail <指令ID>
        print(cmd_command_detail(args[1] if len(args) > 1 else ""))
    else:
        print(f"❌ 未知命令: {cmd}")
        print("命令: ping, all, list, device <ID>, history <设施ID> [天数], device-history <设备ID> [天数], send <设备ID> <类型> [参数], cmd-list <设备ID>, cmd-detail <指令ID>")

if __name__ == "__main__":
    main()