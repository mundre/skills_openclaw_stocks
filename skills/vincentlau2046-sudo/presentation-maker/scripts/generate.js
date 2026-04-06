#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { marked } = require('marked');

// 默认配置
const DEFAULT_CONFIG = {
  theme: 'tech',
  primaryColor: '#76b900', // NVIDIA green
  secondaryColor: '#00a2ff', // tech blue
  outputDir: 'presentation-output'
};

class PresentationMaker {
  constructor(inputFile, options = {}) {
    this.inputFile = inputFile;
    this.options = { ...DEFAULT_CONFIG, ...options };
    this.content = null;
    this.slides = [];
  }

  async run() {
    try {
      await this.loadContent();
      await this.analyzeAndPlan();
      await this.generateSlides();
      await this.createIndex();
      console.log(`✅ 幻灯片生成完成！输出目录: ${this.options.outputDir}`);
    } catch (error) {
      console.error(`❌ 生成失败: ${error.message}`);
      process.exit(1);
    }
  }

  async loadContent() {
    if (!fs.existsSync(this.inputFile)) {
      throw new Error(`输入文件不存在: ${this.inputFile}`);
    }
    
    const content = fs.readFileSync(this.inputFile, 'utf8');
    this.content = content;
    console.log(`📄 已加载输入文件: ${this.inputFile}`);
  }

  async analyzeAndPlan() {
    // 简化的分析逻辑 - 实际项目中会更复杂
    const lines = this.content.split('\n');
    const sections = [];
    let currentSection = { title: '封面', content: [], type: 'cover' };
    
    // 识别章节
    for (const line of lines) {
      if (line.startsWith('# ')) {
        currentSection = { 
          title: line.replace('# ', ''), 
          content: [], 
          type: 'overview' 
        };
        sections.push(currentSection);
      } else if (line.startsWith('## ')) {
        currentSection.content.push({ type: 'subtitle', text: line.replace('## ', '') });
      } else if (line.trim()) {
        currentSection.content.push({ type: 'paragraph', text: line });
      }
    }

    // 规划幻灯片
    this.slides = [
      { id: '01-cover', title: '封面页', type: 'cover' },
      { id: '02-toc', title: '目录页', type: 'toc', sections: sections.map(s => s.title) }
    ];

    // 为每个主要章节创建幻灯片
    sections.forEach((section, index) => {
      this.slides.push({
        id: `0${index + 3}`.padStart(2, '0'),
        title: section.title,
        type: 'content',
        content: section.content
      });
    });

    // 添加总结页
    this.slides.push({
      id: `0${this.slides.length + 1}`.padStart(2, '0'),
      title: '总结',
      type: 'summary'
    });

    console.log(`📋 已规划 ${this.slides.length} 张幻灯片`);
  }

