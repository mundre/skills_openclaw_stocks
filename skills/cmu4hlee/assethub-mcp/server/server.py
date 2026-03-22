#!/usr/bin/env python3
"""
AssetHub MCP Server
Provides asset management API tools via MCP protocol
"""

import json
import urllib.request
import urllib.parse
import sys

BASE_URL = "http://160ttth72797.vicp.fun:59745/api"
TENANT_ID = "2"
_token = None

def login():
    """Login and get token"""
    global _token
    url = f"{BASE_URL}/users/login"
    data = json.dumps({"username": "su", "password": "123456"}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Tenant-ID", TENANT_ID)
    with urllib.request.urlopen(req) as r:
        result = json.loads(r.read())
        if result.get("success"):
            _token = result["data"]["token"]
            return _token
    return None

def api_call(endpoint, method="GET", data=None):
    """Make API call"""
    global _token
    if not _token:
        login()
    
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {_token}")
    req.add_header("X-Tenant-ID", TENANT_ID)
    if data:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode()
    
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# MCP Tools
TOOLS = [
    {
        "name": "list_assets",
        "description": "List assets from the asset management system",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Search keyword"},
                "page": {"type": "number", "description": "Page number", "default": 1},
                "pageSize": {"type": "number", "description": "Page size", "default": 50}
            }
        }
    },
    {
        "name": "get_asset",
        "description": "Get detailed information of a specific asset",
        "inputSchema": {
            "type": "object",
            "properties": {
                "asset_code": {"type": "string", "description": "Asset code"}
            },
            "required": ["asset_code"]
        }
    },
    {
        "name": "create_repair_request",
        "description": "Create a repair request for an asset",
        "inputSchema": {
            "type": "object",
            "properties": {
                "asset_code": {"type": "string", "description": "Asset code"},
                "asset_name": {"type": "string", "description": "Asset name"},
                "fault_description": {"type": "string", "description": "Fault description"},
                "fault_level": {"type": "string", "description": "Fault level: 一般/紧急/严重"},
                "request_person": {"type": "string", "description": "Request person name"},
                "department": {"type": "string", "description": "Department"}
            },
            "required": ["asset_code", "fault_description"]
        }
    },
    {
        "name": "list_repair_requests",
        "description": "List repair requests",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "Filter by status"},
                "page": {"type": "number", "description": "Page number", "default": 1}
            }
        }
    }
]

def handle_tool(name, args):
    """Handle tool calls"""
    if name == "list_assets":
        keyword = args.get("keyword", "")
        page = args.get("page", 1)
        pageSize = args.get("pageSize", 50)
        
        params = f"?page={page}&pageSize={pageSize}"
        if keyword:
            params += f"&keyword={urllib.parse.quote(keyword)}"
        
        result = api_call(f"/assets{params}")
        items = result.get("data", {}).get("list", [])
        
        # Filter by keyword in name if present
        if keyword:
            items = [a for a in items if keyword.lower() in str(a.get('asset_name','')).lower()]
        
        # Return simplified data
        simplified = []
        for a in items[:pageSize]:
            simplified.append({
                "asset_code": a.get("asset_code"),
                "asset_name": a.get("asset_name"),
                "location": a.get("location"),
                "status": a.get("status")
            })
        
        return {"content": [{"type": "text", "text": json.dumps(simplified, ensure_ascii=False, indent=2)}]}
    
    elif name == "get_asset":
        code = args.get("asset_code")
        result = api_call(f"/assets?asset_code={code}")
        items = result.get("data", {}).get("list", [])
        if items:
            a = items[0]
            simplified = {
                "asset_code": a.get("asset_code"),
                "asset_name": a.get("asset_name"),
                "specification": a.get("specification"),
                "location": a.get("location"),
                "department": a.get("department_new"),
                "status": a.get("status"),
                "purchase_price": a.get("purchase_price"),
                "purchase_date": a.get("purchase_date")
            }
            return {"content": [{"type": "text", "text": json.dumps(simplified, ensure_ascii=False, indent=2)}]}
        return {"content": [{"type": "text", "text": "Asset not found"}]}
    
    elif name == "create_repair_request":
        data = {
            "asset_code": args.get("asset_code"),
            "asset_name": args.get("asset_name", ""),
            "fault_description": args.get("fault_description"),
            "fault_level": args.get("fault_level", "一般"),
            "request_person": args.get("request_person", "MCP"),
            "department": args.get("department", "")
        }
        result = api_call("/maintenance/requests", method="POST", data=data)
        return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]}
    
    elif name == "list_repair_requests":
        status = args.get("status", "")
        page = args.get("page", 1)
        params = f"?page={page}&pageSize=20"
        if status:
            params += f"&status={urllib.parse.quote(status)}"
        result = api_call(f"/maintenance/requests{params}")
        
        # Handle different response formats
        if isinstance(result.get("data"), list):
            items = result.get("data", [])
        else:
            items = result.get("data", {}).get("list", [])
        
        simplified = []
        for a in items[:10]:
            simplified.append({
                "request_no": a.get("request_no"),
                "asset_name": a.get("asset_name"),
                "status": a.get("status"),
                "fault_description": a.get("fault_description", "")[:50]
            })
        
        return {"content": [{"type": "text", "text": json.dumps(simplified, ensure_ascii=False, indent=2)}]}
    
    return {"error": f"Unknown tool: {name}"}

# MCP Protocol
def mcp_handler():
    """Handle MCP protocol"""
    request = json.load(sys.stdin)
    
    method = request.get("method")
    
    if method == "tools/list":
        print(json.dumps({"tools": TOOLS}))
    elif method == "tools/call":
        tool = request.get("params", {}).get("name")
        args = request.get("params", {}).get("arguments", {})
        result = handle_tool(tool, args)
        print(json.dumps(result))
    else:
        print(json.dumps({"error": f"Unknown method: {method}"}))

if __name__ == "__main__":
    mcp_handler()
