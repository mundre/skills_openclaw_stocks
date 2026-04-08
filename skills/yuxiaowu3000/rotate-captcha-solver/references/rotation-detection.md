# 旋转角度检测算法详解

本文档详细介绍旋转验证码角度识别的算法原理和优化技巧。

## 核心算法流程

```
截图 → 预处理 → 边缘检测 → 霍夫变换 → 角度计算 → 后处理
```

## 1. 图像预处理

### 1.1 灰度转换

```python
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
```

将彩色图像转换为灰度图，减少计算量。

### 1.2 高斯模糊

```python
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
```

**目的**：减少图像噪声，避免边缘检测产生过多伪边缘。

**参数选择**：
- `(5, 5)`: 核大小，奇数
- `0`: 标准差，自动计算

### 1.3 对比度增强（可选）

```python
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
enhanced = clahe.apply(gray)
```

对于对比度低的验证码，使用 CLAHE 增强局部对比度。

## 2. 边缘检测

### 2.1 Canny 边缘检测

```python
edges = cv2.Canny(blurred, threshold1=50, threshold2=150, apertureSize=3)
```

**参数说明**：
- `threshold1=50`: 低阈值，低于此值的边缘被抑制
- `threshold2=150`: 高阈值，高于此值的边缘被保留
- `apertureSize=3`: Sobel 算子孔径大小

**参数调优**：
| 场景 | threshold1 | threshold2 | 说明 |
|------|------------|------------|------|
| 清晰验证码 | 50 | 150 | 默认值 |
| 低对比度 | 30 | 100 | 降低阈值检测更多边缘 |
| 高噪声 | 80 | 200 | 提高阈值减少伪边缘 |

### 2.2 边缘细化（可选）

```python
kernel = np.ones((3,3),np.uint8)
dilated_edges = cv2.dilate(edges, kernel, iterations=2)
eroded_edges = cv2.erode(dilated_edges, kernel, iterations=1)
```

膨胀 + 腐蚀操作可以连接断开的边缘。

## 3. 霍夫变换检测直线

### 3.1 标准霍夫变换

```python
lines = cv2.HoughLines(edges, rho=1, theta=np.pi/180, threshold=100)
```

**参数说明**：
- `rho=1`: 距离分辨率（像素）
- `theta=np.pi/180`: 角度分辨率（1 度）
- `threshold=100`: 累加器阈值，越高检测到的直线越少

**输出格式**：
```
lines = [[rho1, theta1], [rho2, theta2], ...]
```

### 3.2 概率霍夫变换（更高效）

```python
lines = cv2.HoughLinesP(
    edges, 
    rho=1, 
    theta=np.pi/180, 
    threshold=50,
    minLineLength=50,
    maxLineGap=10
)
```

**优势**：
- 只返回线段的端点，计算量更小
- 可以设置最小线段长度

**输出格式**：
```
lines = [[x1, y1, x2, y2], ...]
```

### 3.3 角度提取

```python
angles = []
for rho, theta in lines[:, 0]:
    # theta 是直线法线与 x 轴的夹角
    angle = np.degrees(theta)
    
    # 转换为 0-180 度范围
    if angle > 90:
        angle = 180 - angle
    
    # 过滤接近水平或垂直的线（可能是边框）
    if 10 < angle < 80:
        angles.append(angle)
```

**为什么要过滤水平和垂直线**：
- 验证码边框通常是水平/垂直的
- 我们关心的是图片内容的倾斜角度

## 4. 角度计算

### 4.1 中位数法（推荐）

```python
median_angle = np.median(angles)
rotation_angle = 90 - median_angle
```

**优势**：
- 对异常值不敏感
- 比平均值更稳定

### 4.2 加权平均法

```python
# 根据直线长度加权
weighted_angles = []
weights = []

for line in lines:
    x1, y1, x2, y2 = line[0]
    length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
    
    angle = np.degrees(np.arctan2(y2-y1, x2-x1))
    weighted_angles.append(angle)
    weights.append(length)

average_angle = np.average(weighted_angles, weights=weights)
```

**优势**：
- 长直线更可靠，权重更高

### 4.3 直方图峰值法

```python
# 构建角度直方图
hist, bins = np.histogram(angles, bins=90, range=(0, 90))

# 找到峰值
peak_bin = np.argmax(hist)
peak_angle = bins[peak_bin]
```

**优势**：
- 可以找到最常见的角度
- 对多组直线有效

## 5. 备用方案：轮廓方法

当霍夫变换无法检测到足够直线时，使用轮廓拟合方法。

