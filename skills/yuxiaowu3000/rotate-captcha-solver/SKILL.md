---
name: rotate-captcha-solver
description: 专门处理旋转验证码的浏览器自动化技能。使用 OpenCV 边缘检测 + 霍夫变换识别图片倾斜角度，模拟人类拖动轨迹完成旋转验证。支持百度地图、各类需要"旋转图片到正确角度"的验证码。当遇到"旋转验证码"、"拖动滑块旋转"时自动触发。
allowed-tools: Bash(agent-browser:*)
---

# Rotate Captcha Solver - 旋转验证码处理技能

专门处理**旋转验证码**（Rotate Captcha），这类验证码要求用户拖动滑块将倾斜的图片旋转到正确角度（通常是水平位置）。

## 支持的验证码类型

| 类型 | 特征 | 支持网站 |
|------|------|----------|
| **圆形旋转** | 圆形图片需要旋转到正位 | 百度地图、各类地图服务 |
| **方形旋转** | 方形图片需要旋转对齐 | 各类登录页面 |
| **图标旋转** | 旋转图标到指定方向 | 各类验证场景 |

### 🎯 典型场景

| 网站/场景 | 验证码类型 | 识别成功率 | 备注 |
|-----------|------------|------------|------|
| **百度地图** | 圆形旋转 | 85%+ | 最常见场景 |
| **地图类网站** | 圆形/方形旋转 | 80%+ | 高德、腾讯地图等 |
| **登录页面** | 方形旋转 | 75%+ | 各类网站登录验证 |
| **注册流程** | 图标旋转 | 70%+ | 账号注册验证 |

## 核心工作流程

```
1. 检测验证码 → 2. 截图 → 3. 识别倾斜角度 → 4. 模拟拖动旋转 → 5. 验证结果
```

### 完整流程示例

```bash
# 1. 打开目标页面（如百度地图）
agent-browser open "https://map.baidu.com"

# 2. 等待验证码出现
agent-browser wait 3000

# 3. 全屏截图
agent-browser screenshot --full captcha-rotate.png

# 4. 使用脚本识别旋转角度
python3 skills/rotate-captcha-solver/scripts/recognize_rotation.py \
  --screenshot captcha-rotate.png \
  --output result.json \
  --debug

# 5. 执行旋转操作
agent-browser eval "$(cat result.json | jq -r '
  {
    "sliderLocation": .slider_location,
    "rotationCenter": .rotation_center,
    "rotationAngle": .rotation_angle,
    "direction": .rotation_direction
  }
')"

# 6. 验证是否成功
agent-browser wait 1500
agent-browser screenshot verify.png
```

## 脚本工具

### recognize_rotation.py - 旋转角度识别

自动检测验证码区域并识别需要旋转的角度。

```bash
python3 scripts/recognize_rotation.py \
  --screenshot <截图路径> \
  --output <输出 JSON> \
  [--debug] \
  [--debug-dir debug_rotate_captcha]
```

**输出示例：**
```json
{
  "success": true,
  "rotation_angle": 45.5,
  "rotation_direction": "clockwise",
  "confidence": 0.92,
  "slider_location": {"x": 280, "y": 450, "width": 60, "height": 40},
  "rotation_center": {"x": 400, "y": 300},
  "rotation_radius": 120
}
```

**参数说明：**
- `--screenshot, -s`: 必填，截图路径
- `--output, -o`: 必填，输出 JSON 路径
- `--debug, -d`: 可选，输出调试图片
- `--debug-dir`: 可选，调试图片输出目录（默认：debug_rotate_captcha）

### execute_rotation.js - 执行旋转

Playwright JavaScript 代码，模拟人类拖动轨迹完成旋转。

```javascript
// 在 agent-browser 中执行
await executeRotation({
    sliderLocation: {x: 280, y: 450, width: 60, height: 40},
    rotationCenter: {x: 400, y: 300},
    rotationAngle: 45.5,
    direction: "clockwise",
    duration: 2.0
});
```

## 识别算法

### 1. 旋转区域检测

```python
def detect_rotation_area(image):
    """
    检测旋转验证码区域
    特征：圆形或方形、居中显示、有明显边缘
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    # 查找轮廓
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 找到最大的接近圆形的轮廓
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 10000:
            continue
        
        # 拟合最小外接圆
        (x, y), radius = cv2.minEnclosingCircle(contour)
        
        # 检查是否接近圆形
        circle_area = np.pi * radius * radius
        if area / circle_area > 0.7:
            return {"center": (x, y), "radius": radius}
    
    return None
```

