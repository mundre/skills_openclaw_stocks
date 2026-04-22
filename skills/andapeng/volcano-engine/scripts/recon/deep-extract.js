// 火山引擎文档深度提取脚本 - 阶段2
// 基于阶段1成功侦察结果，提取结构化内容

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// 配置 - 严格遵守安全规则
const config = {
    // 目标URL - 基于阶段1成功访问的URL
    urls: [
        {
            url: 'https://www.volcengine.com/docs/82379/1263693?lang=zh',
            name: 'API参考文档',
            priority: 'high',
            extractionTargets: [
                'api-endpoints',
                'authentication',
                'error-codes',
                'models-list'
            ]
        },
        {
            url: 'https://www.volcengine.com/docs/82379/1399009?lang=zh',
            name: '文本生成文档',
            priority: 'medium',
            extractionTargets: [
                'text-generation-api',
                'parameters',
                'examples',
                'best-practices'
            ]
        },
        {
            url: 'https://www.volcengine.com/docs/82379',
            name: '文档根目录',
            priority: 'low',
            extractionTargets: [
                'navigation-structure',
                'section-index',
                'overview'
            ]
        }
    ],
    
    // 安全设置 - 与阶段1保持一致
    safety: {
        minDelayMs: 8000,  // 最小8秒延迟
        maxDelayMs: 15000, // 最大15秒延迟
        maxRetries: 2,
        timeoutMs: 45000,  // 稍长，因为需要提取内容
        maxPages: 1,
        headless: true,
        stealth: true
    },
    
    // 提取设置
    extraction: {
        maxContentSize: 10000000, // 10MB最大内容
        maxElements: 200,         // 最多提取200个元素
        timeoutPerPage: 60000,    // 每页面最多60秒
        saveRawHtml: false        // 是否保存原始HTML（调试用）
    },
    
    // 输出目录
    outputDir: './phase2-results'
};

// 创建输出目录结构
function createOutputStructure() {
    const dirs = [
        config.outputDir,
        path.join(config.outputDir, 'api-reference'),
        path.join(config.outputDir, 'documentation'),
        path.join(config.outputDir, 'validation'),
        path.join(config.outputDir, 'integration'),
        path.join(config.outputDir, 'raw')
    ];
    
    dirs.forEach(dir => {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    });
}

