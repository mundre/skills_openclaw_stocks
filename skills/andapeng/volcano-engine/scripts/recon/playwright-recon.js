// 火山引擎文档侦察 - Playwright版本
const { chromium } = require('playwright');

async function testUrl(page, url) {
    console.log(`Testing: ${url}`);
    
    try {
        const response = await page.goto(url, { 
            waitUntil: 'domcontentloaded',
            timeout: 15000 
        });
        
        const status = response.status();
        console.log(`  Status: ${status}`);
        
        if (status === 200) {
            // 获取页面标题
            const title = await page.title();
            console.log(`  Title: ${title}`);
            
            // 检查是否有内容
            const content = await page.content();
            const hasContent = content.length > 1000;
            console.log(`  Has content: ${hasContent} (${content.length} chars)`);
            
            // 检查特定元素
            const hasArticle = await page.$('article, .documentation, main') !== null;
            console.log(`  Has article/doc element: ${hasArticle}`);
            
            return {
                url,
                exists: true,
                status,
                title,
                hasContent,
                hasArticle,
                contentLength: content.length
            };
        } else {
            return {
                url,
                exists: false,
                status,
                error: `HTTP ${status}`
            };
        }
    } catch (error) {
        console.log(`  Error: ${error.message}`);
        return {
            url,
            exists: false,
            status: 0,
            error: error.message
        };
    }
}

async function main() {
    console.log('Starting Volcengine document reconnaissance...');
    
    // 要检查的URL
    const urls = [
        'https://www.volcengine.com/docs/82379/1399009?lang=zh',  // 目标文档
        'https://www.volcengine.com/docs/82379/1263693?lang=zh',  // API参考
        'https://www.volcengine.com/docs/82379/overview?lang=zh',
        'https://www.volcengine.com/docs/82379/models?lang=zh',
        'https://www.volcengine.com/robots.txt',
        'https://www.volcengine.com/sitemap.xml'
    ];
    
    // 启动浏览器
    const browser = await chromium.launch({ 
        headless: true,
        timeout: 30000
    });
    
    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport: { width: 1280, height: 800 }
    });
    
    const page = await context.newPage();
    
    const results = [];
    
    for (const url of urls) {
        const result = await testUrl(page, url);
        results.push(result);
        
        // 延迟，避免太快 (3秒)
        if (url !== urls[urls.length - 1]) {
            console.log('Waiting 3 seconds...');
            await new Promise(resolve => setTimeout(resolve, 3000));
        }
    }
    
    // 关闭浏览器
    await browser.close();
    
    // 输出结果
    console.log('\n=== Reconnaissance Results ===');
    results.forEach(result => {
        if (result.exists) {
            console.log(`✅ ${result.url}`);
            console.log(`   Status: ${result.status}, Title: ${result.title}`);
            console.log(`   Content: ${result.contentLength} chars`);
        } else {
            console.log(`❌ ${result.url}`);
            console.log(`   Status: ${result.status}, Error: ${result.error}`);
        }
        console.log('');
    });
    
    // 保存结果到文件
    const fs = require('fs');
    const outputDir = './playwright-results';
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }
    
    const resultsFile = `${outputDir}/results.json`;
    fs.writeFileSync(resultsFile, JSON.stringify(results, null, 2));
    console.log(`Results saved to: ${resultsFile}`);
    
    // 生成报告
    const foundCount = results.filter(r => r.exists).length;
    const report = `# Volcengine Document Reconnaissance Report

## Summary
- Time: ${new Date().toISOString()}
- URLs tested: ${results.length}
- URLs found: ${foundCount}
- Success rate: ${(foundCount / results.length * 100).toFixed(1)}%

## Detailed Results

${results.map(r => {
    if (r.exists) {
        return `### ✅ ${r.url}\n- Status: ${r.status}\n- Title: ${r.title || 'N/A'}\n- Content length: ${r.contentLength} chars\n- Has article element: ${r.hasArticle}`;
    } else {
        return `### ❌ ${r.url}\n- Status: ${r.status}\n- Error: ${r.error || 'N/A'}`;
    }
}).join('\n\n')}

## Recommendations
1. Check robots.txt for crawling policies
2. Analyze successful document structure
3. Plan next phase based on findings
`;

    const reportFile = `${outputDir}/report.md`;
    fs.writeFileSync(reportFile, report);
    console.log(`Report saved to: ${reportFile}`);
    
    return results;
}

// 执行
main().catch(error => {
    console.error('Reconnaissance failed:', error);
    process.exit(1);
});