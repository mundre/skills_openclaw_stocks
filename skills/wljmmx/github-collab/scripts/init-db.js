/**
 * Database Initialization Script
 * 数据库初始化脚本
 */

const { initDatabase, initDefaultAgents } = require('../db/init');

async function main() {
  console.log('🚀 开始初始化数据库...\n');
  
  try {
    const db = await initDatabase();
    await initDefaultAgents(db);
    
    console.log('\n✅ 数据库初始化完成！');
    console.log('📁 数据库文件:', require('path').join(__dirname, '..', 'db', 'agents.db'));
    
    // 关闭数据库连接
    db.close((err) => {
      if (err) {
        console.error('❌ 关闭数据库失败:', err.message);
      } else {
        console.log('✅ 数据库已关闭');
      }
    });
  } catch (error) {
    console.error('❌ 初始化失败:', error);
    process.exit(1);
  }
}

main();