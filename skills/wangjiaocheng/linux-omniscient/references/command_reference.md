# 系统控制命令速查

## 脚本位置

所有脚本位于：`scripts/`

---

## 1. window_manager.py - 窗口管理

### 列出所有可见窗口
```
python window_manager.py list
```
返回包含进程ID、标题和进程名的 JSON 数组。

### 激活（置于前台）
```
python window_manager.py activate --title "Notepad"
python window_manager.py activate --pid 1234
```

### 关闭窗口
```
python window_manager.py close --title "Untitled - Notepad"
python window_manager.py close --pid 1234
```

### 最小化 / 最大化
```
python window_manager.py minimize --title "Chrome"
python window_manager.py maximize --pid 1234
```

### 调整大小和移动
```
python window_manager.py resize --pid 1234 --x 100 --y 100 --width 800 --height 600
```

### 发送按键（SendKeys 格式）
```
python window_manager.py send-keys --title "Notepad" --text "Hello World"
```
SendKeys 特殊按键：`{ENTER}`, `{TAB}`, `{ESC}`, `{F1}`, `^(c)` 表示 Ctrl+C，`%(f)` 表示 Alt+F

---

## 2. process_manager.py - 进程管理

### 列出所有进程
```
python process_manager.py list
python process_manager.py list --name chrome
```

### 终止进程
```
python process_manager.py kill --name notepad
python process_manager.py kill --pid 1234
python process_manager.py kill --name chrome --force
```

### 启动进程
```
python process_manager.py start "notepad.exe"
python process_manager.py start "code" --dir "C:\Projects"
```

### 查看进程详情
```
python process_manager.py info --pid 1234
```

### 系统资源概览
```
python process_manager.py system
```

---

## 3. hardware_controller.py - 硬件控制

### 音量
```
python hardware_controller.py volume get
python hardware_controller.py volume set --level 75
python hardware_controller.py volume mute
```
注意：精确音量控制需要安装 NirCmd（nircmd.com）

### 屏幕亮度
```
python hardware_controller.py screen brightness
python hardware_controller.py screen brightness --level 50
```
适用于笔记本电脑屏幕和支持 DDC/CI 的显示器。

### 显示器信息
```
python hardware_controller.py screen info
```

### 电源管理
```
python hardware_controller.py power lock
python hardware_controller.py power sleep
python hardware_controller.py power hibernate
python hardware_controller.py power shutdown --delay 30
python hardware_controller.py power restart --delay 30
python hardware_controller.py power cancel
```

### 网络
```
python hardware_controller.py network adapters
python hardware_controller.py network enable --name "Wi-Fi"
python hardware_controller.py network disable --name "Ethernet"
python hardware_controller.py network wifi
python hardware_controller.py network info
```

### USB 设备
```
python hardware_controller.py usb list
```

---

## 4. serial_comm.py - 串口通信

### 列出串口
```
python serial_comm.py list
```

### 自动检测波特率
```
python serial_comm.py detect --port COM3
```

### 发送数据
```
python serial_comm.py send --port COM3 --data "LED_ON" --baud 9600
```

### 接收数据
```
python serial_comm.py receive --port COM3 --baud 9600 --timeout 5
```

### 发送并等待响应
```
python serial_comm.py chat --port COM3 --data "GET_TEMP" --baud 9600
```

### 监听模式（实时）
```
python serial_comm.py monitor --port COM3 --baud 9600 --duration 30
```

依赖：`pip install pyserial`（首次使用时自动安装）

---

## 5. iot_controller.py - 物联网 / 智能家居

### Home Assistant
```
# 列出所有实体
python iot_controller.py homeassistant --url http://192.168.1.100:8123 --token YOUR_TOKEN list

# 查看实体状态
python iot_controller.py homeassistant --url http://192.168.1.100:8123 --token YOUR_TOKEN state --entity-id light.living_room

# 开启/关闭/切换
python iot_controller.py homeassistant --url http://192.168.1.100:8123 --token YOUR_TOKEN on --entity-id light.living_room
python iot_controller.py homeassistant --url http://192.168.1.100:8123 --token YOUR_TOKEN off --entity-id light.living_room
python iot_controller.py homeassistant --url http://192.168.1.100:8123 --token YOUR_TOKEN toggle --entity-id switch.fan

# 调用服务并传参
python iot_controller.py homeassistant --url http://192.168.1.100:8123 --token YOUR_TOKEN on --entity-id light.living_room --data '{"brightness_pct": 50, "color_temp": 350}'

# 调用任意服务
python iot_controller.py homeassistant --url http://192.168.1.100:8123 --token YOUR_TOKEN call --domain climate --service set_temperature --entity-id climate.bedroom --data '{"temperature": 24}'
```

