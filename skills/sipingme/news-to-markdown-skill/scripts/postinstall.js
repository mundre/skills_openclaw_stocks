#!/usr/bin/env node

/**
 * 安装后提示脚本
 * 显示可用功能和使用方式
 */

const CYAN = '\x1b[36m';
const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const RESET = '\x1b[0m';
const BOLD = '\x1b[1m';

console.log(`
${BOLD}${GREEN}✅ news-to-markdown Skill${RESET}

${BOLD}📋 功能说明：${RESET}
   一键将新闻文章转换为 Markdown，支持：
   - 双引擎内容提取（Readability + news-extractor）
   - 智能封面图选择
   - 图片下载到本地
   - 三层 HTML 抓取策略（curl → wget → Playwright）

${BOLD}🌐 支持的平台（13个）：${RESET}
   ${CYAN}头条${RESET}、${CYAN}微信公众号${RESET}、${CYAN}36kr${RESET}、${CYAN}知乎${RESET}、${CYAN}掘金${RESET}、${CYAN}简书${RESET}
   ${CYAN}CSDN${RESET}、${CYAN}人人都是产品经理${RESET}、${CYAN}开源中国${RESET}、${CYAN}B站专栏${RESET}
   ${CYAN}SegmentFault${RESET}、${CYAN}博客园${RESET}、${CYAN}小红书${RESET}

${BOLD}🚀 快速开始：${RESET}

   ${YELLOW}# 基础转换（推荐：下载图片到本地）${RESET}
   npx --yes news-to-markdown@^3.0.0 \\
     --url "https://www.toutiao.com/article/123" \\
     --download-images \\
     --output-dir ./article

   ${YELLOW}# 快速转换（不下载图片）${RESET}
   npx --yes news-to-markdown@^3.0.0 \\
     --url "https://36kr.com/p/123" \\
     --no-download-images \\
     --output article.md

   ${YELLOW}# 自定义提取${RESET}
   npx --yes news-to-markdown@^3.0.0 \\
     --url "https://example.com/news" \\
     --noise ".sidebar,.comments,.ads" \\
     --no-metadata

${BOLD}⚙️  常用参数：${RESET}
   ${CYAN}--url, -u${RESET}            新闻文章的 URL（必需）
   ${CYAN}--output, -o${RESET}         输出文件路径
   ${CYAN}--output-dir, -d${RESET}     输出目录（用于图片下载）
   ${CYAN}--download-images${RESET}    下载图片到本地（默认开启）
   ${CYAN}--no-download-images${RESET} 不下载图片
   ${CYAN}--platform, -p${RESET}       指定平台
   ${CYAN}--noise, -n${RESET}          要移除的元素（逗号分隔）
   ${CYAN}--no-metadata${RESET}        不包含元数据
   ${CYAN}--verbose, -v${RESET}        显示详细日志

${BOLD}📖 更多信息：${RESET}
   npx --yes news-to-markdown@^3.0.0 --help
   https://github.com/sipingme/news-to-markdown
`);
