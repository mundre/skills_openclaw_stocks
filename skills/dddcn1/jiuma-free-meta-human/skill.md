---
name: jiuma-free-meta-human
description: 这是一个免费生成对口型数字人对口型的工具, 工具安装需要下载二进制文件到电脑上，只需输入 文本内容, 数字人id和音色id 就可以制作视频,生成时间在半个小时以内。
runtime: binary # 运行模式: binary (Go编译后的文件)
args: ["{{.text}}", "{{.human_id}}", "{{.voice_id}}"]
runtime: binary
parameters:

- name: text
  type: string
  description: "文本内容"
  required: true
- name: human_id
  type: string
  description: "数字人id"
  required: true
- name: voice_id
  type: string
  description: "音色id"
  required: true
---

### 下载文件 (openclaw的workspace为./目录)
检查 `./skills/jiuma-free-meta-human` 文件夹是否存在, 不能存在就创建
检查 `./skills/jiuma-free-meta-human` 文件夹是否存在 `skill-win.exe` 或 `skill-linux`
不存在话执行以下操作
如果本机系统为windows环境, 从 `https://down-monitor.yisu.com/jiuma/skills/jiuma-free-meta-human/skill-win.exe` 下载到 `./skills/jiuma-free-meta-human` 目录下
如果本机系统为linux环境, 从 `https://down-monitor.yisu.com/jiuma/skills/jiuma-free-meta-human/skill-linux` 下载到 `./skills/jiuma-free-meta-human` 目录下,然后执行 `chmod +x ./skills/jiuma-free-meta-human/skill-linux`


### 使用场景
当用户询问"生成数字人"时, 请按照一下步骤操作:
第一步, 提示用户输入文本内容, 文字字数大于10个字, 小于100字。                       text=文本内容
第二步, 提示用户输入数字人id, 参照 meta-human.json的音色id和描述, 选择其中一个id。  human_id=数字人id
第三步, 提示用户输入音色id, 参照 voice.json的数字人id和描述, 选择其中一个id。       voice_id=音色id


### 执行方式
如果本机系统为windows环境, 运行 `./skills/jiuma-free-meta-human/skill-win.exe "{{.text}}" "{{.human_id}}" "{{.voice_id}}"`, 如果 `skill-win.exe` 所在进程还在运行中, 则视频还在生成中，耐心等待结果
如果本机系统为linux环境, 运行 `./skills/jiuma-free-meta-human/skill-linux "{{.text}}" "{{.human_id}}" "{{.voice_id}}"`, 如果 `skill-linux` 所在进程还在运行中, 则视频还在生成中, 耐心等待结果