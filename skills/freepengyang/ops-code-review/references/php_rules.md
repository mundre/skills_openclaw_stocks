# PHP 代码审计专项规则

## 重点关注场景

### 🔴 高危：安全相关

#### 命令注入
```php
// ❌ 危险
system("ls " . $_GET['dir']);

// ✅ 安全：escapeshellarg
system("ls " . escapeshellarg($_GET['dir']));
// 或避免 shell 执行，使用 PHP 原生函数
```

#### SQL 注入
```php
// ❌ 危险：字符串拼接
$query = "SELECT * FROM users WHERE id=" . $_GET['id'];

// ✅ 安全：预处理语句
$stmt = $pdo->prepare("SELECT * FROM users WHERE id=:id");
$stmt->execute(['id' => $_GET['id']]);
```

#### 文件包含漏洞
```php
// ❌ 危险：用户输入控制文件路径
include($_GET['page'] . '.php');

// ✅ 安全：白名单
$allowed = ['home' => 'home.php', 'about' => 'about.php'];
$page = $allowed[$_GET['page']] ?? 'home.php';
include($page);
```

#### 反序列化漏洞
```php
// ❌ 危险：反序列化用户输入
$data = unserialize($_COOKIE['user_data']);

// ✅ 安全：避免反序列化，或使用 json_decode
$data = json_decode($_COOKIE['user_data'], true);
```

#### 路径遍历
```php
// ❌ 危险
$file = $_GET['file'];
readfile("/var/www/uploads/" . $file);

// ✅ 安全：realpath 验证
$file = basename($_GET['file']);  // 去掉路径
readfile("/var/www/uploads/" . $file);
```

#### XSS
```php
// ❌ 危险：直接输出
echo $_GET['name'];

// ✅ 安全：htmlspecialchars
echo htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8');
```

### 🟡 中危：会话与认证

#### Session 安全
```php
// ❌ 危险：session fixation
session_start();

// ✅ 安全：session  Regenerate
session_start();
session_regenerate_id(true);
```

#### 密码明文存储
```php
// ❌ 危险
$password = $_POST['password'];

// ✅ 安全：password_hash / password_verify
$hash = password_hash($password, PASSWORD_DEFAULT);
if (password_verify($password, $stored_hash)) { ... }
```

#### 敏感信息泄露
```php
// ❌ 危险：生产环境显示错误
ini_set('display_errors', 1);

// ✅ 安全
ini_set('display_errors', 0);
error_log("/var/log/php_errors.log");
```

### 🟢 低危：代码规范

- 缺少 `declare(strict_types=1)`
- 使用 `==` 而非 `===` 比较
- 缺少异常处理（try-catch）
- 过长函数（>100行建议拆分）
- 缺少常量定义，使用魔法数字
