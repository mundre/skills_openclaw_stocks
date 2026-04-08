/**
 * 音频服务 - 核心匹配与查询逻辑
 */

const manifest = require('../manifest.json');

class AudioService {
  constructor() {
    this.audioFiles = manifest.audio_files || [];
    this.libraryPath = manifest.library_path || '';
  }

  // ---- 基础查询 ----

  /**
   * 获取所有音频列表（支持过滤）
   * @param {Object} filters - 过滤条件
   * @param {number} page - 页码（从1开始）
   * @param {number} pageSize - 每页数量
   */
  listAudio(filters = {}, page = 1, pageSize = 20) {
    let result = this.audioFiles;

    // 应用过滤
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

    // 分页
    const total = result.length;
    const start = (page - 1) * pageSize;
    const items = result.slice(start, start + pageSize);

    return {
      total,
      page,
      pageSize,
      totalPages: Math.ceil(total / pageSize),
      items: items.map(a => this._formatAudio(a)),
    };
  }

  /**
   * 获取所有可用场景
   */
  getAvailableScenes() {
    const sceneSet = new Set(this.audioFiles.map(a => a.use_scene));
    return Array.from(sceneSet);
  }

  /**
   * 获取所有可用睡眠亚型
   */
  getAvailableSubtypes() {
    const subtypeMap = new Map();
    this.audioFiles.forEach(a => {
      if (!subtypeMap.has(a.sleep_subtype_code)) {
        subtypeMap.set(a.sleep_subtype_code, {
          code: a.sleep_subtype_code,
          name: a.sleep_subtype,
          count: 1,
        });
      } else {
        subtypeMap.get(a.sleep_subtype_code).count++;
      }
    });
    return Array.from(subtypeMap.values());
  }

  /**
   * 根据 audio_id 获取音频信息
   */
  getAudioInfo(audioId) {
    const audio = this.audioFiles.find(a => a.audio_id === audioId);
    return audio ? this._formatAudio(audio) : null;
  }

  /**
   * 获取音频完整播放 URL
   */
  getAudioUrl(audioId) {
    const audio = this.audioFiles.find(a => a.audio_id === audioId);
    return audio ? audio.file_path : null;
  }

  // ---- 核心匹配逻辑 ----

  /**
   * 多维音频匹配
   * @param {Object} params - { subtype, scene, duration, severity }
   * @returns 匹配的音频对象
   */
  matchAudio({ subtype, scene, duration, severity } = {}) {
    let candidates = this.audioFiles;

    // Step 1: 精确匹配亚型
    candidates = candidates.filter(a => a.sleep_subtype_code === subtype);

    if (candidates.length === 0) {
      // 降级：尝试通用类型
      candidates = this.audioFiles.filter(a => a.sleep_subtype_code === 'general');
    }

    if (candidates.length === 0) {
      return null;
    }

    // Step 2: 匹配场景
    if (scene) {
      const sceneMatched = candidates.filter(a => a.use_scene === scene);
      if (sceneMatched.length > 0) candidates = sceneMatched;
    }

    // Step 3: 匹配严重程度（无则降级：重度→中度→轻度）
    if (severity) {
      const severityOrder = ['重度', '中度', '轻度'];
      const sevIdx = severityOrder.indexOf(severity);

      let sevMatched = candidates.filter(a => a.severity === severity);
      if (sevMatched.length === 0 && sevIdx >= 0) {
        // 降级：从高到低尝试
        for (let i = sevIdx + 1; i < severityOrder.length; i++) {
          sevMatched = candidates.filter(a => a.severity === severityOrder[i]);
          if (sevMatched.length > 0) break;
        }
      }
      if (sevMatched.length > 0) candidates = sevMatched;
    }

    // Step 4: 匹配时长（无则选最接近）
    if (duration) {
      const durMatched = candidates.filter(a => a.duration === duration);
      if (durMatched.length > 0) {
        candidates = durMatched;
      } else {
        // 降级：选最接近的时长
        candidates.sort((a, b) =>
          Math.abs(a.duration - duration) - Math.abs(b.duration - duration)
        );
      }
    }

    // Step 5: 返回最优结果
    return this._formatAudio(candidates[0]);
  }

  // ---- 私有方法 ----

  _formatAudio(audio) {
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
