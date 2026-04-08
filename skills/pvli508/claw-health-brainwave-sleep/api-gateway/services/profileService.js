/**
 * 用户画像服务 - 多 Skill 共享
 */

const fs = require('fs');
const path = require('path');

const config = require('../config/default');
const STORE_PATH = path.join(__dirname, '..', config.DATA_DIR, 'profiles.json');

// 确保 data 目录存在
const dataDir = path.dirname(STORE_PATH);
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

let profileCache = new Map();

if (fs.existsSync(STORE_PATH)) {
  try {
    const raw = fs.readFileSync(STORE_PATH, 'utf-8');
    profileCache = new Map(Object.entries(JSON.parse(raw)));
  } catch (e) {
    // ignore
  }
}

// 每 30 秒自动持久化
setInterval(() => _persist(), 30 * 1000);
process.on('exit', () => _persist());
process.on('SIGINT', () => { _persist(); process.exit(0); });

function _persist() {
  try {
    fs.writeFileSync(STORE_PATH, JSON.stringify(Object.fromEntries(profileCache), null, 2));
  } catch (e) {
    console.warn('[ProfileService] 保存失败:', e.message);
  }
}

class ProfileService {
  getProfile(userId) {
    if (!userId) return null;
    const data = profileCache.get(userId);
    if (!data) return null;
    return { userId, ...data };
  }

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

  deleteProfile(userId) {
    if (!userId) return;
    profileCache.delete(userId);
  }

  listProfiles() {
    return [...profileCache.entries()].map(([userId, data]) => ({ userId, ...data }));
  }
}

module.exports = { ProfileService };
