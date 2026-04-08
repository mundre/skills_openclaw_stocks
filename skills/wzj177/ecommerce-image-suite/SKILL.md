---
name: ecommerce-image-suite
description: >
  电商套图生成助手。用户明确提出需要生成电商套图、商品主图、卖点图、场景图、模特图等图片内容时触发。
  支持国内平台（淘宝、京东、拼多多、抖音）与国际跨境平台（Amazon、独立站）的尺寸规范。
  触发示例：「帮我生成这件T恤的电商套图」「做一套淘宝主图」「生成亚马逊listing图片」。
  不应在用户仅上传图片但未明确提出图片生成需求时触发。
metadata: {"openclaw":{"emoji":"🛍️","requires":{"env":["ANTHROPIC_API_KEY","QWEN_API_KEY"]},"primaryEnv":"QWEN_API_KEY"}}
---

# 电商套图生成助手

## 概览

本 Skill 实现从「商品原始图片 + 卖点信息」到「完整电商套图」的一键生成流程：

```
① 上传商品图片（必须）+ 输入卖点信息（可选）
        ↓
② AI 视觉分析：提取商品主体，智能生成卖点文案（可编辑）
        ↓
③ 选择平台规范 + 套图类型（7种标准图）
        ↓
④ AI 生成每张图的详细 Prompt（可编辑）
        ↓
⑤ 调用图像生成 API，输出完整套图
```

---

## 第一步：收集输入信息

### 必须项
- **商品图片**：用户上传的原始商品图（平铺图/白底图/实物图均可）

### 可选项（若用户未提供，AI 将自动从图片中分析生成）
| 字段 | 说明 |
|------|------|
| 商品名称 | 如"卡通小狗印花宽松精梳棉短袖T恤" |
| 核心卖点 | 材质、版型、设计特点等 3-5 条 |
| 适用人群 | 如"追求舒适简约风的青少年" |
| 期望场景 | 如"校园日常、居家休闲、户外出游" |
| 规格参数 | 材质、颜色、版型、领型、袖长等 |

---

## 第二步：AI 分析与卖点生成

### 视觉分析步骤
1. 识别商品类型、颜色、款式、设计元素
2. 提取商品主体轮廓与关键视觉特征
3. 基于视觉特征推断材质、功能卖点
4. 生成结构化卖点（JSON格式，供后续图片生成使用）

### 卖点 JSON 结构
```json
{
  "product_name": "商品名称",
  "product_type": "服装/3C/家居/其他",
  "visual_features": ["白色", "圆领", "短袖", "卡通小狗印花"],
  "selling_points": [
    {"icon": "fabric", "en": "Combed Cotton", "zh": "精梳棉面料"},
    {"icon": "fit", "en": "Loose & Breathable", "zh": "宽松透气"},
    {"icon": "design", "en": "Cute Design", "zh": "萌趣设计"}
  ],
  "target_audience": "青少年、学生群体",
  "usage_scenes": ["校园", "居家", "户外"],
  "color": "白色",
  "material": "精梳棉"
}
```

> 📄 详细分析 Prompt 见 `references/analysis-prompts.md`

---

## 第三步：选择平台与套图配置

> 📄 各平台规范详见 `references/platforms.md`

### 平台选择
| 平台类型 | 平台 | 推荐尺寸 | 语言 |
|---------|------|---------|------|
| 国内 | 淘宝/天猫 | 800×800 (1:1) | 中文 |
| 国内 | 京东 | 800×800 (1:1) | 中文 |
| 国内 | 拼多多 | 750×750 (1:1) | 中文 |
| 国内 | 抖音/小红书 | 1080×1350 (4:5) 或 1:1 | 中文 |
| 国际 | Amazon | 2000×2000 (1:1) | 英文 |
| 国际 | 独立站/Shopify | 2000×2000 (1:1) 或 16:9 | 英文 |

### 标准套图（7种）
每种图的详细规格见 `references/image-types.md`

