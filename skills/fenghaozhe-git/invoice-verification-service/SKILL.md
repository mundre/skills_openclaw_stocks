---
name: invoice-verification-service
description: 使用发票服务后端 v4 plugin 接口完成 appKey 初始化、套餐查询、额度查询、额度流水查询、文本核验、图片核验、目录批量核验、充值下单和订单状态查询。用户提到“发票核验”“图片核验”“批量核验目录”“给一个本地文件夹批量查发票”“剩余额度”“额度流水”“充值套餐”“有哪些套餐”“查套餐”“充值下单”“订单状态”“appKey 初始化/失效重绑”等需求时使用。
metadata: {"openclaw":{"tools":["shell","read_file"],"requires":{"bins":["node"]}}}
---

# Invoice Verification Service

## Overview

通过 `{baseDir}/scripts/invoice_service.js` 调用 `invoice-api-service` 的 v4 plugin 接口。
优先执行脚本，不要在对话里手写 HTTP 调用细节。

## Quick Start

先确认 Node.js 可用，然后按需执行：

```bash
node "{baseDir}/scripts/invoice_service.js" help
node "{baseDir}/scripts/invoice_service.js" config set --api-base-url http://localhost:18888
node "{baseDir}/scripts/invoice_service.js" init-key
node "{baseDir}/scripts/invoice_service.js" packages
node "{baseDir}/scripts/invoice_service.js" quota
node "{baseDir}/scripts/invoice_service.js" ledger --page 1 --page-size 20
node "{baseDir}/scripts/invoice_service.js" verify --text "发票代码 033002100611, 发票号码 12345678, 开票日期 2025-05-30, 金额 260.65, 校验码 123456" --format both
node "{baseDir}/scripts/invoice_service.js" verify-image --image-file C:\path\invoice.png --format both
node "{baseDir}/scripts/invoice_service.js" verify-directory --dir C:\path\invoice-images --format json
node "{baseDir}/scripts/invoice_service.js" create-order --amount 10
node "{baseDir}/scripts/invoice_service.js" query-order --order-no ORDER123456789
```

建议先执行一次 `init-key`。脚本也会在缺少 `appKey` 时自动调用 `/api/v4/plugin/key/init`。

## Workflow

1. 先配置 `apiBaseUrl`。如果本地还没有配置，先运行 `config set --api-base-url ...`。
2. 再执行目标动作。脚本会自动读取或初始化 `appKey`。
3. 如果接口返回 `INVALID_KEY` 或类似错误，脚本会自动清掉旧 key，重新初始化后再重试一次。
4. 对目录批量核验，优先使用 `verify-directory`，不要自己手写遍历逻辑。

## Supported Actions

### `config`

- `config show`
- `config set --api-base-url <url>`
- `config set --app-key <key>`
- `config set --client-instance-id <id>`
- `config set --device-fingerprint <id>`
- `config clear-app-key`

### `init-key`

初始化或重绑 `appKey`。

```bash
node "{baseDir}/scripts/invoice_service.js" init-key
node "{baseDir}/scripts/invoice_service.js" init-key --rotate-client-instance-id
```

### `quota`

查询剩余额度。

```bash
node "{baseDir}/scripts/invoice_service.js" quota
```

### `packages`

查询当前可选充值套餐。用户在聊天框里主动问“有哪些套餐”“充值套餐怎么选”时优先调用这个命令。

```bash
node "{baseDir}/scripts/invoice_service.js" packages
```

### `ledger`

查询额度流水。

```bash
node "{baseDir}/scripts/invoice_service.js" ledger --page 1 --page-size 20
```

### `verify`

文本核验。

```bash
node "{baseDir}/scripts/invoice_service.js" verify --text "<发票文本>" --format both
```

### `verify-image`

单张图片核验。`--text` 可选，用于补充提取字段。

```bash
node "{baseDir}/scripts/invoice_service.js" verify-image --image-file C:\path\invoice.png --format both
```

或：

```bash
node "{baseDir}/scripts/invoice_service.js" verify-image --image-base64 "<base64>" --mime-type image/png --text "<发票文本>"
```

### `verify-directory`

对本地目录下的发票图片逐张核验，并把 JSON 文件直接落到源目录下。

```bash
node "{baseDir}/scripts/invoice_service.js" verify-directory --dir C:\path\invoice-images --format json
```

可选参数：

- `--recursive true`：递归扫描子目录
- `--format json|base64|base64+json|both`
- `--text "<统一补充文本>"`：给所有图片附加同一段文本
- `--use-sidecar-text true|false`：是否读取同名 `.txt` 辅助文本，默认 `true`

目录批量核验的规则：

- 只扫描 `.png`、`.jpg`、`.jpeg`
- 如果目录里只有 1 张图片，直接在该目录生成 `<原文件名>.verify.json`
- 如果目录里有多张图片，在该目录下生成 `invoice-verify-results-<timestamp>` 文件夹
- 多图结果文件夹内会包含每张图片对应的 `*.verify.json` 和一个 `summary.json`
- 如果存在同名文本文件，例如 `001.png` 和 `001.txt`，脚本默认会把 `001.txt` 作为该图片的补充文本一起上送
- 某一张图片核验失败不会中断整批，失败结果也会写入对应 JSON

### `create-order`

创建充值订单并拿到支付二维码信息。

```bash
node "{baseDir}/scripts/invoice_service.js" create-order --amount 10
```

### `query-order`

查询订单状态。

```bash
node "{baseDir}/scripts/invoice_service.js" query-order --order-no ORDER123456789
```

## Response Handling

- 优先读取 JSON 中的 `ok`、`action`、`data`、`meta`
- 如果 `ok=false`，直接提炼 `error.message`、`error.code`、`error.status`
- 目录批量核验时，优先看 `summary.json`，再按需查看逐张结果 JSON

 - `create-order` 鍚庯紝浼樺厛浣跨敤 `data.paymentPageUrl` 浣滀负鏀粯鍏ュ彛锛岃繖鏄敮浠橀〉閾炬帴
 - `data.paymentPageUrl` 鎵撳紑鍚庡簲鐢ㄦ敮浠橀〉鑷閫夋嫨寰俊鎴栨敮浠樺疂
 - `data.qrCodeImageUrl` 鍙槸浜岀淮鐮佸浘鐗囬摼鎺ワ紝涓嶈浣滀负涓昏鏀粯鍏ュ彛

## Notes

- 配置文件路径是 `~/.openclaw/invoice-skill/config.json`
- 为兼容旧插件迁移，脚本也会读取 `~/.openclaw/invoice-plugin/config.json`
- 支付回调由后端内部接口 `/api/v4/internal/payment/callback` 处理，这个 skill 不直接调用回调接口
