const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const os = require('os');
const https = require('https');
const http = require('http');
const Tesseract = require('tesseract.js');

/**
 * OCR 识别图片文字
 */
async function recognizeImageText(imagePath, imageIndex, totalImages) {
  try {
    console.log(`  🔍 正在识别图片 ${imageIndex}/${totalImages}...`);
    const { data: { text } } = await Tesseract.recognize(
      imagePath,
      'chi_sim+eng', // 中文 + 英文
      {
        logger: m => {
          if (m.status === 'recognizing text') {
            process.stdout.write(`\r  OCR 进度：${(m.progress * 100).toFixed(0)}%`);
          }
        }
      }
    );
    console.log(''); // 换行
    return text.trim();
  } catch (err) {
    console.error(`  ❌ OCR 失败：${err.message}`);
    return '';
  }
}

/**
 * 下载图片到本地
 */
async function downloadImage(url, outputDir, filename) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    const filepath = path.join(outputDir, filename);
    
    client.get(url, (res) => {
      if (res.statusCode === 302 || res.statusCode === 301) {
        // 重定向
        downloadImage(res.headers.location, outputDir, filename).then(resolve).catch(reject);
        return;
      }
      
      const file = fs.createWriteStream(filepath);
      res.pipe(file);
      
      file.on('finish', () => {
        file.close();
        resolve(filepath);
      });
    }).on('error', (err) => {
      fs.unlink(filepath, () => {});
      reject(err);
    });
  });
}

/**
 * 自动查找 Chrome 路径
 */
function findChromePath() {
  if (process.platform === 'win32') {
    const paths = [
      'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
      path.join(os.homedir(), 'AppData', 'Local', 'Google', 'Chrome', 'Application', 'chrome.exe')
    ];
    for (const p of paths) {
      if (fs.existsSync(p)) return p;
    }
  } else if (process.platform === 'darwin') {
    const p = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
    if (fs.existsSync(p)) return p;
  } else {
    const paths = [
      '/usr/bin/google-chrome',
      '/usr/bin/google-chrome-stable',
      '/usr/bin/chromium-browser',
      '/usr/bin/chromium'
    ];
    for (const p of paths) {
      if (fs.existsSync(p)) return p;
    }
  }
  return null;
}

/**
 * 抓取微信公众号文章
 * @param {Object} options - 配置选项
 * @param {string} options.url - 文章 URL
 * @param {boolean} options.saveToFile - 是否保存文件 (默认 false)
 * @param {string} options.outputDir - 输出目录 (默认系统临时目录)
 * @param {string} options.chromePath - Chrome 路径 (可选)
 * @param {string} options.format - 输出格式：text|markdown|html (默认 markdown)
 * @param {boolean} options.downloadImages - 是否下载图片 (默认 true)
 * @param {boolean} options.ocrImages - 是否 OCR 识别图片文字 (默认 false)
 * @returns {Promise<{title: string, author: string, time: string, content: string, images: Array}>}
 */