| # | 图片类型 | 核心目标 | 推荐位置 |
|---|---------|---------|---------|
| 1 | **白底主图** | 商品全貌展示，符合平台收录规则 | 第1张主图 |
| 2 | **核心卖点图** | 3大卖点图标化呈现 | 第2张 |
| 3 | **卖点图** | 单一核心卖点深度展示 | 第3张 |
| 4 | **材质图** | 面料/工艺特写，建立品质信任 | 第4张 |
| 5 | **场景展示图** | 生活方式场景，激发代入感 | 第5张 |
| 6 | **模特展示图** | 真人/AI模特穿搭，直观展示效果 | 第6张 |
| 7 | **多场景拼图** | 多场景适用性对比，提升决策 | 第7张 |

---

## 第四步：生成图片 Prompt

> 📄 各图类型的 Prompt 模板见 `references/image-types.md`

### Prompt 构建原则
1. **商品一致性**：所有图片必须保持商品颜色、结构、比例、细节不变
2. **背景差异化**：每张图背景/场景各不相同，形成完整故事线
3. **文字分离**：图片本身不含文字，文案通过后处理叠加（除非使用图像生成API支持文字）
4. **品质标准**：`photorealistic, high quality, studio lighting, 8K, commercial photography`

### Prompt 结构模板
```
[商品描述] + [版型/颜色/印花精确描述] + [场景/背景描述] + [光线/氛围] + [拍摄角度] + [品质词]
```

---

## 第五步：多供应商图像生成

> 📄 各供应商 API 接入详情见 `references/providers.md`

### 支持的图像生成供应商（5个）
| 供应商 | 模型 | 国内可用 | 特点 |
|--------|------|---------|------|
| OpenAI | DALL·E 3 | 需代理 | 高质量写实，细节清晰 |
| Google | Gemini Imagen 3 | 需代理 | 色彩真实，商业感强 |
| Stability AI | Stable Image Core | 需代理 | 精准控制构图 |
| 阿里云 | 千问 | ✅直连 | 中文场景优化，异步任务 |
| 字节跳动 | 豆包 Seedream | ✅直连 | 中文理解好，风格多样 |

### 供应商检测与选择逻辑
1. 用户在配置面板填入各供应商 API Key（浏览器本地存储）
2. 系统检测哪些供应商已配置（Key 非空）
3. 若只有1个供应商配置 → 自动选择
4. 若有多个 → 展示供应商选择界面让用户选择
5. 若无任何配置 → 提示用户先配置，展示 Prompt 预览模式

## 第六步：Canvas 文案叠加

> 📄 各图类型叠加坐标规范见 `references/providers.md`（Canvas规范部分）

### 核心逻辑
```javascript
async function applyTextOverlay(base64, typeId, sellingPoints, lang) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0);
      
      const texts = OVERLAY_CONFIGS[typeId]?.(sellingPoints, lang) || [];
      texts.forEach(t => {
        const fontSize = Math.round(t.fontSize * canvas.width);
        ctx.font = `${t.weight || "600"} ${fontSize}px "Helvetica Neue", Arial, sans-serif`;
        ctx.textAlign = t.align || "left";
        if (t.shadow) {
          ctx.shadowColor = "rgba(0,0,0,0.5)";
          ctx.shadowBlur = 8;
        }
        ctx.fillStyle = t.color || "#fff";
        ctx.fillText(t.text, t.x * canvas.width, t.y * canvas.height);
        ctx.shadowColor = "transparent";
        ctx.shadowBlur = 0;
      });
      
      resolve(canvas.toDataURL("image/jpeg", 0.92).split(",")[1]);
    };
    img.src = `data:image/jpeg;base64,${base64}`;
  });
}
```

### 叠加规范（各图类型）
- **白底主图 / 模特展示图**：无文案叠加
- **核心卖点图**：右侧区域，WHY CHOOSE US + 3个卖点标签，深色文字
- **卖点图**：左上主标题 + 左下两条副标题，深色文字
- **材质图**：右上主标题 + 右侧两条副标题，深色文字
- **场景展示图**：左上主标题 + 左下两条副标题，白色文字+阴影
- **多场景拼图**：顶部居中主标题 + 底部两侧场景标注，白色文字+阴影

---

## 交互式 Artifact 实现

当用户上传商品图片请求生成套图时，**优先创建交互式 React Artifact**，实现以下 UI 流程：

