#!/usr/bin/env node

const { spawnSync } = require('node:child_process');

// 所需版本（与 config.json 中 dependencies.npm 保持一致）
const REQUIRED_VERSION = '3.1.3';

const command = process.argv[2];
const args = process.argv.slice(3);

if (!command) {
  showHelp();
  process.exit(0);
}

const run = (cmd, cmdArgs) => {
  const result = spawnSync(cmd, cmdArgs, { stdio: 'inherit' });
  if (result.error) {
    console.error(JSON.stringify({ success: false, error: result.error.message }));
    process.exit(1);
  }
  process.exit(result.status ?? 1);
};

/**
 * 使用 npx 执行 news-to-markdown CLI
 */
const runNewsToMarkdown = (cliArgs) => {
  run('npx', ['--yes', `news-to-markdown@^${REQUIRED_VERSION}`, ...cliArgs]);
};

function showHelp() {
  console.log(`
news-to-markdown-skill v2.3.30
ClawHub skill for converting news to markdown

用法: 
  通过 scripts/convert.js convert [选项]
  或直接: npx --yes news-to-markdown@^${REQUIRED_VERSION} [选项]

命令:
  convert    将新闻文章转换为 Markdown
  help       显示帮助信息

选项:
  --url, -u <URL>        新闻文章的 URL（必需）
  --output, -o <文件>    输出 Markdown 文件路径（默认: stdout）
  --output-dir, -d <目录> 输出目录（用于图片下载）
  --download-images      下载图片到本地（默认开启）
  --no-download-images   不下载图片
  --platform, -p <平台>  指定平台 (toutiao, wechat, xiaohongshu, 36kr, ...)
  --selector, -s <选择器> CSS 选择器，指定内容区域
  --noise, -n <选择器>   要移除的元素（逗号分隔）
  --no-metadata          不包含元数据（标题、作者、时间）
  --verbose, -v          显示详细日志
  --help, -h             显示帮助信息

支持的平台:
  toutiao, wechat, xiaohongshu, 36kr, zhihu, juejin, jianshu,
  csdn, woshipm, oschina, bilibili, segmentfault, cnblogs

示例:
  npx --yes news-to-markdown@^${REQUIRED_VERSION} --url "https://www.toutiao.com/article/123" --output article.md
  npx --yes news-to-markdown@^${REQUIRED_VERSION} --url "https://36kr.com/p/123" --download-images --output-dir ./article
  npx --yes news-to-markdown@^${REQUIRED_VERSION} --url "https://mp.weixin.qq.com/s/xxx" --platform wechat
`);
}

switch (command) {
  case 'convert':
    runNewsToMarkdown(args);
    break;
  case 'help':
    showHelp();
    break;
  default:
    console.error(JSON.stringify({ success: false, error: `Unknown command: ${command}` }));
    process.exit(1);
}