### 5.1 阈值分割

```python
_, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
```

### 5.2 查找轮廓

```python
contours, _ = cv2.findContours(
    thresh, 
    cv2.RETR_EXTERNAL, 
    cv2.CHAIN_APPROX_SIMPLE
)
```

### 5.3 最小外接矩形

```python
largest_contour = max(contours, key=cv2.contourArea)
rect = cv2.minAreaRect(largest_contour)
(center, size, angle) = rect
```

**注意**：OpenCV 返回的角度范围是 [-90, 0)，需要根据版本转换。

### 5.4 角度标准化

```python
# OpenCV 4.5.4+ 新版本
if angle < -45:
    angle = -(90 + angle)
else:
    angle = -angle
```

## 6. 置信度评估

### 6.1 基于直线数量

```python
confidence = min(1.0, len(angles) / 20.0)
```

### 6.2 基于角度一致性

```python
if len(angles) > 1:
    std_dev = np.std(angles)
    confidence = max(0, 1 - std_dev / 30)  # 标准差越小越可信
else:
    confidence = 0.5
```

### 6.3 综合置信度

```python
confidence = (
    0.4 * min(1.0, len(angles) / 20.0) +  # 直线数量
    0.4 * max(0, 1 - np.std(angles) / 30) +  # 角度一致性
    0.2 * (cv2.contourArea(largest_contour) / roi_area)  # 轮廓面积比
)
```

## 7. 优化技巧

### 7.1 多尺度检测

```python
scales = [0.5, 0.75, 1.0, 1.25, 1.5]
all_angles = []

for scale in scales:
    resized = cv2.resize(roi, None, fx=scale, fy=scale)
    angle, conf = calculate_rotation_angle(resized)
    if conf > 0.7:
        all_angles.append((angle, conf))

# 加权平均
if all_angles:
    final_angle = np.average([a for a, c in all_angles], 
                             weights=[c for a, c in all_angles])
```

### 7.2 多方法融合

```python
# 霍夫变换结果
hough_angle, hough_conf = calculate_by_hough(roi)

# 轮廓方法结果
contour_angle, contour_conf = calculate_by_contour(roi)

# 融合
if hough_conf > 0.7 and contour_conf > 0.7:
    final_angle = (hough_angle * hough_conf + contour_angle * contour_conf) / (hough_conf + contour_conf)
elif hough_conf > 0.7:
    final_angle = hough_angle
else:
    final_angle = contour_angle
```

### 7.3 模板匹配（已知目标角度）

如果知道目标图片应该是什么样子（如百度地图的 logo），可以使用模板匹配：

```python
# 旋转模板进行匹配
best_angle = 0
best_score = 0

for angle in range(0, 180, 5):
    rotated_template = rotate_image(template, angle)
    result = cv2.matchTemplate(roi, rotated_template, cv2.TM_CCOEFF_NORMED)
    _, score, _, _ = cv2.minMaxLoc(result)
    
    if score > best_score:
        best_score = score
        best_angle = angle

# 精细搜索
for angle in range(best_angle - 5, best_angle + 5):
    # 同样方法精细搜索
    pass
```

## 8. 性能优化

### 8.1 ROI 裁剪

```python
# 只处理旋转区域，不处理整张图
x, y, w, h = rotation_area
roi = image[y:y+h, x:x+w]
```

### 8.2 图像缩放

```python
# 对于大图，先缩小再处理
if roi.shape[0] > 300 or roi.shape[1] > 300:
    scale = 300 / max(roi.shape)
    roi = cv2.resize(roi, None, fx=scale, fy=scale)
    # 记得最后把角度结果乘以 scale
```

### 8.3 缓存中间结果

```python
# 避免重复计算
@lru_cache(maxsize=100)
def compute_edges(image_hash):
    # 计算边缘
    pass
```

## 9. 常见问题

### Q1: 检测到的角度总是偏差几度？

**A**: 可能是边缘检测参数不合适，尝试：
- 降低 Canny 阈值
- 增加霍夫变换的 threshold
- 使用多尺度检测融合结果

### Q2: 有时检测不到任何直线？

**A**: 验证码可能纹理较少，尝试：
- 使用轮廓方法作为备用
- 增加 Canny 的低阈值
- 使用自适应阈值分割

### Q3: 计算速度太慢？

**A**: 优化建议：
- 裁剪 ROI 区域
- 缩小图像尺寸
- 减少霍夫变换的 theta 分辨率（如改为 np.pi/90）
