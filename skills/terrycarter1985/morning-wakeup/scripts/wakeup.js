#!/usr/bin/env node
/**
 * Morning Wakeup Automation Script
 * 根据当日天气自动匹配并播放Sonos音乐预设
 */

const { execSync } = require('child_process');
const https = require('https');

// 天气-音乐映射配置
const WEATHER_MUSIC_MAPPINGS = {
  // WMO天气代码映射: https://open-meteo.com/en/docs
  weatherCodes: {
    0: { name: '晴天', preset: 'Morning Coffee', hotPreset: 'Summer Vibes' },
    1: { name: '晴转多云', preset: 'Chill Morning' },
    2: { name: '多云', preset: 'Chill Morning' },
    3: { name: '阴天', preset: 'Cloudy Day' },
    45: { name: '雾天', preset: 'Ambient Sounds' },
    48: { name: '雾凇', preset: 'Ambient Sounds' },
    51: { name: '小雨', preset: 'Rainy Mood' },
    53: { name: '中雨', preset: 'Rainy Mood' },
    55: { name: '大雨', preset: 'Rainy Mood' },
    56: { name: '冻雨', preset: 'Cozy Winter' },
    57: { name: '冻雨', preset: 'Cozy Winter' },
    61: { name: '小雨', preset: 'Rainy Mood' },
    63: { name: '中雨', preset: 'Rainy Mood' },
    65: { name: '大雨', preset: 'Rainy Mood' },
    66: { name: '冻雨', preset: 'Cozy Winter' },
    67: { name: '冻雨', preset: 'Cozy Winter' },
    71: { name: '小雪', preset: 'Cozy Winter' },
    73: { name: '中雪', preset: 'Cozy Winter' },
    75: { name: '大雪', preset: 'Cozy Winter' },
    77: { name: '雪粒', preset: 'Cozy Winter' },
    80: { name: '阵雨', preset: 'Rainy Mood' },
    81: { name: '阵雨', preset: 'Rainy Mood' },
    82: { name: '暴雨', preset: 'Rainy Mood' },
    85: { name: '阵雪', preset: 'Cozy Winter' },
    86: { name: '阵雪', preset: 'Cozy Winter' },
    95: { name: '雷暴', preset: 'Deep Focus' },
    96: { name: '雷暴冰雹', preset: 'Deep Focus' },
    99: { name: '雷暴大冰雹', preset: 'Deep Focus' }
  },
  defaultPreset: 'Morning Coffee'
};

class MorningWakeup {
  constructor(options = {}) {
    this.options = {
      location: options.location || 'Beijing',
      units: options.units || 'celsius',
      sonosSpeaker: options.sonosSpeaker || '',
      volume: options.volume || 25,
      customMappings: options.customMappings || {},
      ...options
    };
    
    this.weatherData = null;
    this.selectedPreset = null;
  }

  /**
   * 解析位置参数，支持城市名或经纬度
   */
  parseLocation(location) {
    if (location.includes(',')) {
      const [lat, lon] = location.split(',').map(s => parseFloat(s.trim()));
      return { lat, lon, name: location };
    }
    
    // 常用城市坐标
    const cityCoords = {
      'beijing': { lat: 39.9042, lon: 116.4074, name: '北京' },
      'shanghai': { lat: 31.2304, lon: 121.4737, name: '上海' },
      'tokyo': { lat: 35.6762, lon: 139.6503, name: '东京' },
      'new york': { lat: 40.7128, lon: -74.0060, name: '纽约' },
      'london': { lat: 51.5074, lon: -0.1278, name: '伦敦' },
      'paris': { lat: 48.8566, lon: 2.3522, name: '巴黎' },
      'shenzhen': { lat: 22.5431, lon: 114.0579, name: '深圳' },
      'guangzhou': { lat: 23.1291, lon: 113.2644, name: '广州' }
    };
    
    const key = location.toLowerCase().trim();
    return cityCoords[key] || { lat: 39.9042, lon: 116.4074, name: location };
  }

