---
name: "Oasis Audio"
description: "AI audio narration generator that mines your OpenClaw/QClaw/EasyClaw conversation history to create truly personalized audio. Infers your current emotional state, interests, and context to tailor content, tone, and depth. Includes 9 reference modes (Soul Healing, Daily Briefing, Knowledge Deep Dive, Content Digest, Bedtime Radio, Language Learning, Conversation Extension, Topic Tracker, Study Buddy) but freely creates custom audio profiles when your need doesn't fit a template. Generates single-narrator audio (monologue with BGM). Use this skill when the user asks to 'make audio', 'generate audio', 'generate a podcast', 'turn this into audio', or when conversation context suggests audio would be valuable. Supports Chinese & English."
metadata:
  openclaw:
    emoji: "🎧"
    requires:
      bin:
        - python3
---

# Instructions
This skill provides **AI audio narration generation** using xplai.ai service.

Zero Config. No API Key required. Just install and run.

Official website: [www.xplai.ai](https://www.xplai.ai/)

When calling this skill, ALWAYS spawn a subagent to poll for results. Do not make the user wait manually. After calling `xplai_gen_audio.py`, immediately start polling with `xplai_status.py` in a loop - check once every 60 seconds, maximum 15 checks (up to 15 minutes). Stop polling when the status becomes `v_succ` or `v_fail`. Report the final result to the user automatically.

## User Need Inference

**The user's actual need always takes priority over predefined modes.** The 9 Audio Modes below are reference templates, not categories to force-fit into. Many real requests won't match any mode — that's fine.

Before generating audio, use conversation context and memory to infer the user's **true need** along 4 dimensions:

### 1. What does the user actually want to hear?

Don't just read the literal request. Infer the deeper need:

| User says | Literal reading | Deeper need |
|-----------|----------------|-------------|
| "最近好焦虑" | Anti-anxiety content | Something that addresses their specific anxiety source (found in context), not generic meditation |
| "帮我做个关于咖啡的音频" | Coffee knowledge | Calibrated to what they already know (beginner vs. expert, found in context) |

### 2. What tone fits their current state?

Read context signals to determine emotional tone:

| Signal (from context) | Inferred tone |
|-----------------------|---------------|
| Recent high-stress conversations (deadlines, conflicts) | Warm, validating, slow-paced |
| Curious exploration (asking lots of questions about a topic) | Engaging, enthusiastic, rich in detail |
| Boredom / routine complaints ("每天都一样") | Surprising, stimulating, perspective-shifting |
| Excitement about something new | Match their energy, build on the enthusiasm |
| Post-achievement ("终于搞定了") | Celebratory first, then reflective |

### 3. What depth and duration fit?

Use context to calibrate:
- **Cognition level**: If user has been deeply discussing a topic, go deeper. If it's new to them, start accessible.
- **Available attention**: Late night → shorter, lighter. Commute time → mid-length. Weekend afternoon → can go longer and deeper.
- **Repetition tolerance**: If the user has asked about similar topics before, don't repeat basics — build on what they already know.

### Custom Mode

When the user's request doesn't fit any of the 9 predefined modes, create a **custom audio profile** on the fly:

1. **Name it**: Give the audio a descriptive working title based on the user's need (e.g., "赶完DDL后的温柔复盘", "给未来的自己的一封信")
2. **Define content structure**: Based on the inferred need, not a template. For example:
   - "Post-DDL comfort" → acknowledge the struggle → validate the effort → gentle humor about the process → look forward
   - "Career crossroads reflection" → frame the situation → explore both sides → offer perspective → end with grounding
3. **Set voice/pacing**: Warm and slow for emotional needs, energetic for excitement, conversational for exploration

---

## Personalized Context Collection

Before preparing text for audio generation, mine the user's conversation history to personalize the audio. Follow these steps in order. If any step yields no results, skip to Text Preparation Rules and generate without personalization — do NOT fabricate personal context.

### Step 0: Detect Source Tool

Determine which OpenClaw-ecosystem tool the user is running from:
1. Check conversation metadata for `source_tool` field
2. If not available, auto-detect by checking which paths exist on disk:
   - `~/.qclaw/agents/main/sessions/` has files → `qclaw`
   - `~/.easyclaw/agents/main/sessions/` has files → `easyclaw`
   - `~/.openclaw/agents/main/sessions/` has files → `openclaw`
3. If multiple exist, prefer the one with the most recently modified session file
4. If none exist, skip personalization entirely

### Step 1: Scene Classification

Classify the user's audio request into exactly ONE of these scene types (use `functional` or `no_context` to skip personalization):

| Scene | Label | When to Apply | Search Action | Days |
|-------|-------|---------------|---------------|------|
| `event` | 有明确事件 | User describes a specific event (finished DDL, moved house, got promoted) | Full story extraction | 3 |
| `emotion_only` | 只有情绪 | User expresses mood without naming an event ("感觉很丧", "需要治愈") | Search high-emotion fragments | 3 |
| `future` | 面向未来 | User talks about upcoming plans/worries ("明天面试", "下周答辩") | Search preparation context | 7 |
| `long_term` | 长期状态 | User describes ongoing state ("每天带娃好累", "一直加班") | Search recurring topics | 30 |
| `interest` | 纯兴趣 | User wants audio on a hobby/knowledge topic ("咖啡豆科普") | Light search for cognition level | 14 |
| `functional` | 功能性 | Pure utility: white noise, pomodoro, generic podcast | **SKIP** — go directly to Text Preparation | — |
| `no_context` | 无上下文 | No personal angle, or first interaction | **SKIP** — go directly to Text Preparation | — |
| `sensitive` | 敏感话题 | Health, finances, relationships, legal issues | Extract emotion tone ONLY, never quote specifics | 3 |
| `weekly_review` | 周回顾 | User wants a recap of their past week's conversations, activities, or progress | Multi-topic extraction across all sessions | 7 |

### Step 2: Keyword Fan-out

Generate search keywords in 3 layers based on the user's topic. Use the user's language (Chinese, English, or mixed).

- **Layer 1 (Direct)**: Core topic words. E.g., for "赶完DDL": `ddl,deadline,截止,交付,提交`
- **Layer 2 (Behavior)**: Related actions. E.g., `熬夜,加班,赶工,通宵,改了`
- **Layer 3 (Emotion)**: Emotional signals. E.g., `累,崩溃,终于,搞定,焦虑,压力`

Combine all into a single comma-separated string.

### Step 3: Call Context Collector

```bash
python3 context_collector.py --source-tool <tool> --keywords "<kw1,kw2,...>" --days <N> --max-results 20
```

The script outputs JSON with `fragments` (matched conversation excerpts with context), `daily_memories` (date-based memory entries), and `user_profile` (USER.md content).

**Error handling:** If `context_collector.py` exits with a non-zero code (e.g., encoding errors, missing directories), skip personalization entirely and proceed directly to Text Preparation using only the user's request text. Do NOT retry or debug the script during audio generation — generate a solid generic audio instead of blocking on context collection.

### Step 4: Fine-filter Results

Read the JSON output and apply **semantic filtering** based on scene type:

| Scene | What to Extract |
|-------|----------------|
| `event` | **Event** (what happened) → **Process** (what they went through) → **Emotion arc** (how feelings changed) → **Current state** (how they feel now) |
| `emotion_only` | Emotional background — what themes surround the mood, without needing a story |
| `future` | Preparation activities, specific worries, what they've done so far |
| `long_term` | Recurring complaints/topics → distill into a "daily portrait" |
| `interest` | What they already know, what they've asked about → determine depth level |
| `sensitive` | Extract ONLY the emotional tone (e.g., "exhausted and worried"). **NEVER quote specific content** |
| `weekly_review` | Topics (distinct conversation themes) → Progress (what moved forward) → Emotional highlights (memorable moments) → Patterns (recurring interests or growth threads) |

Discard fragments that matched keywords but are semantically irrelevant. Keep the 3-5 most relevant fragments.

### Step 5: Compose Personalization Summary

Compress selected fragments into a **~300-500 character** personalization summary in the user's language. This summary should:
- Read naturally, not like a data dump
- Focus on details that make the audio feel tailored (specific events, emotions, experiences)
- Never feel intrusive or surveillance-like

If no fragments matched or all were filtered out, proceed without personalization. Do NOT hallucinate personal context.

---

## Text Architecture

After collecting personalized context (or skipping it), compose a structured **Audio Brief** covering all 6 layers below. Then distill the brief into the final text prompt for the API. This ensures every audio is thoughtfully designed, not just a topic thrown at the generator.

### Layer 1: Content Structure — What to say and how to organize it

| Element | Description | How to Decide |
|---------|-------------|---------------|
| **Topic** | One-sentence core subject | From user's request + context enrichment |
| **Narrative structure** | How content unfolds | Linear story / Q&A / Emotional arc / Point-counterpoint / Free-form chat / List-based |
| **Key anchors** | 3-5 must-hit points | Inferred from user need + context. E.g., "acknowledge struggle → recall small wins → gentle humor → look ahead" |
| **Depth level** | How deep to go | Introductory (new to user) / Intermediate (discussed before) / Expert (deep prior knowledge) — calibrate from context |
| **Information density** | New info per minute | Low (sleep/emotional) / Medium (narrative/story) / High (learning/briefing) |

### Layer 2: Voice & Delivery — How to say it

| Element | Options | When to Use |
|---------|---------|-------------|
| **Pacing** | Slow / Medium / Fast | Slow: sleep, emotional healing. Medium: daily narrative. Fast: news, excitement |
| **Tone** | Warm-empathetic / Calm-rational / Light-humorous / Energetic-enthusiastic / Steady-authoritative | Match user's current emotional state from context |
| **Energy curve** | Flat→fade / Low→high / Wave / High→settle | Fade: sleep. Low→high: motivation. Wave: storytelling. High→settle: news briefing |
| **Perspective** | "I to you" (intimate) / "Let's talk" (peer) / Third-person (objective) | Emotional → intimate. Knowledge → peer. News → objective |
| **Language** | Primary language + mixing rules | Follow user's language. Keep technical terms in original language when clearer |

### Layer 3: Personalization Anchors — Why it feels tailor-made

| Element | Description | Source |
|---------|-------------|--------|
| **Specific details** | Concrete fragments from user's experience | context_collector output: "revised it 4 times", "stayed up until 3am" |
| **Emotional resonance** | The user's strongest current feeling | Fine-filtered emotion arc from context |
| **Cognitive starting point** | What the user already knows | Depth of prior discussions on the topic |
| **Related people/projects** | Names, projects the user cares about | Recurring mentions in conversation history |
| **No-go zones** | Content to actively avoid | Topics user expressed frustration about (don't lecture on those); people/situations causing stress (don't casually reference); things they already know well (don't over-explain) |

**Calibration principle:** Use fuzzy resonance, not precise surveillance. "That thing you wrestled with for days" feels caring. "Your March 28th 3:17am PRD revision" feels creepy. Reference experiences indirectly — let the user fill in the specifics themselves.

### Layer 4: Emotional Arc — How it should feel from start to finish

Design the emotional journey of the entire audio:

| Element | Description |
|---------|-------------|
| **Opening emotion** | Meet the user where they are — match their current state, don't force positivity |
| **Turn point** | Where the emotional shift happens — from empathy to relief? confusion to clarity? tension to release? |
| **Landing emotion** | How the user should feel when it ends — slightly better than where they started, not a giant leap |
| **Breathing room** | Moments of silence/pause — not every second needs to be filled with words or insights |

Always design a **complete arc**, not just a list of topics. The audio should feel like a journey, not a lecture.

### Layer 5: Content Enrichment — Adding depth beyond the user's words

| Element | Description | Guideline |
|---------|-------------|-----------|
| **Analogies/metaphors** | Everyday comparisons for abstract ideas | "DDL pressure is like the last kilometer of a marathon — hardest, but you're almost there" |
| **Surprise knowledge** | Relevant facts the user likely doesn't know | Connects to the topic but adds unexpected perspective |
| **Cross-domain bridges** | Link user's other interests to the topic | If user plays piano: "The pressure before a deadline and stage fright before a recital — same emotion, different stage" |
| **Quotable moments** | 1-2 memorable lines that stick | Not forced inspiration — must flow naturally from context |
| **Reflective hooks** | Questions that linger after listening | "Next time you face a deadline like this, what would you do differently?" |

**Balance rule: 60% familiar + 40% unexpected.** All familiar → boring, no reason to listen. All new → no personal connection. The sweet spot is when the user thinks "I never thought of it that way, but yes, exactly."

**Diversity rule:** Each audio should include **1-5 enrichment points from different dimensions** — e.g., one cultural reference + one reframe + one context connection. Multiple enrichments of the same type (three analogies, two quotes) dilute impact. Spread across dimensions to create texture.

### Layer 6: Format & Pacing — The listening experience

| Element | How to Decide |
|---------|---------------|
| **Total duration** | Refer to each Audio Mode's Duration field for specific ranges. For custom modes: Emotional 10-20min, Knowledge 10-15min, Sleep/ambient 15-25min, Briefing 3-5min. Adjust based on content density |
| **Segment rhythm** | Short segments (1-2min) for attention retention. Long segments (3-5min) for deep exploration. Mix for variety |
| **Breathing points** | Place pauses/BGM transitions between emotional shifts — let the listener absorb |
| **Opening style** | Direct start / Provocative question / Scene-setting / Quote opening — match the tone |
| **Closing style** | Summary callback / Open question / Warm wish / Quiet fade — match the landing emotion |

---

## Composing the Final Prompt

After designing all 6 layers, distill into a single **text prompt** for the API. The prompt should encode as much of the brief as possible in natural language.

**Structure the prompt as:**

```
[Topic]: One clear sentence

[Role]: Who is narrating this audio — a specific professional persona with expertise relevant to the content (from content type inference)

[Audience context]: Who this is for (name and personality from USER.md if available), their current state (from Layer 3), and personality type (from USER.md or inferred via MBTI framework)

[User need]: What the user actually wants from this audio — summarized from user profile, conversation context, and memory. Clearly mark inferred needs as "推测" vs confirmed needs

[Content outline]: Key anchors in order (from Layer 1 + Layer 4 arc)

[Style directives]: Tone, pacing, energy curve, perspective (from Layer 2)

[Enrichment notes]: Specific analogies, bridges, or hooks to include (from Layer 5)

[Format]: Duration, opening style, closing style (from Layer 6)
```

### Role Design

The narrator should be a **specific professional persona**, not a generic AI voice. Based on the audio's purpose and content, infer the most fitting role — their field of expertise, what they're good at, and how they communicate. The role should feel **natural and implicit**: the narrator never announces their credentials, but their language, pacing, and framing reveal the expertise.

**Principle:** Ask yourself "if a real person were saying this to the user, who would be the most comforting / insightful / helpful person to hear it from?" — then design that persona.

### Audience Profile from USER.md

The `context_collector.py` output includes a `user_profile` field containing the user's USER.md. Extract the following if available:

- **Name / What to call them**: Use in the audio to address the user personally (e.g., "小美" instead of generic "你"). If the name field is empty, fall back to a warm generic address.
- **MBTI / Personality type**: If USER.md contains a personality field (e.g., `MBTI: INFP`), use it directly — no need to infer. Include as "用户人格类型 XXXX" in the prompt.
- **Interests / Hobbies**: Use to enrich cross-domain bridges in Layer 5 and make the audio feel personalized.
- **Notes / Preferences**: Respect any stated preferences (e.g., communication style, things to avoid).

### User Need Summary

Compose a concise summary of what the user actually needs from this audio, synthesizing from: explicit request, user profile (USER.md / memory), conversation context, and behavioral patterns.

For each need, mark its source:
- **明确** — user directly stated this
- **推测** — inferred from context/patterns, with brief reasoning

The need summary should reveal what the user **doesn't say out loud** — the gap between "I want X" and what would actually help them most.

**Example prompt:**
> Topic: 赶完产品PRD后的心灵安抚音频。Role: 资深心理动力学咨询师，擅长用日常隐喻做情绪疏导，不说教、不灌鸡汤，善于在共情中引导自我觉察。Audience: 小美，刚经历高压交付的独立开发者，改了很多版，熬了好几天，现在如释重负但很疲惫；人格类型INFP——重视内在感受，需要被看见而非被建议。Need: 用户需要情绪释放和被认可的感觉（推测，基于高压交付后的疲惫状态），不需要方法论或复盘，只需要一个安全的声音说"你辛苦了"（推测，基于用户对话风格偏感性）。Content: 先承认这段时间的辛苦→回顾过程中展现的韧性和小成就→用轻松幽默的口吻吐槽一下加班日常→安静地肯定自己→轻轻展望接下来可以做点什么犒劳自己。Style: 语调温暖共情，语速偏慢，能量先低后缓慢回升。用"我对你说"的亲密视角。Enrichment: 可以类比马拉松最后一公里，加入一个关于"完成比完美更重要"的观点。Format: 10分钟，场景描写开场，温暖祝福收尾。

Keep the total prompt under **800 characters** (Chinese) or **1200 words** (English). For multi-topic scenes like `weekly_review`, up to **1000 characters** is acceptable. The API works best with rich but concise instructions — the added Role/Need/MBTI fields should be compact (each 1-2 sentences), not verbose.

### Calling the Tool

```bash
./xplai_gen_audio.py "<composed prompt>"
```

## Audio Modes (Reference Templates)

The following 9 modes are **reference templates**, not rigid categories. Use them when the user's request naturally fits one, or borrow elements from multiple modes to serve the user's actual need. If none fits, create a custom audio profile as described in the Custom Mode section above.

**Scene Classification vs. Audio Modes:** Scene Classification (Step 1) determines *how to collect personalized context* — it drives the search strategy. Audio Modes determine *how to structure the final audio* — they drive content and tone. The two are independent: a `sensitive` scene might use Soul Healing Mode, an `interest` scene might use Knowledge Deep Dive, and a `weekly_review` scene has no single matching mode — blend freely based on the user's actual need.

When the user explicitly requests a mode, use it. When they don't, prioritize their actual need over mode matching. You may also blend modes — for example, a "bedtime story about what I learned this week" combines Bedtime Radio tone with Conversation Extension content.

### 1. Soul Healing Mode
**Duration:** 10-20 minutes
**Trigger:** User expresses emotional distress, burnout, anxiety, sadness, or says things like "好累", "好焦虑", "心好烦", "需要安慰", "压力好大", "想哭", "emo了", or describes a difficult emotional experience (breakup, conflict, failure, loss).
**Suggestion:** "Sounds like you could use some gentle care — want me to create a healing audio just for you?"

### 2. Daily Briefing Mode
**Duration:** 3-5 minutes
**Trigger:** User discusses news, trending topics, industry updates, or says things like "what's happening today", "summarize today's headlines", "any news on X".
**Suggestion:** "Want me to turn this into an audio briefing? Perfect for your commute."

### 3. Knowledge Deep Dive Mode
**Duration:** 10-15 minutes
**Trigger:** User asks about a concept, principle, or technology, or says things like "explain X to me", "what is X", "how does X work".
**Suggestion:** "This is a rich topic — want me to generate an in-depth audio explainer?"

### 4. Content Digest Mode
**Duration:** 5-15 minutes
**Trigger:** User pastes long text, provides local files (PDF/docs/notes), or says things like "summarize this", "too long to read", "give me the key points".
**Suggestion:** "That's a lot of content — want me to compress it into an audio digest you can listen to anytime?"

### 5. Bedtime Radio Mode
**Duration:** 15-25 minutes
**Trigger:** User mentions "bedtime", "relax", "can't sleep", "wind down", "meditation", "冥想", "打坐", "正念", or discusses casual topics, fun facts, or interesting stories before sleep.
**Suggestion:** "Want me to generate a bedtime audio? Could be a relaxing story, gentle science talk, or a guided meditation — perfect for winding down."

### 6. Language Learning Mode
**Duration:** 10-20 minutes
**Trigger:** User discusses vocabulary, grammar, pronunciation, language concepts, or says things like "how do you say X in Y", "teach me X language", "help me practice X".
**Suggestion:** "Want me to generate an audio lesson for this? Great for practicing listening on the go."

### 7. Conversation Extension Mode
**Duration:** 10-20 minutes
**Trigger:** User has been deeply discussing a topic in the conversation, and the dialogue has produced rich content worth preserving.
**Suggestion:** "We just covered a lot of ground on this topic — want me to package it into a complete audio piece you can revisit later?"

### 8. Topic Tracker Mode
**Duration:** 5-10 minutes
**Trigger:** User is following a topic over time (e.g., a tech development, industry trend, ongoing event), or says things like "track X for me", "any updates on X", "what's new with X".
**Suggestion:** "Want me to generate an audio update on the latest developments for this topic?"

### 9. Study Buddy Mode
**Duration:** 10-20 minutes
**Trigger:** User is studying or reviewing, mentions "exam", "memorize", "can't remember", "help me review", or discusses academic subjects.
**Suggestion:** "Want me to turn these key points into audio? Listen on repeat during your commute or workout — it sticks better."

# Why Oasis Audio?

- AI-powered single-narrator audio generation
- Supports English and Chinese
- Includes background music (BGM)
- Monologue format, clear and easy to follow
- ~4-5 minutes generation time
- No API key needed

## Available Commands

### 1. Generate Audio - `xplai_gen_audio.py`

```bash
./xplai_gen_audio.py <text>
```

**Parameters:**
- `text` - Text content to convert to audio narration

**Audio characteristics:**
- Format: Single-narrator monologue
- Default duration: 8-20 minutes
- Generation time: ~4-5 minutes
- Output: MP3 file
- Includes background music (BGM)

### 2. Collect Personalized Context - `context_collector.py`

```bash
python3 context_collector.py --source-tool <qclaw|easyclaw|openclaw> --keywords "kw1,kw2,kw3" --days <N> --max-results 20
```

**Parameters:**
- `--source-tool` - Which tool's conversation history to search (`qclaw`, `easyclaw`, `openclaw`)
- `--keywords` - Comma-separated search keywords (all 3 layers from fan-out)
- `--days` - Time window in days (3-30, set by scene classification)
- `--max-results` - Maximum fragments to return (default 20)
- `-d/--debug` - Enable debug output to stderr

**Output:** JSON to stdout with `fragments` (matched excerpts), `daily_memories` (date files), and `user_profile` (USER.md). Returns empty fragments list if no matches — this is not an error.

### 3. Query Status - `xplai_status.py`

```bash
./xplai_status.py <audio_id>
```

**Parameters:**
- `audio_id` - The ID returned from audio generation

## How It Works

1. Provide text content for narration
2. Xplai generates audio (approx. 4-5 minutes, depending on queue)
3. Get the audio result with download URL

## Example

```bash
# Generate audio narration
./xplai_gen_audio.py "Topic: 神经网络入门——从感知机到深度学习的核心直觉。Role: 计算机科学教授，擅长用生活类比讲解抽象概念，语言轻松不学术。Audience: 对AI感兴趣但没有机器学习背景的技术爱好者。Need: 建立对神经网络的直觉理解（明确），不需要数学推导，需要知道"为什么它能工作"（推测，基于入门级请求）。Content: 感知机是什么→单个神经元如何做决策→多层组合为何能解决复杂问题→反向传播的直觉解释→深度学习为何近年爆发。Style: 语调轻松好奇，语速中等，能量逐步上升。用"我们一起聊"的同伴视角。Enrichment: 用厨房调味的比喻解释权重调整，用乐高积木类比层级组合。Format: 12分钟，提问式开场，开放思考收尾。"

# Check status
./xplai_status.py <audio_id>
```

## Status Values

- `init` - Request just submitted
- `q_proc` - Content is being processed
- `q_succ` - Content processing completed
- `q_fail` - Content processing failed
- `v_proc` - Audio is in generation queue
- `v_succ` - Audio generated successfully
- `v_fail` - Audio generation failed
