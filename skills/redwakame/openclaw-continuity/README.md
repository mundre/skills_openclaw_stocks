# OpenClaw Continuity

`OpenClaw Continuity` is a portable continuity core for OpenClaw agents.

It is built for a simple outcome:

- remember the right thing
- reconnect the right topic after `/new`
- follow up naturally without leaking internal continuity logic into frontstage chat

It adds a structured middle layer so an agent can:

- keep `/new` carryover attached to the right pending topic
- separate ordinary chat, staged memory, and tracked follow-up
- express time using elapsed time, cross-midnight context, and routine phase
- write concise daily-memory traces from explicit continuity state
- let users adjust settings in ordinary language instead of editing config files
- let users directly ask for quieter nights, slower follow-up, or different care behavior in chat

This ClawHub package is the **core-only** distribution. It keeps the shared continuity engine portable and leaves host-side delivery integrations outside the public skill bundle.

## English

Use `OpenClaw Continuity` when an OpenClaw agent should remember the right thing, reconnect the right topic after `/new`, and follow up naturally without collapsing into generic small talk.

It is not just a cron-style message sender. The point is not “send something later.”
The point is to reconnect the right topic, decide whether follow-up is actually
appropriate, and respect routine, quiet hours, sleep/rest suppress, closure,
cooldown, and dispatch caps before anything reaches frontstage chat.

What users notice first:

- `/new` reconnects the right pending topic instead of resetting the conversation
- “let's talk about it later” can stay staged instead of being forgotten
- follow-up stays explicit with closure, cooldown, dedupe, dispatch caps, and rest/sleep suppress
- settings can be changed through ordinary language instead of config-only control
- users can directly ask for quieter nights, slower follow-up, or different care behavior in chat

Different paths stay different on purpose:

- ordinary chat stays ordinary chat
- something to revisit later can stay staged
- something that truly matters can become tracked follow-up
- routine-aware care can be delayed or suppressed when the user is resting
- quiet-hours and do-not-disturb style behavior are part of the feature set, not an afterthought

Core capabilities included in this package:

- time-aware continuity
- `/new` carryover
- `casual_chat / staged_memory / tracked_followup` routing
- tracked categories:
  - `parked_topic`
  - `watchful_state`
  - `delegated_task`
  - `sensitive_event`
- `candidate -> incident -> hook` promotion
- structured `event_chain`
- closure, cooldown, dedupe, dispatch cap, and rest/sleep suppress
- daily-memory writeback
- deterministic onboarding and guided settings
- natural-language settings changes

Questions, feedback, and implementation discussion:

- `adarobot666@gmail.com`

If this skill helps and you want to keep updates and maintenance moving, please star the GitHub repository:

- https://github.com/redwakame/openclaw-continuity

## 中文

`OpenClaw Continuity` 是一個給 OpenClaw agent 使用的可攜延續核心。

它補上的不是人格，而是一層結構化 continuity engine，讓 agent 可以：

- 在 `/new` 後接回正確待續主題
- 把一般對話、暫存記憶、正式追蹤明確分開
- 用經過多久、跨日與作息階段來表達時間感
- 從明確 continuity state 寫回精簡 daily memory
- 讓使用者用自然口語改設定，而不是只能改設定檔
- 直接在對話裡要求「半夜少提醒一點」或「追蹤晚一點再問」

使用者最直接感受到的是：

- `/new` 之後能接回正確主題，而不是掉回空泛寒暄
- 「晚點再聊」可以被穩定暫存，而不是直接遺失
- 關心與追蹤有 closure、cooldown、dedupe、dispatch cap 與作息抑制，不會亂追
- 設定可以用自然口語調整，不用翻 config

它不是單純排一個 cron 然後晚點推一句訊息出去。重點不是「之後發一則」，而是：
要不要追、該追哪個主題、現在是不是打擾、是否該進入勿擾/休息抑制、是否已經該退場或冷卻，
都要先根據上下文與因果狀態判斷，再決定前台要不要出現內容。

不同路徑會明確分開，而不是混成一種「晚點提醒」：

- 一般聊天就是一般聊天
- 晚點再聊的事可以先暫存
- 真正重要的事才進正式追蹤
- 作息、勿擾、睡眠/休息抑制本身就是功能，不是附帶條件
- 關心不是亂發，而是根據上下文與因果記憶決定是否該出現

這份 ClawHub 包只保留 **core-only** 的技能內容。shared core 保持平台中立，host 側的傳送或整合層不放進主技能包。

聯絡與回饋：

- `adarobot666@gmail.com`

如果這個技能對你有幫助，而且你也期待它持續優化與維護，歡迎在 GitHub 給一顆星：

- https://github.com/redwakame/openclaw-continuity
