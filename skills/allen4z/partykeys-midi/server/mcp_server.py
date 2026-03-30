"""
PartyKeys MCP Server
支持多种 Gateway 模式的音乐硬件控制服务
"""
import asyncio
import json
import subprocess
import os
from typing import Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
import aiohttp
from aiohttp import web
from script_ble_client import ScriptBLEClient

# Gateway 管理器
class GatewayManager:
    def __init__(self):
        self.gateway_url: Optional[str] = None
        self.connected = False
        self.web_server_process: Optional[subprocess.Popen] = None
        self.script_client: Optional[ScriptBLEClient] = None
        self.mode: Optional[str] = None

    def start_web_server(self) -> dict:
        """启动 Web Gateway Server"""
        try:
            web_dir = os.path.join(os.path.dirname(__file__), "..", "web-gateway")
            self.web_server_process = subprocess.Popen(
                ["node", "server.js"],
                cwd=web_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.gateway_url = "http://localhost:9527"
            return {"success": True, "url": "http://localhost:9527", "message": "请在浏览器中打开 http://localhost:9527 进行连接"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop_web_server(self):
        """停止 Web Gateway Server"""
        if self.web_server_process:
            self.web_server_process.terminate()
            self.web_server_process = None

    async def send_command(self, command: str, params: dict) -> dict:
        """发送命令到 Gateway"""
        if not self.gateway_url:
            return {"error": "Gateway not connected"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.gateway_url}/command",
                    json={"command": command, "params": params},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    return await resp.json()
        except Exception as e:
            return {"error": str(e)}

# 全局实例
gateway = GatewayManager()
app = Server("partykeys")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """定义 MCP Tools"""
    return [
        Tool(
            name="music_connect",
            description="连接音乐硬件设备",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["script", "mobile", "web"],
                        "description": "连接模式：script(脚本连接), mobile(手机中转-待实现), web(Web浏览器连接)",
                        "default": "web"
                    },
                    "address": {
                        "type": "string",
                        "description": "设备地址（script模式下可选，用于直接连接指定设备）"
                    }
                },
            }
        ),
        Tool(
            name="music_disconnect",
            description="断开音乐硬件连接",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="music_light_keys",
            description="点亮指定按键的 LED 灯",
            inputSchema={
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "音符列表，如 ['C4', 'E4', 'G4']"
                    },
                    "color": {
                        "type": "string",
                        "description": "颜色，如 'red', 'green', 'blue'",
                        "default": "blue"
                    },
                    "brightness": {
                        "type": "number",
                        "description": "亮度 0-100",
                        "default": 100
                    }
                },
                "required": ["keys"]
            }
        ),
        Tool(
            name="music_listen",
            description="监听用户弹奏输入",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "number",
                        "description": "超时时间（毫秒）",
                        "default": 5000
                    },
                    "mode": {
                        "type": "string",
                        "description": "监听模式：single(单音符) 或 continuous(持续)",
                        "default": "single"
                    }
                }
            }
        ),
        Tool(
            name="music_play_sequence",
            description="播放音符序列（用于曲谱实时点亮）",
            inputSchema={
                "type": "object",
                "properties": {
                    "sequence": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "keys": {"type": "array", "items": {"type": "string"}},
                                "delay": {"type": "number", "description": "延迟时间（毫秒）"}
                            }
                        },
                        "description": "音符序列，每个元素包含 keys 和 delay"
                    }
                }
            }
        ),
        Tool(
            name="music_follow_mode",
            description="跟弹模式 - 点亮音符并等待用户弹奏正确后继续",
            inputSchema={
                "type": "object",
                "properties": {
                    "notes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "音符序列（按顺序）"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "每个音符的超时时间（毫秒）",
                        "default": 30000
                    }
                },
                "required": ["notes"]
            }
        ),
        Tool(
            name="music_status",
            description="获取硬件连接状态",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """处理工具调用"""

    if name == "music_connect":
        mode = arguments.get("mode", "web")

        if mode == "script":
            gateway.script_client = ScriptBLEClient()
            address = arguments.get("address")
            result = await gateway.script_client.connect(address)
            if result.get("success"):
                gateway.mode = "script"
                gateway.connected = True
                result["message"] = f"已通过脚本连接设备: {result['address']}"
        elif mode == "mobile":
            result = {"success": False, "error": "手机中转模式尚未实现，敬请期待"}
        elif mode == "web":
            server_result = gateway.start_web_server()
            if not server_result["success"]:
                result = server_result
            else:
                gateway.mode = "web"
                result = {
                    "success": True,
                    "mode": "web",
                    "message": f"Web Server 已启动！\n请在浏览器中打开: {server_result['url']}\n然后点击页面上的'连接设备'按钮完成蓝牙配对"
                }
        else:
            result = {"success": False, "error": f"未知的连接模式: {mode}"}

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False)
        )]

    elif name == "music_disconnect":
        if gateway.mode == "script":
            result = await gateway.script_client.disconnect()
            gateway.script_client = None
        else:
            result = await gateway.send_command("disconnect", {})
            gateway.stop_web_server()

        gateway.connected = False
        gateway.mode = None

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False)
        )]

    elif name == "music_light_keys":
        if gateway.mode == "script":
            result = await gateway.script_client.light_keys(arguments["keys"], arguments.get("color", 1), arguments.get("brightness", 100))
        else:
            result = await gateway.send_command("light_keys", arguments)

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False)
        )]

    elif name == "music_play_sequence":
        if gateway.mode == "script":
            result = await gateway.script_client.play_sequence(arguments["sequence"])
        else:
            result = {"success": False, "error": "仅 script 模式支持序列播放"}

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False)
        )]

    elif name == "music_follow_mode":
        if gateway.mode == "script":
            result = await gateway.script_client.follow_mode(arguments["notes"], arguments.get("timeout", 30000))
        else:
            result = {"success": False, "error": "仅 script 模式支持跟弹模式"}

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False)
        )]

    elif name == "music_listen":
        result = await gateway.send_command("listen", arguments)

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False)
        )]

    elif name == "music_status":
        status = {
            "connected": gateway.connected,
            "gateway_url": gateway.gateway_url,
            "gateway_type": "web-bluetooth"
        }

        return [TextContent(
            type="text",
            text=json.dumps(status, ensure_ascii=False)
        )]

    else:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"})
        )]

async def main():
    """启动 MCP Server"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