  async generateSlides() {
    const outputDir = this.options.outputDir;
    const slidesDir = path.join(outputDir, 'slides');
    const cssDir = path.join(outputDir, 'css');
    const jsDir = path.join(outputDir, 'js');

    // 创建目录
    [outputDir, slidesDir, cssDir, jsDir].forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });

    // 生成CSS
    this.generateCSS(cssDir);
    
    // 生成JS
    this.generateJS(jsDir);

    // 生成每张幻灯片
    for (const slide of this.slides) {
      const html = this.generateSlideHTML(slide);
      const filePath = path.join(slidesDir, `${slide.id}-${slide.type}.html`);
      fs.writeFileSync(filePath, html);
      console.log(`🖼️  已生成: ${slide.id} - ${slide.title}`);
    }
  }

  generateCSS(cssDir) {
    const cssContent = `
/* 全局样式 - 亮色调科技感 */
:root {
  --primary-color: ${this.options.primaryColor};
  --secondary-color: ${this.options.secondaryColor};
  --accent-color: #ff6b35;
  --text-light: #ffffff;
  --text-gray: #cccccc;
  --bg-dark: #0a0a1a;
  --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  --card-bg: rgba(255, 255, 255, 0.08);
  --border-radius: 12px;
  --transition: all 0.3s ease;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
  background: var(--bg-gradient);
  color: var(--text-light);
  overflow: hidden;
  height: 100vh;
}

.slide-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
  position: relative;
}

.slide h1 {
  font-size: 32px;
  margin-bottom: 30px;
  color: var(--text-light);
  text-align: center;
}

.data-card {
  background: var(--card-bg);
  padding: 20px;
  border-radius: var(--border-radius);
  text-align: center;
  min-width: 150px;
}

.data-card .value {
  font-size: 28px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.data-card .label {
  font-size: 14px;
  color: var(--text-gray);
}

/* 确保16:9比例 */
.slide {
  width: 100vw;
  height: 56.25vw;
  max-height: 100vh;
  max-width: 177.78vh;
}
`;
    fs.writeFileSync(path.join(cssDir, 'style.css'), cssContent);
  }

  generateJS(jsDir) {
    const jsContent = `
class SlidePresenter {
  constructor() {
    this.currentSlide = 0;
    this.totalSlides = document.querySelectorAll('.slide').length;
    this.init();
  }

  init() {
    this.bindKeyboardEvents();
    this.updateSlideVisibility();
  }

  bindKeyboardEvents() {
    document.addEventListener('keydown', (e) => {
      switch(e.key) {
        case 'ArrowRight':
        case ' ':
          e.preventDefault();
          this.nextSlide();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          this.prevSlide();
          break;
        case 'f':
        case 'F':
          e.preventDefault();
          this.toggleFullscreen();
          break;
      }
    });
  }

  nextSlide() {
    if (this.currentSlide < this.totalSlides - 1) {
      this.currentSlide++;
      this.updateSlideVisibility();
    }
  }

  prevSlide() {
    if (this.currentSlide > 0) {
      this.currentSlide--;
      this.updateSlideVisibility();
    }
  }

  updateSlideVisibility() {
    document.querySelectorAll('.slide').forEach((slide, index) => {
      slide.style.display = index === this.currentSlide ? 'block' : 'none';
    });
    window.location.hash = \`slide-\${this.currentSlide}\`;
  }

  toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(err => {
        console.log(\`Error attempting to enable fullscreen: \${err.message}\`);
      });
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  }

  handleHashChange() {
    const hash = window.location.hash;
    if (hash.startsWith('#slide-')) {
      const slideIndex = parseInt(hash.replace('#slide-', ''));
      if (!isNaN(slideIndex) && slideIndex >= 0 && slideIndex < this.totalSlides) {
        this.currentSlide = slideIndex;
        this.updateSlideVisibility();
      }
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const presenter = new SlidePresenter();
  window.addEventListener('hashchange', () => presenter.handleHashChange());
  presenter.handleHashChange();
  
  // 添加全屏按钮
  document.querySelectorAll('.slide').forEach(slide => {
    const fullscreenBtn = document.createElement('button');
    fullscreenBtn.textContent = '⛶';
    fullscreenBtn.style.position = 'absolute';
    fullscreenBtn.style.top = '20px';
    fullscreenBtn.style.right = '20px';
    fullscreenBtn.style.background = 'rgba(255,255,255,0.1)';
    fullscreenBtn.style.border = '1px solid rgba(255,255,255,0.3)';
    fullscreenBtn.style.color = 'white';
    fullscreenBtn.style.width = '40px';
    fullscreenBtn.style.height = '40px';
    fullscreenBtn.style.borderRadius = '50%';
    fullscreenBtn.style.cursor = 'pointer';
    fullscreenBtn.style.zIndex = '1000';
    slide.appendChild(fullscreenBtn);
    fullscreenBtn.addEventListener('click', () => presenter.toggleFullscreen());
  });
});

// 确保16:9比例
function enforceAspectRatio() {
  const slides = document.querySelectorAll('.slide');
  slides.forEach(slide => {
    const aspectRatio = 16 / 9;
    const windowRatio = window.innerWidth / window.innerHeight;
    
    if (windowRatio > aspectRatio) {
      slide.style.width = \`\${window.innerHeight * aspectRatio}px\`;
      slide.style.height = \`\${window.innerHeight}px\`;
    } else {
      slide.style.width = \`\${window.innerWidth}px\`;
      slide.style.height = \`\${window.innerWidth / aspectRatio}px\`;
    }
  });
}

window.addEventListener('resize', enforceAspectRatio);
enforceAspectRatio();
`;
    fs.writeFileSync(path.join(jsDir, 'main.js'), jsContent);
  }

  generateSlideHTML(slide) {
    let contentHTML = '';
    
    switch (slide.type) {
      case 'cover':
        contentHTML = `
        <div class="slide-container">
          <div>
            <h1>${slide.title}</h1>
            <h2>AI算力时代的巅峰业绩</h2>
          </div>
          <div class="date">2026年3月</div>
        </div>`;
        break;
        
      case 'toc':
        const tocItems = slide.sections.map(section => 
          `<div class="toc-item">${section}</div>`
        ).join('');
        contentHTML = `
        <div class="slide-container">
          <h1>目录</h1>
          <div class="toc-list">
            ${tocItems}
          </div>
        </div>`;
        break;
        
      case 'summary':
        contentHTML = `
        <div class="slide-container">
          <h1>${slide.title}</h1>
          <div class="slide-content">
            <div class="data-card" style="background: rgba(118, 185, 0, 0.2); width: 100%;">
              <div style="font-size: 22px; margin-bottom: 15px; color: var(--primary-color);">核心结论</div>
              <div style="font-size: 18px; color: var(--text-gray);">
                • 业绩、利润、毛利率全面创历史新高<br>
                • 数据中心业务形成绝对统治力<br>
                • 现金流充沛，增长韧性极强
              </div>
            </div>
          </div>
        </div>`;
        break;
        
      default:
        contentHTML = `
        <div class="slide-container">
          <h1>${slide.title}</h1>
          <div class="slide-content">
            <div class="data-card">
              <div style="font-size: 20px; margin-bottom: 15px;">内容概要</div>
              <div style="font-size: 16px; color: var(--text-gray);">
                此处显示${slide.title}的核心内容和数据...
              </div>
            </div>
          </div>
        </div>`;
    }

    return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${slide.title}</title>
    <link rel="stylesheet" href="../css/style.css">
</head>
<body>
    <div class="slide ${slide.type}">
        ${contentHTML}
    </div>
    <script src="../js/main.js"></script>
</body>
</html>`;
  }

  async createIndex() {
    const indexHTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>演示幻灯片</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: white;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        
        .container {
            text-align: center;
            padding: 40px;
        }
        
        h1 {
            font-size: 36px;
            margin-bottom: 30px;
            background: linear-gradient(90deg, white, ${this.options.secondaryColor});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .slides-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin-top: 20px;
        }
        
        .slide-link {
            background: rgba(255, 255, 255, 0.08);
            padding: 20px;
            border-radius: 12px;
            text-decoration: none;
            color: white;
            transition: all 0.3s ease;
            display: block;
            text-align: left;
        }
        
        .slide-link:hover {
            background: rgba(0, 162, 255, 0.2);
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>演示幻灯片</h1>
        <div class="slides-list">
            ${this.slides.map(slide => 
              `<a href="slides/${slide.id}-${slide.type}.html" class="slide-link">${slide.title}</a>`
            ).join('')}
        </div>
    </div>
</body>
</html>`;

    fs.writeFileSync(path.join(this.options.outputDir, 'index.html'), indexHTML);
  }
}

// 命令行接口
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('用法: presentation-maker <input-file> [options]');
    console.log('选项:');
    console.log('  --output-dir, -o  输出目录 (默认: presentation-output)');
    console.log('  --theme, -t       主题 (默认: tech)');
    console.log('  --primary-color   主色 (默认: #76b900)');
    console.log('  --secondary-color 辅色 (默认: #00a2ff)');
    process.exit(1);
  }

  const inputFile = args[0];
  const options = {};
  
  // 解析命令行参数
  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--output-dir' || arg === '-o') {
      options.outputDir = args[++i];
    } else if (arg === '--theme' || arg === '-t') {
      options.theme = args[++i];
    } else if (arg === '--primary-color') {
      options.primaryColor = args[++i];
    } else if (arg === '--secondary-color') {
      options.secondaryColor = args[++i];
    }
  }

  const maker = new PresentationMaker(inputFile, options);
  await maker.run();
}

if (require.main === module) {
  main().catch(console.error);
}