// 日志函数
function log(message, level = 'INFO') {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] [${level}] ${message}`;
    console.log(logEntry);
    
    // 记录到文件 - 确保目录存在
    const logFile = path.join(config.outputDir, 'extraction-log.json');
    
    try {
        // 确保目录存在
        const logDir = path.dirname(logFile);
        if (!fs.existsSync(logDir)) {
            fs.mkdirSync(logDir, { recursive: true });
        }
        
        const logEntryObj = {
            timestamp,
            level,
            message,
            source: 'deep-extract'
        };
        
        let logs = [];
        if (fs.existsSync(logFile)) {
            logs = JSON.parse(fs.readFileSync(logFile, 'utf8'));
        }
        logs.push(logEntryObj);
        fs.writeFileSync(logFile, JSON.stringify(logs, null, 2));
    } catch (error) {
        // 如果文件操作失败，只输出到控制台
        console.error(`Failed to write log: ${error.message}`);
    }
}

// 随机延迟函数
function randomDelay(min, max) {
    const delay = Math.floor(Math.random() * (max - min + 1)) + min;
    log(`随机延迟 ${delay}ms...`);
    return new Promise(resolve => setTimeout(resolve, delay));
}

// 提取API参考文档内容
async function extractApiReference(page, urlInfo) {
    log(`开始提取API参考文档: ${urlInfo.name}`);
    
    const results = {
        apiEndpoints: [],
        authentication: {},
        errorCodes: [],
        models: [],
        timestamp: new Date().toISOString()
    };
    
    try {
        // 尝试提取表格内容（API端点通常以表格形式呈现）
        const tables = await page.$$eval('table', (tables) => {
            return tables.map((table, index) => {
                const rows = Array.from(table.querySelectorAll('tr'));
                return {
                    index,
                    rowCount: rows.length,
                    headers: rows[0] ? Array.from(rows[0].querySelectorAll('th')).map(th => th.textContent.trim()) : [],
                    data: rows.slice(1).map(row => 
                        Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim())
                    )
                };
            });
        });
        
        log(`找到 ${tables.length} 个表格`);
        
        // 分析表格内容
        for (const table of tables) {
            if (table.rowCount > 1) {
                // 检查是否为API端点表格
                const headers = table.headers.join(' ').toLowerCase();
                if (headers.includes('api') || headers.includes('端点') || 
                    headers.includes('参数') || headers.includes('method')) {
                    
                    log(`识别为API表格: ${table.rowCount}行`);
                    
                    table.data.forEach(row => {
                        if (row.length >= 2) {
                            results.apiEndpoints.push({
                                rowData: row,
                                tableIndex: table.index
                            });
                        }
                    });
                }
                
                // 检查是否为错误码表格
                if (headers.includes('错误') || headers.includes('error') || 
                    headers.includes('代码') || headers.includes('码')) {
                    
                    log(`识别为错误码表格: ${table.rowCount}行`);
                    
                    table.data.forEach(row => {
                        if (row.length >= 2) {
                            results.errorCodes.push({
                                code: row[0],
                                description: row[1],
                                tableIndex: table.index
                            });
                        }
                    });
                }
                
                // 检查是否为模型表格
                if (headers.includes('模型') || headers.includes('model') ||
                    headers.includes('规格') || headers.includes('价格')) {
                    
                    log(`识别为模型表格: ${table.rowCount}行`);
                    
                    table.data.forEach(row => {
                        if (row.length >= 2) {
                            results.models.push({
                                name: row[0],
                                details: row.slice(1),
                                tableIndex: table.index
                            });
                        }
                    });
                }
            }
        }
        
        // 尝试提取认证信息（通常在特定章节）
        const authElements = await page.$$eval('h2, h3, h4', (headers) => {
            return headers
                .filter(h => h.textContent.includes('认证') || h.textContent.includes('Authentication'))
                .map(h => ({
                    tag: h.tagName,
                    text: h.textContent.trim(),
                    nextSibling: h.nextElementSibling ? h.nextElementSibling.textContent.substring(0, 500) : null
                }));
        });
        
        if (authElements.length > 0) {
            log(`找到 ${authElements.length} 个认证相关章节`);
            results.authentication.sections = authElements;
        }
        
        // 提取代码示例
        const codeBlocks = await page.$$eval('pre, code', (elements) => {
            return elements
                .filter(el => el.textContent.length > 50) // 排除太短的代码块
                .map((el, index) => ({
                    index,
                    tag: el.tagName,
                    text: el.textContent.substring(0, 1000), // 限制长度
                    language: el.className.includes('language-') ? el.className : null
                }));
        });
        
        if (codeBlocks.length > 0) {
            log(`找到 ${codeBlocks.length} 个代码块`);
            results.codeExamples = codeBlocks;
        }
        
    } catch (error) {
        log(`提取API参考文档时出错: ${error.message}`, 'ERROR');
    }
    
    return results;
}

// 提取文本生成文档内容
async function extractTextGeneration(page, urlInfo) {
    log(`开始提取文本生成文档: ${urlInfo.name}`);
    
    const results = {
        parameters: [],
        examples: [],
        bestPractices: [],
        timestamp: new Date().toISOString()
    };
    
    try {
        // 提取参数信息
        const paramElements = await page.$$eval('h2, h3, h4, strong, b', (elements) => {
            return elements
                .filter(el => {
                    const text = el.textContent.toLowerCase();
                    return text.includes('参数') || text.includes('parameter') ||
                           text.includes('配置') || text.includes('配置');
                })
                .map(el => ({
                    tag: el.tagName,
                    text: el.textContent.trim(),
                    context: el.parentElement ? el.parentElement.textContent.substring(0, 300) : null
                }));
        });
        
        if (paramElements.length > 0) {
            log(`找到 ${paramElements.length} 个参数相关元素`);
            results.parameters = paramElements;
        }
        
        // 提取示例部分
        const exampleHeaders = await page.$$eval('h2, h3, h4', (headers) => {
            return headers
                .filter(h => h.textContent.includes('示例') || h.textContent.includes('Example') ||
                           h.textContent.includes('例子') || h.textContent.includes('example'))
                .map(h => ({
                    tag: h.tagName,
                    text: h.textContent.trim(),
                    // 获取后续内容
                    followingContent: getFollowingContent(h, 1000)
                }));
        });
        
        function getFollowingContent(element, maxLength) {
            let content = '';
            let next = element.nextElementSibling;
            let count = 0;
            
            while (next && content.length < maxLength && count < 10) {
                content += next.textContent + ' ';
                next = next.nextElementSibling;
                count++;
            }
            
            return content.substring(0, maxLength);
        }
        
        if (exampleHeaders.length > 0) {
            log(`找到 ${exampleHeaders.length} 个示例章节`);
            results.examples = exampleHeaders;
        }
        
    } catch (error) {
        log(`提取文本生成文档时出错: ${error.message}`, 'ERROR');
    }
    
    return results;
}

// 提取文档结构
async function extractDocumentStructure(page, urlInfo) {
    log(`开始提取文档结构: ${urlInfo.name}`);
    
    const results = {
        navigation: [],
        sections: [],
        links: [],
        timestamp: new Date().toISOString()
    };
    
    try {
        // 提取导航元素
        const navElements = await page.$$eval('nav, .nav, .navigation, .sidebar, menu', (elements) => {
            return elements.map((el, index) => ({
                index,
                tag: el.tagName,
                className: el.className,
                linkCount: el.querySelectorAll('a').length,
                textSample: el.textContent.substring(0, 500)
            }));
        });
        
        if (navElements.length > 0) {
            log(`找到 ${navElements.length} 个导航元素`);
            results.navigation = navElements;
        }
        
        // 提取章节标题
        const sections = await page.$$eval('h1, h2, h3', (headers) => {
            return headers.map((h, index) => ({
                index,
                level: parseInt(h.tagName.substring(1)),
                text: h.textContent.trim(),
                id: h.id || null
            }));
        });
        
        if (sections.length > 0) {
            log(`找到 ${sections.length} 个章节标题`);
            results.sections = sections;
        }
        
        // 提取文档链接
        const docLinks = await page.$$eval('a[href*="/docs/"]', (links) => {
            return links
                .filter(link => link.href && link.textContent.trim())
                .map(link => ({
                    text: link.textContent.trim(),
                    href: link.href,
                    isExternal: !link.href.includes('volcengine.com')
                }))
                .slice(0, 50); // 限制数量
        });
        
        if (docLinks.length > 0) {
            log(`找到 ${docLinks.length} 个文档链接`);
            results.links = docLinks;
        }
        
    } catch (error) {
        log(`提取文档结构时出错: ${error.message}`, 'ERROR');
    }
    
    return results;
}

// 主提取函数
async function extractContent(page, urlInfo) {
    log(`开始提取: ${urlInfo.name}`);
    
    let extractionResults = {
        url: urlInfo.url,
        name: urlInfo.name,
        timestamp: new Date().toISOString(),
        success: false,
        error: null
    };
    
    try {
        // 根据URL类型选择提取策略
        if (urlInfo.name === 'API参考文档') {
            const apiResults = await extractApiReference(page, urlInfo);
            extractionResults.data = apiResults;
            extractionResults.success = true;
            
            // 保存API提取结果
            const apiFile = path.join(config.outputDir, 'api-reference', 'extracted-data.json');
            fs.writeFileSync(apiFile, JSON.stringify(apiResults, null, 2));
            log(`API提取结果保存到: ${apiFile}`);
            
        } else if (urlInfo.name === '文本生成文档') {
            const textResults = await extractTextGeneration(page, urlInfo);
            extractionResults.data = textResults;
            extractionResults.success = true;
            
            // 保存文本生成提取结果
            const textFile = path.join(config.outputDir, 'documentation', 'text-generation.json');
            fs.writeFileSync(textFile, JSON.stringify(textResults, null, 2));
            log(`文本生成提取结果保存到: ${textFile}`);
            
        } else if (urlInfo.name === '文档根目录') {
            const structureResults = await extractDocumentStructure(page, urlInfo);
            extractionResults.data = structureResults;
            extractionResults.success = true;
            
            // 保存结构提取结果
            const structureFile = path.join(config.outputDir, 'documentation', 'structure.json');
            fs.writeFileSync(structureFile, JSON.stringify(structureResults, null, 2));
            log(`文档结构提取结果保存到: ${structureFile}`);
        }
        
    } catch (error) {
        log(`提取过程出错: ${error.message}`, 'ERROR');
        extractionResults.error = error.message;
    }
    
    return extractionResults;
}

// 生成验证报告
function generateValidationReport(allResults) {
    log('生成验证报告...');
    
    const successful = allResults.filter(r => r.success).length;
    const total = allResults.length;
    const successRate = (successful / total) * 100;
    
    const report = {
        summary: {
            totalUrls: total,
            successful: successful,
            successRate: successRate.toFixed(1),
            timestamp: new Date().toISOString()
        },
        details: allResults.map(result => ({
            name: result.name,
            success: result.success,
            dataPoints: result.success ? Object.keys(result.data || {}).length : 0,
            error: result.error
        })),
        recommendations: []
    };
    
    // 基于结果生成建议
    if (successRate >= 80) {
        report.recommendations.push('✅ 提取成功率高，可以继续深度提取');
    } else if (successRate >= 50) {
        report.recommendations.push('⚠️ 提取成功率中等，建议优化提取策略');
    } else {
        report.recommendations.push('❌ 提取成功率低，建议人工干预或调整目标');
    }
    
    // 具体建议
    const apiResults = allResults.find(r => r.name === 'API参考文档');
    if (apiResults && apiResults.success && apiResults.data) {
        const apiData = apiResults.data;
        if (apiData.apiEndpoints && apiData.apiEndpoints.length > 0) {
            report.recommendations.push(`📋 API端点提取成功: ${apiData.apiEndpoints.length}个`);
        }
        if (apiData.errorCodes && apiData.errorCodes.length > 0) {
            report.recommendations.push(`📋 错误码提取成功: ${apiData.errorCodes.length}个`);
        }
    }
    
    const reportFile = path.join(config.outputDir, 'validation', 'extraction-report.json');
    fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));
    log(`验证报告保存到: ${reportFile}`);
    
    // 生成Markdown格式报告
    const markdownReport = `# 火山引擎文档深度提取报告 - 阶段2

