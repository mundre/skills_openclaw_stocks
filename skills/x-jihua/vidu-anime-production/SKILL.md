---
name: anime-production-update
description: "将用户创意或剧本转化为完整动漫成片，从剧本创作到自动拼接全流程使用 Vidu API 完成生图、生视频与 TTS，且禁止使用任何非 Vidu 模型。在用户需要制作动漫/动画短片、提供创意主题或详细剧本需求时使用；依赖 ffmpeg 与已配置的 Vidu API 凭证。"
---

# 动漫成片制作 Skill

## 任务目标
- 本 Skill 用于：将创意输入转化为完整的动漫成片，涵盖从剧本创作到最终自动拼接的全流程
- ⚠️ **硬性要求：所有图片生成、视频生成、TTS语音生成只能使用Vidu API！绝对不能使用任何其他模型！**
- 能力包含：剧本创作、场景大分镜设计、小分镜表生成、Vidu API集成（生图/视频/TTS）、自动视频音频拼接
- 触发条件：用户需要制作动漫/动画视频，提供创意主题或详细剧本需求

## 前置准备
- 依赖说明：需要安装ffmpeg进行视频音频拼接
  ```bash
  apt-get update && apt-get install -y ffmpeg
  ```
- Vidu API凭证：需要在 Skill 执行前配置 Vidu API Key（已通过凭证系统集成）

