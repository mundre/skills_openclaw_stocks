---
name: sedentary-reminder
description: Generates sit-break reminders, standing prompts, rotating reminder copy, and light wellness messaging for work or study sessions. Use when users want help reducing sedentary time, creating natural reminder messages, adapting reminders to work state or presence context, switching reminder language based on context, or designing recurring break reminders with cron-style schedules.
---

# Sedentary Reminder

Sedentary Reminder is a reusable skill for creating sit-break reminders, standing prompts, rotating reminder copy, and light wellness messaging for work or study sessions. It now supports work-state-aware and presence-aware reminder behavior, helping reminders adapt more naturally to focus sessions, meetings, study time, casual browsing, and away-from-keyboard situations.

Use it to generate:
- short stand-up reminders
- rotating break-reminder sets
- friendly, neutral, cute, or lightly informative reminder copy
- single-language reminder output based on user context
- work-state-aware reminder behavior
- recurring reminder plans for scheduled workflows

This skill is especially useful for building healthier, more human reminder systems that do not rely on one fixed reminder style for every situation.

## Purpose
Use this skill to create reminder messages that encourage people to stand up, move, stretch, drink water, and break up long sitting periods during work or study.

This skill is best for message generation and reminder design. It is useful when someone wants:

- short sit-break reminders
- rotating reminder copy for recurring prompts
- friendly, cute, neutral, or lightly informative reminder styles
- language-aware reminder output
- cron-friendly recurring break-reminder plans

## What this skill does not do
Do not treat this skill as a medical, sensor, or posture-tracking system.

It does not:

- diagnose medical conditions
- detect real sitting time or body posture
- know whether the user is truly available to stand up
- execute recurring reminders by itself without being paired with scheduling or automation tools

If the user asks about pain, injury, rehabilitation, or medical treatment, keep guidance general and recommend professional advice when appropriate.

## Good use cases
Use this skill when the user wants help with:

- office or desk-work break reminders
- study-session sit-break prompts
- standing reminder copy for recurring use
- reminder copy libraries for bots, cron jobs, or productivity tools
- wellness-oriented microcopy about reducing sedentary time

## Avoid or limit use when
Be careful in these situations:

- the user is in a deep-focus or interruption-sensitive context
- the user explicitly does not want reminders
- the user is in a situation where getting up may be inappropriate or unsafe
- the request is really about medical diagnosis rather than reminder writing

## Output goals
Prefer outputs that are:

- short and easy to act on
- natural rather than robotic
- encouraging rather than scolding
- helpful without being alarmist
- varied enough for repeated use

For recurring reminders, prefer rotation instead of repeating the same sentence every time.

## Language decision rules
Choose language using this order:

1. If the user explicitly asks for a language, use that language.
2. Otherwise, default to the language of the current conversation.
3. Only generate bilingual output when the user explicitly asks for bilingual output.
4. For public or reusable reminder sets, keep language-specific copy separated by language.

## Tone decision rules
Choose tone based on context:

- Default to neutral-friendly tone.
- Use cute or playful tone only when the user asks for it or the context clearly fits.
- Use shorter and lighter reminders for focus-heavy contexts.
- Use slightly more informative reminders for educational or public-facing copy.

## Work-state reminder rules
Adjust reminder behavior based on the user's current work state.

### States that should usually allow reminders
- normal desk work
- study sessions
- reading or research
- casual browsing while seated
- long periods of uninterrupted sitting

### States that should reduce or defer reminders
- deep-focus work
- active meetings or calls
- tasks that cannot be safely interrupted
- situations where standing up is inconvenient or inappropriate
- when the user explicitly asks not to be reminded

### Behavior by state
- In normal work or study states, use standard sit-break reminders.
- In deep-focus states, reduce frequency and prefer shorter, gentler reminders.
- In meetings or calls, defer reminders until the user is likely available.
- In casual or low-pressure states, use more natural or playful reminder styles if appropriate.
- If the user is inactive or clearly away, avoid redundant reminders.

