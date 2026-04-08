/**
 * 睡眠脑波路由
 * /sleep/* → 睡眠脑波 Skill 能力
 */

const Router = require('@koa/router');
const fs = require('fs');
const path = require('path');
const config = require('../config/default');

const router = new Router({ prefix: '/sleep' });

// 懒加载 service（避免循环依赖）
let _audioService, _profileService;
const getServices = () => {
  if (!_audioService) {
    const { AudioService } = require('../services/audioService');
    const { ProfileService } = require('../services/profileService');
    _audioService = new AudioService();
    _profileService = new ProfileService();
  }
  return { audioService: _audioService, profileService: _profileService };
};

// ---- 音频查询 ----

/**
 * GET /sleep/audio/list
 * 音频清单（支持过滤）
 */
router.get('/audio/list', (ctx) => {
  const { subtype, scene, duration, severity, page = 1, pageSize = 20 } = ctx.query;
  const { audioService } = getServices();

  const filters = {};
  if (subtype) filters.sleep_subtype_code = subtype;
  if (scene) filters.use_scene = scene;
  if (duration) filters.duration = parseInt(duration);
  if (severity) filters.severity = severity;

  const result = audioService.listAudio(filters, parseInt(page), parseInt(pageSize));
  const hostPrefix = _getHostPrefix(ctx);

  result.items = result.items.map(item => ({
    ...item,
    streamUrl: `${hostPrefix}/sleep/audio/stream/${item.audioId}`,
  }));

  ctx.body = { code: 0, message: 'success', data: result };
});

/**
 * GET /sleep/audio/scenes
 * 可用场景列表
 */
router.get('/audio/scenes', (ctx) => {
  const { audioService } = getServices();
  ctx.body = { code: 0, message: 'success', data: audioService.getAvailableScenes() };
});

/**
 * GET /sleep/audio/subtypes
 * 可用睡眠亚型列表
 */
router.get('/audio/subtypes', (ctx) => {
  const { audioService } = getServices();
  ctx.body = { code: 0, message: 'success', data: audioService.getAvailableSubtypes() };
});

/**
 * GET /sleep/audio/match
 * 智能匹配音频
 */
router.get('/audio/match', (ctx) => {
  const { subtype, scene, duration, severity, userId } = ctx.query;
  const { audioService, profileService } = getServices();

  if (!subtype) {
    ctx.status = 400;
    ctx.body = { code: 400, message: '缺少必填参数：subtype', data: null };
    return;
  }

  let finalSeverity = severity;
  if (userId && !severity) {
    const profile = profileService.getProfile(userId);
    if (profile?.severity) finalSeverity = profile.severity;
  }

  const matchResult = audioService.matchAudio({
    subtype,
    scene: scene || null,
    duration: duration ? parseInt(duration) : null,
    severity: finalSeverity || null,
  });

  if (matchResult) {
    const hostPrefix = _getHostPrefix(ctx);
    matchResult.streamUrl = `${hostPrefix}/sleep/audio/stream/${matchResult.audioId}`;
  }

  ctx.body = {
    code: 0,
    message: matchResult ? 'success' : '未找到匹配的音频',
    data: matchResult,
  };
});

/**
 * GET /sleep/audio/:audioId/info
 * 音频详细信息
 */
router.get('/audio/:audioId/info', (ctx) => {
  const { audioId } = ctx.params;
  const { audioService } = getServices();
  const info = audioService.getAudioInfo(audioId);

  if (!info) {
    ctx.status = 404;
    ctx.body = { code: 404, message: `音频不存在: ${audioId}`, data: null };
    return;
  }

  const hostPrefix = _getHostPrefix(ctx);
  ctx.body = {
    code: 0,
    message: 'success',
    data: { ...info, streamUrl: `${hostPrefix}/sleep/audio/stream/${audioId}` },
  };
});

/**
 * GET /sleep/audio/:audioId/url
 * 音频地址信息
 */
router.get('/audio/:audioId/url', (ctx) => {
  const { audioId } = ctx.params;
  const { audioService } = getServices();
  const info = audioService.getAudioInfo(audioId);

  if (!info) {
    ctx.status = 404;
    ctx.body = { code: 404, message: `音频不存在: ${audioId}`, data: null };
    return;
  }

  const hostPrefix = _getHostPrefix(ctx);
  ctx.body = {
    code: 0,
    message: 'success',
    data: {
      audioId,
      filename: info.filename,
      localPath: info.file_path,
      streamUrl: `${hostPrefix}/sleep/audio/stream/${audioId}`,
      duration: info.duration,
      sleepSubtype: info.sleepSubtype,
    },
  };
});

