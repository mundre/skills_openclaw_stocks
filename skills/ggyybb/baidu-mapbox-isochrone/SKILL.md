---
name: baidu-mapbox-isochrone
description: 生成等时圈（isochrone）。通过百度地理编码API将地址转为BD-09坐标，转换为WGS84后，调用Mapbox Isochrone API生成等时圈SHP文件和Python预览图。当用户需要：给定地址生成等时圈地图、百度坐标转WGS84后做等时圈分析、生成等时圈shapefile并提供预览图时使用此技能。
---

# 等时圈生成器

通过百度地理编码 + 坐标转换 + Mapbox Isochrone API 生成等时圈 SHP 文件和预览图。

## 工作流程

执行 `scripts/generate_isochrone.py`，分 6 步完成：

```
[Step 1] 百度地理编码 (BD-09)
    → 地址 → 百度AK → BD-09 经纬度
[Step 2] 坐标转换 (BD-09 → WGS84)
    → coord_convert.bd2wgs()
[Step 3] Mapbox 等时圈 API
    → WGS84 坐标 + 出行模式 + 时间 → GeoJSON 等时圈面
[Step 4] 保存 Shapefile
    → point.shp（起点） + isochrone.shp（等时圈面）
[Step 5] 获取 WGS84 底图
    → ESRI World Imagery 瓦片（EPSG:3857）→ rasterio 重投影为 WGS84 (EPSG:4326) GeoTIFF
[Step 6] 生成预览图
    → WGS84 底图 + 等时圈（WGS84，alpha=0.35半透明）叠加渲染 + WGS84经纬度标注
```

## 参数（按顺序）

| 序号 | 参数 | 说明 | 示例 |
|------|------|------|------|
| 1 | 地址 | 任意百度地图可识别的地址 | `北京市朝阳区建国路88号` |
| 2 | 百度 AK | 百度地图开放平台 AK | `your_baidu_ak_here` |
| 3 | Mapbox AK | Mapbox 访问令牌 | `your_mapbox_ak_here` |
| 4 | 出行模式 | driving / walking / cycling | `driving` |
| 5 | 时间(分钟) | 等时圈时长 | `30` |
| 6 | 输出目录 | 可选，默认为 /tmp/isochrone_output | `/root/result` |

## 输出文件

生成在 `<输出目录>/` 下：

| 文件 | 说明 | CRS |
|------|------|-----|
| `point.shp` | 起点（经纬度点） | EPSG:4326 |
| `isochrone.shp` | 等时圈面 | EPSG:4326 |
| `isochrone_preview.png` | 预览图（Mapbox街道底图 + 半透明等时圈 + 中心点标注） | — |
| `base_map_wgs84.tif` | ESRI 卫星底图（WGS84 重投影） | EPSG:4326 |

## 使用示例

```
请帮我生成等时圈：
- 地址：北京市朝阳区建国路88号
- 百度AK：abc123
- Mapbox AK：xyz789
- 出行模式：driving
- 时间：30分钟
```

Agent 应执行：
```bash
cd /root/.openclaw/workspace/skills/baidu-mapbox-isochrone
python3 scripts/generate_isochrone.py "北京市朝阳区建国路88号" "abc123" "xyz789" "driving" 30
```

## 脚本执行结果

脚本成功后会输出 `RESULT_JSON`，包含：
- `address`：地址名称
- `bd09`：百度坐标
- `wgs84`：WGS84 坐标
- `mode`、`minutes`：出行参数
- `files.point_shp`、`files.isochrone_shp`、`files.preview_png`：输出文件路径

将结果中的文件路径和预览图返回给用户。

## 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| `百度地理编码失败` | AK 无效或地址无法识别 | 检查 AK / 换用更精确的地址 |
| `Mapbox API 认证失败` | Mapbox AK 错误 | 核对 AK |
| `Mapbox API 参数错误 (422)` | 坐标超出支持区域 | 确认地址在支持范围内 |
| 依赖缺失 | 包未安装 | `pip install coord_convert geopandas shapely pyshp matplotlib --break-system-packages` |

## 依赖

系统需安装中文字体（matplotlib 使用的字体名为 `Noto Sans CJK JP`，来自 NotoSansCJK-Regular.ttc）。如预览图中文显示异常，检查系统是否有可用中文字体，或在脚本中调整 `plt.rcParams["font.sans-serif"]`。

Python 依赖：
```
coord_convert, geopandas, shapely, pyshp, matplotlib, rasterio, scipy, pykdtree
```
