#!/usr/bin/env node
/**
 * 代码质量分析系统 - 安装脚本
 * 
 * 用法：npm run setup
 * 
 * 此脚本会：
 * 1. 检查环境（Node.js、PostgreSQL）
 * 2. 安装依赖
 * 3. 初始化数据库
 * 4. 创建配置文件（如果不存在）
 * 5. 启动服务
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const SKILL_DIR = path.join(__dirname, '..');
const CONFIG_FILE = path.join(SKILL_DIR, 'config.json');
const CONFIG_EXAMPLE = path.join(SKILL_DIR, 'config.example.json');
const BACKEND_DIR = path.join(SKILL_DIR, 'backend');
const FRONTEND_DIR = path.join(SKILL_DIR, 'frontend');
const ENV_FILE = path.join(BACKEND_DIR, '.env');
const ENV_EXAMPLE = path.join(BACKEND_DIR, '.env.example');

const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkCommand(command, name) {
  try {
    execSync(`${command} --version`, { stdio: 'ignore' });
    log(`✅ ${name} 已安装`, 'green');
    return true;
  } catch {
    log(`❌ ${name} 未安装`, 'red');
    return false;
  }
}

function checkPostgreSQL() {
  try {
    execSync('psql --version', { stdio: 'ignore' });
    log('✅ PostgreSQL 已安装', 'green');
    return true;
  } catch {
    log('⚠️ PostgreSQL 未安装或未配置 PATH', 'yellow');
    log('   请先安装 PostgreSQL: https://www.postgresql.org/download/', 'yellow');
    return false;
  }
}

function installDependencies() {
  log('\n📦 安装依赖...', 'blue');
  
  try {
    log('   安装后端依赖...');
    execSync('npm install', { cwd: BACKEND_DIR, stdio: 'inherit' });
    log('   ✅ 后端依赖安装完成', 'green');
  } catch (err) {
    log('   ❌ 后端依赖安装失败', 'red');
    return false;
  }
  
  try {
    log('   安装前端依赖...');
    execSync('npm install', { cwd: FRONTEND_DIR, stdio: 'inherit' });
    log('   ✅ 前端依赖安装完成', 'green');
  } catch (err) {
    log('   ❌ 前端依赖安装失败', 'red');
    return false;
  }
  
  return true;
}

function initDatabase() {
  log('\n🗄️ 初始化数据库...', 'blue');
  
  try {
    // 生成 Prisma Client
    log('   生成 Prisma Client...');
    execSync('npx prisma generate', { cwd: BACKEND_DIR, stdio: 'inherit' });
    
    // 运行迁移
    log('   运行数据库迁移...');
    execSync('npx prisma migrate deploy', { cwd: BACKEND_DIR, stdio: 'inherit' });
    
    log('   ✅ 数据库初始化完成', 'green');
    return true;
  } catch (err) {
    log('   ❌ 数据库初始化失败', 'red');
    log('   请确保数据库已创建：createdb code_quality', 'yellow');
    return false;
  }
}

function createConfigFiles() {
  log('\n📝 创建配置文件...', 'blue');
  
  // 创建 config.json
  if (!fs.existsSync(CONFIG_FILE)) {
    if (fs.existsSync(CONFIG_EXAMPLE)) {
      fs.copyFileSync(CONFIG_EXAMPLE, CONFIG_FILE);
      log('   ✅ 创建 config.json（请修改配置）', 'green');
    }
  } else {
    log('   ℹ️ config.json 已存在', 'yellow');
  }
  
  // 创建 .env
  if (!fs.existsSync(ENV_FILE)) {
    if (fs.existsSync(ENV_EXAMPLE)) {
      fs.copyFileSync(ENV_EXAMPLE, ENV_FILE);
      log('   ✅ 创建 backend/.env（请修改数据库连接）', 'green');
    }
  } else {
    log('   ℹ️ backend/.env 已存在', 'yellow');
  }
  
  // 创建前端 .env
  const frontendEnvFile = path.join(FRONTEND_DIR, '.env');
  const frontendEnvExample = path.join(FRONTEND_DIR, '.env.example');
  if (!fs.existsSync(frontendEnvFile) && fs.existsSync(frontendEnvExample)) {
    fs.copyFileSync(frontendEnvExample, frontendEnvFile);
    log('   ✅ 创建 frontend/.env', 'green');
  }
  
  return true;
}

async function promptForConfig() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  return new Promise((resolve) => {
    rl.question('\n请输入代码仓库目录路径（如 /Users/xxx/projects）: ', (codebaseDir) => {
      rl.question('是否现在配置 Teams 和 SMTP？（y/n）: ', (configNow) => {
        rl.close();
        
        if (configNow.toLowerCase() === 'y') {
          log('\n请在 config.json 中配置以下内容：', 'yellow');
          log('  - teams.webhookUrl（Webhook 地址）和 teams.secret');
          log('  - smtp.host, smtp.user, smtp.pass');
          log('  - emailRecipients（收件人邮箱列表）');
        }
        
        // 更新配置文件
        if (fs.existsSync(CONFIG_FILE)) {
          const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
          config.codebaseDir = codebaseDir.trim();
          fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
          log('\n✅ 已更新代码仓库目录', 'green');
        }
        
        resolve();
      });
    });
  });
}

function printNextSteps() {
  log('\n========================================', 'blue');
  log('  ✅ 安装完成！', 'green');
  log('========================================\n');
  log('下一步操作：');
  log('1. 创建数据库：createdb code_quality');
  log('2. 修改配置文件：');
  log('   - config.json（代码目录、Teams、SMTP）');
  log('   - backend/.env（数据库连接）');
  log('3. 启动服务：npm run start');
  log('4. 访问前端：http://localhost:5173');
  log('\n或者直接告诉 AI 助手：');
  log('  "帮我初始化代码质量分析系统"\n');
}

async function main() {
  log('========================================', 'blue');
  log('  代码质量分析系统 - 安装向导', 'blue');
  log('========================================\n');
  
  // 检查环境
  log('🔍 检查环境...', 'blue');
  const nodeOk = checkCommand('node', 'Node.js');
  const npmOk = checkCommand('npm', 'npm');
  const pgOk = checkPostgreSQL();
  
  if (!nodeOk || !npmOk) {
    log('\n❌ 请先安装 Node.js: https://nodejs.org/', 'red');
    process.exit(1);
  }
  
  // 创建配置文件
  createConfigFiles();
  
  // 安装依赖
  if (!installDependencies()) {
    process.exit(1);
  }
  
  // 初始化数据库（如果 PostgreSQL 可用）
  if (pgOk) {
    initDatabase();
  }
  
  // 提示配置
  await promptForConfig();
  
  // 打印下一步
  printNextSteps();
}

main().catch(console.error);