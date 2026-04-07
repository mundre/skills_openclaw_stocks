#!/bin/bash
# ============================================================
# 语音服务启动脚本
# 版本：2.0.0
# 说明：启动语音转录服务（SenseVoice）
# ============================================================

set -e

# 配置
VOICE_SERVICE_DIR="/tmp/sensevoice_service"
LOG_FILE="/tmp/sensevoice.log"
PYTHON_SCRIPT="$VOICE_SERVICE_DIR/voice_service.py"
PORT=8080

# 检查是否已运行
if curl -s "http://localhost:$PORT/health" | grep -q "ok"; then
    echo "✅ 语音服务已在运行 (port $PORT)"
    exit 0
fi

# 创建服务目录
mkdir -p "$VOICE_SERVICE_DIR"

# 创建 Python 服务
cat > "$PYTHON_SCRIPT" << 'EOF'
#!/usr/bin/env python3
"""
语音转录服务
使用 SenseVoice 模型进行语音识别
"""
import os
import logging
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/sensevoice.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Service")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查响应
class HealthResponse(BaseModel):
    status: str
    model: str
    version: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "model": "SenseVoiceSmall",
        "version": "2.0.0"
    }

@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    model: str = Form(default="SenseVoiceSmall")
):
    """
    语音转录
    
    Args:
        file: 音频文件
        model: 模型名称（默认 SenseVoiceSmall）
    
    Returns:
        JSON: {"text": "转录文本", "language": "语言", "success": true/false}
    """
    try:
        # 读取音频文件
        audio_bytes = await file.read()
        
        # TODO: 实际集成 SenseVoice 模型
        # 这里是一个示例实现
        logger.info(f"收到音频文件：{file.name}，大小：{len(audio_bytes)} bytes")
        
        # 模拟转录（实际应该调用 SenseVoice）
        transcribed_text = "（此处为转录文本，需要集成 SenseVoice 模型）"
        language = "zh"
        success = True
        
        logger.info(f"转录成功：{transcribed_text}")
        
        return {
            "text": transcribed_text,
            "language": language,
            "success": success
        }
    
    except Exception as e:
        logger.error(f"转录失败：{e}")
        return {
            "text": "",
            "language": "",
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    logger.info("启动语音服务...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
EOF

# 检查依赖
echo "检查依赖..."
python3 -c "import fastapi" 2>/dev/null || {
    echo "安装依赖中..."
    pip install fastapi uvicorn python-multipart || {
        echo "❌ 无法安装依赖，请手动安装："
        echo "   pip install fastapi uvicorn python-multipart"
        exit 1
    }
}

# 启动服务
echo "启动语音服务..."
nohup python3 "$PYTHON_SCRIPT" > "$LOG_FILE" 2>&1 &
PID=$!

# 等待服务启动
sleep 3

# 检查服务状态
if curl -s "http://localhost:$PORT/health" | grep -q "ok"; then
    echo "✅ 语音服务启动成功 (PID: $PID, port: $PORT)"
    echo "   健康检查：curl http://localhost:$PORT/health"
    echo "   转录接口：curl -X POST http://localhost:$PORT/transcribe -F \"file=@audio.ogg\""
    echo "   日志：tail -f $LOG_FILE"
else
    echo "❌ 语音服务启动失败"
    echo "   查看日志：tail -f $LOG_FILE"
    exit 1
fi