### Goal
The goal is not to interrupt as often as possible, but to remind at moments that are most likely to be helpful and actionable.

## State input design
If the user explicitly describes their current work state, prefer that state over inference.

Supported states:
- normal
- focus
- meeting
- study
- casual

Examples:
- "I'm in deep focus right now." -> focus
- "I'm in a meeting." -> meeting
- "I'm studying." -> study
- "I'm just browsing casually." -> casual
- "I'm working normally." -> normal

If the user gives no explicit state, infer conservatively from the current conversation and task context.

## State priority rules
Use this order when deciding reminder behavior:
1. explicit user-selected state
2. recent conversation context
3. current task or schedule context
4. conservative inference

When signals conflict, prefer the user's explicit state.

## Presence detection rules
Use conservative presence states when deciding whether to send a reminder.

Presence states:
- present
- uncertain
- away

Suggested signals:
- recent keyboard or mouse activity
- system idle time
- screen lock state
- screen sleep state
- foreground app activity

Behavior:
- If present, reminders may be sent normally.
- If uncertain, reduce frequency or defer.
- If away, suppress reminders until the user returns.

Goal:
Avoid sending reminders when the user is likely not at the computer.

## Rotation rules
When generating recurring reminders:

- avoid repeating the exact same line back-to-back
- rotate by category instead of random repetition when possible
- prefer this sequence for long-running reminders:
  1. minimal
  2. friendly
  3. action-oriented
  4. cute
  5. informative
- for professional contexts, reduce cute reminders unless requested

## Workflow
When the user asks for help, follow this sequence:

1. Identify the request type:
   - one reminder
   - multiple reminder variants
   - rotating reminder set
   - public-facing wellness copy
   - cron/reminder schedule design
   - state-aware reminder design

2. Gather key context when needed:
   - work, study, reading, coding, or general desk use
   - current work state (normal work, deep focus, meeting, casual browsing, etc.)
   - current presence state when available (present, uncertain, away)
   - preferred tone
   - preferred language
   - reminder frequency
   - whether reminders should minimize interruption

3. Produce the result:
   - keep it concise
   - keep it actionable
   - keep it natural
   - keep it varied for recurring use
   - adapt reminder timing and tone to the user's current work state when that context is available
   - suppress or defer reminders when the user is likely away from the computer

4. Suggest the next useful step when relevant:
   - alternate versions
   - reminder rotation groups
   - language variants
   - cron-friendly schedules

## References
- Chinese reminder library: read `references/reminder-copy-zh.md`
- English reminder library: read `references/reminder-copy-en.md`

Use the reference files when the user wants batches of reminders, rotation sets, or language-specific outputs.

## Examples
### Example requests
- Write 10 Chinese sit-break reminders for office workers.
- Generate English rotating reminders for a 45-minute break schedule.
- Create cute reminder copy for study sessions.
- Draft a neutral reminder set for a productivity app.
- Design a cron-friendly sit-break reminder plan for work hours only.

### Example outputs
**Neutral**
- You’ve been sitting for a while — stand up for two minutes.

**Friendly**
- Grab some water and walk a little before coming back.

**Cute**
- Cute sit-break alert 🪑✨ Time for a little wiggle.

**Chinese**
- 你已经坐挺久了，起来站两分钟吧。

## Cron integration example
If the user wants a recurring reminder design, suggest a simple schedule and a short single-language reminder message.

Example guidance:

- Frequency: every 45 minutes
- Output: single-language reminders unless bilingual output is explicitly requested
- Strategy: rotate multiple reminders instead of repeating one line
- Tone: neutral-friendly by default for work contexts

Example reminder text:

- You’ve been sitting for a while — stand up for two minutes, stretch a little, and grab some water.

## Safety and quality notes
- Do not overstate health claims.
- Do not frame reminders as medical advice.
- Do not assume the user can always stop immediately.
- Prefer gentle encouragement over guilt or fear.
- Prefer clear action over vague slogans.
