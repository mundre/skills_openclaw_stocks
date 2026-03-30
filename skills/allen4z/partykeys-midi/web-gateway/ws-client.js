// WebSocket 客户端 - 连接到 Gateway Server
let ws = null;

function connectWebSocket() {
    ws = new WebSocket('ws://localhost:9528');

    ws.onopen = () => {
        log('✅ WebSocket 已连接到 Gateway Server');
    };

    ws.onmessage = async (event) => {
        const { id, command, params } = JSON.parse(event.data);
        log(`📥 收到命令: ${command}`);

        let result;
        try {
            result = await handleCommand(command, params);
        } catch (error) {
            result = { success: false, error: error.message };
        }

        ws.send(JSON.stringify({ id, ...result }));
    };

    ws.onerror = (error) => {
        log('❌ WebSocket 错误: ' + error.message);
    };

    ws.onclose = () => {
        log('⚠️ WebSocket 已断开');
        setTimeout(connectWebSocket, 3000);
    };
}

async function handleCommand(command, params) {
    switch (command) {
        case 'connect':
            return await bleClient.connect();
        case 'disconnect':
            return await bleClient.disconnect();
        case 'light_keys':
            return await bleClient.lightKeys(params.keys, params.color, params.brightness);
        case 'listen':
            return await bleClient.listen(params.timeout, params.mode);
        default:
            return { success: false, error: '未知命令' };
    }
}

// 页面加载时连接
window.addEventListener('load', connectWebSocket);
