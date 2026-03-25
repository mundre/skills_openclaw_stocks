/**
 * Configuration Manager
 * 配置管理模块
 */

const fs = require('fs');
const path = require('path');
const { validateAndUpdate } = require('./db/config-sync');
const { validateSessionConfig } = require('./db/session-validator');

class Config {
    constructor() {
        this.config = {};
        this.load();
    }

    /**
     * 加载配置
     */
    async load() {
        // 从环境变量加载
        this.config.github = {
            token: process.env.GITHUB_TOKEN || '',
            owner: process.env.GITHUB_OWNER || 'default-owner'
        };

        this.config.agents = {
            dev_count: parseInt(process.env.DEV_AGENT_COUNT) || 2,
            test_count: parseInt(process.env.TEST_AGENT_COUNT) || 1,
            review_count: parseInt(process.env.REVIEW_AGENT_COUNT) || 1
        };

        this.config.logging = {
            level: process.env.LOG_LEVEL || 'info',
            file: process.env.LOG_FILE || 'github-collab.log'
        };

        // 从数据库加载并同步 Agent 配置（方案 C）
        try {
            await validateAndUpdate();
            const { AGENT_ADDRESSES } = require('./agent-addresses');
            
            this.config.qq = {
                enabled: process.env.QQ_ENABLED === 'true',
                token: process.env.QQ_TOKEN || '',
                // 默认使用 main-agent 地址
                defaultTarget: process.env.QQ_TARGET || AGENT_ADDRESSES['main-agent'].target,
                // 所有 Agent 的独立地址
                agentAddresses: AGENT_ADDRESSES,
                // 数据库配置状态
                dbConfigured: true,
                lastSync: new Date().toISOString()
            };
            
            console.log('✅ Agent 配置已从数据库加载并同步');
        } catch (error) {
            console.warn('⚠️ 从数据库加载配置失败，使用默认配置:', error.message);
            
            // 降级到默认配置
            const { AGENT_ADDRESSES } = require('./agent-addresses');
            
            this.config.qq = {
                enabled: process.env.QQ_ENABLED === 'true',
                token: process.env.QQ_TOKEN || '',
                defaultTarget: process.env.QQ_TARGET || AGENT_ADDRESSES['main-agent'].target,
                agentAddresses: AGENT_ADDRESSES,
                dbConfigured: false,
                error: error.message
            };
        }

        // 从配置文件加载（如果存在）
        const configPath = path.join(__dirname, '.github-collab-config.json');
        if (fs.existsSync(configPath)) {
            try {
                const fileConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
                this.config = { ...this.config, ...fileConfig };
            } catch (error) {
                console.warn('Failed to load config file:', error.message);
            }
        }

        console.log('[Config] Configuration loaded:', JSON.stringify(this.config, null, 2));
    }

    /**
     * 获取配置
     * @param {string} key - 配置键（支持点号分隔）
     * @returns {any} - 配置值
     */
    get(key) {
        const keys = key.split('.');
        let value = this.config;
        for (const k of keys) {
            value = value?.[k];
        }
        return value;
    }

    /**
     * 设置配置
     * @param {string} key - 配置键
     * @param {any} value - 配置值
     */
    set(key, value) {
        const keys = key.split('.');
        let config = this.config;
        for (let i = 0; i < keys.length - 1; i++) {
            if (!config[keys[i]]) {
                config[keys[i]] = {};
            }
            config = config[keys[i]];
        }
        config[keys[keys.length - 1]] = value;
    }

    /**
     * 保存配置到文件
     */
    save() {
        const configPath = path.join(__dirname, '.github-collab-config.json');
        fs.writeFileSync(configPath, JSON.stringify(this.config, null, 2));
        console.log('[Config] Configuration saved to:', configPath);
    }

    /**
     * 重新加载配置
     */
    reload() {
        this.load();
    }
}

module.exports = { Config };