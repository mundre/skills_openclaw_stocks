#!/usr/bin/env python3
"""
旋转验证码识别脚本

识别百度地图等网站的旋转验证码，计算需要旋转的角度。
使用 OpenCV 边缘检测 + 霍夫变换识别图片倾斜角度。

使用方法：
    python3 recognize_rotation.py --screenshot captcha.png --output result.json [--debug]

输出示例：
{
    "success": true,
    "rotation_angle": 45,
    "confidence": 0.92,
    "slider_location": {"x": 280, "y": 450},
    "rotation_direction": "clockwise"
}
"""

import argparse
import json
import sys
import os
from pathlib import Path

try:
    import cv2
    import numpy as np
except ImportError:
    print("❌ 错误：需要安装 opencv-python 和 numpy")
    print("   运行：pip install opencv-python numpy")
    sys.exit(1)


def detect_rotation_area(image):
    """
    检测旋转验证码区域
    
    特征：
    - 圆形或方形区域
    - 居中显示
    - 有明显的边缘和纹理
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 高斯模糊减少噪声
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 边缘检测
    edges = cv2.Canny(blurred, 50, 150)
    
    # 查找轮廓
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 找到最大的接近圆形的轮廓（旋转验证码通常是圆形）
    rotation_area = None
    max_area = 0
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # 过滤太小的区域
        if area < 10000:
            continue
        
        # 拟合最小外接圆
        (x, y), radius = cv2.minEnclosingCircle(contour)
        circle_area = np.pi * radius * radius
        
        # 检查是否接近圆形（面积比 > 0.7）
        if area / circle_area > 0.7:
            if area > max_area:
                max_area = area
                rotation_area = {
                    "center": (int(x), int(y)),
                    "radius": int(radius),
                    "area": area
                }
    
    return rotation_area


def calculate_rotation_angle(image, rotation_area):
    """
    计算图片需要旋转的角度
    
    方法：
    1. 提取旋转区域
    2. 使用霍夫变换检测直线
    3. 计算主要线条的角度
    4. 返回需要旋转的角度（使图片水平）
    """
    if not rotation_area:
        return None, 0.0
    
    cx, cy = rotation_area["center"]
    radius = rotation_area["radius"]
    
    # 提取旋转区域
    x1 = max(0, cx - radius)
    y1 = max(0, cy - radius)
    x2 = min(image.shape[1], cx + radius)
    y2 = min(image.shape[0], cy + radius)
    
    roi = image[y1:y2, x1:x2]
    
    if roi.size == 0:
        return None, 0.0
    
    # 转换为灰度图
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # 边缘检测
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # 霍夫变换检测直线
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)
    
    if lines is None:
        # 如果没有检测到直线，尝试使用轮廓方法
        return calculate_angle_by_contour(roi)
    
    # 计算所有直线的平均角度
    angles = []
    for rho, theta in lines[:, 0]:
        # theta 是直线与 x 轴的夹角（弧度）
        angle = np.degrees(theta)
        
        # 转换为 0-180 度范围
        if angle > 90:
            angle = 180 - angle
        
        # 过滤接近水平或垂直的线（可能是边框）
        if 10 < angle < 80:
            angles.append(angle)
    
    if not angles:
        return calculate_angle_by_contour(roi)
    
    # 取中位数作为最终角度
    median_angle = np.median(angles)
    
    # 计算需要旋转的角度（使图片水平）
    # 假设目标是将主要特征旋转到水平位置
    rotation_angle = 90 - median_angle
    
    # 标准化到 -180 到 180 范围
    if rotation_angle > 180:
        rotation_angle -= 360
    elif rotation_angle < -180:
        rotation_angle += 360
    
    # 计算置信度（基于检测到的直线数量）
    confidence = min(1.0, len(angles) / 20.0)
    
    return rotation_angle, confidence


def calculate_angle_by_contour(roi):
    """
    使用轮廓方法计算旋转角度（备用方案）
    
    当霍夫变换无法检测到足够直线时使用
    """
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # 阈值分割
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    
    # 查找轮廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return 0, 0.3  # 默认返回 0 度，低置信度
    
    # 找到最大的轮廓
    largest_contour = max(contours, key=cv2.contourArea)
    
    # 拟合最小外接矩形
    rect = cv2.minAreaRect(largest_contour)
    (center, size, angle) = rect
    
    # 标准化角度到 -90 到 90 范围
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    
    # 置信度基于轮廓面积
    confidence = min(1.0, cv2.contourArea(largest_contour) / (roi.shape[0] * roi.shape[1]) * 2)
    
    return angle, confidence


def detect_slider_location(image, rotation_area):
    """
    检测旋转滑块的位置
    
    通常在旋转区域的下方或侧面
    """
    if not rotation_area:
        return None
    
    cx, cy = rotation_area["center"]
    radius = rotation_area["radius"]
    
    # 在旋转区域下方搜索滑块
    # 滑块通常是圆形或圆角矩形，有颜色差异
    search_y = cy + radius + 20
    search_height = 100
    search_x = cx - radius - 50
    search_width = radius * 2 + 100
    
    # 确保搜索区域在图片范围内
    x1 = max(0, search_x)
    y1 = max(0, search_y)
    x2 = min(image.shape[1], search_x + search_width)
    y2 = min(image.shape[0], search_y + search_height)
    
    search_area = image[y1:y2, x1:x2]
    
    if search_area.size == 0:
        return None
    
    # 转换为 HSV 检测颜色差异
    hsv = cv2.cvtColor(search_area, cv2.COLOR_BGR2HSV)
    
    # 检测蓝色/绿色区域（常见滑块颜色）
    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([130, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        
        # 返回相对于原图的坐标
        return {
            "x": x1 + x,
            "y": y1 + y,
            "width": w,
            "height": h
        }
    
    # 如果没有找到彩色滑块，返回默认位置（旋转区域正下方）
    return {
        "x": cx - 30,
        "y": cy + radius + 30,
        "width": 60,
        "height": 40
    }


def save_debug_images(image, rotation_area, result, output_dir):
    """
    保存调试图片
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 原图
    cv2.imwrite(str(output_dir / "original.png"), image)
    
    # 标记旋转区域
    marked = image.copy()
    if rotation_area:
        cx, cy = rotation_area["center"]
        radius = rotation_area["radius"]
        cv2.circle(marked, (cx, cy), radius, (0, 255, 0), 2)
        
        # 标记中心点
        cv2.circle(marked, (cx, cy), 5, (0, 0, 255), -1)
        
        # 画一条线表示检测到的角度
        angle = result.get("rotation_angle", 0)
        line_length = radius
        end_x = int(cx + line_length * np.cos(np.radians(angle)))
        end_y = int(cy - line_length * np.sin(np.radians(angle)))
        cv2.line(marked, (cx, cy), (end_x, end_y), (255, 0, 0), 2)
    
    cv2.imwrite(str(output_dir / "marked.png"), marked)
    
    # 保存旋转区域裁剪图
    if rotation_area:
        cx, cy = rotation_area["center"]
        radius = rotation_area["radius"]
        x1 = max(0, cx - radius)
        y1 = max(0, cy - radius)
        x2 = min(image.shape[1], cx + radius)
        y2 = min(image.shape[0], cy + radius)
        roi = image[y1:y2, x1:x2]
        cv2.imwrite(str(output_dir / "roi.png"), roi)