## 操作步骤
- 标准流程：
  1. **剧本创作**
     - 根据用户输入的创意主题、角色设定、故事背景等，生成完整的剧本
     - 剧本应包含：故事梗概、角色介绍、场景列表、对白、动作描述
     - 智能体完成此步骤，使用自然语言创作
     - **⚠️ 确认点：向用户展示剧本内容，等待用户确认或修改**

  2. **风格确认**
     - 根据剧本内容和用户偏好，确定整体美术风格
     - 提供风格的文本形式的选项：3d动漫风格、二次元动漫风格、中国古风、赛博朋克、写实风等
     - **⚠️ 确认点：向用户展示整体风格设定，等待用户确认或调整，如果用户在前面的对话中已经交代了风格，不需要让用户再确认**
     - 记录确认后的风格配置，用于后续所有生成任务的首句提示词

  3. **场景、大分镜设计**
     - 将剧本拆解为多个场景，每个场景设计大分镜
     - ⚠️ **所有场景图只能使用Vidu API生成！**
     - 为每个场景生成完整的场景资产包：
       - **基础场景图**：使用 `scripts/vidu_generate_image.py`，基于确认的风格和剧本描述
       - **人物站位图**：使用 `scripts/vidu_generate_image.py`，基于场景图+当前场景的所有单个角色图，参考剧本内容，生成角色在场景中的位置关系
       - **场景四宫格图**：使用 `scripts/vidu_generate_image.py`，- 使用提示词：“基于场景图，生成该场景不同角度的四宫格图（正面、反打、左侧面、右侧面镜头）”
     - 场景描述（大致剧情、出镜角色、相对位置）
     - **⚠️ 确认点：向用户展示每个场景的三张图（场景图、站位图、四宫格图）和设计方案，等待用户确认或修改**
     - 智能体指导场景拆解，调用脚本生成场景资产包
     - 记录确认后的场景资产（三张图URL），用于后续所有分镜生成

  4. **角色资产确认（含三视图检测）**
     - 检查用户上传的角色图是否是三视图
     - ⚠️ **如果不是三视图，只能使用Vidu API生成角色三视图！**
       - 使用 `scripts/vidu_generate_image.py`
       - 使用提示词："参考图角色，中心区域生成全身三视图以及一张面部特写（最左边占满三分之一的位置是超大的面部特写，右边三分之二放正视图、侧视图、后视图），角色比例适中，清晰可见。严格按照比例设定，包括身高对比和头身比，线条简洁明了，线条流畅自然，色彩搭配协调，保持整体风格统一和原图一致，背景与角色形成对比，视觉焦点集中在角色身上，确保角色比例准确，表情动作自然流畅，如果角色没有服装，服装设计需要符合角色背景，角色为自然站立状态，比例16:9"
       - 参考文档详见 [references/character-three-views.md](references/character-three-views.md)
     - ⚠️ **所有TTS只能使用Vidu API！**
     - 为每个角色匹配TTS音色（参考 [references/voice-list.md](references/voice-list.md)）
     - 为每个角色的音色生成试听音频（使用 `scripts/vidu_generate_audio.py`）
     - **⚠️ 确认点：向用户展示每个角色的三视图、音色名称和试听音频，等待用户确认或调整**
     - 记录确认后的角色资产配置（角色三视图URL + 音色ID）

  5. **资产整合**
     - 校验每个场景的资产完整性：
       - 角色图及对应音色（已确认，包含三视图）
       - 场景图（已确认，包含三张图）
       - 整体风格（已确认）
     - 输出镜头n的资产包（结构见 [references/storyboard-format.md](references/storyboard-format.md)）
     - 智能体完成资产校验与整理
     - **⚠️ 确认点：向用户展示完整的资产清单（角色、场景、风格），等待用户最终确认后进入生成阶段**

  6. **小分镜表生成**
     - 根据场景大分镜生成详细的小分镜表
     - 每个分镜包含：输入图（使用已确认的角色图、场景图、人物站位图、场景四宫格图）、分镜提示词、说话人、情绪、台词、时长
     - 在某场景下，每个分镜的输入图必须包含该场景人物站位图和该场景四宫格
     - 分镜提示词必须遵循规范：风格/景别/机位/构图/运镜 + 画面描述 + 图片强调
     - **特别注意**：
       - 若使用 **viduq3** 模型：提示词中必须包含台词内容，例如 "他说：'xxxx'"。
       - 图片强调必须参考人物站位图中的角色位置关系。
     - **特别注意**：对于双人对话镜头，必须参考 [references/camera-shots.md](references/camera-shots.md) 中的机位描述，选择合适的镜头类型（如内反拍、外反拍等）来丰富画面语言。
     - 风格部分使用已确认的整体风格词
     - 参考 [references/storyboard-format.md](references/storyboard-format.md) 中的格式规范
     - 智能体生成结构化的小分镜表
     - **⚠️ 确认点：向用户展示小分镜表（关键分镜的预览），等待用户确认或调整**

  7. **生成分段TTS**
     - ⚠️ **所有TTS只能使用Vidu API！**
     - **策略分支**：
       - **若使用 viduq3 模型**：跳过此步骤。viduq3 支持在生视频时直接生成对话和音效，无需单独生成TTS。
       - **若使用 viduq2 模型**：遍历小分镜表，为每个有台词的分镜生成语音。
         - 调用 `scripts/vidu_generate_audio.py`，传入：text（台词）、voice_id（已确认的音色）、emotion（情绪）
         - 脚本执行，返回音频文件URL

  8. **生成视频片段**
     - ⚠️ **所有视频只能使用Vidu API！**
     - **模型选择**：
       - **viduq3**（推荐）：支持长达16秒视频，支持**对话和音效生成**，提示词需包含台词。
       - **viduq2**：仅生成画面，需配合TTS使用。
     - 遍历小分镜表，为每个分镜生成视频片段
     - 调用 `scripts/vidu_generate_video.py`
       - 通用参数：images（参考图）、duration（时长）
       - **viduq3 特有参数**：model="viduq3"、audio=True、prompt（包含台词的提示词）
       - **viduq2 特有参数**：model="viduq2"、audio=False、prompt（仅画面描述）
     - 脚本执行返回task_id，使用 `scripts/vidu_query_task.py --task_id {task_id} --wait` 轮询等待任务完成
     - 智能体管理任务状态并收集视频片段
     - **⚠️ 确认点：每生成一个视频片段，向用户展示预览，等待用户确认后继续下一个**

  9. **根据剧情、时间轴自动拼接成片** (第9个确认点)
     - ⚠️ 我会直接执行：根据剧本剧情和小分镜表的时间轴，将生成的视频片段和语音文件整合，自动调用脚本进行拼接
     - 生成时间轴配置JSON（见 [references/timeline-config.md](references/timeline-config.md)）
     - 调用 `scripts/merge_video_audio.py` 拼接视频和音频，生成最终成片
     - 支持转场效果、背景音乐混合
     - **⚠️ 确认点：向用户展示拼接完成的成片，等待用户确认或调整**

  10. **最终交付**
      - 交付最终成片（MP4格式）
      - 交付时间轴配置文档
      - 提供素材清单（所有视频片段、音频片段的来源信息）

- 可选分支：
  - 当需要仅生图：**只能使用Vidu API！** 调用 `scripts/vidu_generate_image.py` 生成场景图，使用 `scripts/vidu_query_task.py --task_id {task_id} --wait` 获取结果
  - 当需要仅生视频：**只能使用Vidu API！** 调用 `scripts/vidu_generate_video.py` 生成视频片段，使用 `scripts/vidu_query_task.py --task_id {task_id} --wait` 获取结果
  - 当需要仅生语音：**只能使用Vidu API！** 调用 `scripts/vidu_generate_audio.py` 生成TTS语音（同步接口，直接返回结果）

