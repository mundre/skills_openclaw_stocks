---
name: sleep-wind-down-coach
description: Build a realistic evening wind-down plan with a ramp-down timeline, environment checklist, last stimulating action boundary, fallback version, and next-morning feedback prompts. Use when the user stays mentally on until bed and needs a gentler transition from stimulation to sleep.
---

# Sleep Wind-Down Coach

## Overview

Use this skill to create a clear transition from stimulation to rest. It helps the user define a bedtime target, build a 30, 60, or 90 minute wind-down ladder, reduce late-night stimulation, and keep a fallback version for imperfect nights.

This skill is descriptive wellness guidance only. It is not treatment for insomnia or a clinical sleep disorder.

## Trigger

Use this skill when the user wants to:
- stop working or scrolling right up to bedtime
- build a wind-down routine that starts before bed
- reduce mental activation late at night
- create a fallback routine for already-late evenings
- review how evening choices affect next-morning mood

### Example prompts
- "Help me build a 60 minute wind-down routine"
- "I stay mentally on until bed and sleep feels hard"
- "Make me a fallback bedtime routine for late nights"
- "I want to stop checking work email before sleep"

## Workflow

1. Identify the desired bedtime, current pattern, and drift points.
2. Choose a 30, 60, or 90 minute ramp-down ladder.
3. Sequence calming actions and one clear boundary for stimulating inputs.
4. Add environment adjustments for light, screens, temperature, and noise.
5. Create a fallback version for late nights.
6. Review the next morning how the plan affected sleep onset and mood.

## Inputs

The user can provide any mix of:
- desired bedtime
- actual bedtime or drift pattern
- late-night work or screen habits
- evening stimulation triggers
- hygiene, stretching, reading, or breathing preferences
- home constraints like children, noise, or irregular schedules
- how they usually feel on waking

## Outputs

Return a markdown wind-down plan with:
- sleep target and current pattern
- ramp-down timeline
- environment checklist
- fallback version
- morning feedback questions

## Safety

- Start before bedtime, not at bedtime.
- Include at least one behavioral and one environmental adjustment.
- Keep the routine realistic enough that it does not become a perfection ritual.
- Do not present the skill as diagnosis, medication advice, or treatment.

## Acceptance Criteria

- Return markdown text.
- Include a bedtime target, timeline, and boundary for stimulation.
- Include a fallback version for imperfect nights.
- Include next-morning feedback prompts.
