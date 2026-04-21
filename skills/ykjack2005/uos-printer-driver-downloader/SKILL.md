---
name: uos-printer-driver-downloader
description: 本技能用于从统信UOS驱动中心搜索并下载打印机驱动程序。技能包含多个Python脚本，提供分离式和一体化两种使用方式。
---

# 打印机驱动下载技能

## 技能描述

本技能用于从统信UOS驱动中心搜索并下载打印机驱动程序。技能包含多个Python脚本，提供两种使用方式：
1. **分离式**：先搜索保存列表，再选择下载（适合需要反复选择对比的场景）
2. **一体化**：搜索下载一键完成（适合命令行和快速下载）

## 技能组成

### 脚本文件

#### 1. list_printers.py - 打印机驱动搜索脚本
- **功能**：搜索打印机驱动并以表格形式展示所有结果
- **输出**：自动保存所有搜索结果到 `driver_list.json` 文件
- **特点**：
  - 分离式工作流的第一步，保存结果供后续下载
  - **支持命令行参数**：`python list_printers.py LJ2405`
  - 不传参数时保持交互式输入

#### 2. download_driver.py - 打印机驱动下载脚本
- **功能**：从 `driver_list.json` 加载驱动列表，让用户选择后下载
- **输出**：下载的驱动程序文件（.deb 格式）到桌面
- **特点**：分离式工作流的第二步，默认保存到桌面

#### 3. download_printer.py - 一体化打印机驱动下载脚本
- **功能**：搜索并下载一体化，支持命令行参数
- **用法**：`python download_printer.py <打印机型号> [下载目录] [--arch <架构>]`
- **示例**：
  - `python download_printer.py "联想 LJ2405" /Users/yangkaijian/Desktop`
  - `python download_printer.py "联想 LJ2405" /Users/yangkaijian/Desktop --arch arm64`
- **特点**：
  - 支持命令行参数，适合自动化
  - 自动优先选择指定架构驱动（默认 `amd64`，可通过 `--arch` 修改，如 `arm64`、`all`）
  - 单个驱动时自动下载，多个时支持交互式选择
  - 自动处理两层下载逻辑（先获取OSS临时链接，再下载真实 `.deb` 文件）

## 使用方法

### 前提条件

确保已安装以下依赖：

```bash
pip install requests
```

### 方式一：分离式使用（推荐用于对比选择）

#### macOS 系统

```bash
# 步骤一：搜索并保存驱动列表（交互式）
/opt/miniconda3/bin/python3 list_printers.py

# 或直接用命令行参数搜索
/opt/miniconda3/bin/python3 list_printers.py LJ2405

# 步骤二：选择并下载驱动
/opt/miniconda3/bin/python3 download_driver.py
```

#### 统信 UOS 系统

```bash
# 步骤一：搜索并保存驱动列表（交互式）
python3 list_printers.py

# 或直接用命令行参数搜索
python3 list_printers.py LJ2405

# 步骤二：选择并下载驱动
python3 download_driver.py
```

### 方式二：一体化使用（推荐用于快速下载）

```bash
# macOS（默认优先 amd64）
/opt/miniconda3/bin/python3 download_printer.py "联想 LJ2405" /Users/yangkaijian/Desktop

# 指定 arm64 架构
/opt/miniconda3/bin/python3 download_printer.py "联想 LJ2405" /Users/yangkaijian/Desktop --arch arm64

# 统信 UOS（默认优先 amd64）
python3 download_printer.py "联想 LJ2405" ~/Desktop

# 指定 arm64 架构
python3 download_printer.py "联想 LJ2405" ~/Desktop --arch arm64
```

### 交互说明

**分离式 - 步骤一**（搜索并保存驱动列表）：
- 输入打印机型号关键词（如 `1102`、`hp`、`canon` 等）
- 查看搜索结果表格
- 所有结果自动保存到 `driver_list.json`

**分离式 - 步骤二**（选择并下载驱动）：
- 脚本自动读取 `driver_list.json` 文件
- 显示可下载的驱动列表
- 输入序号选择要下载的驱动
- 输入 `y` 确认下载，或 `n` 取消

**一体化**（搜索并直接下载）：
- 自动搜索指定型号的驱动
- 如果只有一个结果，直接下载
- 如果有多个结果，优先选择 `--arch` 指定的架构（默认 `amd64`），未匹配时支持交互式选择
- 自动下载到指定目录（默认为当前目录）