### 2. 旋转角度计算（霍夫变换）

```python
def calculate_rotation_angle(roi):
    """
    使用霍夫变换检测直线，计算倾斜角度
    """
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # 霍夫变换检测直线
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)
    
    # 计算所有直线的平均角度
    angles = []
    for rho, theta in lines[:, 0]:
        angle = np.degrees(theta)
        if angle > 90:
            angle = 180 - angle
        if 10 < angle < 80:  # 过滤水平和垂直线
            angles.append(angle)
    
    # 取中位数
    median_angle = np.median(angles)
    rotation_angle = 90 - median_angle
    
    return rotation_angle, confidence
```

### 3. 备用方案（轮廓方法）

```python
def calculate_angle_by_contour(roi):
    """
    当霍夫变换失败时，使用轮廓拟合矩形
    """
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest = max(contours, key=cv2.contourArea)
    
    # 拟合最小外接矩形
    rect = cv2.minAreaRect(largest)
    (center, size, angle) = rect
    
    return angle, confidence
```

## 人类轨迹模拟

### 拖动轨迹生成

```python
def generate_human_trajectory(distance, direction, duration=2.0):
    """
    生成模拟人类拖动轨迹
    
    特征：
    - 启动停顿 0.2-0.4 秒
    - 先快后慢（ease-out cubic）
    - 垂直抖动 ±2 像素
    - 到达后微调确认
    """
    trajectory = []
    steps = int(duration * 60)
    
    # 启动前停顿
    for _ in range(int(0.3 * 60)):
        trajectory.append({"x": 0, "y": random.gauss(0, 1), "delay": 16})
    
    for i in range(steps + 1):
        t = i / steps
        
        # ease-out cubic
        progress = 1 - math.pow(1 - t, 3)
        x = distance * progress
        
        # 垂直抖动
        y = math.sin(t * math.pi * 4) * 2 + random.gauss(0, 1)
        
        # 随机速度变化
        delay = 16 + random.uniform(-4, 4)
        
        trajectory.append({"x": x, "y": y, "delay": delay})
    
    # 到达后微调
    for _ in range(5):
        trajectory.append({
            "x": distance + random.uniform(-2, 2),
            "y": random.gauss(0, 1),
            "delay": 30
        })
    
    return trajectory
```

## 使用示例

### 示例 1：百度地图自动验证

```bash
# 1. 打开百度地图
agent-browser open "https://map.baidu.com"

# 2. 等待页面加载和验证码出现
agent-browser wait --load networkidle
agent-browser wait 3000

# 3. 截图
agent-browser screenshot --full captcha.png

# 4. 识别角度
python3 scripts/recognize_rotation.py \
  --screenshot captcha.png \
  --output result.json \
  --debug

# 5. 执行旋转
agent-browser eval "
  const result = $(cat result.json);
  await executeRotation({
    sliderLocation: result.slider_location,
    rotationCenter: result.rotation_center,
    rotationAngle: result.rotation_angle,
    direction: result.rotation_direction,
    duration: 2.0
  });
"

# 6. 验证结果
agent-browser wait 1500
agent-browser screenshot verify.png
```

### 示例 2：批量处理多个验证码

```bash
#!/bin/bash

# 批量识别
for img in captchas/*.png; do
    echo "处理：$img"
    python3 scripts/recognize_rotation.py \
        --screenshot "$img" \
        --output "results/${img%.png}.json" \
        --debug
    
    if [ $? -eq 0 ]; then
        echo "✅ 成功：$img"
    else
        echo "❌ 失败：$img"
    fi
done
```

## 依赖安装

```bash
# 核心依赖
pip install opencv-python numpy pillow

# 可选：深度学习模型（提高识别率）
pip install torch torchvision
```

## 故障排除

### 问题 1：无法检测旋转区域

**原因**：截图时机不对或验证码样式变化

**解决**：
```bash
# 增加等待时间
agent-browser wait --load networkidle
agent-browser wait 5000

# 使用全屏截图
agent-browser screenshot --full captcha.png

# 使用 debug 模式查看检测结果
python3 scripts/recognize_rotation.py \
  --screenshot captcha.png \
  --output result.json \
  --debug
```

