// BLE 客户端 - 处理 Web Bluetooth 连接
class BLEClient {
    constructor() {
        this.device = null;
        this.server = null;
        this.service = null;
        this.characteristics = {};
    }

    async connect() {
        try {
            // 请求 BLE 设备
            this.device = await navigator.bluetooth.requestDevice({
                filters: [{ services: ['03b80e5a-ede8-4b33-a751-6ce34ec4c700'] }],
                optionalServices: ['03b80e5a-ede8-4b33-a751-6ce34ec4c700']
            });

            log('设备已选择: ' + this.device.name);

            // 连接 GATT Server
            this.server = await this.device.gatt.connect();
            log('GATT 已连接');

            // 获取服务
            this.service = await this.server.getPrimaryService('03b80e5a-ede8-4b33-a751-6ce34ec4c700');
            log('服务已获取');

            // 列出所有特征值
            const characteristics = await this.service.getCharacteristics();
            log(`发现 ${characteristics.length} 个特征值:`);
            characteristics.forEach(char => {
                log(`  UUID: ${char.uuid}`);
            });

            // 使用第一个特征值作为 LED 和 MIDI 通道
            if (characteristics.length >= 1) {
                this.characteristics.led = characteristics[0];
                this.characteristics.midi = characteristics[0];
                log('已映射特征值（共用通道）');
            } else {
                throw new Error('未找到特征值');
            }

            // 监听 MIDI 输入
            await this.characteristics.midi.startNotifications();
            log('✅ 已启用 MIDI 输入监听');

            this.characteristics.midi.addEventListener('characteristicvaluechanged', (e) => {
                this.handleMIDIInput(e.target.value);
            });

            log('✅ 硬件连接成功');
            return { success: true };

        } catch (error) {
            log('❌ 连接失败: ' + error.message);
            return { success: false, error: error.message };
        }
    }

    async disconnect() {
        if (this.device && this.device.gatt.connected) {
            this.device.gatt.disconnect();
            log('已断开连接');
        }
        return { success: true };
    }

    frameBleMidiPackets(sysexBytes) {
        const timestamp = 0x80 | (Math.floor(performance.now()) & 0x7f);
        const packets = [];

        const data = Array.from(sysexBytes);
        const f0 = data[0];
        const f7 = data[data.length - 1];
        const body = data.slice(1, -1);

        // 第一个包: header(1) + timestamp(1) + F0(1) + 最多17字节
        const firstPayload = [0x80, timestamp, f0, ...body.slice(0, 17)];
        packets.push(new Uint8Array(firstPayload));

        // 后续包: header(1) + 最多19字节
        let offset = 17;
        while (offset < body.length) {
            const chunk = body.slice(offset, offset + 19);
            packets.push(new Uint8Array([0x80, ...chunk]));
            offset += 19;
        }

        // 最后添加 timestamp + F7
        const lastPacket = packets[packets.length - 1];
        if (lastPacket.length + 2 <= 20) {
            const withF7 = new Uint8Array(lastPacket.length + 2);
            withF7.set(lastPacket);
            withF7[withF7.length - 2] = timestamp;
            withF7[withF7.length - 1] = f7;
            packets[packets.length - 1] = withF7;
        } else {
            packets.push(new Uint8Array([0x80, timestamp, f7]));
        }

        return packets;
    }

