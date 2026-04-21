# Django 代码审计专项规则

## 重点关注场景

### 🔴 高危：安全相关

#### SQL 注入
```python
# ❌ 危险：字符串拼接 SQL
cursor.execute("SELECT * FROM users WHERE id=" + user_id)

# ✅ 安全：参数化查询
cursor.execute("SELECT * FROM users WHERE id=%s", [user_id])
```

#### XSS 跨站脚本
```python
# ❌ 危险：直接渲染用户输入
return HttpResponse(request.GET['name'])

# ✅ 安全：使用 Django 模板或 mark_safe 仅在可信场景
from django.utils.html import escape
return HttpResponse(escape(request.GET['name']))
```

#### SECRET_KEY 硬编码
```python
# ❌ 危险
SECRET_KEY = 'your-secret-key-here'

# ✅ 安全：使用环境变量
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
```

#### DEBUG 模式开启
```python
# ❌ 生产环境危险
DEBUG = True
ALLOWED_HOSTS = ['*']

# ✅ 安全
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['.example.com']
```

#### 不安全的重定向
```python
# ❌ 危险：开放重定向
return redirect(request.GET.get('next', '/'))

# ✅ 安全：验证 URL
from django.utils.http import is_safe_url
next_url = request.GET.get('next', '/')
if is_safe_url(next_url, allowed_hosts=request.get_host()):
    return redirect(next_url)
```

#### 命令注入
```python
# ❌ 危险
os.system('ls ' + user_input)

# ✅ 安全：使用 subprocess.run 列表形式
subprocess.run(['ls'], shell=False)
```

### 🟡 中危：性能与规范

#### N+1 查询
```python
# ❌ 危险：循环内查询
for order in orders:
    print(order.user.name)  # 每个订单触发一次查询

# ✅ 安全：使用 select_related / prefetch_related
orders = Order.objects.select_related('user').all()
for order in orders:
    print(order.user.name)
```

#### 不当的异常处理
```python
# ❌ 危险：暴露敏感信息
except Exception as e:
    return HttpResponse(str(e))

# ✅ 安全：记录日志，返回通用错误
except Exception as e:
    logger.error(f"Error: {e}")
    return HttpResponse("Server error")
```

#### 缺少事务
```python
# ❌ 危险：多步操作无事务
def transfer(request):
    Account.objects.create(user=u1, balance=-100)
    Account.objects.create(user=u2, balance=+100)

# ✅ 安全：使用 transaction.atomic
from django.db import transaction
def transfer(request):
    with transaction.atomic():
        Account.objects.create(user=u1, balance=-100)
        Account.objects.create(user=u2, balance=+100)
```

#### 密码明文处理
```python
# ❌ 危险
user.password = password

# ✅ 安全：使用 make_password
from django.contrib.auth.hashers import make_password
user.password = make_password(password)
```

### 🟢 低危：代码规范

- 缺少 `__str__` 方法
- 未使用 bulk_create 批量操作
- 日志级别使用不当（生产环境用 DEBUG）
- 过长函数（>100行建议拆分）
