// 火山引擎文档安全侦察脚本
// 严格遵守速率限制和robots.txt规则

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// 配置 - 严格遵守安全规则
const config = {
    // 目标URL - 只检查最关键的几个
    urls: [
        {
            url: 'https://www.volcengine.com/docs/82379/1399009?lang=zh',
            name: '目标文档-文本生成',
            priority: 'high'
        },
        {
            url: 'https://www.volcengine.com/docs/82379/1263693?lang=zh',
            name: 'API参考文档',
            priority: 'high'
        },
        {
            url: 'https://www.volcengine.com/docs/82379',
            name: '文档根目录',
            priority: 'medium'
        }
    ],
    
    // 安全设置
    safety: {
        minDelayMs: 8000,  // 最小8秒延迟
        maxDelayMs: 15000, // 最大15秒延迟
        maxRetries: 2,
        timeoutMs: 30000,
        maxPages: 1,       // 只开一个页面，顺序访问
        headless: true,
        stealth: true
    },
    
    // 输出目录
    outputDir: './safe-results'
};

// 创建输出目录
if (!fs.existsSync(config.outputDir)) {
    fs.mkdirSync(config.outputDir, { recursive: true });
}

// 日志函数
function log(message, level = 'INFO') {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] [${level}] ${message}`;
    console.log(logEntry);
    
    // 记录到文件
    fs.appendFileSync(path.join(config.outputDir, 'recon.log'), logEntry + '\n');
}

// 随机延迟函数
function randomDelay(min, max) {
    const delay = Math.floor(Math.random() * (max - min + 1)) + min;
    log(`随机延迟 ${delay}ms...`);
    return new Promise(resolve => setTimeout(resolve, delay));
}

// 检查URL
async function checkUrl(page, urlInfo) {
    const { url, name } = urlInfo;
    
    log(`检查: ${name}`);
    log(`URL: ${url}`);
    
    try {
        // 访问页面
        const response = await page.goto(url, {
            waitUntil: 'domcontentloaded',
            timeout: config.safety.timeoutMs
        });
        
        const status = response.status();
        log(`状态码: ${status}`);
        
        if (status === 200) {
            // 获取页面信息
            const title = await page.title();
            const contentLength = (await page.content()).length;
            
            // 检查是否有实际内容（非空白页面）
            const hasContent = contentLength > 5000; // 假设有内容的页面至少5KB
            const hasText = (await page.textContent('body')).trim().length > 100;
            
            // 检查特定元素
            const selectors = [
                'article', '.documentation', 'main', '.content', 
                'section', '.doc-content', '.markdown-body'
            ];
            
            let hasDocElement = false;
            for (const selector of selectors) {
                const element = await page.$(selector);
                if (element) {
                    hasDocElement = true;
                    break;
                }
            }
            
            // 提取少量文本样本（不保存完整内容）
            const sampleText = await page.evaluate(() => {
                const body = document.querySelector('body');
                if (!body) return '';
                
                const text = body.innerText || body.textContent || '';
                // 取前500字符作为样本
                return text.substring(0, 500).trim();
            });
            
            log(`标题: ${title || 'N/A'}`);
            log(`内容长度: ${contentLength} 字符`);
            log(`是否有内容: ${hasContent}`);
            log(`是否有文档元素: ${hasDocElement}`);
            log(`文本样本: ${sampleText ? '已提取' : '无'}`);
            
            return {
                url,
                name,
                exists: true,
                status,
                title: title || '',
                hasContent,
                hasDocElement,
                contentLength,
                sampleText,
                timestamp: new Date().toISOString()
            };
            
        } else {
            log(`页面返回非200状态: ${status}`);
            return {
                url,
                name,
                exists: false,
                status,
                error: `HTTP ${status}`,
                timestamp: new Date().toISOString()
            };
        }
        
    } catch (error) {
        log(`访问错误: ${error.message}`, 'ERROR');
        return {
            url,
            name,
            exists: false,
            status: 0,
            error: error.message,
            timestamp: new Date().toISOString()
        };
    }
}

// 主函数
async function main() {
    log('=== 火山引擎文档安全侦察开始 ===');
    log(`严格遵守速率限制: ${config.safety.minDelayMs}-${config.safety.maxDelayMs}ms 延迟`);
    log(`检查 ${config.urls.length} 个URL`);
    log(`输出目录: ${config.outputDir}`);
    
    // 记录robots.txt规则遵守声明
    log('遵守robots.txt规则:');
    log('  - User-agent: *');
    log('  - Disallow: /notice (已避开)');
    log('  - Disallow: /products/11111111emr (已避开)');
    log('  - Disallow: /theme, /themes (已避开)');
    log('  - /docs/ 目录未禁止，但谨慎访问');
    
    let browser = null;
    const results = [];
    
    try {
        // 启动浏览器 - 使用系统Chrome避免下载
        log('启动浏览器(使用系统Chrome)...');
        browser = await chromium.launch({
            channel: 'chrome',  // 使用已安装的Chrome
            headless: config.safety.headless,
            timeout: 60000
        });
        
        // 创建上下文，模拟真实浏览器
        const context = await browser.newContext({
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport: { width: 1280, height: 800 },
            locale: 'zh-CN',
            timezoneId: 'Asia/Shanghai'
        });
        
        const page = await context.newPage();
        
        // 按顺序检查每个URL
        for (let i = 0; i < config.urls.length; i++) {
            const urlInfo = config.urls[i];
            
            log(`\n--- 检查 ${i+1}/${config.urls.length}: ${urlInfo.name} ---`);
            
            // 如果不是第一个URL，先延迟
            if (i > 0) {
                await randomDelay(config.safety.minDelayMs, config.safety.maxDelayMs);
            }
            
            // 检查URL
            const result = await checkUrl(page, urlInfo);
            results.push(result);
            
            // 保存中间结果（以防中断）
            fs.writeFileSync(
                path.join(config.outputDir, 'results-interim.json'),
                JSON.stringify(results, null, 2)
            );
            
            // 如果遇到疑似封锁，立即停止
            if (result.status === 403 || result.status === 429) {
                log(`⚠️ 检测到疑似封锁状态 (${result.status})，立即停止！`, 'WARN');
                break;
            }
        }
        
        // 关闭浏览器
        await browser.close();
        browser = null;
        
    } catch (error) {
        log(`侦察过程出错: ${error.message}`, 'ERROR');
        if (browser) {
            try {
                await browser.close();
            } catch (e) {
                // 忽略关闭错误
            }
        }
    }
    
    // 保存最终结果
    const resultsFile = path.join(config.outputDir, 'results.json');
    fs.writeFileSync(resultsFile, JSON.stringify(results, null, 2));
    log(`\n结果保存到: ${resultsFile}`);
    
    // 生成报告
    const foundCount = results.filter(r => r.exists).length;
    const report = `# 火山引擎文档安全侦察报告

