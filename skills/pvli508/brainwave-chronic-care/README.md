# 慢病脑波声疗助手 Skill

## 简介

这是一个适配 OpenClaw 平台的慢病脑波声疗助手 Skill，为高血压、糖尿病、睡眠障碍、心脑血管、康复期等慢病患者提供脑波音频播放服务。

## 文件结构

```
brainwave-chronic-care/
├── SKILL.md          # Skill 完整定义（意图、槽位、话术、接口）
├── _meta.json        # Skill 元数据
├── README.md         # 本文件
└── src/
    └── handler.js    # 意图处理器示例代码
```

## 快速开始

### 1. 部署 Skill

将本目录复制到 OpenClaw 的 skill 目录：

```bash
cp -r brainwave-chronic-care /path/to/openclaw/skills/
```

### 2. 配置租户

在后台添加租户，获取 tenant_id 和 api_key。

### 3. 上传音频资源

按规范命名上传脑波音频到 OSS/COS：
```
bw_{慢病类型}_{场景}_{时长}_v{版本}.mp3
例：bw_hypertension_relax_15min_v2.mp3
```

### 4. 对接接口

实现以下接口：
- `/openclaw/skill/auth` - 技能唤醒鉴权
- `/openclaw/skill/intent` - 意图解析与执行
- `/openclaw/skill/callback` - 状态回调

详见 SKILL.md 接口清单部分。

## 意图处理器示例

详见 `src/handler.js`

## 测试

```bash
# 测试播放意图
curl -X POST /openclaw/skill/intent \
  -d '{
    "user_id": "user_123",
    "tenant_id": "tenant_456",
    "intent_id": "PLAY_BRAINWAVE_AUDIO",
    "slots": {
      "chronic_type": "高血压",
      "scene": "睡前",
      "duration": 15
    },
    "device_info": {"device_id": "device_001"}
  }'
```

## 合规声明

所有音频播放必须包含：
> 本音频为非药物健康辅助，不替代医疗诊断、治疗及用药

## 许可证

MIT
