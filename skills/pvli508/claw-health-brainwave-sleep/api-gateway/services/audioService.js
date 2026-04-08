/**
 * 音频服务 - 多 Skill 共享
 * 直接复用 api-server 中的 audioService 逻辑
 */

const path = require('path');
const fs = require('fs');

// 尝试从 api-server 目录加载 manifest（复用数据）
let manifest;
try {
  const manifestPath = path.join(__dirname, '../../api-server/manifest.json');
  if (fs.existsSync(manifestPath)) {
    manifest = require(manifestPath);
  }
} catch (e) {
  // ignore
}

// 如果找不到，尝试 skill 目录
if (!manifest) {
  try {
    const skillManifest = path.join(__dirname, '../../audio_library/manifest.json');
    if (fs.existsSync(skillManifest)) {
      manifest = require(skillManifest);
    }
  } catch (e) {
    // ignore
  }
}

class AudioService {
  constructor() {
    this.audioFiles = (manifest && manifest.audio_files) || [];
    this.libraryPath = (manifest && manifest.library_path) || '';
  }

  listAudio(filters = {}, page = 1, pageSize = 20) {
    let result = this.audioFiles;
    if (filters.sleep_subtype_code) {
      result = result.filter(a => a.sleep_subtype_code === filters.sleep_subtype_code);
    }
    if (filters.use_scene) {
      result = result.filter(a => a.use_scene === filters.use_scene);
    }
    if (filters.duration) {
      result = result.filter(a => a.duration === filters.duration);
    }
    if (filters.severity) {
      result = result.filter(a => a.severity === filters.severity);
    }
    const total = result.length;
    const start = (page - 1) * pageSize;
    const items = result.slice(start, start + pageSize).map(a => this._format(a));
    return { total, page, pageSize, totalPages: Math.ceil(total / pageSize), items };
  }

  getAvailableScenes() {
    return [...new Set(this.audioFiles.map(a => a.use_scene))];
  }

  getAvailableSubtypes() {
    const map = new Map();
    this.audioFiles.forEach(a => {
      if (!map.has(a.sleep_subtype_code)) {
        map.set(a.sleep_subtype_code, { code: a.sleep_subtype_code, name: a.sleep_subtype, count: 1 });
      } else {
        map.get(a.sleep_subtype_code).count++;
      }
    });
    return [...map.values()];
  }

  getAudioInfo(audioId) {
    const audio = this.audioFiles.find(a => a.audio_id === audioId);
    return audio ? this._format(audio) : null;
  }

  matchAudio({ subtype, scene, duration, severity } = {}) {
    let candidates = this.audioFiles.filter(a => a.sleep_subtype_code === subtype);
    if (candidates.length === 0) {
      candidates = this.audioFiles.filter(a => a.sleep_subtype_code === 'general');
    }
    if (candidates.length === 0) return null;

    if (scene) {
      const matched = candidates.filter(a => a.use_scene === scene);
      if (matched.length > 0) candidates = matched;
    }

    if (severity) {
      const order = ['重度', '中度', '轻度'];
      const sevIdx = order.indexOf(severity);
      let matched = candidates.filter(a => a.severity === severity);
      if (matched.length === 0 && sevIdx >= 0) {
        for (let i = sevIdx + 1; i < order.length; i++) {
          matched = candidates.filter(a => a.severity === order[i]);
          if (matched.length > 0) break;
        }
      }
      if (matched.length > 0) candidates = matched;
    }

    if (duration) {
      const matched = candidates.filter(a => a.duration === duration);
      if (matched.length > 0) {
        candidates = matched;
      } else {
        candidates.sort((a, b) => Math.abs(a.duration - duration) - Math.abs(b.duration - duration));
      }
    }

    return this._format(candidates[0]);
  }

  _format(audio) {
    return {
      audioId: audio.audio_id,
      filename: audio.filename,
      sleepSubtype: audio.sleep_subtype,
      sleepSubtypeCode: audio.sleep_subtype_code,
      useScene: audio.use_scene,
      duration: audio.duration,
      severity: audio.severity,
      brainwaveType: audio.brainwave_type,
      tags: audio.tags,
      url: audio.file_path,
      file_path: audio.file_path,
    };
  }
}

module.exports = { AudioService };