### 通用 HTTP/REST
```
# GET 请求
python iot_controller.py http --url http://192.168.1.50:8080 get --path /api/status
python iot_controller.py http --url http://192.168.1.50:8080 get --path /api/data --header "Authorization: Bearer TOKEN"

# POST 请求
python iot_controller.py http --url http://192.168.1.50:8080 post --path /api/command --body '{"action":"on"}'

# PUT 请求
python iot_controller.py http --url http://192.168.1.50:8080 put --path /api/config --body '{"name":"updated"}'
```

### 米家 / 小米
```
python iot_controller.py mijia discover
```
需要：`pip install miio`（需手动安装）

依赖：`pip install requests`（首次使用时自动安装）

---

## 常用场景

### Arduino 灯光控制
1. 通过 USB 连接 Arduino
2. 列出端口：`python serial_comm.py list`
3. 发送指令：`python serial_comm.py send --port COM3 --data "LED_ON" --baud 9600`
4. 读取传感器：`python serial_comm.py chat --port COM3 --data "READ_TEMP" --baud 9600`

### 智能家居自动化
1. 列出灯光：`python iot_controller.py homeassistant --url ... --token ... list`
2. 开灯：`python iot_controller.py homeassistant --url ... --token ... on --entity-id light.bedroom`
3. 调亮度：`python iot_controller.py homeassistant --url ... --token ... on --entity-id light.bedroom --data '{"brightness_pct":30}'`

### 应用自动化
1. 查找窗口：`python window_manager.py list`
2. 激活：`python window_manager.py activate --title "Excel"`
3. 发送输入：`python window_manager.py send-keys --title "Excel" --text "^(s)"`（Ctrl+S）
4. 关闭：`python window_manager.py close --title "Excel"`

---

## 6. gui_controller.py - 图形界面自动化

### 鼠标控制
```
python gui_controller.py mouse position
python gui_controller.py mouse move --x 500 --y 300 [--duration 0.3]
python gui_controller.py mouse click [--x 500] [--y 300]
python gui_controller.py mouse right-click [--x 500] [--y 300]
python gui_controller.py mouse double-click [--x 500] [--y 300]
python gui_controller.py mouse drag --start-x 100 --start-y 200 --end-x 500 --end-y 400 [--duration 0.5]
python gui_controller.py mouse scroll [--x 500] [--y 300] [--clicks 5] [--direction up|down]
```
注意：坐标为屏幕绝对坐标，不指定时使用鼠标当前位置。

### 键盘控制
```
python gui_controller.py keyboard type --text "Hello World"
python gui_controller.py keyboard press --keys "ctrl+c"
python gui_controller.py keyboard press --keys "alt+tab"
python gui_controller.py keyboard key-down --key shift
python gui_controller.py keyboard key-up --key shift
```
`press` 支持单键（如 `enter`、`esc`）和多键组合（如 `ctrl+shift+esc`）。

### 截图
```
python gui_controller.py screenshot full
python gui_controller.py screenshot active-window
python gui_controller.py screenshot region --x 0 --y 0 --width 800 --height 600
python gui_controller.py screenshot list
python gui_controller.py screenshot size
```

### 视觉识别 / OCR
```
python gui_controller.py visual ocr [--x 0] [--y 0] [--width 1920] [--height 1080] [--lang chi_sim+eng]
python gui_controller.py visual find --template "icon.png" [--confidence 0.9]
python gui_controller.py visual click-image --template "button.png" [--confidence 0.9] [--offset-x 0] [--offset-y 0]
python gui_controller.py visual find-color --color "#FF0000" [--x 0] [--y 0] [--width 1920] [--height 1080]
python gui_controller.py visual pixel --x 100 --y 200
```
- `ocr`：默认全屏识别，支持中英文混合（`chi_sim+eng`）
- `find`/`click-image`：模板图像可在截图目录或 `assets/` 子目录下搜索，支持相对路径
- `find-color`：在指定区域（或全屏）内按颜色查找像素，支持十六进制颜色（如 `#FF0000`）
- `pixel`：获取指定坐标像素的 RGB 和十六进制颜色值

依赖：`pip install pyautogui pillow`（首次使用时自动安装）
OCR 依赖：`pip install pytesseract`（可选，需要 Tesseract 引擎并配置语言包）

