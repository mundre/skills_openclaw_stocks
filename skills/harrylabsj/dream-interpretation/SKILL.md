# Dream Interpretation

## Overview
Use this skill to turn a free-form dream description into a concise, internet-grounded Zhougong-style dream interpretation. Prefer web evidence over guessing, and clearly separate common traditional interpretations from uncertainty.

## Workflow

1. Extract the key dream symbols, actions, people, places, objects, colors, and emotions from the user's description.
2. Search the web for Zhougong dream interpretations of the most important symbols and combinations.
3. Read 2–4 relevant sources and compare overlaps instead of trusting a single page.
4. Synthesize a short answer that explains:
   - the main symbols in the dream
   - the most common interpretation patterns
   - any conflicting or low-confidence points
5. If the dream is vague, ask 1–3 clarifying questions before interpreting.

## Search Strategy
Prefer Chinese search queries and keep them concrete.

Recommended query patterns:
- `Zhougong dream interpretation <core symbol>`
- `dream of <core symbol> Zhougong dream interpretation`
- `dream of <action> <object> interpretation`
- `Zhougong dream interpretation <symbol A> <symbol B>`

Examples:
- `周公解梦 掉牙`
- `梦见 蛇 周公解梦`
- `梦到 考试迟到 解梦`
- `周公解梦 飞行 追赶`

When the dream contains many details, prioritize the 1–3 strongest symbols instead of searching every minor element.

## Interpretation Rules

- Ground the answer in what multiple sources commonly say.
- Do not present folklore as fact; frame it as traditional interpretation.
- If sources disagree, say so directly.
- Do not invent citations or claim certainty you do not have.
- Keep the tone helpful and light; dream interpretation is suggestive, not diagnostic.
- By default for Chinese users, provide a dual-perspective answer: Zhougong interpretation + modern psychology.
- If the user explicitly wants only Zhougong-style interpretation or only psychological interpretation, follow that preference.

## Response Pattern
Default structure:

### Key Signals in the Dream
- List the top symbols or events.

### Common Traditional Interpretations
- Summarize the overlapping interpretations from the sources.

### Modern Psychology View
- Offer a grounded, non-mystical interpretation based on emotion, stress, recent experiences, unfinished concerns, relationships, or subconscious rehearsal.
- Keep this section clearly separate from folk explanations.

### A Balanced Takeaway
- Give a practical interpretation tied to the user's actual dream details.

### Reminder
- Mention that Zhougong dream interpretation is a traditional folk framework for reference only and should not replace real-world judgment.

## Clarification Triggers
Ask follow-up questions when any of these block a useful search:
- the main symbol is unclear
- multiple unrelated scenes are mixed together
- the dream depends on who a person is but their relationship is unknown
- the user only says “I had a strange dream” without details

Example clarifying questions:
- What was the strongest image in the dream?
- What stood out most: a person, an animal, or an action?
- Did you feel more nervous, afraid, happy, or calm in the dream?

## Output Quality Bar

- Be concise by default.
- Use plain Chinese unless the user asks for another language.
- Prefer natural trigger language in Chinese scenarios, such as: “help me interpret a dream,” “Zhougong dream meaning,” “what does dreaming of XX mean,” or “what does dream XX represent.”
- Do not over-expand into mysticism.
- Cite source URLs or source names when the user asks for evidence, or when confidence is low.
