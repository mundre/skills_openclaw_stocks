# 腾讯云资源管理 - 快速参考

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip3 install --break-system-packages \
  tencentcloud-sdk-python \
  cos-python-sdk-v5 \
  python-dotenv
```

### 2. 配置凭证

```bash
cp skills/tencentcloud-manager/config/.env.example \
   skills/tencentcloud-manager/config/.env
```

编辑 `.env` 文件，填入 SecretId 和 SecretKey。

### 3. 验证配置

```bash
cd skills/tencentcloud-manager/src
python3 tencentcloud_manager.py verify
```

---

## 📋 常用命令

### 查询促销

```python
from tencentcloud_manager import TencentCloudManager
tcm = TencentCloudManager()

tcm.show_promotions(service='lighthouse')
tcm.show_promotions(service='cvm')
```

### 创建资源

```python
# 创建 Lighthouse 实例
instance = tcm.create_resource(
    service='lighthouse',
    plan_id='new-2c4g',
    blueprint_id='bp-ubuntu-2204',
    instance_name='my-server'
)

# 创建 COS 存储桶
bucket = tcm.create_resource(
    service='cos',
    bucket_name='my-bucket',
    storage_class='STANDARD'
)
```

### 管理实例

```python
# 列出所有实例
instances = tcm.list_all_instances()

# 查询实例状态
status = tcm.get_resource_status('lighthouse', instance_id)

# 启动/停止/重启
tcm.start_resource('lighthouse', instance_id)
tcm.stop_resource('lighthouse', instance_id)
tcm.restart_resource('lighthouse', instance_id)
```

### COS 操作

```python
# 上传文件
tcm.upload_to_cos(
    bucket='bucket.cos.ap-singapore.myqcloud.com',
    local_path='/tmp/file.txt',
    key='path/file.txt'
)

# 设置生命周期
tcm.set_cos_lifecycle('bucket', [
    {
        'id': 'rule1',
        'prefix': 'data/',
        'transitions': [
            {'days': 7, 'storage_class': 'STANDARD_IA'},
            {'days': 30, 'storage_class': 'ARCHIVE'}
        ]
    }
])
```

---

## 💰 促销方案

### Lighthouse 新人特惠

| 方案 ID | 配置 | 价格 | 适合场景 |
|--------|------|------|---------|
| new-1c1g | 1 核 1G/30G/30M | ¥60/年 | 个人博客 |
| new-2c2g | 2 核 2G/50G/30M | ¥95/年 | 小型网站 |
| new-2c4g | 2 核 4G/60G/30M | ¥168/年 | 数据采集 |
| new-4c8g | 4 核 8G/80G/30M | ¥338/年 | 大型应用 |

### CVM 按量付费

| 方案 ID | 配置 | 月成本 | 适合场景 |
|--------|------|--------|---------|
| payg-2c2g | 2 核 2G | ~¥86/月 | 测试环境 |
| payg-2c4g | 2 核 4G | ~¥130/月 | 开发环境 |
| payg-4c8g | 4 核 8G | ~¥259/月 | 生产环境 |

---

## 📚 完整文档

- [技能说明](../SKILL.md)
- [权限配置](permission-policy.md)
