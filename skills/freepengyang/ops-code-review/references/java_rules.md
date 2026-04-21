# Java 代码审计专项规则

## 重点关注场景

### 🔴 高危：安全相关

#### SQL 注入
```java
// ❌ 危险：字符串拼接
String query = "SELECT * FROM users WHERE id=" + userId;
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery(query);

// ✅ 安全：预处理语句
String query = "SELECT * FROM users WHERE id=?";
PreparedStatement ps = conn.prepareStatement(query);
ps.setInt(1, userId);
```

#### 反序列化漏洞
```java
// ❌ 危险：反序列化不可信数据
ObjectInputStream ois = new ObjectInputStream(inputStream);
Object obj = ois.readObject();

// ✅ 安全：使用 JSON 替代，或使用安全的反序列化框架
ObjectMapper mapper = new ObjectMapper();
MyObject obj = mapper.readValue(jsonString, MyObject.class);
```

#### 命令注入
```java
// ❌ 危险
Runtime.getRuntime().exec("ls " + userInput);

// ✅ 安全：避免 shell 执行
ProcessBuilder pb = new ProcessBuilder("ls");
pb.start();
```

#### 敏感信息泄露
```java
// ❌ 危险：日志输出敏感信息
logger.info("Password: " + password);

// ✅ 安全：脱敏或避免记录
logger.info("User login attempt for: {}", username);
```

### 🟡 中危：异常处理

#### 空指针异常
```java
// ❌ 危险
String name = user.getName().toLowerCase();

// ✅ 安全：空值检查
String name = user.getName() != null ? user.getName().toLowerCase() : null;
```

#### 资源未关闭
```java
// ❌ 危险：资源泄漏
Connection conn = dataSource.getConnection();
ResultSet rs = stmt.executeQuery(query);

// ✅ 安全：try-with-resources
try (Connection conn = dataSource.getConnection();
     PreparedStatement ps = conn.prepareStatement(query);
     ResultSet rs = ps.executeQuery()) {
    // 使用
}
```

### 🟢 低危：性能与规范

- 循环内字符串拼接（应用 StringBuilder）
- 未使用批量操作（batch insert/update）
- 过长的方法（>50行建议拆分）
- 缺少 @Override 注解
- 魔法数字未定义为常量