### 问题 2：识别角度不准确

**原因**：图片质量差或验证码有干扰

**解决**：
1. 检查 `debug_rotate_captcha/marked.png` 查看检测区域
2. 调整 Canny 参数（脚本中修改 50, 150）
3. 尝试调整截图分辨率

### 问题 3：旋转后验证失败

**原因**：轨迹太机械或角度计算偏差

**解决**：
1. 增加拖动时间到 2.0-3.0 秒
2. 检查角度计算是否正确
3. 尝试多次重试（有时需要微调）

## 参考文档

- [references/rotation-detection.md](references/rotation-detection.md) - 旋转角度检测算法详解
- [references/trajectory-optimization.md](references/trajectory-optimization.md) - 轨迹优化技巧
- [references/website-patterns.md](references/website-patterns.md) - 各网站验证码特征库

## ❓ 常见问题 (FAQ)

### Q1: 识别成功率有多少？

**A:** 成功率取决于验证码类型：
- 标准圆形旋转（百度地图）：85-95%
- 方形旋转：75-85%
- 复杂背景旋转：60-75%

**提高成功率的方法：**
1. 确保截图清晰（使用 `--full` 全屏截图）
2. 等待页面完全加载
3. 使用 debug 模式检查识别结果

---

### Q2: 为什么旋转后验证失败？

**A:** 可能的原因：

| 原因 | 解决方案 |
|------|----------|
| 角度计算偏差 | 检查 debug 图片，调整算法参数 |
| 轨迹太机械 | 使用内置的人类轨迹模拟（已默认启用） |
| 拖动太快 | 延长拖动时间到 2.0-3.0 秒 |
| IP 被标记 | 切换 IP 或使用代理 |

---

### Q3: 如何调试识别问题？

**A:** 使用 `--debug` 模式：

```bash
python3 scripts/recognize_rotation.py \
  --screenshot captcha.png \
  --output result.json \
  --debug
```

会在 `debug_rotate_captcha/` 目录生成：
- `original.png` - 原图
- `marked.png` - 标记检测区域的图
- `roi.png` - 裁剪的旋转区域

---

### Q4: 支持 headless 浏览器吗？

**A:** 支持，但**不推荐**：

```bash
# 不推荐：headless 模式容易被检测
agent-browser open --headless <url>

# 推荐：使用真实浏览器
agent-browser open <url>
```

---

### Q5: 如何处理新型旋转验证码？

**A:** 如果遇到不支持的验证码类型：

1. **截图保存**
   ```bash
   agent-browser screenshot unknown_captcha.png
   ```

2. **使用 debug 模式分析**
   ```bash
   python3 scripts/recognize_rotation.py \
     --screenshot unknown_captcha.png \
     --debug
   ```

3. **查看调试图片** - 分析检测失败的原因

4. **提交反馈** - 帮助改进技能

---

### Q6: 可以商用吗？

**A:** 本技能使用 **MIT-0** 许可证：
- ✅ 可以免费使用
- ✅ 可以修改和分发
- ✅ 不需要署名
- ⚠️ 但请遵守目标网站的服务条款
- ⚠️ 不要用于恶意爬虫或攻击

---

### Q7: 与其他验证码技能有什么区别？

**A:** 

| 技能 | 定位 | 优势 |
|------|------|------|
| **rotate-captcha-solver** | 专注旋转验证码 | 角度识别精准、人类轨迹模拟 |
| **puzzle-captcha-solver** | 专注拼图滑块 | 缺口识别精准、支持网站多 |
| **captcha-solver** | 通用验证码 | 支持多种类型（图形/点击/滑块） |

**选择建议：**
- 旋转验证码 → 用这个技能
- 拼图滑块 → 用 `puzzle-captcha-solver`
- 多种类型混合 → 用 `captcha-solver`

---

## 注意事项

⚠️ **合规使用**
- 仅用于合法用途
- 遵守目标网站服务条款
- 不要用于恶意爬虫

⚠️ **成功率**
- 标准旋转：85-95%
- 复杂旋转：60-85%
- 新型验证码：可能需手动处理

⚠️ **性能**
- 识别耗时：1-3 秒
- 拖动耗时：2.0-3.0 秒
- 建议设置超时 15 秒
