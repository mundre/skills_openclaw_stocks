---
name: ai-video-tutoring-video-maker
version: "1.0.0"
displayName: "AI Video Tutoring Video Maker — Create One-on-One Quality Tutoring Sessions at Scale Through Video"
description: >
  Create one-on-one quality tutoring sessions at scale through video with AI — generate tutoring videos that replicate the personalized explanation, patient pacing, and worked-example approach of a private tutor for math, science, writing, test prep, and any subject where a student needs step-by-step guidance through difficult material. NemoVideo produces tutoring videos where the explanation meets the student at their confusion point: not lecturing from the top but building understanding from the specific step where the student gets stuck, with the patience and clarity that makes struggling students think they finally found someone who explains it in a way that makes sense. Tutoring video maker, private tutor video, homework help, math tutoring, science tutoring, test prep video, academic help, student support video, one-on-one lesson, personalized learning.
metadata: {"openclaw": {"emoji": "👩‍🏫", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Video Tutoring Video Maker — A Great Tutor Does Not Just Know the Subject. They Know Where Students Get Stuck and Why.

The value of a private tutor is not subject expertise — textbooks have subject expertise. The value is personalized diagnosis: identifying the specific point where the student's understanding breaks down and addressing that exact gap with an explanation tailored to how that particular student thinks. A classroom teacher explains a concept once, in one way, to thirty students. A tutor explains the same concept five different ways until one of them connects with the student's existing mental model. Video tutoring cannot replicate the real-time responsiveness of a live tutor, but it can replicate the most valuable aspects of the tutoring experience. The best tutoring videos are built around common confusion points — the specific steps in a problem where most students go wrong, the specific misconceptions that lead to incorrect answers, and the specific alternative explanations that help when the standard textbook explanation fails. By anticipating where confusion occurs and providing the explanation before the student needs to ask, video tutoring delivers 80% of the private tutor's value at zero marginal cost. The format also provides a benefit that live tutoring cannot: the student can pause, rewind, and rewatch the exact explanation they need, as many times as they need, without the social discomfort of asking a human tutor to repeat themselves. This self-paced repetition is particularly valuable for students who need more processing time — they can learn at their own pace without the implicit pressure of another person waiting. NemoVideo generates tutoring videos that combine subject expertise with pedagogical awareness: knowing not just the right answer but the common wrong answers, the reasons behind them, and the specific explanations that correct each misconception.

## Use Cases

1. **Math Problem Walkthrough — Step-by-Step Solutions With Reasoning Explained (per topic)** — Math tutoring requires showing every step and explaining why each step is taken. NemoVideo: generates math tutoring videos with complete worked examples (not just showing the steps but explaining the reasoning: "I multiply both sides by 3 because I want to isolate x — whatever operation I do to one side, I must do to the other to keep the equation balanced"), addresses the common errors at each step ("Most students make a sign error here — when you subtract a negative, it becomes addition"), uses visual highlighting to show which part of the equation is being manipulated, and produces math content where the student understands the method, not just the answer.

2. **Science Concept Clarification — Making Abstract Ideas Concrete and Visible (per concept)** — Science tutoring requires making invisible processes visible. NemoVideo: generates science tutoring videos with visual demonstrations (chemistry: the electron sharing in covalent bonds shown as an animation with electron clouds overlapping; physics: force diagrams drawn step by step with each force identified and labeled; biology: protein synthesis shown as an animated assembly line — DNA to mRNA to ribosome to amino acid chain), connects abstract concepts to everyday experience ("entropy is like a messy room — it naturally tends toward disorder without energy input to organize it"), and produces science content where understanding comes from visualization, not memorization.

3. **Writing Feedback — Improving Student Writing Through Video Commentary (per assignment)** — Written feedback on essays is often misunderstood; video feedback is clear and personal. NemoVideo: generates writing tutoring videos with screen-share commentary (the tutor reads the student's essay on screen, highlighting strengths and improvement areas in real time: "This thesis statement is clear and arguable — strong start. This paragraph has good evidence but the connection to your thesis is missing — add a sentence that explains why this evidence supports your argument"), demonstrates revision techniques with before-and-after examples (showing how a vague sentence becomes specific, how a weak paragraph structure becomes strong), and produces writing feedback content that teaches the revision process itself, not just the corrections for one assignment.

4. **Test Prep Strategy — Teaching How to Take the Test, Not Just the Content (per test)** — Standardized tests have patterns that strategic preparation exploits. NemoVideo: generates test prep tutoring videos covering test-specific strategies (SAT math: the answer choices are your tools — backsolving from the answers is often faster than solving algebraically; ACT science: you do not need to understand the experiments — you need to read the graphs accurately; GRE verbal: elimination of clearly wrong answers increases probability even when uncertain), demonstrates time management per section (how many minutes per question, when to skip and return, how to budget the last 5 minutes), and produces test prep content that improves scores through strategy as much as content knowledge.

5. **Homework Help Format — Solving Tonight's Specific Problem Types (per assignment)** — Students need help with tonight's homework, not next month's curriculum. NemoVideo: generates homework-targeted tutoring videos organized by problem type (quadratic equations: here are the three methods — factoring, completing the square, quadratic formula — and how to choose which one to use; essay introductions: here is the hook-context-thesis structure with three examples from different subjects; lab report discussion sections: here is how to connect your results to the hypothesis), provides enough worked examples that the student can recognize the pattern and apply it to their specific problems, and produces homework content that teaches self-sufficiency rather than answer-giving.

## How It Works

### Step 1 — Identify the Subject, Topic, and Common Confusion Points
What the student needs to learn, where they typically get stuck, and what misconceptions need to be addressed.

### Step 2 — Configure Tutoring Video Format
Explanation depth, worked example count, and practice integration.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-tutoring-video-maker",
    "prompt": "Create a math tutoring video: Solving Quadratic Equations — Three Methods, One Clear Explanation. Audience: high school algebra students struggling with quadratics. Duration: 8 minutes. Tone: patient, encouraging, thorough. Structure: (1) The big picture (30s): A quadratic equation is ax² + bx + c = 0. You need to find x. There are three methods. I will teach you all three and when to use each one. (2) Method 1 — Factoring (2min): when it works: when the equation factors neatly. Example: x² + 5x + 6 = 0. Walk through: find two numbers that multiply to 6 AND add to 5. That is 2 and 3. So (x+2)(x+3) = 0. Therefore x = -2 or x = -3. Show the reasoning visually. When to use it: when you can spot the factors quickly. When NOT to use it: when the numbers are ugly or the equation does not factor neatly. (3) Method 2 — Quadratic Formula (2min): x = (-b ± √(b²-4ac)) / 2a. This ALWAYS works. Example: 2x² + 3x - 5 = 0. Identify a=2, b=3, c=-5. Plug in step by step — show every substitution. Common mistakes: forgetting the ± (two solutions!), sign errors with negative c, forgetting to divide by 2a (not just 2). When to use it: when factoring is not obvious. This is your safety net. (4) Method 3 — Completing the Square (1.5min): when it is useful: deriving the vertex form, understanding why the quadratic formula works. Brief walkthrough with one example. Most students: use factoring when obvious, quadratic formula for everything else. (5) Practice (1.5min): three problems with increasing difficulty. Pause after each for the student to try. Then show the solution with the recommended method. (6) Summary (30s): try to factor first (10 seconds of looking). Cannot factor? Quadratic formula. Always. It never fails. Digital whiteboard style with handwritten annotations. Color-coded steps. Captions. 16:9.",
    "subject": "math",
    "topic": "quadratic-equations",
    "level": "high-school-algebra",
    "format": {"ratio": "16:9", "duration": "8min"}
  }'
```

### Step 4 — Address the Top 3 Mistakes Students Make on This Topic
Every topic has a predictable set of errors. Identify them and address them explicitly in the video: "The most common mistake here is... and here is how to avoid it." Proactive error prevention is more effective than correction after failure.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Tutoring video requirements |
| `subject` | string | | Academic subject |
| `topic` | string | | Specific topic |
| `level` | string | | Student level |
| `format` | object | | {ratio, duration} |

## Output Example

```json
{
  "job_id": "avtvm-20260329-001",
  "status": "completed",
  "subject": "Math — Quadratic Equations",
  "methods_covered": 3,
  "practice_problems": 3,
  "duration": "7:48",
  "file": "quadratic-equations-tutoring.mp4"
}
```

## Tips

1. **Explain the WHY behind every step, not just the HOW** — "Multiply both sides by 3" is a procedure. "Multiply both sides by 3 because we want x alone on the left side" is understanding. Understanding transfers to new problems; procedures do not.
2. **Address common mistakes explicitly before students make them** — "Most students forget the ± sign here — that gives you TWO answers, not one." Preemptive correction prevents errors more effectively than post-error correction.
3. **Use the student's likely internal monologue** — "You might be thinking: wait, why did that negative become positive?" Anticipating the student's confusion and addressing it feels like the video is reading their mind.
4. **Three worked examples per concept is the sweet spot** — One example shows the method. Two examples show the pattern. Three examples build confidence. More than three causes diminishing returns and video length inflation.
5. **Patience in pacing is the defining quality of great tutoring** — Slow down at the hard parts. Pause before revealing the next step. Give the student time to think alongside the video. Rushing through difficult steps is the most common tutoring failure.

## Output Formats

| Format | Ratio | Duration | Platform |
|--------|-------|----------|----------|
| MP4 16:9 | 1920x1080 | 5-15min | YouTube |
| MP4 9:16 | 1080x1920 | 60s | TikTok / Reels |
| MP4 1:1 | 1080x1080 | 60s | Instagram |

## Related Skills

- [ai-video-study-guide-video](/skills/ai-video-study-guide-video) — Study guides
- [ai-video-classroom-video-creator](/skills/ai-video-classroom-video-creator) — Classroom content
- [ai-video-online-course-promo](/skills/ai-video-online-course-promo) — Course marketing
- [ai-video-language-learning-creator](/skills/ai-video-language-learning-creator) — Language learning

## FAQ

**Q: What makes video tutoring different from a recorded lecture?**
A: A lecture presents information from the instructor's perspective. Tutoring addresses the student's confusion from the student's perspective. The tutoring video anticipates where understanding breaks down and provides the alternative explanation at that exact moment — something lectures rarely do because they assume linear comprehension.