## 输出说明

### 表格格式

搜索结果和选择列表都以以下格式显示：

```
序号   | 架构       | 驱动型号 (Model)                              | 版本 (Version)    | 包名 (Package)
------ | ---------- | -------------------------------------------- | ----------------- | ---------------
1      | amd64      | HP LaserJet Pro MFP M125nw                   | 1.0.5             | hplip
2      | arm64      | HP LaserJet Pro MFP M126nw                   | 1.0.6             | hplip
```

### 保存文件格式

`driver_list.json` 文件内容示例（驱动列表格式）：

```json
[
  {
    "deb_id": "12345",
    "driver_id": "67890",
    "package": "hplip",
    "model": "HP LaserJet Pro MFP M125nw",
    "arch": "amd64",
    "version": "1.0.5"
  },
  {
    "deb_id": "12346",
    "driver_id": "67891",
    "package": "hplip",
    "model": "HP LaserJet Pro MFP M126nw",
    "arch": "amd64",
    "version": "1.0.6"
  }
]
```

### 下载文件命名

驱动物件文件命名格式：`{package}_{version}_{arch}.deb`

例如：`hplip_1.0.5_amd64.deb`

## 常见问题

### Q1：搜索不到需要的打印机驱动怎么办？

- 尝试使用不同的关键词（如型号的一部分、厂商名称等）
- 检查关键词拼写
- 确认打印机确实支持UOS/统信系统

### Q2：下载失败怎么办？

- 检查网络连接
- 确认 `driver_list.json` 文件存在且内容正确
- 尝试重新运行 `list_printers.py` 重新搜索

### Q3：如何下载多个不同的驱动？

- **分离式**：每次下载新驱动前，重新运行 `list_printers.py` 搜索新驱动，这会覆盖 `driver_list.json` 文件
- **一体化**：直接多次运行 `download_printer.py` 指定不同型号

### Q4：下载的文件保存在哪里？

- `download_driver.py`：默认保存到桌面（`/Users/yangkaijian/Desktop`）
- `download_printer.py`：默认保存到当前目录，可通过第二个参数指定目录

### Q5：三种脚本如何选择？

| 场景 | 推荐脚本 |
|------|----------|
| 需要对比多个驱动后再选择 | `list_printers.py` + `download_driver.py` |
| 快速下载，知道具体型号 | `download_printer.py` |
| 批量自动化下载 | `download_printer.py` |

## API 信息

本技能使用统信UOS官方驱动中心API：

- 搜索API：`https://www.chinauos.com/driver-api/v1/driver/query/list`
- 下载API：`https://www.chinauos.com/driver-api/v1/driver/download`

## 技术细节

### API 参数说明

搜索接口参数：
- `keyword`：搜索关键词
- `source`：数据源标识（固定值：`2`）
- `pageIndex`：页码
- `pageSize`：每页数量

下载接口参数：
- `deb_id`：DEB包ID
- `driver_id`：驱动ID

### 下载流程

统信驱动中心的下载 API 采用**两层下载逻辑**：
1. 向 `driver-api/v1/driver/download` 发送请求，获取包含真实 OSS 临时签名链接的 JSON
2. 解析 JSON 中的 `data.url`，再请求该链接下载真实的 `.deb` 驱动文件

脚本已自动处理该流程，确保下载的是有效的 Debian 安装包。

### 错误处理

脚本包含以下错误处理：
- 网络连接超时（10秒搜索 / 60秒下载）
- HTTP错误状态码
- 文件写入错误
- JSON解析错误
- 序号超出范围

## 适用场景

- 在统信UOS系统上安装打印机驱动
- 批量搜索并筛选打印机驱动
- 离线环境下的驱动预下载
- 驱动版本管理与归档

## 注意事项

1. 本技能仅适用于统信UOS系统或兼容其驱动包的Linux发行版
2. 下载的驱动文件为 `.deb` 格式，适用于Debian/Ubuntu等系统
3. 建议在下载前确认打印机型号与驱动版本的兼容性
4. 脚本运行需要互联网连接
5. 存储空间需预留足够的驱动物件大小（通常10-50MB）
6. `driver_list.json` 文件包含完整的驱动信息（deb_id 和 driver_id），请妥善保存
