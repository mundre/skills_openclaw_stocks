// Gateway HTTP Server - 接收 MCP Server 的命令
const API_PORT = 3000;

// 命令处理器
const commandHandlers = {
    connect: async () => {
        return await bleClient.connect();
    },

    disconnect: async () => {
        return await bleClient.disconnect();
    },

    light_keys: async (params) => {
        const { keys, color = 'blue', brightness = 100 } = params;
        return await bleClient.lightKeys(keys, color, brightness);
    },

    listen: async (params) => {
        const { timeout = 5000, mode = 'single' } = params;

        // 等待用户输入
        window.lastNote = null;
        const startTime = Date.now();

        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                if (window.lastNote) {
                    clearInterval(checkInterval);
                    resolve({ success: true, note: window.lastNote });
                } else if (Date.now() - startTime > timeout) {
                    clearInterval(checkInterval);
                    resolve({ success: false, error: 'Timeout' });
                }
            }, 100);
        });
    }
};

// 启动简易 HTTP Server（使用 fetch polyfill）
async function startGatewayServer() {
    log('🚀 Gateway Server 启动在 http://localhost:3000');

    // 注意：浏览器中无法直接启动 HTTP Server
    // 这里使用 Service Worker 或需要配合 Node.js 后端
    // 简化方案：使用轮询或 WebSocket
}

// 初始化
window.addEventListener('load', () => {
    log('Gateway 已就绪');
    log('请点击"连接设备"按钮');
});