async function fetchWechatArticle(options = {}) {
  const {
    url,
    saveToFile = false,
    outputDir = path.join(os.tmpdir(), 'wechat-articles'),
    chromePath = findChromePath(),
    format = 'markdown',
    downloadImages = true,
    ocrImages = false
  } = options;

  if (!url) {
    throw new Error('缺少文章 URL');
  }

  if (!chromePath) {
    throw new Error('未找到 Chrome 浏览器，请手动指定 chromePath 或安装 Chrome');
  }

  let browser;
  try {
    console.log('🚀 正在启动 Chrome...');
    
    browser = await puppeteer.launch({
      executablePath: chromePath,
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
      ]
    });
    
    console.log('✅ Chrome 已启动');
    
    const page = await browser.newPage();
    
    // 移动端 User-Agent
    await page.setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0');
    await page.setViewport({ width: 375, height: 812 });
    
    console.log('📖 正在加载文章:', url);
    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: 60000
    });
    
    console.log('✅ 页面加载完成');
    
    // 等待内容
    await page.waitForSelector('#js_content, .rich_media_content', { timeout: 10000 })
      .catch(() => console.log('⚠️  未找到标准内容选择器'));
    
    // 确保输出目录存在
    if (saveToFile && !fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // 提取正文、元信息和图片
    const articleData = await page.evaluate(() => {
      // 检查是否被拦截或页面已删除
      const titleEl = document.querySelector('#activity-name') || document.querySelector('title');
      const title = titleEl?.innerText?.trim() || '无标题';
      
      const isDeleted = document.body.innerText.includes('该内容已被发布者删除') || 
                        document.body.innerText.includes('此内容因违规无法查看');
      
      if (isDeleted) {
        return { error: '文章已被删除或违规下架' };
      }

      // 作者
      const author = document.querySelector('.rich_media_meta_nickname')?.innerText?.trim() || '未知';
      
      // 时间
      const time = document.querySelector('.rich_media_meta_text')?.innerText?.trim() || '未知';
      
      // 提取图片和文字
      const contentEl = document.querySelector('#js_content') || 
                        document.querySelector('.rich_media_content') || 
                        document.querySelector('.rich_media_area_primary') || 
                        document.querySelector('article');
      
      const images = [];
      let markdownContent = '';
      let textContent = '';
      
      if (contentEl) {
        // 提取所有图片（支持多种标签和属性）
        const imgSelectors = [
          'img[data-src]',
          'img[src]',
          'mp-img[data-src]',
          'mp-img[src]',
          'weixin-img[data-src]',
          'section img',
          '.rich_media_content img'
        ];
        
        imgSelectors.forEach(selector => {
          const imgs = contentEl.querySelectorAll(selector);
          imgs.forEach(img => {
            const src = img.getAttribute('data-src') || 
                       img.getAttribute('data-original') || 
                       img.getAttribute('src');
            if (src && src.startsWith('http') && !images.includes(src)) {
              images.push(src);
            }
          });
        });
        
        // 遍历所有子节点提取文字
        const nodes = contentEl.childNodes;
        nodes.forEach(node => {
          if (node.nodeType === 1) { // Element node
            const tagName = node.tagName?.toLowerCase();
            if (tagName === 'img' || tagName === 'mp-img' || tagName === 'weixin-img') {
              const src = node.getAttribute('data-src') || 
                         node.getAttribute('data-original') || 
                         node.getAttribute('src');
              if (src && src.startsWith('http')) {
                const imgIndex = images.indexOf(src);
                if (imgIndex >= 0) {
                  markdownContent += `\n![图片 ${imgIndex + 1}](${src})\n`;
                }
              }
            } else if (tagName === 'p' || tagName === 'br' || tagName === 'div' || tagName === 'section') {
              const text = node.innerText?.trim();
              if (text && text.length > 0) {
                markdownContent += text + '\n\n';
                textContent += text + '\n';
              }
            } else {
              const text = node.innerText?.trim();
              if (text && text.length > 0) {
                markdownContent += text + '\n\n';
                textContent += text + '\n';
              }
            }
          } else if (node.nodeType === 3) { // Text node
            const text = node.textContent?.trim();
            if (text && text.length > 0) {
              markdownContent += text + '\n\n';
              textContent += text + '\n';
            }
          }
        });
        
        // 如果还是没有图片，尝试从整个页面查找
        if (images.length === 0) {
          const allImages = document.querySelectorAll('img[data-src], img[src]');
          allImages.forEach(img => {
            const src = img.getAttribute('data-src') || 
                       img.getAttribute('data-original') || 
                       img.getAttribute('src');
            if (src && src.startsWith('http') && 
                !src.includes('mmbiz.qpic.cn/mmbiz_png') && // 过滤微信默认图
                !images.includes(src)) {
              images.push(src);
            }
          });
        }
      }
      
      // 如果没有提取到内容，尝试 Fallback
      if (!markdownContent.trim()) {
        const clones = document.body.cloneNode(true);
        const removes = clones.querySelectorAll('script, style, nav, footer, .qr_code_pc, #js_profile_qrcode');
        removes.forEach(n => n.remove());
        textContent = clones.innerText.trim();
        markdownContent = textContent;
      }
      
      return { 
        title, 
        author, 
        time, 
        content: markdownContent,
        textContent,
        images,
        htmlContent: contentEl?.innerHTML || ''
      };
    });

    if (articleData.error) {
      throw new Error(`页面异常: ${articleData.error}`);
    }
    
    console.log('\n📄 ========== 文章信息 ==========\n');
    console.log('标题:', articleData.title);
    console.log('作者:', articleData.author);
    console.log('时间:', articleData.time);
    console.log('图片数量:', articleData.images?.length || 0);
    console.log('\n📝 ========== 文章内容 ==========\n');
    console.log(articleData.content.substring(0, 500) + (articleData.content.length > 500 ? '...' : ''));
    console.log('\n========== 文章结束 ==========\n');
    
    // 下载图片
    const downloadedImages = [];
    if (downloadImages && articleData.images && articleData.images.length > 0) {
      console.log(`🖼️  正在下载 ${articleData.images.length} 张图片...`);
      const imagesDir = path.join(outputDir, 'images');
      if (saveToFile && !fs.existsSync(imagesDir)) {
        fs.mkdirSync(imagesDir, { recursive: true });
      }
      
      for (let i = 0; i < articleData.images.length; i++) {
        const imgUrl = articleData.images[i];
        try {
          const ext = path.extname(new URL(imgUrl).pathname) || '.jpg';
          const filename = `image_${i + 1}${ext}`;
          
          if (saveToFile) {
            const imgPath = await downloadImage(imgUrl, imagesDir, filename);
            const imgData = {
              originalUrl: imgUrl,
              localPath: imgPath,
              filename: filename,
              ocrText: ''
            };
            
            // OCR 识别
            if (ocrImages) {
              imgData.ocrText = await recognizeImageText(imgPath, i + 1, articleData.images.length);
              if (imgData.ocrText) {
                console.log(`  📝 识别到 ${imgData.ocrText.length} 字`);
              } else {
                console.log(`  📝 未识别到文字`);
              }
            }
            
            downloadedImages.push(imgData);
            console.log(`  ✅ 已下载：${filename}`);
          } else {
            downloadedImages.push({
              originalUrl: imgUrl,
              localPath: null,
              filename: filename,
              ocrText: ''
            });
          }
        } catch (err) {
          console.log(`  ❌ 下载失败：${imgUrl} - ${err.message}`);
        }
      }
    }
    
    // 保存文件
    if (saveToFile) {
      const timestamp = Date.now();
      let filename, content;
      
      // 整理 OCR 识别结果
      let ocrContent = '';
      if (ocrImages && downloadedImages.length > 0) {
        ocrContent = '\n\n---\n\n## 🖼️ 图片文字识别结果\n\n';
        downloadedImages.forEach((img, idx) => {
          if (img.ocrText) {
            ocrContent += `### 图片 ${idx + 1}\n\n${img.ocrText}\n\n`;
          }
        });
      }
      
      if (format === 'html') {
        filename = `article-wechat-${timestamp}.html`;
        content = `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>${articleData.title}</title></head>
<body>
<h1>${articleData.title}</h1>
<p>作者：${articleData.author} | 时间：${articleData.time}</p>
${articleData.htmlContent}
${ocrImages ? '<h2>图片文字识别</h2>' + downloadedImages.map((img, i) => `<h3>图片 ${i + 1}</h3><p>${img.ocrText || '无文字'}</p>`).join('') : ''}
</body>
</html>`;
      } else if (format === 'markdown') {
        filename = `article-wechat-${timestamp}.md`;
        content = `# ${articleData.title}\n\n**作者**: ${articleData.author}  \n**时间**: ${articleData.time}\n\n---\n\n${articleData.content}${ocrContent}`;
      } else {
        filename = `article-wechat-${timestamp}.txt`;
        content = `标题：${articleData.title}\n作者：${articleData.author}\n时间：${articleData.time}\n\n${articleData.textContent}${ocrImages ? '\n\n---\n图片文字识别:\n' + downloadedImages.map((img, i) => `图片 ${i + 1}:\n${img.ocrText || '无文字'}`).join('\n\n') : ''}`;
      }
      
      const filepath = path.join(outputDir, filename);
      fs.writeFileSync(filepath, content, 'utf8');
      console.log(`💾 内容已保存到：${filepath}`);
      
      // 生成图片清单
      if (downloadedImages.length > 0) {
        const manifestPath = path.join(outputDir, `images-${timestamp}.json`);
        fs.writeFileSync(manifestPath, JSON.stringify(downloadedImages, null, 2), 'utf8');
        console.log(`📋 图片清单已保存到：${manifestPath}`);
        
        // 单独保存 OCR 结果
        if (ocrImages) {
          const ocrPath = path.join(outputDir, `ocr-${timestamp}.txt`);
          const ocrText = downloadedImages.map((img, i) => `=== 图片 ${i + 1} ===\n${img.ocrText || '无文字'}`).join('\n\n');
          fs.writeFileSync(ocrPath, ocrText, 'utf8');
          console.log(`📝 OCR 结果已保存到：${ocrPath}`);
        }
      }
    }
    
    await browser.close();
    console.log('🔒 浏览器已关闭');
    
    return {
      title: articleData.title,
      author: articleData.author,
      time: articleData.time,
      content: articleData.content,
      textContent: articleData.textContent,
      images: downloadedImages.length > 0 ? downloadedImages : articleData.images,
      imageCount: articleData.images?.length || 0
    };
    
  } catch (error) {
    console.error('❌ 错误:', error.message);
    console.error(error.stack);
    if (browser) await browser.close();
    throw error;
  }
}

