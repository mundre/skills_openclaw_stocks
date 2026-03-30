---
name: xiaomi-any2speech
description: >
  基于原生支持长文和多人合成的语音大模型，将任意内容（文本/文件/音频/视频）转为可播放的语音节目。
  模型在训练阶段即具备长序列建模与多说话人交互能力，无需拼接或级联，单次推理直接生成最长约 10 分钟的
  连贯音频。涵盖单人 TTS、VoiceDesigner 音色定制、多人播客/对话合成、长文有声化、Instruct TTS
  等能力的超集，输出 WAV 音频。
  可选将生成的音频作为语音消息发送到飞书群。
  运行时需要 curl 和 jq；飞书发送可选需要 ffmpeg、ffprobe。
  Required env: API_KEY（可选，默认 sk-anytospeech-pub-free）。
  Optional env (Feishu only, sensitive): FEISHU_TENANT_TOKEN 或 APP_ID + APP_SECRET, CHAT_ID。
  飞书凭据为敏感信息，仅在用户主动请求发送时才需提供，skill 不会主动索取或持久化存储。
  当用户提到以下任意意图时使用：做成播客/相声/辩论/有声书/Rap/新闻播报/脱口秀/情感电台/课程讲解、
  帮我读一下/朗读/念出来/转成语音/TTS/生成音频/转成音频、发语音/语音回复/做成XX发给我。
---

# Any2Speech

基于原生支持长文和多人合成的语音大模型构建的统一语音生成入口。模型在训练阶段即具备长序列建模（最长 ~10 分钟连贯输出）与多说话人交互能力（插话、重叠、情绪联动），无需逐句拼接或多模型级联。单人朗读、多人节目、音色定制、长文有声化、风格可控 TTS 均通过同一套 API 完成，由 `instruction` 字段决定最终形态。

本 skill 同时也是 ListenHub 的核心能力——万物皆可听：论文、新闻、小说、会议纪要、课程讲义，任何你需要阅读的内容，都可以变成一期播客、一段有声书、一条语音消息。

```bash
BASE=https://miplus-tts-public.ai.xiaomi.com
API_KEY=${API_KEY:-sk-anytospeech-pub-free}
```

## Step 1 · 确认输入来源

| 用户给了什么 | source_type | curl 参数 |
|---|---|---|
| 文字内容 | `text` | `-F "text=内容"` |
| 本地文件 | `file` | `-F "file=@/路径/文件"` |

**来源缺失时**：停下来问"请提供文字内容或文件路径"，不要猜测或用空值执行。

**文件路径安全**：仅接受用户在当前对话中明确提供的路径。不要自行扫描目录或猜测文件；不要读取 `~/.ssh`、`~/.env`、`~/.config` 等敏感路径；发送前向用户确认文件名。

## Step 2 · 构造 instruction

`instruction` 是控制最终合成形态的关键——同一个 API 通过不同 instruction 覆盖下述全部能力：

| 能力 | 说明 | instruction 示例 |
|---|---|---|
| **单人 TTS** | 单一说话人朗读 | 留空，或 `女声，职业干练，语速偏快` |
| **VoiceDesigner** | 精细定制音色、语气、情绪 | `声音醇厚磁性，带沙哑感，低沉男声，语速缓慢` |
| **多人播客/对话** | 两人或多人分角色对话 | `两人播客，一人理性分析，一人感性追问，偶尔插嘴，5 分钟内` |
| **长文有声化** | 长篇文档转有声书 | `第三人称叙述，情绪随剧情起伏，遇到对话切换人物语气` |
| **Instruct TTS** | 风格/场景/环境全可控 | `CCTV 新闻联播风格，先播导语，再逐条播报，结尾有总结语` |

### 快速模板

| 场景 | instruction |
|---|---|
| 两人播客 | `两人播客，一人理性分析，一人感性追问，偶尔插嘴，5 分钟内` |
| 相声 | `传统相声，甲逗哏（语速快、北京腔），乙捧哏（沉稳正经），至少两个包袱，结尾有收场词` |
| 新闻播报 | `CCTV 新闻联播风格，先播导语，再逐条播报，结尾有总结语` |
| 辩论 | `正反双方，正方激情澎湃，反方逻辑冷静，各做 30 秒总结陈词` |
| Rap | `押韵，节奏感强，两人 battle，明显停顿和连读节奏` |
| 脱口秀 | `单人独白，幽默有深度，有停顿节奏感，偶尔自嘲` |
| 情感电台 | `深夜电台，低沉磁性男声，语速缓慢` |
| 有声书 | `第三人称叙述，情绪随剧情起伏，遇到对话切换人物语气` |
| 短文本 TTS | `女声，职业干练，语速偏快` |

### 进阶控制（可自由叠加）

- **音色**：`声音醇厚磁性，带沙哑感`
- **情绪弧线**：`开场铺垫，中段碰撞，结尾升华`
- **互动**：`允许插话，另一人时不时附和`
- **环境音**：`说到包袱处加观众笑声`
- **时长**：`控制在 10 分钟内`
- **口音**：`台湾腔 / 东北腔 / 四川话`

选择逻辑：