// ---- 流媒体播放 ----

/**
 * GET /sleep/audio/stream/:audioId
 * 流媒体播放（支持 Range 拖动）
 */
router.get('/audio/stream/:audioId', async (ctx) => {
  const { audioId } = ctx.params;
  const { audioService } = getServices();
  const audioInfo = audioService.getAudioInfo(audioId);

  if (!audioInfo) {
    ctx.status = 404;
    ctx.body = { code: 404, message: `音频不存在: ${audioId}`, data: null };
    return;
  }

  const localFilePath = audioInfo.file_path;

  if (!fs.existsSync(localFilePath)) {
    ctx.status = 404;
    ctx.body = { code: 404, message: `音频文件未找到: ${localFilePath}`, data: null };
    return;
  }

  const stat = fs.statSync(localFilePath);
  const fileSize = stat.size;
  const range = ctx.request.headers.range;

  ctx.set('Content-Type', 'audio/mpeg');
  ctx.set('Accept-Ranges', 'bytes');
  ctx.set('Access-Control-Allow-Origin', '*');
  ctx.set('Content-Length', fileSize);
  ctx.set('Cache-Control', 'public, max-age=3600');

  if (range) {
    const parts = range.replace(/bytes=/, '').split('-');
    const start = parseInt(parts[0], 10);
    const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
    const chunkSize = end - start + 1;

    ctx.status = 206;
    ctx.set('Content-Range', `bytes ${start}-${end}/${fileSize}`);
    ctx.set('Content-Length', String(chunkSize));
    ctx.body = fs.createReadStream(localFilePath, { start, end });
  } else {
    ctx.status = 200;
    ctx.body = fs.createReadStream(localFilePath);
  }
});

// ---- 用户画像 ----

/**
 * GET /sleep/profile/:userId
 * 获取用户画像
 */
router.get('/profile/:userId', (ctx) => {
  const { userId } = ctx.params;
  const { profileService } = getServices();
  ctx.body = { code: 0, message: 'success', data: profileService.getProfile(userId) };
});

/**
 * POST /sleep/profile
 * 创建/更新用户画像
 */
router.post('/profile', (ctx) => {
  const body = ctx.request.body;
  const { profileService } = getServices();

  if (!body?.userId) {
    ctx.status = 400;
    ctx.body = { code: 400, message: '缺少必填参数：userId', data: null };
    return;
  }

  profileService.updateProfile(body.userId, {
    disorderSubtype: body.disorderSubtype,
    severity: body.severity,
    ageGroup: body.ageGroup,
    gender: body.gender,
    comorbidity: body.comorbidity,
  });

  ctx.body = {
    code: 0,
    message: 'success',
    data: profileService.getProfile(body.userId),
  };
});

/**
 * GET /sleep/recommend/:userId
 * 智能推荐
 */
router.get('/recommend/:userId', (ctx) => {
  const { userId } = ctx.params;
  const { scene } = ctx.query;
  const { audioService, profileService } = getServices();
  const profile = profileService.getProfile(userId);
  const hostPrefix = _getHostPrefix(ctx);

  if (!profile) {
    const result = audioService.matchAudio({ subtype: 'general', scene: scene || '睡前', duration: null, severity: '轻度' });
    if (result) result.streamUrl = `${hostPrefix}/sleep/audio/stream/${result.audioId}`;
    ctx.body = { code: 0, message: '无用户画像，返回通用推荐', data: { profile: null, audio: result } };
    return;
  }

  const result = audioService.matchAudio({
    subtype: profile.disorderSubtype || 'general',
    scene: scene || profile.scene || null,
    duration: null,
    severity: profile.severity || null,
  });

  if (result) result.streamUrl = `${hostPrefix}/sleep/audio/stream/${result.audioId}`;
  ctx.body = { code: 0, message: 'success', data: { profile, audio: result } };
});

// ---- 私有方法 ----

function _getHostPrefix(ctx) {
  const protocol = ctx.protocol === 'https' ? 'https' : 'http';
  const host = config.HOST === '0.0.0.0' ? 'localhost' : config.HOST;
  return `${protocol}://${host}:${config.PORT}`;
}

module.exports = router;
