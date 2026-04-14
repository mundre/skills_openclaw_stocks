# 发布流程

## 固定顺序

1. 读取本地配置文件
2. 检查配置文件被 Git 忽略
3. 对齐版本号和发布元数据
4. 运行 `scripts/release_guard.py`
5. 如果是 plugin，再发布 npm
6. 发布 ClawHub
7. 回读 npm / ClawHub 结果
8. 若最新版本仍是 `suspicious` / `flagged`，立刻修复、递增版本、重新发布

## 闭环停止条件

只有同时满足以下条件才能结束：

- `clawhub inspect <slug>` 已经指向最新版本
- 页面版本已经更新到最新版本
- 页面或页面内嵌数据里不再出现 `suspicious` / `flagged`
- `staticScan.status = clean`

如果只是页面还在 `pending`，可以等待。

如果已经确认同一版本还是 `suspicious` / `flagged`：

- 不要继续无意义轮询
- 必须切换到修复动作
- 修复后递增版本再发布

## ClawHub 固定动作

每次发布前都执行：

```bash
clawhub logout
clawhub login
clawhub whoami
```

## 为什么要临时发布目录

直接发布仓库根目录，经常会把这些内容带上去：

- `.npmrc`
- `.env`
- `*.tgz`
- 本地配置
- 本地 IDE / Claude / Codex 配置

所以发布前要按白名单复制到临时目录，只上传必要文件。

## npm 复核

发布前：

```bash
npm whoami
npm pack --dry-run
```

发布后：

```bash
npm view <package-name> version dist-tags --json
```

## ClawHub 复核

发布后同时看：

```bash
clawhub inspect <slug>
curl -L -A 'Mozilla/5.0' -s https://clawhub.ai/<owner>/<slug>
```

原因：

- CLI 往往比网页更快反映最新版本
- 网页可能有缓存
- 有时页面还是旧扫描结果，但页面内嵌数据已经是新版本
- 一旦确认最新版本仍然可疑，就别继续重复检查，直接修
