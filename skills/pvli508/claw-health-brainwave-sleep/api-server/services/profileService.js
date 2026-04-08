/**
 * 用户画像服务
 * 当前为内存存储，重启后数据丢失
 * 生产环境建议替换为 Redis / MySQL 持久化
 */

const fs = require('fs');
const path = require('path');

const STORE_PATH = path.join(__dirname, '../data/profiles.json');

// 确保 data 目录存在
const dataDir = path.dirname(STORE_PATH);
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// 内存缓存
let profileCache = new Map();

// 启动时从磁盘加载（如有）
if (fs.existsSync(STORE_PATH)) {
  try {
    const raw = fs.readFileSync(STORE_PATH, 'utf-8');
    const obj = JSON.parse(raw);
    profileCache = new Map(Object.entries(obj));
    console.log(`[ProfileService] 已从磁盘加载 ${profileCache.size} 条用户画像`);
  } catch (e) {
    console.warn('[ProfileService] 画像文件加载失败，将从空开始:', e.message);
  }
}

// 定期持久化（每 30 秒）
setInterval(() => {
  _persist();
}, 30 * 1000);

// 关闭时持久化
process.on('exit', () => _persist());
process.on('SIGINT', () => { _persist(); process.exit(0); });

function _persist() {
  try {
    const obj = Object.fromEntries(profileCache);
    fs.writeFileSync(STORE_PATH, JSON.stringify(obj, null, 2), 'utf-8');
  } catch (e) {
    console.warn('[ProfileService] 画像保存失败:', e.message);
  }
}

class ProfileService {
  /**
   * 获取用户画像
   * @param {string} userId
   */
  getProfile(userId) {
    if (!userId) return null;
    const data = profileCache.get(userId);
    if (!data) return null;
    return {
      userId,
      disorderSubtype: data.disorderSubtype || null,
      severity: data.severity || null,
      ageGroup: data.ageGroup || null,
      gender: data.gender || null,
      comorbidity: data.comorbidity || null,
      scene: data.scene || null,
      updateTime: data.updateTime || null,
    };
  }

  /**
   * 创建或更新用户画像
   * @param {string} userId
   * @param {Object} fields
   */
  updateProfile(userId, fields = {}) {
    if (!userId) return;

    const existing = profileCache.get(userId) || {};

    const updated = {
      ...existing,
      disorderSubtype: fields.disorderSubtype ?? existing.disorderSubtype ?? null,
      severity: fields.severity ?? existing.severity ?? null,
      ageGroup: fields.ageGroup ?? existing.ageGroup ?? null,
      gender: fields.gender ?? existing.gender ?? null,
      comorbidity: fields.comorbidity ?? existing.comorbidity ?? null,
      scene: fields.scene ?? existing.scene ?? null,
      updateTime: new Date().toISOString(),
    };

    profileCache.set(userId, updated);
    return updated;
  }

  /**
   * 删除用户画像
   * @param {string} userId
   */
  deleteProfile(userId) {
    if (!userId) return;
    profileCache.delete(userId);
  }

  /**
   * 列出所有已存储的用户（管理接口）
   */
  listProfiles() {
    const entries = Array.from(profileCache.entries());
    return entries.map(([userId, data]) => ({ userId, ...data }));
  }
}

module.exports = { ProfileService };
