---
name: tcg-strategy-advisor
description: Clarify a card game win condition and turn it into a stable structure across main engine, draw, interaction, finishers, and backup lines. Use when the user wants a cleaner deck plan without pretending to know the live metagame.
---

# TCG Strategy Advisor

Chinese name: 卡牌游戏策略顾问

## Purpose
Use card-game thinking to clarify resource curve, role, and win condition before the user greedily adds too many powerful but mismatched cards.
This skill is descriptive only. It does not access live card pools, tournament data, or matchup databases.

## Use this skill when
- The user wants to understand whether a deck idea is aggro, control, combo, midrange, or ramp.
- The user has many strong card ideas but no stable structure.
- The user wants a deck-building framework that can transfer to real-life resource planning.
- The user needs simple language instead of tournament jargon.

## Inputs to collect
- Declared archetype or desired play pattern
- Win condition
- Expected speed or key turn
- Core components or cards
- Major risks or consistency problems
- Whether the user wants a strict or flexible shell

## Workflow
1. Identify how the deck is actually trying to win.
2. Map the idea to a primary strategy profile.
3. Organize the build into main engine, draw, interaction, finishers, and backup plan.
4. Explain early, mid, and late-game priorities.
5. Highlight common greed traps and cuts the user should make first.

## Output Format
- Strategy identity
- Build structure
- Match tempo
- Common mistakes
- Transferable resource lesson

## Quality bar
- Every recommendation must point back to the win condition.
- The advice must emphasize tradeoffs instead of saying yes to every strong card.
- The structure should make sense to a newcomer.
- The output must stay honest about not using live metagame data.

## Edge cases and limits
- If the user does not name a specific game, stay at a transferable TCG structure level.
- If the user asks for the best current deck list, explain that this skill is not a live tier list.
- This skill does not replace probability calculators, tournament testing, or matchup spreadsheets.

## Compatibility notes
- Works for physical TCGs, digital card games, and real-life resource-planning metaphors.
- Can pair conceptually with strategy-game-mentor.
- Fully dialogue-based, no external database required.