  /**
   * 从Open-Meteo获取天气数据
   */
  async fetchWeather() {
    const coords = this.parseLocation(this.options.location);
    
    return new Promise((resolve, reject) => {
      const url = `https://api.open-meteo.com/v1/forecast?latitude=${coords.lat}&longitude=${coords.lon}&current=temperature_2m,relative_humidity_2m,weather_code,precipitation_probability&timezone=auto`;
      
      const req = https.get(url, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const json = JSON.parse(data);
            this.weatherData = {
              location: coords.name,
              temperature: json.current.temperature_2m,
              humidity: json.current.relative_humidity_2m,
              weatherCode: json.current.weather_code,
              precipitationProbability: json.current.precipitation_probability || 0,
              units: json.current_units.temperature_2m
            };
            resolve(this.weatherData);
          } catch (e) {
            reject(e);
          }
        });
      }).on('error', reject);
      
      // 添加请求超时
      req.setTimeout(10000, () => {
        req.destroy();
        reject(new Error('Weather API request timeout'));
      });
    });
  }

  /**
   * 根据天气匹配音乐预设
   */
  matchMusicPreset() {
    if (!this.weatherData) {
      throw new Error('Weather data not loaded');
    }

    const { temperature, weatherCode } = this.weatherData;
    const mapping = WEATHER_MUSIC_MAPPINGS.weatherCodes[weatherCode];
    
    if (!mapping) {
      this.selectedPreset = WEATHER_MUSIC_MAPPINGS.defaultPreset;
      return this.selectedPreset;
    }

    // 晴天根据温度选择不同预设
    if (weatherCode === 0) {
      if (temperature >= 25) {
        this.selectedPreset = mapping.hotPreset || 'Summer Vibes';
      } else {
        this.selectedPreset = mapping.preset || 'Morning Coffee';
      }
    } else {
      this.selectedPreset = mapping.preset;
    }

    return this.selectedPreset;
  }

  /**
   * 获取Sonos设备
   */
  findSonosSpeaker() {
    try {
      const output = execSync('sonos discover 2>/dev/null || true', { encoding: 'utf8', timeout: 10000 });
      const lines = output.split('\n').filter(line => line.trim() && !line.includes('Discovering') && line.includes('─'));
      
      if (lines.length > 0) {
        const match = lines[0].match(/│\s*([^│]+?)\s*│/);
        if (match) {
          return match[1].trim();
        }
      }
      return '';
    } catch (e) {
      return '';
    }
  }

  /**
   * Shell转义函数，防止命令注入
   */
  escapeShellArg(arg) {
    return arg.replace(/'/g, "'\\''");
  }

  /**
   * 播放Sonos音乐
   */
  playSonosPreset() {
    const speaker = this.options.sonosSpeaker || this.findSonosSpeaker();
    
    if (!speaker) {
      console.log('⚠️  未找到Sonos设备，跳过播放');
      return false;
    }

    try {
      const safeSpeaker = this.escapeShellArg(speaker);
      const safePreset = this.escapeShellArg(this.selectedPreset || '');
      
      // 设置音量
      execSync(`sonos volume set ${this.options.volume} --name '${safeSpeaker}' 2>/dev/null || true`, { timeout: 10000 });
      
      // 尝试播放预设
      try {
        execSync(`sonos favorites open '${safePreset}' --name '${safeSpeaker}' 2>/dev/null`, { timeout: 15000 });
      } catch (e) {
        // 如果预设不存在，尝试播放第一个收藏
        console.log(`⚠️  预设 "${this.selectedPreset}" 不存在，尝试播放默认音乐`);
        execSync(`sonos play --name '${safeSpeaker}' 2>/dev/null || true`, { timeout: 10000 });
      }

      return true;
    } catch (e) {
      console.log(`⚠️  Sonos播放失败: ${e.message}`);
      return false;
    }
  }

  /**
   * 执行完整的唤醒流程
   */
  async run() {
    console.log('🌅 开始执行晨间唤醒流程...\n');

    try {
      // 1. 获取天气
      console.log('🌤️  获取天气数据...');
      await this.fetchWeather();
      
      const weatherInfo = WEATHER_MUSIC_MAPPINGS.weatherCodes[this.weatherData.weatherCode];
      const weatherName = weatherInfo ? weatherInfo.name : '未知天气';
      
      console.log(`   📍 位置: ${this.weatherData.location}`);
      console.log(`   🌡️  温度: ${this.weatherData.temperature}${this.weatherData.units}`);
      console.log(`   ☁️  天气: ${weatherName}`);
      console.log(`   💧 降水概率: ${this.weatherData.precipitationProbability}%`);
      console.log(`   💧 湿度: ${this.weatherData.humidity}%\n`);

      // 2. 匹配音乐预设
      console.log('🎵 匹配音乐预设...');
      this.matchMusicPreset();
      console.log(`   已选择预设: ${this.selectedPreset}\n`);

      // 3. 播放Sonos
      console.log('🔊 准备播放Sonos...');
      const playSuccess = this.playSonosPreset();
      
      // 4. 输出总结
      console.log('\n' + '='.repeat(50));
      console.log('✅ 晨间唤醒流程执行完成');
      console.log('='.repeat(50));
      console.log(`📍 位置: ${this.weatherData.location}`);
      console.log(`🌡️  天气: ${weatherName}，${this.weatherData.temperature}${this.weatherData.units}`);
      console.log(`💧 降水概率: ${this.weatherData.precipitationProbability}%`);
      console.log(`🎵 匹配预设: ${this.selectedPreset}`);
      console.log(`🔊 播放状态: ${playSuccess ? '正在播放' : '已跳过'}`);
      console.log('='.repeat(50));

      return {
        success: true,
        weather: this.weatherData,
        preset: this.selectedPreset,
        playSuccess
      };

    } catch (error) {
      console.error(`❌ 执行失败: ${error.message}`);
      throw error;
    }
  }
}

// 命令行参数解析
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {};

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--location' && args[i + 1]) {
      options.location = args[i + 1];
      i++;
    } else if (args[i] === '--speaker' && args[i + 1]) {
      options.sonosSpeaker = args[i + 1];
      i++;
    } else if (args[i] === '--volume' && args[i + 1]) {
      options.volume = parseInt(args[i + 1]);
      i++;
    }
  }

  return options;
}

// 主程序
if (require.main === module) {
  const options = parseArgs();
  const wakeup = new MorningWakeup(options);
  
  wakeup.run().catch(err => {
    process.exit(1);
  });
}

module.exports = MorningWakeup;