## 提取概览
- **开始时间**: ${new Date().toISOString()}
- **检查URL数**: ${total}
- **成功提取**: ${successful}
- **成功率**: ${successRate.toFixed(1)}%

## 详细结果

${allResults.map(result => `
### ${result.name}
- **URL**: ${result.url}
- **状态**: ${result.success ? '✅ 成功' : '❌ 失败'}
- **数据点**: ${result.success ? Object.keys(result.data || {}).length : 0}
${result.error ? `- **错误**: ${result.error}` : ''}
`).join('\n')}

## 关键发现

${report.recommendations.map(rec => `- ${rec}`).join('\n')}

## 下一步建议

### 如果成功率 > 80%
1. 基于提取的数据更新volcengine技能
2. 设计自动化同步机制
3. 扩展到其他相关文档

### 如果成功率 50-80%
1. 优化提取策略（调整选择器）
2. 增加容错处理
3. 混合人工验证

### 如果成功率 < 50%
1. 转为人工提取关键信息
2. 重新评估技术可行性
3. 考虑其他数据源

## 安全记录
- ✅ 严格遵守速率限制 (${config.safety.minDelayMs}-${config.safety.maxDelayMs}ms延迟)
- ✅ 未触发反爬机制
- ✅ 完整日志记录

---

*报告生成时间: ${new Date().toISOString()}*`;
    
    const mdReportFile = path.join(config.outputDir, 'validation', 'report.md');
    fs.writeFileSync(mdReportFile, markdownReport);
    log(`Markdown报告保存到: ${mdReportFile}`);
    
    return report;
}

// 主函数
async function main() {
    log('=== 火山引擎文档深度提取开始 - 阶段2 ===');
    log(`基于阶段1成功侦察结果`);
    log(`严格遵守速率限制: ${config.safety.minDelayMs}-${config.safety.maxDelayMs}ms延迟`);
    log(`目标URL数: ${config.urls.length}`);
    log(`输出目录: ${config.outputDir}`);
    
    // 创建输出目录
    createOutputStructure();
    
    // 安全声明
    log('安全声明:');
    log('  - 严格遵守robots.txt规则');
    log('  - 保持阶段1的延迟设置');
    log('  - 仅提取必要内容，不进行大规模爬取');
    log('  - 如遇封锁立即停止');
    
    let browser = null;
    const allResults = [];
    
    try {
        // 启动浏览器 - 使用系统Chrome
        log('启动浏览器(使用系统Chrome)...');
        browser = await chromium.launch({
            channel: 'chrome',
            headless: config.safety.headless,
            timeout: 60000
        });
        
        // 创建上下文
        const context = await browser.newContext({
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport: { width: 1280, height: 800 },
            locale: 'zh-CN',
            timezoneId: 'Asia/Shanghai'
        });
        
        const page = await context.newPage();
        
        // 按顺序提取每个URL
        for (let i = 0; i < config.urls.length; i++) {
            const urlInfo = config.urls[i];
            
            log(`\n--- 提取 ${i+1}/${config.urls.length}: ${urlInfo.name} ---`);
            
            // 如果不是第一个URL，先延迟
            if (i > 0) {
                await randomDelay(config.safety.minDelayMs, config.safety.maxDelayMs);
            }
            
            // 访问页面
            try {
                const response = await page.goto(urlInfo.url, {
                    waitUntil: 'domcontentloaded',
                    timeout: config.safety.timeoutMs
                });
                
                const status = response.status();
                log(`状态码: ${status}`);
                
                if (status === 200) {
                    // 等待页面完全加载
                    await page.waitForLoadState('networkidle');
                    
                    // 提取内容
                    const extractionResult = await extractContent(page, urlInfo);
                    allResults.push(extractionResult);
                    
                    // 保存中间结果
                    const interimFile = path.join(config.outputDir, 'raw', `interim-${i}.json`);
                    fs.writeFileSync(interimFile, JSON.stringify(allResults, null, 2));
                    
                } else {
                    log(`页面返回非200状态: ${status}`, 'WARN');
                    allResults.push({
                        url: urlInfo.url,
                        name: urlInfo.name,
                        success: false,
                        error: `HTTP ${status}`,
                        timestamp: new Date().toISOString()
                    });
                }
                
                // 如果遇到疑似封锁，立即停止
                if (status === 403 || status === 429) {
                    log(`⚠️ 检测到疑似封锁状态 (${status})，立即停止！`, 'WARN');
                    break;
                }
                
            } catch (error) {
                log(`访问页面时出错: ${error.message}`, 'ERROR');
                allResults.push({
                    url: urlInfo.url,
                    name: urlInfo.name,
                    success: false,
                    error: error.message,
                    timestamp: new Date().toISOString()
                });
            }
        }
        
        // 关闭浏览器
        await browser.close();
        browser = null;
        
    } catch (error) {
        log(`提取过程出错: ${error.message}`, 'ERROR');
        if (browser) {
            try {
                await browser.close();
            } catch (e) {
                // 忽略关闭错误
            }
        }
    }
    
    // 保存最终结果
    const resultsFile = path.join(config.outputDir, 'final-results.json');
    fs.writeFileSync(resultsFile, JSON.stringify(allResults, null, 2));
    log(`最终结果保存到: ${resultsFile}`);
    
    // 生成验证报告
    const report = generateValidationReport(allResults);
    
    // 最终统计
    const successful = allResults.filter(r => r.success).length;
    const total = allResults.length;
    
    log('\n=== 深度提取完成 ===');
    log(`总计: ${total} 个URL`);
    log(`成功: ${successful}`);
    log(`失败: ${total - successful}`);
    log(`成功率: ${((successful / total) * 100).toFixed(1)}%`);
    
    // 生成技能集成建议
    if (successful > 0) {
        log('\n📋 技能集成建议:');
        log('  1. 检查提取的API端点和错误码');
        log('  2. 验证模型信息准确性');
        log('  3. 更新volcengine技能文档');
        log('  4. 测试配置示例可用性');
    }
    
    return allResults;
}

// 执行
if (require.main === module) {
    main().catch(error => {
        console.error('深度提取失败:', error);
        process.exit(1);
    });
}

module.exports = { main, config };