    async lightKeys(keys, color = 1, brightness = 100) {
        if (!this.characteristics.led) {
            return { success: false, error: 'Not connected' };
        }

        try {
            // 步骤1: 发送初始化命令
            const initCmd = [0xF0, 0x05, 0x30, 0x7f, 0x7f, 0x20, 0x00, 0x0f, 0x05, 0xF7];
            const initPackets = this.frameBleMidiPackets(initCmd);

            log(`💡 发送初始化命令 (${initPackets.length} 包)...`);
            for (const packet of initPackets) {
                await this.characteristics.led.writeValue(packet);
                log(`   [${Array.from(packet).map(b => b.toString(16).padStart(2, '0')).join(' ')}]`);
            }

            await new Promise(resolve => setTimeout(resolve, 100));

            // 步骤2: 构造亮灯命令
            const header = [0xF0, 0x05, 0x30, 0x7f, 0x7f, 0x20, 0x00, 0x71];
            const keyData = [];
            keys.forEach(key => {
                let midiNote;
                if (typeof key === 'string' && /^[0-9a-fA-F]+$/.test(key)) {
                    midiNote = parseInt(key, 16);
                } else if (typeof key === 'string') {
                    midiNote = this.nameToNote(key);
                } else {
                    midiNote = key;
                }
                keyData.push(midiNote, color);
            });

            const lightCmd = [...header, keys.length, ...keyData, 0xF7];
            const lightPackets = this.frameBleMidiPackets(lightCmd);

            log(`💡 发送亮灯命令 (${lightPackets.length} 包)...`);
            for (const packet of lightPackets) {
                await this.characteristics.led.writeValue(packet);
                log(`   [${Array.from(packet).map(b => b.toString(16).padStart(2, '0')).join(' ')}]`);
            }

            log('✅ 命令发送完成');
            return { success: true };

        } catch (error) {
            log('❌ 控制失败: ' + error.message);
            return { success: false, error: error.message };
        }
    }

    handleMIDIInput(value) {
        const data = new Uint8Array(value.buffer);
        log(`📥 MIDI: [${Array.from(data).map(b => b.toString(16).padStart(2, '0')).join(' ')}]`);
    }

    encodeKeys(keys) {
        // 简化：将音符名转换为 MIDI 编号
        return keys.map(k => this.nameToNote(k));
    }

    nameToNote(name) {
        const notes = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
        const octave = parseInt(name.slice(-1));
        const note = name.slice(0, -1);
        return notes[note] + (octave + 1) * 12;
    }

    noteToName(midi) {
        const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
        const octave = Math.floor(midi / 12) - 1;
        return notes[midi % 12] + octave;
    }
}

// 全局实例
const bleClient = new BLEClient();

// UI 控制
async function connectDevice() {
    const result = await bleClient.connect();
    if (result.success) {
        updateStatus(true);
    }
}

async function disconnectDevice() {
    await bleClient.disconnect();
    updateStatus(false);
}

function updateStatus(connected) {
    const status = document.getElementById('status');
    const connectBtn = document.getElementById('connectBtn');
    const disconnectBtn = document.getElementById('disconnectBtn');
    const testBtn = document.getElementById('testBtn');
    const rawBtn = document.getElementById('rawBtn');

    if (connected) {
        status.className = 'status connected';
        status.textContent = '✅ 已连接';
        connectBtn.disabled = true;
        disconnectBtn.disabled = false;
        testBtn.disabled = false;
        rawBtn.disabled = false;
    } else {
        status.className = 'status disconnected';
        status.textContent = '❌ 未连接';
        connectBtn.disabled = false;
        disconnectBtn.disabled = true;
        testBtn.disabled = true;
        rawBtn.disabled = true;
    }
}

async function testLightKeys() {
    log('🧪 测试点亮 C4, E4, G4...');
    const result = await bleClient.lightKeys(['C4', 'E4', 'G4']);
    if (result.success) {
        log('✅ 测试成功');
    } else {
        log('❌ 测试失败: ' + result.error);
    }
}

async function testRawCommand() {
    log('🧪 测试原始命令...');
    // 测试：F0 05 30 7f 7f 20 00 71 05 30 01 34 01 37 03 3b 01 3e 05 F7
    const cmd = new Uint8Array([0xF0, 0x05, 0x30, 0x7f, 0x7f, 0x20, 0x00, 0x71, 0x05, 0x30, 0x01, 0x34, 0x01, 0x37, 0x03, 0x3b, 0x01, 0x3e, 0x05, 0xF7]);
    log(`   发送: [${Array.from(cmd).map(b => b.toString(16).padStart(2, '0')).join(' ')}]`);
    try {
        await bleClient.characteristics.led.writeValue(cmd);
        log('✅ 原始命令已发送');
    } catch (e) {
        log('❌ 发送失败: ' + e.message);
    }
}

function log(message) {
    const logDiv = document.getElementById('log');
    const item = document.createElement('div');
    item.className = 'log-item';
    item.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logDiv.appendChild(item);
    logDiv.scrollTop = logDiv.scrollHeight;
}
