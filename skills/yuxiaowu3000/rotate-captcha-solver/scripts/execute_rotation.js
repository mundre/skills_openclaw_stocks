/**
 * 执行旋转验证码的拖动操作
 * 
 * 模拟人类拖动轨迹，将滑块从起始位置拖动到目标位置
 * 用于完成旋转验证码的验证
 * 
 * @param {Object} params - 参数
 * @param {Object} params.sliderLocation - 滑块位置 {x, y, width, height}
 * @param {Object} params.rotationCenter - 旋转中心 {x, y}
 * @param {number} params.rotationAngle - 旋转角度（度）
 * @param {string} params.direction - 旋转方向 "clockwise" | "counterclockwise"
 * @param {number} params.duration - 拖动持续时间（秒）
 */
async function executeRotation(params) {
    const {
        sliderLocation,
        rotationCenter,
        rotationAngle,
        direction = "clockwise",
        duration = 2.0
    } = params;
    
    // 1. 找到滑块元素
    const slider = await findSliderElement(sliderLocation);
    if (!slider) {
        throw new Error("未找到滑块元素");
    }
    
    // 2. 获取滑块边界
    const box = await slider.boundingBox();
    if (!box) {
        throw new Error("无法获取滑块边界");
    }
    
    // 3. 计算拖动距离（基于旋转角度）
    // 通常滑块拖动距离与旋转角度成正比
    // 假设 180 度对应 200 像素拖动距离
    const dragDistance = (rotationAngle / 180) * 200;
    
    // 4. 生成人类拖动轨迹
    const trajectory = generateHumanTrajectory(dragDistance, direction, duration);
    
    // 5. 执行拖动
    await performDrag(slider, box, trajectory);
    
    console.log(`✅ 旋转验证完成：${rotationAngle}° ${direction}`);
}

/**
 * 查找滑块元素
 */
async function findSliderElement(location) {
    // 尝试多种选择器
    const selectors = [
        '.slider-btn',
        '.rotate-slider',
        '[class*="slider"]',
        '[class*="rotate"]',
        'canvas + div[class*="slider"]',
    ];
    
    for (const selector of selectors) {
        try {
            const element = await document.querySelector(selector);
            if (element) {
                return element;
            }
        } catch (e) {
            continue;
        }
    }
    
    // 如果找不到，尝试通过位置查找
    return null;
}

/**
 * 生成人类拖动轨迹
 * 
 * 特征：
 * - 启动停顿 0.2-0.4 秒
 * - 先快后慢（ease-out）
 * - 轻微抖动
 * - 到达后微调
 */
function generateHumanTrajectory(distance, direction, duration) {
    const trajectory = [];
    const steps = Math.floor(duration * 60); // 60 FPS
    const isClockwise = direction === "clockwise";
    const actualDistance = isClockwise ? distance : -distance;
    
    // 启动前停顿
    const pauseSteps = Math.floor(0.3 * 60);
    for (let i = 0; i < pauseSteps; i++) {
        trajectory.push({
            x: 0,
            y: Math.random() * 2 - 1, // 轻微抖动
            delay: 16
        });
    }
    
    // 主拖动阶段
    for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        
        // ease-out cubic: 1 - (1-t)^3
        const progress = 1 - Math.pow(1 - t, 3);
        
        // 计算当前位置
        const x = actualDistance * progress;
        
        // 垂直抖动（模拟手部不稳定）
        const y = Math.sin(t * Math.PI * 4) * 2 + (Math.random() * 2 - 1);
        
        // 随机速度变化
        const delay = 16 + Math.random() * 8 - 4;
        
        trajectory.push({ x, y, delay });
    }
    
    // 到达后微调（模拟确认动作）
    for (let i = 0; i < 5; i++) {
        trajectory.push({
            x: actualDistance + (Math.random() * 4 - 2),
            y: Math.random() * 2 - 1,
            delay: 30
        });
    }
    
    return trajectory;
}

/**
 * 执行拖动操作
 */
async function performDrag(slider, box, trajectory) {
    const page = slider._context._page;
    
    // 1. 鼠标移动到滑块中心
    const startX = box.x + box.width / 2;
    const startY = box.y + box.height / 2;
    
    await page.mouse.move(startX, startY);
    
    // 2. 等待一小段时间（模拟观察）
    await sleep(200 + Math.random() * 200);
    
    // 3. 按下鼠标
    await page.mouse.down();
    
    // 4. 按轨迹移动
    let currentX = startX;
    let currentY = startY;
    
    for (const point of trajectory) {
        currentX += point.x;
        currentY += point.y;
        
        await page.mouse.move(currentX, currentY);
        await sleep(point.delay);
    }
    
    // 5. 保持片刻（模拟确认）
    await sleep(300 + Math.random() * 200);
    
    // 6. 释放鼠标
    await page.mouse.up();
    
    // 7. 等待验证结果
    await sleep(1000);
}

/**
 * 睡眠函数
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// 导出函数
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { executeRotation };
}
