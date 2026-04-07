---
name: weather-pulse
description: "Get current weather and air quality forecasts — real-time temperature, 3-30 day forecasts, hourly forecasts, AQI/PM2.5, wind, humidity, UV, weather indices, and life tips. Powered by free QWeather (50k/mo) and WAQI (1k/hr) APIs. Supports Chinese/English city names, coordinates, and CityId. — 城市天气实时 + 3-30 天预报 + 24-168 小时逐小时 + 空气质量 AQI + 天气生活指数。",
summary: "Get current weather and air quality forecasts — real-time temperature, 3-30 day forecasts, hourly forecasts, AQI/PM2.5, wind, humidity, UV, weather indices, and life tips. Powered by free QWeather (50k/mo) and WAQI (1k/hr) APIs. Supports Chinese/English city names, coordinates, and CityId. — 城市天气实时 + 3-30 天预报 + 24-168 小时逐小时 + 空气质量 AQI + 天气生活指数。"
tags:
  weather: "1.3.1"
  forecast: "1.3.1"
  air-quality: "1.3.1"
  aqi: "1.3.1"
  qweather: "1.3.1"
  temperature: "1.3.1"
  chinese: "1.3.1"
trigger_patterns:
  - "天气"
  - "查天气"
  - "哪里天气"
  - "天气预报"
  - "详细天气"
  - "气温"
  - "温度"
  - "下雨"
  - "下雨吗"
  - "会下雨"
  - "下雨了"
  - "湿度"
  - "风力"
  - "AQI"
  - "空气质量"
  - "空气质量指数"
  - "PM25"
  - "天气怎么样"
  - "什么天气"
  - "weather"
  - "forecast"
homepage: "https://dev.qweather.com/docs"
requiredEnvs:
  - name: QWEATHER_API_HOST
    description: "QWeather API Host from console settings (e.g. xxxxxxx.re.qweatherapi.com). Required for weather endpoints."
    required: false
  - name: QWEATHER_API_KEY
    description: "QWeather API Key from project credentials. Required for weather endpoints."
    required: false
  - name: WAQI_API_TOKEN
    description: "WAQI token from https://aqicn.org/data-platform/token/. Required for AQI endpoint."
    required: false
---

# weather-pulse

Weather + air quality query tool. **Two free APIs** — both registration links below.

> **⚠️ Two APIs, Two Registrations Required:**
> - 🌤️ **Weather Data** → QWeather: https://console.qweather.com
> - 🌫️ **Air Quality Data** → WAQI: https://aqicn.org/api/
>
> **You need BOTH for all features.** Weather-only works without WAQI token. AQI-only works without QWeather credentials.

## Quick Start

### 1. 获取 API 凭证

#### 和风天气 (QWeather) - 免费 50,000 次/月

> 注册获取 API Host + API Key

1. 打开 https://console.qweather.com 注册/登录
2. **创建项目** → 项目名任意（如 Demo）
3. **添加凭据** → 项目 → 凭据设置 → 创建凭据 → 选择 API KEY
4. **获取 API Host** → 左侧菜单「设置」→ 复制 `xxxxxxx.re.qweatherapi.com`

| 配置项 | 必须 | 在哪获取 | 示例 |
|--------|------|---------|------|
| `QWEATHER_API_HOST` | 天气功能 | 和风控制台 → 设置 → API Host | `xxxxxxx.re.qweatherapi.com` |
| `QWEATHER_API_KEY` | 天气功能 | 和风控制台 → 项目 → 凭据 → API KEY | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |

