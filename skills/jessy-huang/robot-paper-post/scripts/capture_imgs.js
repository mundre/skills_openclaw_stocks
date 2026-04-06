/**
 * 机器人论文图片自动采集脚本
 * 用于从 arXiv 论文页面自动采集 Figure 图片
 * 
 * 使用方法：
 * 1. 确保已安装 Node.js 和 Playwright
 * 2. 运行: npm install playwright && npx playwright install chromium
 * 3. 修改下方的 PAPER_ARXIV_ID 为目标论文的 arXiv ID
 * 4. 运行: node capture_imgs.js
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

// ========== 配置区域 ==========
// 修改这里为你的论文 arXiv ID，例如：2604.00202
const PAPER_ARXIV_ID = process.argv[2] || '2604.00202';

// 输出目录
const OUTPUT_DIR = path.join(process.cwd(), 'paper_imgs');

// 是否同时采集项目主页（如果存在）
const CAPTURE_PROJECT_PAGE = true;
const PROJECT_PAGE_URL = null; // 或手动指定，如 'https://genrobo.github.io/DreamControl-v2/'

// ========== 核心逻辑 ==========
if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    console.log(`📁 创建输出目录: ${OUTPUT_DIR}`);
}

async function capturePaperFigures() {
    console.log('🚀 开始采集论文图片...\n');
    
    const browser = await chromium.launch({ 
        headless: true, 
        args: ['--no-sandbox', '--disable-setuid-sandbox'] 
    });
    
    const page = await browser.newPage();
    await page.setViewportSize({ width: 1440, height: 900 });

    const capturedImages = [];
    
    // 1. 采集 arXiv HTML 版本的论文图片
    try {
        console.log('📄 正在访问 arXiv 论文页面...');
        const arxivUrl = `https://arxiv.org/html/${PAPER_ARXIV_ID}`;
        
        await page.goto(arxivUrl, { timeout: 60000 });
        await page.waitForTimeout(3000); // 等待页面加载
        
        // 查找所有论文中的图片
        const figures = await page.$$('figure');
        console.log(`   找到 ${figures.length} 个图表\n`);
        
        for (let i = 0; i < figures.length; i++) {
            const figure = figures[i];
            
            // 获取图片标题/说明
            const caption = await figure.$eval('figcaption', el => el.innerText).catch(() => `Figure ${i + 1}`);
            const captionShort = caption.substring(0, 50).replace(/[<>:"/\\|?*]/g, '_');
            
            // 查找图片元素
            const img = await figure.$('img');
            if (img) {
                const src = await img.getAttribute('src');
                if (src && !src.includes('data:')) {
                    const filename = `arxiv_fig_${i + 1}.png`;
                    const filepath = path.join(OUTPUT_DIR, filename);
                    
                    // 尝试直接截图
                    await figure.screenshot({ path: filepath, timeout: 10000 });
                    capturedImages.push({ filename, caption, filepath });
                    console.log(`   ✅ 采集: ${filename} - ${captionShort}...`);
                }
            }
        }
        
        // 采集 arXiv 页面概览图
        const htmlFile = path.join(OUTPUT_DIR, '10_arxiv_html.png');
        await page.screenshot({ path: htmlFile, fullPage: false });
        capturedImages.push({ filename: '10_arxiv_html.png', caption: 'arXiv论文页面概览', filepath: htmlFile });
        console.log('   ✅ 采集: 10_arxiv_html.png - arXiv论文页面概览\n');
        
    } catch (error) {
        console.error(`   ❌ arXiv 页面采集失败: ${error.message}\n`);
    }

    // 2. 尝试采集项目主页截图
    if (CAPTURE_PROJECT_PAGE) {
        try {
            // 从 arXiv 页面提取项目主页链接
            console.log('🌐 正在查找项目主页链接...');
            const projectLinks = await page.$$eval('a[href]', links => 
                links.map(a => a.href).filter(h => 
                    h.includes('github.io') || 
                    h.includes('project') ||
                    h.includes('generalrobotics')
                )
            );
            
            const projectUrl = PROJECT_PAGE_URL || (projectLinks.length > 0 ? projectLinks[0] : null);
            
            if (projectUrl) {
                console.log(`   找到项目主页: ${projectUrl}`);
                await page.goto(projectUrl, { timeout: 45000 });
                await page.waitForTimeout(2000);
                
                const projectFile = path.join(OUTPUT_DIR, '11_project_page.png');
                await page.screenshot({ path: projectFile, fullPage: false });
                capturedImages.push({ filename: '11_project_page.png', caption: '项目主页', filepath: projectFile });
                console.log('   ✅ 采集: 11_project_page.png - 项目主页\n');
            } else {
                console.log('   ⚠️ 未找到项目主页链接\n');
            }
        } catch (error) {
            console.error(`   ❌ 项目主页采集失败: ${error.message}\n`);
        }
    }

    await browser.close();
    
    // 3. 输出汇总
    console.log('='.repeat(50));
    console.log(`📊 图片采集完成！共采集 ${capturedImages.length} 张图片\n`);
    console.log('采集结果：');
    capturedImages.forEach((img, i) => {
        console.log(`   ${i + 1}. ${img.filename}`);
        console.log(`      位置: ${img.filepath}`);
        console.log(`      说明: ${img.caption.substring(0, 80)}...\n`);
    });
    
    console.log('='.repeat(50));
    console.log(`📁 图片保存在: ${OUTPUT_DIR}`);
    console.log('\n💡 提示：将采集的图片复制到推文同目录，然后在推文中使用相对路径引用');
    console.log('   示例: ![Figure 1](arxiv_fig_1.png)\n');
    
    return capturedImages;
}

// 执行
capturePaperFigures().catch(console.error);