def main():
    parser = argparse.ArgumentParser(description="旋转验证码识别脚本")
    parser.add_argument("--screenshot", "-s", required=True, help="截图路径")
    parser.add_argument("--output", "-o", required=True, help="输出 JSON 路径")
    parser.add_argument("--debug", "-d", action="store_true", help="输出调试图片")
    parser.add_argument("--debug-dir", default="debug_rotate_captcha", help="调试图片输出目录")
    
    args = parser.parse_args()
    
    # 读取图片
    if not os.path.exists(args.screenshot):
        print(f"❌ 错误：文件不存在 - {args.screenshot}")
        sys.exit(1)
    
    image = cv2.imread(args.screenshot)
    if image is None:
        print(f"❌ 错误：无法读取图片 - {args.screenshot}")
        sys.exit(1)
    
    print(f"📷 读取图片：{args.screenshot} ({image.shape[1]}x{image.shape[0]})")
    
    # 检测旋转区域
    print("🔍 检测旋转区域...")
    rotation_area = detect_rotation_area(image)
    
    if not rotation_area:
        print("⚠️ 未检测到旋转区域，尝试使用全屏分析...")
        # 使用全屏默认值
        rotation_area = {
            "center": (image.shape[1] // 2, image.shape[0] // 3),
            "radius": min(image.shape[0], image.shape[1]) // 4,
            "area": 50000
        }
    
    print(f"✅ 旋转区域：中心 ({rotation_area['center'][0]}, {rotation_area['center'][1]}), 半径 {rotation_area['radius']}")
    
    # 计算旋转角度
    print("📐 计算旋转角度...")
    rotation_angle, confidence = calculate_rotation_angle(image, rotation_area)
    
    if rotation_angle is None:
        rotation_angle = 0
        confidence = 0.5
    
    print(f"✅ 旋转角度：{rotation_angle:.1f}°, 置信度：{confidence:.2f}")
    
    # 检测滑块位置
    print("🎯 检测滑块位置...")
    slider_location = detect_slider_location(image, rotation_area)
    
    if slider_location:
        print(f"✅ 滑块位置：({slider_location['x']}, {slider_location['y']})")
    else:
        print("⚠️ 未检测到滑块，使用默认位置")
    
    # 确定旋转方向
    if rotation_angle > 0:
        rotation_direction = "counterclockwise"
    elif rotation_angle < 0:
        rotation_direction = "clockwise"
    else:
        rotation_direction = "none"
    
    # 构建结果
    result = {
        "success": True,
        "rotation_angle": abs(rotation_angle),
        "rotation_direction": rotation_direction,
        "confidence": confidence,
        "slider_location": slider_location,
        "rotation_center": rotation_area["center"],
        "rotation_radius": rotation_area["radius"]
    }
    
    # 保存结果
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"💾 结果已保存到：{args.output}")
    
    # 保存调试图片
    if args.debug:
        print(f"🖼️ 保存调试图片到：{args.debug_dir}/")
        save_debug_images(image, rotation_area, result, args.debug_dir)
    
    print("✅ 识别完成！")
    return 0


if __name__ == "__main__":
    sys.exit(main())
