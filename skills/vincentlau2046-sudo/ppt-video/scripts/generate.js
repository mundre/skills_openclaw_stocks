#!/usr/bin/env node
/**
 * PPT to Video Generator v3.2
 * 
 * 通用技能：输入文件夹 → 自动输出视频
 * 
 * 使用方式:
 *   node generate.js --input /path/to/project/
 * 
 * 支持的输入结构（任意一种）:
 *   project/xxx.pptx + notes/*.md
 *   project/xxx.pptx + notes_export/*.md
 *   project/xxx.pptx + scripts_rewritten/*.md (已改写讲稿，优先使用)
 *   project/xxx.pptx + *.md (根目录)
 * 
 * 支持的讲稿文件名:
 *   01_xxx.md, 02_xxx.md... (推荐)
 *   0.md, 1.md, 2.md...
 *   1.md, 2.md, 3.md...
 *   封面.md, 摘要.md... (按字母排序)
 * 
 * 自动完成:
 *   1. 灵活扫描文件夹（不限制目录名和文件名）
 *   2. 优先使用 scripts_rewritten/（已改写讲稿），降级使用 notes/
 *   3. PPT 截图
 *   4. TTS 语音合成
 *   5. 视频合成
 *   6. 输出到同目录
 * 
 * 讲稿改写由 LLM 在技能执行前完成，技能只负责技术工作
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const DEFAULT_RATE = '+25%';
const VOICE_PROFILES = {
  news: { voice: 'zh-CN-XiaoxiaoNeural', rate: '+25%', style: '新闻播报' },
  tech: { voice: 'zh-CN-YunxiNeural', rate: '+25%', style: '技术讲解' },
  politics: { voice: 'zh-CN-YunjianNeural', rate: '+25%', style: '时事政治' },
  casual: { voice: 'zh-CN-XiaoyiNeural', rate: '+25%', style: '轻松讲解' }
};

// ========== 参数解析 ==========
function parseArgs(args) {
  const result = { input: null, output: null, date: null, cleanup: false };
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      let value = true;
      if (i + 1 < args.length && !args[i + 1].startsWith('--')) {
        value = args[i + 1];
        i++;
      }
      result[key] = value;
    }
  }
  return result;
}

// ========== 阶段 1: 灵活扫描输入文件夹 ==========
function scanInputDir(inputDir) {
  console.log('📂 扫描输入文件夹：' + inputDir);
  
  const result = { ppt: null, scripts: [], scriptsRewritten: [] };
  
  // 优先方案：从 notes/ 目录读取讲稿（避免重复）
  const notesDir = path.join(inputDir, 'notes');
  if (fs.existsSync(notesDir)) {
    console.log('📝 从 notes/ 目录读取讲稿');
    const notesFiles = fs.readdirSync(notesDir)
      .filter(f => f.startsWith('slide_') && (f.endsWith('.md') || f.endsWith('.txt')))
      .sort();
    notesFiles.forEach(f => {
      result.scripts.push(path.join(notesDir, f));
    });
  }
  
  // 降级方案：递归扫描目录（仅当 notes/ 不存在时）
  if (result.scripts.length === 0) {
    console.log('⚠️  未找到 notes/，扫描整个目录');
    
    function scanDir(dir) {
      try {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        
        for (const entry of entries) {
          const fullPath = path.join(dir, entry.name);
          
          if (entry.isDirectory()) {
            // 跳过隐藏目录和临时目录
            if (!entry.name.startsWith('.') && entry.name !== 'node_modules') {
              scanDir(fullPath);
            }
          } else if (entry.isFile()) {
            const ext = path.extname(entry.name).toLowerCase();
            const name = entry.name.toLowerCase();
            
            // PPT 文件
            if (['.pptx', '.ppt', '.pdf'].includes(ext)) {
              result.ppt = fullPath;
            }
            
            // 讲稿文件（支持多种命名格式）
            if (ext === '.md' || ext === '.txt') {
              // 已改写讲稿（优先）
              if (dir.includes('scripts_rewritten')) {
                if (/^\d+[_\-\.]/.test(name) || /^\d+\.md$/.test(name)) {
                  result.scriptsRewritten.push(fullPath);
                }
              }
              // 原始讲稿（降级）
              else if (/^\d+[_\-\.]/.test(name) || 
                       /^\d+\.md$/.test(name) ||
                       name.includes('讲稿') || 
                       name.includes('script') ||
                       name.includes('封面') ||
                       name.includes('摘要')) {
                result.scripts.push(fullPath);
              }
            }
          }
        }
      } catch (e) {
        // 忽略权限错误
      }
    }
    
    scanDir(inputDir);
  } else {
    // 从 notes/ 读取时，PPT 文件单独查找
    const pptFiles = ['presentation.pptx', 'presentation_compatible.pptx', 'output.pptx'];
    for (const ppt of pptFiles) {
      const pptPath = path.join(inputDir, ppt);
      if (fs.existsSync(pptPath)) {
        result.ppt = pptPath;
        break;
      }
    }
  }
  
  // 排序讲稿文件（按文件名数字排序）
  result.scripts.sort((a, b) => {
    const baseA = path.basename(a);
    const baseB = path.basename(b);
    const numA = baseA.match(/^\d+/);
    const numB = baseB.match(/^\d+/);
    if (numA && numB) return parseInt(numA[0]) - parseInt(numB[0]);
    return baseA.localeCompare(baseB);
  });
  
  result.scriptsRewritten.sort((a, b) => {
    const baseA = path.basename(a);
    const baseB = path.basename(b);
    const numA = baseA.match(/^\d+/);
    const numB = baseB.match(/^\d+/);
    if (numA && numB) return parseInt(numA[0]) - parseInt(numB[0]);
    return baseA.localeCompare(baseB);
  });
  
  // 验证
  if (!result.ppt) {
    console.error('❌ 错误：未找到 PPT 文件（.pptx/.ppt/.pdf）');
    return null;
  }
  
  // 优先使用已改写讲稿
  if (result.scriptsRewritten.length >= 5) {
    console.log('✓ 找到 PPT 文件：' + path.basename(result.ppt));
    console.log('✓ 找到已改写讲稿：' + result.scriptsRewritten.length + ' 页（scripts_rewritten/）');
    return { ppt: result.ppt, scripts: result.scriptsRewritten, isRewritten: true };
  }
  
  // 降级使用原始讲稿
  if (result.scripts.length >= 5) {
    console.log('⚠️  未找到 scripts_rewritten/，使用原始讲稿：' + result.scripts.length + ' 页');
    console.log('💡 建议：先让 LLM 改写讲稿到 scripts_rewritten/ 目录');
    return { ppt: result.ppt, scripts: result.scripts, isRewritten: false };
  }
  
  console.error('❌ 错误：讲稿文件不足 5 页（找到 ' + (result.scripts.length + result.scriptsRewritten.length) + ' 页）');
  return null;
}

// ========== 检测内容风格 ==========
function detectStyle(text) {
  const lower = text.toLowerCase();
  const politicsKeywords = ['政策', '政府', '国家', '政治', '外交'];
  const techKeywords = ['技术', '代码', 'api', '算法', '模型', 'ai'];
  const newsKeywords = ['新闻', '报道', '今日', '快讯', '动态'];
  
  let scores = { politics: 0, tech: 0, news: 0 };
  politicsKeywords.forEach(k => { if (lower.includes(k)) scores.politics++; });
  techKeywords.forEach(k => { if (lower.includes(k)) scores.tech++; });
  newsKeywords.forEach(k => { if (lower.includes(k)) scores.news++; });
  
  const maxScore = Math.max(scores.politics, scores.tech, scores.news);
  if (maxScore === 0) return 'news';
  if (scores.politics === maxScore) return 'politics';
  if (scores.tech === maxScore) return 'tech';
  if (scores.news === maxScore) return 'news';
  return 'casual';
}

// ========== 阶段 3: PPT 截图 ==========
async function screenshotSlides(pptPath, outputDir, projectDir) {
  fs.mkdirSync(outputDir, { recursive: true });
  const screenshots = [];
  
  // 优先方案：直接从 svg_final/ 生成 PNG（完美保留中文字体）
  const svgFinalDir = path.join(projectDir, 'svg_final');
  if (fs.existsSync(svgFinalDir)) {
    console.log('📐 使用 svg_final/ 直接生成 PNG（完美字体渲染）');
    const svgFiles = fs.readdirSync(svgFinalDir)
      .filter(f => f.endsWith('.svg'))
      .sort();
    
    for (let i = 0; i < svgFiles.length; i++) {
      const svgFile = svgFiles[i];
      const svgPath = path.join(svgFinalDir, svgFile);
      const pngPath = path.join(outputDir, String(i + 1).padStart(2, '0') + '-page.png');
      
      try {
        // 使用 Inkscape 或 ImageMagick 转换 SVG 为 PNG
        // 优先尝试 Inkscape（质量更好）
        try {
          execSync('inkscape --export-type=png --export-width=1280 --export-height=720 --export-filename="' + pngPath + '" "' + svgPath + '"', { timeout: 60000 });
        } catch (e) {
          // 降级使用 ImageMagick
          execSync('convert -density 300 -resize 1280x720 -background none "' + svgPath + '" "' + pngPath + '"', { timeout: 60000 });
        }
        
        if (fs.existsSync(pngPath) && fs.statSync(pngPath).size > 0) {
          screenshots.push(pngPath);
        }
      } catch (e) {
        console.warn('  ⚠️  SVG 转 PNG 失败（' + svgFile + '）：' + e.message);
      }
    }
    
    if (screenshots.length > 0) {
      console.log('✅ 从 svg_final/ 生成 ' + screenshots.length + ' 页 PNG');
      return screenshots;
    }
  }
  
  // 降级方案：从 PPTX 转换
  console.log('⚠️  未找到 svg_final/，使用 PPTX 转换方案');
  
  if (pptPath.endsWith('.pptx') || pptPath.endsWith('.ppt')) {
    try {
      execSync('libreoffice --headless --convert-to pdf --outdir "' + outputDir + '" "' + pptPath + '"', { timeout: 120000 });
      const pdfFile = fs.readdirSync(outputDir).find(f => f.endsWith('.pdf') && !f.startsWith('temp_'));
      if (pdfFile) {
        const pdfPath = path.join(outputDir, pdfFile);
        const slidePrefix = path.join(outputDir, 'slide');
        execSync('pdftoppm -png -r 150 "' + pdfPath + '" "' + slidePrefix + '"', { timeout: 120000 });
        fs.unlinkSync(pdfPath);
        
        const pngFiles = fs.readdirSync(outputDir).filter(f => f.startsWith('slide-') && f.endsWith('.png')).sort();
        pngFiles.forEach((png, i) => {
          const oldPath = path.join(outputDir, png);
          const newPath = path.join(outputDir, String(i + 1).padStart(2, '0') + '-page.png');
          fs.renameSync(oldPath, newPath);
          screenshots.push(newPath);
        });
      }
    } catch (e) {
      console.warn('PPT 截图失败：' + e.message);
    }
  } else if (pptPath.endsWith('.pdf')) {
    try {
      const slidePrefix = path.join(outputDir, 'slide');
      execSync('pdftoppm -png -r 150 "' + pptPath + '" "' + slidePrefix + '"', { timeout: 120000 });
      const pngFiles = fs.readdirSync(outputDir).filter(f => f.startsWith('slide-') && f.endsWith('.png')).sort();
      pngFiles.forEach((png, i) => {
        const oldPath = path.join(outputDir, png);
        const newPath = path.join(outputDir, String(i + 1).padStart(2, '0') + '-page.png');
        fs.renameSync(oldPath, newPath);
        screenshots.push(newPath);
      });
    } catch (e) {
      console.warn('PDF 截图失败：' + e.message);
    }
  }
  
  return screenshots;
}

// ========== 阶段 4: TTS 语音合成 ==========
async function synthesizeTTS(scripts, voiceConfig, audioDir) {
  fs.mkdirSync(audioDir, { recursive: true });
  const audioFiles = [];
  
  for (let i = 0; i < scripts.length; i++) {
    const audioFile = path.join(audioDir, 'audio_' + String(i + 1).padStart(2, '0') + '.mp3');
    const scriptPath = scripts[i];
    
    if (!scriptPath || scriptPath.trim() === '') {
      audioFiles.push(null);
      continue;
    }
    
    // 读取文件内容
    let scriptContent = fs.readFileSync(scriptPath, 'utf-8');
    
    // 清理文本（移除 markdown，适合 TTS）
    const cleanText = scriptContent
      .replace(/#{1,6}\s+/g, '')
      .replace(/\*\*/g, '')
      .replace(/\*/g, '')
      .replace(/`/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/\n+/g, '，')
      .replace(/\s+/g, ' ')
      .replace(/"/g, '\\"');
    
    // 重试机制：最多重试 3 次
    let success = false;
    let lastError = null;
    
    for (let retry = 0; retry < 3 && !success; retry++) {
      if (retry > 0) {
        console.log('  🔄 第 ' + (i + 1) + '页 重试 ' + retry + '/3...');
        // 重试前等待 1 秒
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      try {
        execSync(
          'edge-tts --text "' + cleanText + '" --voice ' + voiceConfig.voice + ' --rate ' + voiceConfig.rate + ' --write-media "' + audioFile + '"',
          { stdio: 'pipe', timeout: 120000 }
        );
        
        if (fs.existsSync(audioFile) && fs.statSync(audioFile).size > 0) {
          audioFiles.push(audioFile);
          const sizeKB = Math.round(fs.statSync(audioFile).size / 1024);
          const duration = getAudioDuration(audioFile).toFixed(1);
          console.log('  ✓ 第 ' + (i + 1) + '页 ' + sizeKB + 'KB ' + duration + 's');
          success = true;
        } else {
          lastError = new Error('生成的音频文件为空');
        }
      } catch (e) {
        lastError = e;
        // 清理失败的文件
        if (fs.existsSync(audioFile)) {
          fs.unlinkSync(audioFile);
        }
      }
    }
    
    if (!success) {
      audioFiles.push(null);
      console.warn('  ⚠️  第 ' + (i + 1) + '页 TTS 失败（重试 3 次后放弃）：' + lastError.message);
    }
  }
  
  return audioFiles;
}

// ========== 阶段 5: 视频合成 ==========
async function synthesizeVideo(screenshots, audioFiles, clipsDir, finalVideo) {
  fs.mkdirSync(clipsDir, { recursive: true });
  const clipFiles = [];
  
  for (let i = 0; i < screenshots.length && i < audioFiles.length; i++) {
    const screenshot = screenshots[i];
    const audioFile = audioFiles[i];
    const clipFile = path.join(clipsDir, 'clip_' + String(i + 1).padStart(2, '0') + '.mp4');
    
    if (!audioFile) continue;
    
    try {
      execSync(
        'ffmpeg -y -loop 1 -i "' + screenshot + '" -i "' + audioFile + '" ' +
        '-c:v libx264 -tune stillimage -c:a aac -b:a 128k -pix_fmt yuv420p ' +
        '-vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" ' +
        '-shortest -movflags +faststart "' + clipFile + '"',
        { stdio: 'pipe' }
      );
      
      if (fs.existsSync(clipFile) && fs.statSync(clipFile).size > 0) {
        clipFiles.push(clipFile);
      }
    } catch (e) {
      console.warn('  ⚠️  第 ' + (i + 1) + '页视频合成失败');
    }
  }
  
  if (clipFiles.length === 0) {
    console.error('❌ 视频合成失败');
    return false;
  }
  
  const fileList = path.join(clipsDir, 'files.txt');
  fs.writeFileSync(fileList, clipFiles.map(c => 'file \'' + c + '\'').join('\n'));
  
  execSync(
    'ffmpeg -y -f concat -safe 0 -i "' + fileList + '" -c copy -movflags +faststart "' + finalVideo + '"',
    { stdio: 'pipe' }
  );
  
  return true;
}

// ========== 辅助函数 ==========
function getAudioDuration(audioFile) {
  try {
    const output = execSync('ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 "' + audioFile + '"', { encoding: 'utf-8' });
    return parseFloat(output.trim());
  } catch (e) {
    return 5.0;
  }
}

function getVideoDuration(videoFile) {
  try {
    const output = execSync('ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 "' + videoFile + '"', { encoding: 'utf-8' });
    return parseFloat(output.trim());
  } catch (e) {
    return 0;
  }
}

// ========== 主函数 ==========
async function main() {
  const args = parseArgs(process.argv.slice(2));
  
  console.log('\n🎬 PPT to Video Generator (v3.2 - 简化版)');
  console.log();
  
  // 验证输入
  if (!args.input || !fs.existsSync(args.input)) {
    console.error('❌ 错误：请指定输入文件夹 (--input /path/to/project/)');
    process.exit(1);
  }
  
  const inputDir = path.resolve(args.input);
  const outputDir = args.output ? path.resolve(args.output) : inputDir;
  const date = args.date || new Date().toISOString().split('T')[0];
  
  console.log('📁 输入目录：' + inputDir);
  console.log('📁 输出目录：' + outputDir);
  console.log();
  
  // 阶段 1: 灵活扫描
  console.log('=== 阶段 1: 扫描输入文件夹 ===');
  const scanResult = scanInputDir(inputDir);
  if (!scanResult) {
    process.exit(1);
  }
  
  // 阶段 2: 检测风格（讲稿已改写，无需再次处理）
  console.log('\n=== 阶段 2: 检测内容风格 ===');
  const style = detectStyle(fs.readFileSync(scanResult.scripts[0], 'utf-8'));
  const voiceConfig = VOICE_PROFILES[style];
  console.log('🎯 内容风格：' + style);
  console.log('🎤 TTS 音色：' + voiceConfig.voice);
  
  if (!scanResult.isRewritten) {
    console.log('\n⚠️  提示：使用原始讲稿，建议先让 LLM 改写讲稿');
    console.log('   改写后保存到：' + inputDir + '/scripts_rewritten/');
  }
  
  // 阶段 3: PPT 截图
  console.log('\n=== 阶段 3: PPT 截图 ===');
  const tempDir = path.join(inputDir, '.ppt_video_temp');
  const screenshots = await screenshotSlides(scanResult.ppt, tempDir, inputDir);
  console.log('✅ 共 ' + screenshots.length + ' 页截图');
  
  if (screenshots.length === 0) {
    console.error('❌ 截图失败');
    process.exit(1);
  }
  
  // 阶段 4: TTS 语音合成
  console.log('\n=== 阶段 4: TTS 语音合成 ===');
  const audioDir = path.join(tempDir, 'audio');
  const audioFiles = await synthesizeTTS(scanResult.scripts, voiceConfig, audioDir);
  
  // 阶段 5: 视频合成
  console.log('\n=== 阶段 5: 视频合成 ===');
  const clipsDir = path.join(tempDir, 'clips');
  const finalVideo = path.join(outputDir, 'video_' + date + '.mp4');
  const success = await synthesizeVideo(screenshots, audioFiles, clipsDir, finalVideo);
  
  if (!success) {
    process.exit(1);
  }
  
  // 阶段 6: 清理
  console.log('\n=== 阶段 6: 清理临时文件 ===');
  if (args.cleanup) {
    try {
      fs.rmSync(tempDir, { recursive: true, force: true });
      console.log('✓ 已清理临时目录');
    } catch (e) {
      console.warn('⚠️  清理失败：' + e.message);
    }
  } else {
    console.log('💡 临时目录保留：' + tempDir);
    console.log('   使用 --cleanup 参数可自动清理');
  }
  
  // 完成
  const videoSize = (fs.statSync(finalVideo).size / 1024 / 1024).toFixed(1);
  const videoDuration = getVideoDuration(finalVideo).toFixed(1);
  
  console.log('\n🎉 全部完成！');
  console.log('\n📹 输出视频：' + finalVideo);
  console.log('   大小：' + videoSize + ' MB');
  console.log('   时长：' + videoDuration + ' 秒');
  console.log();
}

// 启动
main().catch(err => {
  console.error('\n❌ 执行失败:', err.message);
  console.error(err.stack);
  process.exit(1);
});
