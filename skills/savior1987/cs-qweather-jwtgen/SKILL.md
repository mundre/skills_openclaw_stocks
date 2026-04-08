# cs-qweather-jwtgen

和风天气 JWT Token 生成工具。

## 使用场景

当需要生成和风天气 API 的 JWT 认证 Token 时使用此 skill。

## 功能

- 使用 EdDSA 算法生成 JWT Token
- 自动保存 token 到 `~/.myjwtkey/last-token.dat`
- 日志输出到 `/tmp/cslog/generateJWTtoken-YYYYMMDD.log`

## 依赖

- Python 3
- `pyjwt` 库（`pip install pyjwt`）

## 环境变量

- `QWEATHER_SUB` - 和风账户的用户标识（sub 字段）
- `QWEATHER_KID` - 和风账户的密钥 ID（kid 字段）

## 私钥文件

私钥文件必须位于 `~/.myjwtkey/ed25519-private.pem`

## 使用方法

```bash
python3 qweather-jwtgen/scripts/generateJWTtoken.py
```

## 输出

- JWT Token 输出到 stdout
- Token 同时保存到 `~/.myjwtkey/last-token.dat`
- 日志写入 `/tmp/cslog/generateJWTtoken-YYYYMMDD.log`

## 注意事项

- Token 有效期为 24 小时（exp = iat + 84000 秒）
- 私钥文件权限应为 600（仅本人可读写）
- 日志中敏感信息已脱敏（sub、kid、JWT token）