### UI 流程（5步）
```
① API配置 → ② 图片上传+AI分析 → ③ 供应商选择（检测已配置的） 
→ ④ 套图类型+语言选择 → ⑤ 生成（含Canvas叠加）→ 预览+下载
```

### Artifact 核心功能模块
1. **ProviderConfig**：5个供应商API Key配置，检测已配置项，浏览器本地存储
2. **ProviderDetect**：自动检测已配置供应商，多个时弹出选择，单个时自动选中
3. **ImageUploader**：拖拽上传，支持 jpg/png/webp
4. **AIAnalysis**：Claude Vision分析商品图片，输出结构化卖点JSON
5. **SellingPointEditor**：卖点卡片编辑，中英文切换
6. **ImageTypeSelector**：7种类型多选+平台/语言配置
7. **GenerationPipeline**：逐张调用供应商API，实时进度显示
8. **CanvasOverlay**：Canvas API文案叠加，各图类型独立文字位置规范
9. **DownloadPanel**：逐张预览+批量下载

> 📄 完整 Artifact 代码见 `scripts/suite_artifact.jsx`

---

## 执行检查清单

- [ ] 商品图片已上传（必须）
- [ ] 商品卖点已生成或用户已填写
- [ ] 平台已选择（决定语言和尺寸）
- [ ] 套图类型已选择（至少1种）
- [ ] 所有 Prompt 已审核（可选）
- [ ] 图像生成 API 可用

---

## 参考文件索引

| 文件 | 内容 |
|------|------|
| `references/platforms.md` | 各平台尺寸规范、主图要求、文案风格指南 |
| `references/image-types.md` | 7种套图的详细视觉规格与 Prompt 模板 |
| `references/analysis-prompts.md` | AI商品分析与卖点提取的系统 Prompt |
| `scripts/suite_artifact.jsx` | 交互式套图生成 React Artifact |

---

## API Key 配置

本 Skill 使用两类 API：

| 变量 | 用途 | 是否必需 |
|---|---|---|
| `ANTHROPIC_API_KEY` | Claude Vision 分析商品图片、提取卖点 JSON | ✅ 必需 |
| `QWEN_API_KEY` | 千问 qwen-image-2.0-pro 图像生成（国内直连） | ✅ 至少一个图像供应商 |
| `DOUBAO_API_KEY` | 豆包 Seedream 图像生成（国内直连） | 可选 |
| `OPENAI_API_KEY` | DALL·E 3 图像生成（需代理） | 可选 |
| `GEMINI_API_KEY` | Imagen 3 图像生成（需代理） | 可选 |
| `STABILITY_API_KEY` | Stable Image Core（需代理） | 可选 |

> **安全声明**：所有 API Key 仅存于浏览器 `localStorage`，由客户端直接调用各供应商官方 Endpoint，不经过任何第三方服务器中转。建议使用权限最小化的 Key，并定期轮换。

### 方式一：环境变量

```bash
# 必需
export ANTHROPIC_API_KEY="sk-ant-..."
export QWEN_API_KEY="sk-..."            # 阿里云 DashScope（国内直连）

# 可选图像供应商（配置一个以上即可）
export DOUBAO_API_KEY="..."             # 字节跳动火山引擎（国内直连）
export OPENAI_API_KEY="sk-..."         # 需代理
export GEMINI_API_KEY="AIzaSy..."      # 需代理
export STABILITY_API_KEY="sk-..."      # 需代理
```

加入 `~/.zshrc` 或 `~/.bashrc` 后永久生效。

### 方式二：OpenClaw 配置文件

在 `$OPENCLAW_CONFIG_PATH`（默认 `~/.openclaw/openclaw.json`）中配置 `apiKey`，对应 `primaryEnv`（即 `QWEN_API_KEY`）：

```json5
{
  skills: {
    "ecommerce-image-suite": {
      apiKey: "QWEN_API_KEY_HERE",
    },
  },
}
```

`ANTHROPIC_API_KEY` 及其他可选图像供应商 Key 通过环境变量（方式一）补充。

### 方式三：Artifact UI 内配置

在生成器界面点击 **⚙️ API设置**，逐个填入各供应商 Key。  
Key 存于浏览器 `localStorage`，刷新页面后仍有效。
