"""
Web Gateway HTTP Server
提供 HTTP API 供 MCP Server 调用
"""
from aiohttp import web
import asyncio

# 存储来自浏览器的命令结果
pending_commands = {}
command_results = {}

async def handle_command(request):
    """接收 MCP Server 的命令"""
    data = await request.json()
    command_id = str(id(data))

    # 存储命令，等待浏览器处理
    pending_commands[command_id] = data

    # 等待结果（最多 10 秒）
    for _ in range(100):
        if command_id in command_results:
            result = command_results.pop(command_id)
            return web.json_response(result)
        await asyncio.sleep(0.1)

    return web.json_response({"error": "Timeout"})

async def handle_poll(request):
    """浏览器轮询获取待处理命令"""
    if pending_commands:
        command_id, command = pending_commands.popitem()
        return web.json_response({"id": command_id, "command": command})
    return web.json_response({"id": None})

async def handle_result(request):
    """浏览器提交命令结果"""
    data = await request.json()
    command_results[data["id"]] = data["result"]
    return web.json_response({"success": True})

async def handle_index(request):
    """返回 HTML 页面"""
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'web-gateway', 'index.html')
    with open(file_path, 'r', encoding='utf-8') as f:
        return web.Response(text=f.read(), content_type='text/html')

async def handle_js(request):
    """返回 JS 文件"""
    import os
    filename = request.match_info['filename']
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'web-gateway', f'{filename}.js')
    with open(file_path, 'r', encoding='utf-8') as f:
        return web.Response(text=f.read(), content_type='application/javascript')

app = web.Application()
app.router.add_post('/command', handle_command)
app.router.add_get('/poll', handle_poll)
app.router.add_post('/result', handle_result)
app.router.add_get('/', handle_index)
app.router.add_get('/{filename}.js', handle_js)

if __name__ == '__main__':
    print('🚀 Web Gateway Server 启动在 http://localhost:3000')
    web.run_app(app, host='localhost', port=3000)