// 命令行支持
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.includes('--test')) {
    require('./tests/run-tests');
  } else {
    const url = args.find(a => !a.startsWith('-'));
    const saveToFile = args.includes('--save');
    const format = args.find(a => a.startsWith('--format='))?.split('=')[1] || 'markdown';
    const downloadImages = !args.includes('--no-images');
    const ocrImages = args.includes('--ocr');
    
    if (!url) {
      console.log('用法：node fetch-wechat-article.js <文章 URL> [选项]');
      console.log('      node fetch-wechat-article.js --test  # 运行测试');
      console.log('选项：');
      console.log('  --save          保存到临时目录 (默认不保存)');
      console.log('  --format=TYPE   输出格式：text|markdown|html (默认 markdown)');
      console.log('  --no-images     不下载图片 (默认下载)');
      console.log('  --ocr           OCR 识别图片文字 (需要 --save)');
      console.log('示例：');
      console.log('  node fetch-wechat-article.js https://mp.weixin.qq.com/s/xxx');
      console.log('  node fetch-wechat-article.js https://mp.weixin.qq.com/s/xxx --save');
      console.log('  node fetch-wechat-article.js https://mp.weixin.qq.com/s/xxx --save --ocr');
      console.log('  node fetch-wechat-article.js https://mp.weixin.qq.com/s/xxx --save --format=html --ocr');
      process.exit(1);
    }
    
    fetchWechatArticle({ url, saveToFile, format, downloadImages, ocrImages })
      .then((result) => {
        console.log('✅ 抓取完成');
        console.log(`📊 统计：${result.imageCount} 张图片`);
      })
      .catch((error) => {
        console.error('❌ 抓取失败:', error.message);
        process.exit(1);
      });
  }
}

module.exports = { fetchWechatArticle };