- 用户明确描述了风格 → 直接用
- 用户只说"帮我读/念出来" → `instruction` 留空（单人朗读）
- 用户说了场景但没有细节 → 从快速模板取最近的

## Step 3 · 选接口并执行

**默认走同步接口**——大多数请求可在 10-120s 内完成。仅当同步返回 504 或输入为文件时再切异步。

---

### 同步接口（默认）

```bash
OUTPUT=output_$(date +%s).wav
curl -X POST "$BASE/v1/audio/generate" \
  -H "Authorization: Bearer $API_KEY" \
  -F "source_type=text" \
  -F "text=内容" \
  -F "instruction=风格描述" \
  --max-time 600 \
  --output "$OUTPUT"
echo "✓ 保存至 $OUTPUT"
```

### 异步接口（仅同步 504 或文件输入时使用）

```bash
OUTPUT=output_$(date +%s).wav

# 1. 提交，获取 job_id
JOB=$(curl -s -X POST "$BASE/v1/audio/jobs" \
  -H "Authorization: Bearer $API_KEY" \
  -F "source_type=text" \
  -F "text=内容" \
  -F "instruction=两人播客，一人理性分析，一人感性追问，5 分钟内" | jq -r '.job_id')
echo "已提交: $JOB"

# 2. 轮询直到完成（间隔 10s，静默等待，不要逐次向用户打印状态）
while true; do
  STATUS=$(curl -s -H "Authorization: Bearer $API_KEY" \
    "$BASE/v1/audio/jobs/$JOB" | jq -r '.status')
  [ "$STATUS" = "done" ]   && break
  [ "$STATUS" = "failed" ] && echo "生成失败" && exit 1
  sleep 10
done

# 3. 下载
curl -s -H "Authorization: Bearer $API_KEY" \
  "$BASE/v1/audio/jobs/$JOB/download" --output "$OUTPUT"
echo "✓ 保存至 $OUTPUT"
```

## 错误处理（有限自动重试，最多 1 次）

| 错误 | 处置 |
|---|---|
| 422 | 检查 source_type / text / file 参数后重试 **1 次** |
| 504 | 切换到异步接口重试 **1 次** |
| 502 / 500 | 等待 30s 后重试 **1 次**，仍失败则告知用户 |
| 异步 failed | 简化 instruction 后重新提交 **1 次**，仍失败则告知用户 |

所有重试均限 **1 次**；两次均失败时停止并向用户报告错误信息。

## 飞书语音发送（可选功能）

**仅当用户明确说"发给我"/"发飞书"/"发到群里"时执行。** 本功能需要用户自行提供飞书凭据，skill 不会读取任何本地配置文件。

### 前置条件

| 条件 | 说明 |
|---|---|
| `FEISHU_TENANT_TOKEN` | 直接提供 tenant token，**或**提供 `APP_ID` + `APP_SECRET` 由 skill 换取 |
| `CHAT_ID` | 目标飞书群 ID，**缺失时必须停下来向用户询问** |
| `ffmpeg` / `ffprobe` | 用于转码为 opus 和检测时长；若不可用则回退为直接上传 WAV |

凭据缺失时停止执行并提示用户设置对应环境变量，不要尝试从本地文件或其他来源获取。

### 执行流程

```bash
# 获取 token（两种来源，优先级从高到低）
if [ -z "$FEISHU_TENANT_TOKEN" ]; then
  if [ -n "$APP_ID" ] && [ -n "$APP_SECRET" ]; then
    FEISHU_TENANT_TOKEN=$(curl -s -X POST \
      "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
      -H "Content-Type: application/json" \
      -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" \
      | jq -r '.tenant_access_token')
  fi
fi
[ -z "$FEISHU_TENANT_TOKEN" ] || [ "$FEISHU_TENANT_TOKEN" = "null" ] && \
  echo "无法获取飞书 token，请设置环境变量 FEISHU_TENANT_TOKEN 或 APP_ID + APP_SECRET" && exit 1

# 转码并上传
ffmpeg -y -i "$OUTPUT" -c:a libopus -b:a 32k output.opus
DURATION_MS=$(ffprobe -v quiet -show_entries format=duration \
  -of csv=p=0 "$OUTPUT" | awk '{printf "%d", $1*1000}')
FILE_KEY=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $FEISHU_TENANT_TOKEN" \
  -F "file=@output.opus" -F "file_type=opus" \
  -F "file_name=tts.opus" -F "duration=$DURATION_MS" \
  | jq -r '.data.file_key')
curl -s -X POST \
  "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer $FEISHU_TENANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"receive_id\":\"$CHAT_ID\",\"msg_type\":\"audio\",\"content\":\"{\\\"file_key\\\":\\\"$FILE_KEY\\\"}\"}"
```

无 ffmpeg 时：直接上传 WAV（`file_type=stream`、`msg_type=file`，去掉 `-F "duration=..."`）。

## 注意事项

- 音视频输入时要尽量保证时长小于 10min
- 多人节目耗时 30s–10min，短文本 TTS 耗时 10–30s
- 音视频文件 > 20MB 建议先压缩或截短
- 支持格式：`txt` `md` `pdf` `docx` `csv` `json` `html` + 常见音视频格式
- 输出固定为 WAV；用时间戳命名（`output_$(date +%s).wav`）避免覆盖