📖 [文档](https://dev.qweather.com/docs/start/) · [定价](https://dev.qweather.com/docs/finance/pricing/)

#### 空气质量 (WAQI) - 免费 1,000 次/小时

> 注册获取 Token

1. 打开 https://aqicn.org/data-platform/token/#/
2. 勾选同意 → 填写邮箱和名字 → 提交
3. 查看邮箱 → 点击确认链接 → 获取 Token

| 配置项 | 必须 | 在哪获取 | 示例 |
|--------|------|---------|------|
| `WAQI_API_TOKEN` | 空气质量功能 | WAQI 邮件确认页 | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |

📖 [文档](https://aqicn.org/api/) · [城市查询](https://aqicn.org/city/)

### 2. 配置凭证

**⚠️ 推荐使用环境变量，不要把 KEY 写进脚本文件！**

> 安全提醒：将 API Key 直接写入代码可能导致泄露（意外提交到 Git、共享设备等）。
> 请使用环境变量或 `.env` 文件管理凭证。

#### 方式 A: 环境变量（推荐 · 唯一推荐）

**只需配置你要用的功能对应的凭证：**

```bash
# 天气功能（Linux/macOS）
export QWEATHER_API_HOST="你的API Host"
export QWEATHER_API_KEY="你的API Key"

# 天气功能（Windows PowerShell）
$env:QWEATHER_API_HOST = "你的API Host"
$env:QWEATHER_API_KEY = "你的API Key"

# 空气质量功能
$env:WAQI_API_TOKEN = "你的WAQI Token"
```

#### 方式 B: .env 文件

创建 `.env` 文件（与 `weather.py` 同级），每次运行前加载：

```bash
# .env 文件内容
QWEATHER_API_HOST=你的API Host
QWEATHER_API_KEY=你的API Key
WAQI_API_TOKEN=你的WAQI Token
```

```bash
# Linux/macOS
set -a && source .env && set +a && python scripts/weather.py ...

# Windows PowerShell
Get-Content .env | ForEach-Object { $k,$v = $_.Split('='); Set-Item "env:$k" $v }
python scripts/weather.py ...
```

### 3. 运行测试

```bash
# 实况天气 (需要 CityId)
python scripts/weather.py 101180301

# 空气质量 (支持城市名)
python scripts/weather.py xinxiang --endpoint aqi
```

---

## Call Method

```bash
python scripts/weather.py <location> [--endpoint ENDPOINT] [--json]
```

### Location 格式（自动智能解析）

| 类型 | 格式 | 支持端点 | 示例 |
|------|------|----------|------|
| CityId | 纯数字 | 所有 | `101180301` |
| 英文城市名 | 任意 | **所有端点**（天气端点自动转为CityId） | `Shanghai`、`Beijing` |
| 中文城市名 | 任意 | **所有端点**（天气端点自动转为CityId） | `上海`、`新乡` |
| 经纬度 | `经度,纬度` 或 `纬度,经度`（自动检测纠正） | 所有 | `113.92,35.30` |
| geo:格式 | 仅 aqi 端点 | aqi 端点 | `geo:35.30;113.92` |
| WAQI ID | `@数字` | aqi 端点 | `@5789` |
| 当前位置 | `here` | aqi 端点 | `here` |

> ✅ 城市名输入会自动通过和天气 GeoAPI 解析为 CityId，**无需手动查 ID**。
> ✅ 经纬度输入自动识别顺序（经度,纬度 / 纬度,经度都支持）。
> ✅ AQI 端点支持 WAQI 格式（英文城市名、@ID、geo:），无需解析。

### 可用端点

| 端点 | 数据源 | 免费额度 | 说明 |
|------|--------|---------|------|
| `now` | QWeather | 50k/月 | 实况天气 |
| `3d` | QWeather | 50k/月 | 3天逐日 |
| `7d` | QWeather | 50k/月 | 7天逐日 |
| `10d` | QWeather | 50k/月 | 10天逐日 |
| `15d` | QWeather | 50k/月 | 15天逐日 |
| `30d` | QWeather | 50k/月 | 30天逐日 |
| `24h` | QWeather | 50k/月 | 24小时逐小时 |
| `72h` | QWeather | 50k/月 | 72小时逐小时 |
| `168h` | QWeather | 50k/月 | 168小时逐小时 |
| `indices` | QWeather | 50k/月 | 天气生活指数(19种) |
| `aqi` | WAQI | 1k/小时 | 空气质量+PM2.5/PM10预报 |

---

## Data Reference

### 实况天气 `now`

| 字段 | 说明 | 单位 |
|------|------|------|
| `temp` | 温度 | °C |
| `feelsLike` | 体感温度 | °C |
| `text` / `icon` | 天气描述 / 图标 | — |
| `windDir` / `windScale` | 风向 / 风力 | Beaufort |
| `windSpeed` | 风速 | km/h |
| `humidity` | 湿度 | % |
| `precip` | 过去1h降水量 | mm |
| `pressure` | 气压 | hPa |
| `vis` | 能见度 | km |
| `cloud` | 云量 | % |
| `dew` | 露点温度 | °C |

### 逐日预报 `3d/7d/10d/15d/30d`

| 字段 | 说明 | 单位 |
|------|------|------|
| `fxDate` | 日期 | — |
| `sunrise` / `sunset` | 日出 / 日落 | HH:MM |
| `moonrise` / `moonset` | 月升 / 月落 | HH:MM |
| `moonPhase` | 月相 | — |
| `tempMax` / `tempMin` | 最高温 / 最低温 | °C |
| `textDay` / `textNight` | 白天 / 夜间天气 | — |
| `windDirDay` + `Night` | 白天 / 夜间风向 | — |
| `windScaleDay` + `Night` | 白天 / 夜间风力 | Beaufort |
| `humidity` | 湿度 | % |
| `precip` | 当天总降水量 | mm |
| `uvIndex` | 紫外线指数 | — |
| `pressure` | 气压 | hPa |
| `vis` | 能见度 | km |

### 逐小时预报 `24h/72h/168h`

| 字段 | 说明 | 单位 |
|------|------|------|
| `fxTime` | 时间 (ISO8601) | — |
| `temp` | 温度 | °C |
| `text` | 天气 | — |
| `windDir` / `windScale` | 风向 / 风力 | Beaufort |
| `humidity` | 湿度 | % |
| `pop` | 降水概率 | % |
| `precip` | 降水量 | mm |
| `pressure` | 气压 | hPa |
| `cloud` | 云量 | % |
| `dew` | 露点温度 | °C |

### 天气指数 `indices`

19种指数：运动、洗车、穿衣、钓鱼、紫外线、旅游、过敏、舒适度、**感冒**、污染扩散、空调、太阳镜、化妆、晾晒、交通、防晒。中国全部19种可用，海外仅支持 5种(运动/洗车/穿衣/钓鱼/紫外线)。

| 字段 | 说明 |
|------|------|
| `name` | 指数类型 |
| `category` | 等级名称 |
| `text` | 详细建议 |

### 空气质量 `aqi`

数据来源: WAQI (aqicn.org)

| 字段 | 说明 | 单位 |
|------|------|------|
| `aqi` | 空气质量指数 | — |
| `dominentpol` | 主要污染物 | pm25/pm10/o3/no2 |
| `pm25` | PM2.5 | μg/m³ |
| `pm10` | PM10 | μg/m³ |
| `co` | CO | mg/m³ |
| `no2` / `o3` / `so2` | NO₂ / O₃ / SO₂ | μg/m³ |
| `t` / `h` | 温度 / 湿度 | °C / % |
| `p` / `w` | 气压 / 风速 | hPa / km/h |
| `forecast.pm25[]` | 7天 PM2.5 预报 | avg/min/max |
| `forecast.pm10[]` | 7天 PM10 预报 | avg/min/max |

AQI 等级：优(≤50) · 良(≤100) · 轻度污染(≤150) · 中度污染(≤200) · 重度污染(≤300) · 严重污染(>300)

---

## Examples

```bash
# 实况天气 (CityId)
python scripts/weather.py 101180301

# 实况天气 (英文城市名，自动解析)
python scripts/weather.py Shanghai

# 实况天气 (中文城市名，自动解析)
python scripts/weather.py 上海

# 7天预报
python scripts/weather.py 101180301 --endpoint 7d

# 24小时逐小时
python scripts/weather.py 101180301 --endpoint 24h

# 15天预报 (经纬度，自动识别顺序)
python scripts/weather.py 113.92,35.30 --endpoint 15d
python scripts/weather.py 35.30,113.92 --endpoint 15d

# 天气指数
python scripts/weather.py 101180301 --endpoint indices

# 空气质量 (城市名)
python scripts/weather.py xinxiang --endpoint aqi
python scripts/weather.py 新乡 --endpoint aqi

# 空气质量 (经纬度方式)
python scripts/weather.py "geo:35.30;113.92" --endpoint aqi

# JSON 原始输出
python scripts/weather.py 101180301 --json
```

## Error Codes

| QWeather code | WAQI status | Meaning |
|--------------|-------------|---------|
| 200 | ok | ✅ 成功 |
| 400 | error | ❌ 参数错误 |
| 401 | error | ❌ 认证失败 (检查 key/token) |
| 402 | — | ❌ 额度用尽 |
| 403 | — | ❌ API Host 错误 |

## FAQ

**Q: 提示"配置项未设置"？**
A: 需要在 CONFIG 区域填写 3 个凭证，或设置环境变量。

**Q: 怎么查城市 CityId？**
A: **不用查了！** 直接输入城市名（中英文都行），脚本会自动解析。

**Q: 支持的常用城市**
A: 北京、上海、广州、深圳、天津、重庆、长沙、武汉、成都、杭州、南京、郑州、西安、新乡、东京、New York 等，只要和风天气 GeoAPI 能识别的都支持。