## 资源索引
- 必要脚本：
  - [scripts/vidu_generate_image.py](scripts/vidu_generate_image.py)（用途：生成场景图，参数：prompt、images、aspect_ratio、resolution）
  - [scripts/vidu_generate_video.py](scripts/vidu_generate_video.py)（用途：生成视频片段，参数：images、videos、prompt、duration、model等）
  - [scripts/vidu_generate_audio.py](scripts/vidu_generate_audio.py)（用途：生成TTS语音，参数：text、voice_id、speed、volume、pitch、emotion）
  - [scripts/vidu_query_task.py](scripts/vidu_query_task.py)（用途：查询异步任务状态和结果，参数：task_id，支持--wait轮询）
  - [scripts/merge_video_audio.py](scripts/merge_video_audio.py)（用途：拼接视频和音频生成最终成片，参数：config、output）
- 领域参考：
  - [references/storyboard-format.md](references/storyboard-format.md)（何时读取：生成小分镜表时，包含分镜提示词编写规范）
  - [references/camera-shots.md](references/camera-shots.md)（何时读取：生成小分镜表时，处理双人对话镜头时参考）
  - [references/voice-list.md](references/voice-list.md)（何时读取：选择TTS音色时）
  - [references/async-task-flow.md](references/async-task-flow.md)（何时读取：处理Vidu异步任务时）
  - [references/asset-confirmation-flow.md](references/asset-confirmation-flow.md)（何时读取：处理资产确认流程时）
  - [references/timeline-config.md](references/timeline-config.md)（何时读取：生成时间轴配置和拼接视频音频时）
  - [references/scene-assets-generation.md](references/scene-assets-generation.md)（何时读取：生成场景资产包时）
  - [references/character-three-views.md](references/character-three-views.md)（何时读取：生成角色三视图时）

## 注意事项
- ⚠️ **绝对禁止使用任何非Vidu的图片、视频、TTS模型！所有生成任务只能使用Vidu API！**
- ⚠️ **视频模型支持 viduq3 和 viduq2！**
- 所有 Vidu API 调用需要配置 API Key 凭证，凭证已通过 skill_credentials 集成
- 小分镜表格式必须严格遵循 [references/storyboard-format.md](references/storyboard-format.md) 的规范
- **分镜提示词编写规范**：必须按三部分结构编写（风格/景别/机位/构图/运镜 + 画面描述 + 图片强调），详见参考文档
- **资产确认流程**：每个关键环节都需要用户确认，包括剧本、风格、角色图、音色试听、场景图、小分镜表、TTS音频、视频片段
- TTS 支持情绪控制，可根据台词内容自动选择合适的情绪
- 视频生成支持参考图和参考视频，建议使用场景图作为参考
- **生图、生视频为异步任务**：调用后获得task_id，需使用 `vidu_query_task.py --task_id {task_id} --wait` 轮询等待完成，结果URL有效期24小时
- TTS 为同步接口，直接返回音频文件 URL
- **风格一致性**：确认后的整体风格必须在所有后续生成任务中保持一致
- **角色一致性**：确认后的角色图必须在所有分镜中作为参考图使用
- **质量把控**：每个生成环节都需要用户确认后才进入下一环节，确保质量可控
- **⚠️ 我会直接执行拼接**：在视频音频拼接环节，我会直接调用脚本按时间轴拼接素材，不需要额外指导

## 使用示例

### 示例1：完整动漫短片制作
- 功能说明：从创意到成片的完整制作流程，包含所有确认环节，最终自动拼接成片
- ⚠️ **所有图片、视频、TTS只能使用Vidu API！**
- 执行方式：混合模式（智能体+脚本）
- 关键步骤：
  1. 用户输入："制作一个关于少年冒险的3分钟动漫短片"
  2. 智能体生成剧本 → **⚠️ 等待用户确认剧本**
  3. 智能体确定风格并使用Vidu API生成参考图 → **⚠️ 等待用户确认风格**
  4. 智能体使用Vidu API生成场景图 → **⚠️ 等待用户确认场景图**
  5. 智能体使用Vidu API生成角色图并匹配音色 → **⚠️ 等待用户确认角色图和音色试听**
  6. 智能体展示资产清单 → **⚠️ 等待用户最终确认**
  7. 智能体生成小分镜表 → **⚠️ 等待用户确认小分镜表**
  8. 调用 vidu_generate_audio.py 生成所有TTS语音 → **无需用户确认，直接下一步**
  9. 调用 vidu_generate_video.py 逐个生成视频片段（仅用viduq2）→ **⚠️所有片段生成完毕后等待用户确认**
  10. ⚠️ 我会直接执行：自动生成时间轴配置，调用 merge_video_audio.py 拼接成片 → **⚠️ 等待用户确认成片**
  11. 交付最终成片
