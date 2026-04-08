#!/usr/bin/env node
/**
 * Bucket List File Server
 * 让 HTML 和 Clawd 能共同读写 bucket-list.json
 * 
 * 安全限制：仅允许 localhost 访问
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 9999;
const SKILL_DIR = __dirname;
const WORKSPACE_DIR = path.join(SKILL_DIR, '..', '..');
const DATA_DIR = path.join(WORKSPACE_DIR, 'data');
const DATA_FILE = path.join(DATA_DIR, 'bucket-list.json');

// 确保数据文件存在
function ensureDataFile() {
    if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
    if (!fs.existsSync(DATA_FILE)) {
        fs.writeFileSync(DATA_FILE, JSON.stringify({
            version: '1.0',
            wishes: [],
            createdAt: new Date().toISOString().split('T')[0]
        }, null, 2));
    }
}

// 读取数据
function readData() {
    ensureDataFile();
    try {
        return fs.readFileSync(DATA_FILE, 'utf-8');
    } catch (e) {
        return JSON.stringify({ version: '1.0', wishes: [] });
    }
}

// 写入数据
function writeData(data) {
    ensureDataFile();
    fs.writeFileSync(DATA_FILE, data);
}

const server = http.createServer((req, res) => {
    // CORS - 仅允许 localhost（安全限制）
    const origin = req.headers.origin || '';
    if (origin.startsWith('http://localhost') || origin.startsWith('http://127.0.0.1')) {
        res.setHeader('Access-Control-Allow-Origin', origin);
    }
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // 只处理 data/bucket-list.json
    if (req.url === '/data/bucket-list.json' || req.url === '/data/bucket-list.json/') {
        if (req.method === 'GET') {
            const data = readData();
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(data);
        } else if (req.method === 'POST') {
            let body = '';
            req.on('data', chunk => body += chunk);
            req.on('end', () => {
                try {
                    // 验证 JSON 格式
                    const parsed = JSON.parse(body);
                    if (!parsed.wishes || !Array.isArray(parsed.wishes)) {
                        res.writeHead(400);
                        res.end('{"error": "无效数据格式"}');
                        return;
                    }
                    writeData(body);
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(body);
                } catch (e) {
                    res.writeHead(400);
                    res.end('{"error": "无效 JSON"}');
                }
            });
        } else {
            res.writeHead(405);
            res.end('{"error": "Method not allowed"}');
        }
    } else {
        // 静态文件服务
        let filePath = req.url === '/' ? '/bucket-list.html' : req.url;
        filePath = path.join(__dirname, filePath);

        if (!filePath.startsWith(__dirname)) {
            res.writeHead(403);
            res.end('Forbidden');
            return;
        }

        fs.readFile(filePath, (err, data) => {
            if (err) {
                res.writeHead(404);
                res.end('Not found');
            } else {
                const ext = path.extname(filePath);
                const types = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css', '.json': 'application/json' };
                res.writeHead(200, { 'Content-Type': types[ext] || 'application/octet-stream' });
                res.end(data);
            }
        });
    }
});

ensureDataFile();
server.listen(PORT, '127.0.0.1', () => {
    console.log(`🦞 Bucket List Server 运行中`);
    console.log(`   网页: http://localhost:${PORT}/`);
    console.log(`   数据: ${DATA_FILE}`);
    console.log(`   安全: 仅 localhost 访问`);
});