# authorize — 媒体账号 OAuth 授权

> 为尚未绑定或 Token 已失效的媒体账号发起 OAuth 授权，在浏览器中完成授权后自动跳回账号管理页。

---

## 用法

```bash
siluzan-cso authorize --media-type YouTube
siluzan-cso authorize --media-type TikTokBusinessAccount   # TikTok（注意不是 TikTok）
siluzan-cso authorize --media-type Instagram
siluzan-cso authorize --media-type Facebook
siluzan-cso authorize --media-type LinkedIn
siluzan-cso authorize --media-type Twitter    # X（推特）
```

命令执行后会自动在系统默认浏览器中打开授权页，用户在浏览器中完成操作后跳回账号管理页即可。

---

## 支持的平台

| 用户说法 | `--media-type` 参数值 | 备注 |
|----------|----------------------|------|
| YouTube | `YouTube` | |
| TikTok | `TikTokBusinessAccount` | ⚠️ 必须用这个值，传 `TikTok` 会跳到错误的授权页 |
| Instagram / IG | `Instagram` | |
| Facebook / FB | `Facebook` | |
| LinkedIn | `LinkedIn` | |
| Twitter（即 X / 推特，同一平台） | `Twitter` | Twitter 已更名为 X，前端显示为"X"，但 API 参数固定为 `Twitter` |


---

## 何时需要重新授权

以下情况需要对账号重新执行 `authorize`：

- `list-accounts --json` 输出中 `invalidOAuthToken: true`
- `list-accounts` 显示账号状态为"异常"或"已过期"
- 发布任务失败，错误原因为 Token 失效

---

## 交叉引用

- 查看账号 Token 状态 → 参见 `references/list-accounts.md`
- 重新发布失败的任务项 → 参见 `references/task.md`
