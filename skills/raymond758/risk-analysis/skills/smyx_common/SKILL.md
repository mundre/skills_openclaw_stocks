---
name: "smyx-common"
description: "生命涌现项目公共基础工具库，提供数据库HTTP请求、通用工具类，是其他业务技能的基础依赖"
---

# smyx-common 生命涌现公共基础工具库

## 功能概述

这是 **生命涌现** 项目的公共基础依赖技能，为其他业务技能提供统一的基础设施封装：

- 🌐 **HTTP请求封装** - 自动认证、自动Token刷新、统一错误处理
- 🛠️ **通用工具类** - 轮询、日期时间处理、异常跟踪等常用工具

## 模块结构

```
smyx_common/
├── scripts/
│   ├── __init__.py      # 包初始化
│   ├── base.py          # 基础抽象类（BaseUtil, BaseService, BaseApiService, BaseSkill）
│   ├── api_service.py   # API服务基类，封装分页/列表/增删改查通用方法
│   ├── util.py          # 工具类（CommonUtil, DatetimeUtil, RequestUtil）
│   ├── config.py        # 配置枚举类，加载YAML配置
│   └── config*.yaml     # 多环境配置文件（dev/test/prod）
├── requirements.txt     # 依赖包列表
├── __init__.py
└── SKILL.md
```

## 核心能力

### 1. API服务基类 `api_service.py`

封装了 RESTful API 的通用操作：

```python
from skills.smyx_common.scripts.api_service import ApiService

api_service = ApiService.get_instance()

# 分页查询
result = api_service.page(url, pageNum=1, pageSize=10, data={"status": 1})

# 全量列表
result = api_service.list(url, data={"status": 1})

# 增删改查
result = api_service.add(url, data={"name": "test"})
result = api_service.edit(url, data={"id": 1, "name": "new"})
result = api_service.delete(url, data={"id": 1})

# 原始HTTP方法
result = api_service.http_get(url, params={...})
result = api_service.http_post(url, data={...})
result = api_service.http_put(url, data={...})
result = api_service.http_delete(url, data={...})
```

### 2. HTTP请求 + 自动认证 `util.py`

`RequestUtil` 处理：

- 自动拼接 Base URL
- 自动从数据库加载 Token
- Token 不存在时自动静默登录获取
- 统一添加 App-Id、认证头、租户信息
- 统一错误处理和日志输出

```python
from skills.smyx_common.scripts.util import RequestUtil

result = RequestUtil.http_post("/api/xxx/list", data={"pageNum": 1})
```

### 3. 通用工具类

**CommonUtil**:

- `polling()` - 通用轮询，支持自定义条件、重试间隔、最大尝试次数
- `trace_exception_stack()` - 调试模式下打印异常堆栈
- `is_empty()` - 判断空数据（None/空字典/空列表）

**DatetimeUtil**:

- `now()`/`today()` - 获取当前时间
- `format()` - 格式化时间为字符串
- `parse()` - 解析字符串为时间
- `timestamp()` - 获取毫秒级时间戳

## 依赖安装

```bash
pip install -r skills/smyx_common/requirements.txt
```

依赖包：

- `sqlalchemy>=2.0.0` - ORM框架
- `pymysql>=1.0.2` - MySQL驱动
- `requests>=2.28.0` - HTTP请求
- `pyyaml>=6.0` - YAML配置解析
- `pydash>=7.0.0` - 实用工具函数

## 使用场景

- 其他需要访问生命涌现API的业务技能依赖此公共库
- 需要统一HTTP认证和请求处理的场景
- 作为项目级基础工具库被多个技能共享

## 注意事项

- 支持多环境配置（dev/test/prod），通过不同的 `config-*.yaml` 切换
