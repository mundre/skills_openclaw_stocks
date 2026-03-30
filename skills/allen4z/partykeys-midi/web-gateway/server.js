import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = 9527;

app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

let wsClient = null;
const pendingRequests = new Map();
let requestId = 0;

// WebSocket Server
const wss = new WebSocketServer({ port: 9528 });

wss.on('connection', (ws) => {
  console.log('浏览器客户端已连接');
  wsClient = ws;

  ws.on('message', (data) => {
    const response = JSON.parse(data.toString());
    const pending = pendingRequests.get(response.id);
    if (pending) {
      pending.resolve(response);
      pendingRequests.delete(response.id);
    }
  });

  ws.on('close', () => {
    console.log('浏览器客户端断开');
    wsClient = null;
  });
});

// 发送命令到浏览器
async function sendCommand(command, params) {
  if (!wsClient) {
    return { success: false, error: '浏览器未连接' };
  }

  const id = ++requestId;
  const promise = new Promise((resolve) => {
    pendingRequests.set(id, { resolve });
    setTimeout(() => {
      if (pendingRequests.has(id)) {
        pendingRequests.delete(id);
        resolve({ success: false, error: '请求超时' });
      }
    }, 10000);
  });

  wsClient.send(JSON.stringify({ id, command, params }));
  return promise;
}

// HTTP API
app.post('/command', async (req, res) => {
  const { command, params } = req.body;
  const result = await sendCommand(command, params);
  res.json(result);
});

app.listen(PORT, () => {
  console.log(`Gateway Server 运行在 http://localhost:${PORT}`);
  console.log(`WebSocket Server 运行在 ws://localhost:9528`);
});