## 安全声明
- **严格遵守** robots.txt 规则
- **严格遵守** 速率限制 (${config.safety.minDelayMs}-${config.safety.maxDelayMs}ms 延迟)
- **仅检查** ${config.urls.length} 个关键URL
- **未进行** 大规模爬取或内容下载

## 侦察概要
- 时间: ${new Date().toISOString()}
- 检查URL数: ${config.urls.length}
- 成功访问: ${foundCount}
- 成功率: ${((foundCount / config.urls.length) * 100).toFixed(1)}%

## 详细结果

${results.map(r => {
    if (r.exists) {
        return `### ✅ ${r.name}
- URL: ${r.url}
- 状态: ${r.status}
- 标题: ${r.title || 'N/A'}
- 内容长度: ${r.contentLength} 字符
- 是否有文档元素: ${r.hasDocElement}
- 时间: ${r.timestamp}`;
    } else {
        return `### ❌ ${r.name}
- URL: ${r.url}
- 状态: ${r.status || 'N/A'}
- 错误: ${r.error || 'N/A'}
- 时间: ${r.timestamp}`;
    }
}).join('\n\n')}

## 发现总结
${foundCount > 0 ? 
`1. ${results.filter(r => r.exists).map(r => r.name).join(', ')} 可访问
2. 建议进一步分析可访问页面的结构
3. 如果大部分页面不可访问，可能需要调整访问策略` : 
`1. 所有文档URL均无法访问
2. 可能原因: 反爬机制、需要认证、或URL模式已变更
3. 建议: 人工验证URL有效性，或尝试其他访问方法`}

## 安全记录
- 所有请求均遵守了速率限制
- 未触发 robots.txt 禁止规则
- 如遇疑似封锁已立即停止

## 建议
${foundCount > 0 ? 
`1. 基于成功访问的页面，分析DOM结构
2. 制定更详细的提取方案
3. 继续保持谨慎的访问频率` : 
`1. 人工检查目标URL是否可访问
2. 检查是否需要特定请求头或Cookie
3. 考虑使用官方API替代文档爬取`}
`;

    const reportFile = path.join(config.outputDir, 'report.md');
    fs.writeFileSync(reportFile, report);
    log(`报告保存到: ${reportFile}`);
    
    // 最终统计
    log('\n=== 侦察完成 ===');
    log(`总计: ${config.urls.length} 个URL`);
    log(`成功: ${foundCount}`);
    log(`失败: ${config.urls.length - foundCount}`);
    
    // 安全提醒
    if (foundCount === 0) {
        log('⚠️  所有文档URL访问失败，建议暂停自动化尝试', 'WARN');
        log('   可能触发反爬机制，建议人工验证', 'WARN');
    }
    
    return results;
}

// 执行
if (require.main === module) {
    main().catch(error => {
        console.error('侦察失败:', error);
        process.exit(1);
    });
}

module.exports = { main, config };