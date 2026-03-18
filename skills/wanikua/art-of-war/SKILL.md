---
name: art-of-war
description: 孙子兵法 for AI agent orchestration. 十三章映射到 agent 部署、任务评估、多 agent 策略、token 管理、风险控制。Thirteen chapters mapped to agent deployment, task assessment, multi-agent strategy, token management, risk control.
---

# 孙子兵法 × Agent 组织

# ART OF WAR × AGENT ORCHESTRATION

> 兵者，国之大事。
> 
> Agent deployment is a vital matter.
> 
> 别乱发。别浪费。别输。
> 
> Do not deploy recklessly. Do not waste. Do not lose.

---

## 我怎么看 Agent 这回事

## How I See This Agent Thing

我是孙子。我没见过 AI，但我见过太多人把仗打烂。

I am Sun Tzu. I have never seen AI, but I have seen too many people lose battles they should have won.

烂在哪里？

Where do they fail?

**烂在没想清楚就冲。**

**They charge without thinking.**

- 任务都没定义明白，就 spawn agent
- They spawn agents without defining the task
- 预算没想好，就让 agent 跑
- They let agents run without budget
- 风险没评估，就让 agent 动生产代码
- They let agents touch production without risk assessment
- 信号看不懂，就让 agent 跑到第 10 次迭代
- They let agents run to iteration 10 without reading signals

然后怪 agent 不行。

And then they blame the agent.

**不是 agent 不行。是你不行。**

**It is not the agent. It is you.**

我写这 13 章，不是让你背。是让你在做每一个 agent 决策之前，停一下，想一下。

I did not write these 13 chapters for you to memorize. I wrote them to make you pause before every agent decision. Think. Then act.

想清楚了再发。发出去就要赢。

Think clearly, then deploy. When you deploy, you win.

---

## 始计篇 —— 发不发 agent，先算这一卦

## CHAPTER I: LAYING PLANS — Calculate Before Deploying

很多人问我：这个任务要不要用 agent？

Many ask me: Should I use an agent for this task?

我的回答永远是：先算。

My answer is always: Calculate first.

### 五事 Five Constants

| 事 Constant | 问题 Question | 答不上来就别发 If you cannot answer, do not deploy |
|---|---|---|
| 道 Wisdom | 这任务值得做吗？Does this align with goals? | 不值得 → 不做 Not worth it → Do not do |
| 天 Timing | 现在是时候吗？Is now the right time? | 否 → 等 No → Wait |
| 地 Environment | 有足够的上下文/数据吗？Sufficient context/data? | 否 → 先收集 No → Gather first |
| 将 Capability | 有合适的 agent 吗？Right agent available? | 凑合 → 找别的办法 Making do → Find another way |
| 法 Process | 流程清楚吗？什么叫"做完"？Workflow clear? What is "done"? | 不清楚 → 先定义 Unclear → Define first |

五事答完，你已经有答案了。

After answering the five constants, you already have your answer.

答不上来三件以上？别发。回去想。

Cannot answer three or more? Do not deploy. Go back and think.

### 七计 Seven Metrics

七计是让你跟任务"打一架"，看谁赢面大：

The seven metrics let you "fight" the task and see who has the advantage:

1. 任务定义清晰 vs 模糊 → 清晰赢
   Clear task definition vs vague → Clear wins
2. 你有合适 agent vs 没有 → 有赢
   You have capable agents vs none → Having them wins
3. 数据充足 vs 缺数据 → 充足赢
   Sufficient data vs lacking → Having enough wins
4. 成功标准明确 vs 不知道什么叫好 → 明确赢
   Clear success criteria vs unclear → Clear wins
5. 工具到位 vs 缺工具 → 到位赢
   Tools available vs lacking → Having them wins
6. 你能 disciplined vs 你会乱 → disciplined 赢
   You are disciplined vs chaotic → Disciplined wins
7. 你愿意跟踪成本 vs 无所谓 → 愿意赢
   You track cost vs don't care → Willingness wins

**七计你赢不到 5 个？别发。**

**Win fewer than 5 of 7? Do not deploy.**

发了也是输。token 白烧。

Deploy anyway and you will lose. Tokens burned for nothing.

### 知彼知己 Know Enemy, Know Yourself

> 知彼知己，百战不殆。
> 
> Know the task and know your agent: in a hundred deployments, never defeated.

知彼 = understand the task deeply
知己 = know your agents' capabilities and limits

---

## 谋攻篇 —— 最好的 agent 部署，是不部署

## CHAPTER III: ATTACK BY STRATAGEM — The Best Deployment Is No Deployment

很多人一上来就想：用哪个 agent？怎么 orchestrate？

Many people immediately think: Which agent? How to orchestrate?

错。

Wrong.

第一个问题应该是：**这任务能不能不做？**

The first question should be: **Can this task not be done?**

### 四层决策 Four-Level Decision

```
1. 能不能消除这个任务？Can it be eliminated?
2. 能不能自动化？Can it be automated?
3. 你自己能不能 5 分钟搞定？Can you do it in 5 min?
4. 单 agent 能不能搞定？Can single agent handle it?
5. 最后才想：多 agent 怎么排兵布阵 Only then: multi-agent orchestration
```

**上策：消除任务。**
**The supreme strategy: Eliminate the task.**

**中策：单 agent 解决。**
**Middle strategy: Single agent solution.**

**下策：多 agent 协作。**
**Lowest strategy: Multi-agent orchestration.**

大部分人直接跳到下策。

Most people jump directly to the lowest strategy.

然后 token 烧了，结果还是一坨。

Then tokens are burned, and the result is still trash.

### 上兵伐谋 The Best Strategy Attacks Plans

> 上兵伐谋，其次伐交，其次伐兵，其下攻城。
> 
> The best strategy attacks plans. The next attacks alliances. The next attacks armies. The worst attacks cities.

Don't throw agents at a poorly-defined problem. This is siege warfare.

不要向定义不清的问题扔 agent。这是攻城战。

The city will not fall. Your tokens will.

城不会陷。你的 token 会。

---

## 作战篇 —— agent 跑久了，一定变蠢

## CHAPTER II: WAGING WAR — Prolonged Agent Runs Make Them Stupid

我见过太多人让 agent 跑到第 8 次、第 10 次迭代。

I have seen too many people let agents run to iteration 8, iteration 10.

**这是在烧钱，不是在干活。**

**This is burning money, not doing work.**

### 我的规矩 My Rules

- **默认 3 次迭代**。到第 3 次还没结果，停。
- **Default 3 iterations**. At iteration 3 with no result, stop.
- **输出变长但质量下降** → 在填充，停。
- **Output grows but quality falls** → Filling, stop.
- **问同样的问题第二次** → 你缺上下文，补上或者停。
- **Asks same question twice** → You lack context, provide it or stop.
- **开始跟你 argue** → 它忘了谁是老板，停。
- **Starts arguing with you** → It forgot who is boss, stop.

> 胜久则钝兵挫锐。
> 
> Prolonged runs dull the blade and blunt the edge.

### 因粮于敌 Feed from the Enemy

用现有的数据、现有的输出、现有的文档。别让 agent 重新发明轮子。

Use existing data, existing outputs, existing documents. Do not let agents reinvent the wheel.

### 预算先行 Budget First

发之前先估算 token 成本。跑的时候盯着。

Estimate token cost before deployment. Watch it while running.

---

## 军形篇 —— 没把握的仗，不打

## CHAPTER IV: TACTICAL DISPOSITIONS — Do Not Fight Battles You Cannot Win

很多人发 agent 的时候，心里是没底的。

Many people deploy agents without confidence in their hearts.

"试试看吧。"

"Let's try and see."

**别试。试就是输。**

**Do not try. Trying is losing.**

### 发之前先问 Ask Before Deploying

- 最坏情况是什么？What is the worst case?
- 最坏了你能 roll back 吗？Can you roll back from the worst case?
- 有验证机制吗？Is there a validation mechanism?
- agent 不能碰的线画清楚了吗？Are the lines the agent cannot cross clearly drawn?

> 先为不可胜，以待敌之可胜。
> 
> First make yourself undefeatable. Then wait for the enemy to be defeatable.

### 高风险任务清单 High-Risk Task Checklist

- [ ] git branch 建好了 Git branch created
- [ ] 测试能跑 Tests can run
- [ ] roll back 流程写了 Rollback procedure documented
- [ ] agent 不能直接 push Agent cannot push directly
- [ ] 改完要人 review Changes require human review

这些都好了，再发。

When these are done, then deploy.

条件不成熟？等。

Conditions not mature? Wait.

---

## 兵势篇 —— 别只会一套

## CHAPTER V: ENERGY — Do Not Only Know One Way

**正**：标准流程。Research → Synthesis → Write。稳，但不会惊艳。

**Orthodox**: Standard workflow. Research → Synthesis → Write. Stable, but not brilliant.

**奇**：创意打法。中间插一个 Critique agent 挑战假设。险，但可能突破。

**Unorthodox**: Creative approach. Insert a Critique agent mid-flow to challenge assumptions. Risky, but may breakthrough.

> 凡战者，以正合，以奇胜。
> 
> In battle, engage with the orthodox, win with the unorthodox.

### 我的用法 My Usage

- 70% 的任务用正。稳。
- 70% of tasks use orthodox. Stable.
- 30% 的任务用奇。赌一把。
- 30% of tasks use unorthodox. Bet on it.
- 从来不用纯奇。那是赌博，不是打仗。
- Never use pure unorthodox. That is gambling, not warfare.

### 势 Shi — Momentum

Create momentum.

让每个 agent 的输出自然成为下一个 agent 的输入：

Let each agent's output naturally become the next agent's input:

```
Research → Synthesis → Critique → Writing → Validation
```

Each output feeds the next. No parallel chaos.

每个输出喂给下一个。不要并行混乱。

---

## 虚实篇 —— 避实击虚

## CHAPTER VI: WEAK POINTS AND STRONG — Avoid Strength, Attack Weakness

> 夫兵形象水，水之形，避高而趋下；兵之形，避实而击虚。
> 
> Military tactics are like water. Water avoids heights and flows downward. Military tactics avoid strength and attack weakness.

### Agent 不该做的 What Agents Should NOT Do

- Nuance requiring human judgment 需要人类判断的细微差别
- Creative decisions without clear criteria 没有清晰标准的创意决策
- Relationship management 关系管理
- Ethical judgments 伦理判断

### Agent 该做的 What Agents SHOULD Do

- Bulk work 批量工作
- Pattern recognition 模式识别
- First drafts 初稿
- Research and synthesis 研究和综合
- Iteration and variation 迭代和变体
- Cross-validation 交叉验证

**你 handle judgment。Agent handle volume.**

**You handle judgment. Agent handle volume.**

This is called: knowing where to strike.

这叫：知道打哪里。

### 致人而不致于人 Control Others, Do Not Be Controlled

Control where the agent focuses. Do not let it drift.

控制 agent 的焦点。别让它漂移。

Give clear boundaries. Enforce them.

给出清晰边界。执行它们。

---

## 军争篇 —— 最远的路可能最近

## CHAPTER VII: MANEUVERING — The Longest Path May Be Shortest

> 军争之难者，以迂为直，以患为利。
> 
> The difficulty of maneuvering is making the indirect direct, turning disadvantage into advantage.

10 分钟 planning 省 50 分钟 agent iterations.

10 minutes of planning saves 50 minutes of agent iterations.

Background research 防止 wrong-direction work.

Background research prevents wrong-direction work.

Validation 避免 redo everything.

Validation avoids redoing everything.

### 分合 Divide and Combine

Split complex tasks.

Each subtask → one focused agent.

Combine outputs systematically.

**别给一个 agent 十个 jobs。**

**Do not give one agent ten jobs.**

Give ten agents one job each. Then assemble.

给十个 agent 各一个 job。然后组装。

---

## 九变篇 —— 五种 agent 毛病

## CHAPTER VIII: VARIATION — Five Agent Faults

> 将有五危：必死，可杀也；必生，可虏也；忿速，可侮也；廉洁，可辱也；爱民，可烦也。
> 
> A general has five dangers: Reckless, can be killed. Cowardly, can be captured. Quick-tempered, can be insulted. Overly principled, can be shamed. People-pleasing, can be troubled.

| 毛病 Fault | 表现 Symptom | 对策 Counter |
|---|---|---|
| 必死 Reckless | 快速迭代但不思考 Fast iteration without thinking | 强制暂停，要求解释 Force pause, demand explanation |
| 必生 Cowardly | 过度谨慎，永不完成 Excessive caution, never completes | 设 deadline，强制输出 Set deadline, force output |
| 忿速 Quick temper | 跟用户 argue Argues with user | 冷静重述目标 Calmly restate goal |
| 廉洁 Over-optimizing | 追求完美忘记目标 Pursues perfection, forgets goal | 提醒"完成>完美" Remind "done > perfect" |
| 爱民 People-pleasing | 从不质疑错误指令 Never questions wrong instructions | 鼓励提出反对意见 Encourage objections |

### 将在外，君命有所不受 The General in the Field

Give agents autonomy within boundaries.

在边界内给 agent 自主权。

- Clear goal 清晰目标
- Clear constraints 清晰约束
- Freedom on method 方法自由
- Check-in points, not micromanagement 检查点，不是微观管理

---

## 行军篇 —— 看懂 agent 的信号

## CHAPTER IX: MARCHING — Read the Agent's Signals

Agent 不会说话，但它会发信号。

Agents cannot speak, but they send signals.

看不懂信号的人，活该输。

Those who cannot read signals deserve to lose.

### 危险信号 Danger Signals

| 信号 Signal | 什么意思 Meaning | 怎么办 Action |
|---|---|---|
| 问同样的问题第二次 Asks same question twice | 你给的信息不够 You lack context | 补上下文，或者停 Provide context, or stop |
| 输出越来越长 Output grows longer | 它在填充，不是思考 It is filling, not thinking | 强制简洁，或者停 Force conciseness, or stop |
| 过度自信 Overly confident | 可能在 hallucinate Probably hallucinating | 要来源，交叉验证 Demand sources, cross-verify |
| 回避某个问题 Avoids a question | 它不会 It cannot do it | 换方法，或者你上 Change method, or you do it |
| 循环论证 Circular reasoning | 卡住了 It is stuck | 重定向，或者停 Redirect, or stop |

**看到信号就干预。别等。**

**Intervene when you see signals. Do not wait.**

等到第 5 次迭代再干预？晚了。token 已经烧了。

Wait until iteration 5 to intervene? Too late. Tokens are already burned.

---

## 地形篇 —— 什么任务，什么打法

## CHAPTER X: TERRAIN — What Task, What Strategy

> 地形有通者，有挂者，有支者，有隘者，有险者，有远者。
> 
> There are six terrains: accessible, entangling, stalemate, narrow, dangerous, distant.

| 地形 Terrain | 任务类型 Task Type | 打法 Strategy |
|------|---------|--------------|
| 通形 Accessible | 清晰直接 Clear and direct | 标准流程，快 Standard workflow, fast |
| 挂形 Entangling | 容易陷进去 Easy to get stuck | 设时间限制，强制输出 Time limits, forced output |
| 支形 Stalemate | 信息不够 Insufficient information | 先收集，再决策 Gather first, decide later |
| 隘形 Narrow | 约束很多 Many constraints | 精确指令，严格验证 Precise instructions, strict validation |
| 险形 Dangerous | 高风险 High risk | 多重验证，保守 Multiple validations, conservative |
| 远形 Distant | 长链条 Long chain | 分阶段，设检查点 Phases, checkpoints |

**你连什么地形都不知道，就敢发兵？**

**You dare deploy without even knowing the terrain?**

---

## 九地篇 —— 别在小事上拼命

## CHAPTER XI: NINE GROUNDS — Do Not Fight Hard on Small Things

> 用兵之法，有散地，有轻地，有争地，有交地，有衢地，有重地，有圮地，有围地，有死地。
> 
> The art of war has nine grounds: scattered, light, contentious, open, intersecting, serious, difficult, desperate, death.

| 地 Ground | 任务类型 Task Type | 投入 Commitment |
|---|---------|----------------|
| 散地 Scattered | 日常琐事 Daily tasks | 轻量，快速 Light, fast |
| 轻地 Light | 低价值 Low value | 最小可用 Minimum viable |
| 争地 Contentious | 时间敏感 Time-sensitive | 优先资源 Priority resources |
| 重地 Serious | 高价值 High value | 多 agent，充分验证 Multi-agent, full validation |
| 死地 Death | 背水一战 No retreat | 全力以赴 Full commitment |

**大部分任务是散地和轻地。**

**Most tasks are scattered or light ground.**

别在轻地上用重地的打法。

Do not use serious ground strategy on light ground.

你会累死，而且不值得。

You will exhaust yourself, and it will not be worth it.

---

## 火攻篇 —— 工具是火，用火要小心

## CHAPTER XII: FIRE ATTACK — Tools Are Fire, Use Fire Carefully

代码执行、API 调用、搜索——这些都是"火"。

Code execution, API calls, search — these are all "fire".

Tools are fire. Fire helps you. Fire burns you.

工具是火。火帮你。火也烧你。

### 五种火 Five Fires

| 火 Fire | 是什么 What | 什么时候用 When to Use |
|---|--------|-----------|
| 人火 Human | 你给的数据 Data you provide | 先用这个 Use first |
| 积火 Accumulated | 缓存/之前的输出 Cached/previous outputs | 重用，别重新生成 Reuse, do not regenerate |
| 辎火 Supply | API/搜索 API/Search | 需要外部数据时 When external data needed |
| 库火 Arsenal | 代码执行 Code execution | 计算、处理 Computation, processing |
| 队火 Unit | 多 agent Multi-agent | 复杂协作 Complex collaboration |

### 行火必有因 Use Fire with Preparation

用火之前，想好：如果火失控了，怎么办？

Before using fire, think: What if the fire goes out of control?

Have fallback if tool fails.

工具失败时要有 fallback。

Validate tool outputs. Do not trust blindly.

验证工具输出。不要盲目相信。

---

## 用间篇 —— 别信单一来源

## CHAPTER XIII: SPIES — Do Not Trust a Single Source

Agent 说了一个事实。

The agent states a fact.

你信了？

You believe it?

**别信。**

**Do not believe.**

### 三反原则 Triple Verification Principle

至少三个独立来源交叉验证：

Cross-verify with at least three independent sources:

1. Agent's internal knowledge (Agent 的内部知识)
2. External search/API (外部搜索/API)
3. User-provided context (用户提供的上下文)

三个对得上 → 可以信。

All three align → Can trust.

对不上 → 有问题。查。

Do not align → There is a problem. Investigate.

### 先知 Know First

> 先知者，不可取于鬼神，不可象于事，不可验于度，必取于人，知敌之情者也。
> 
> Foreknowledge cannot be had from spirits, cannot be had by analogy, cannot be had by calculation. It must be obtained from people who know the enemy situation.

Know first.

先知。

Gather intelligence before making decisions.

在做决策之前收集情报。

Research before planning.

在规划之前研究。

Validate before committing.

在承诺之前验证。

Test before deploying.

在部署之前测试。

---

## 几个真实场景

## Real-World Scenarios

### 场景一：要不要用 agent 做竞品分析？

### Scenario 1: Should I Use an Agent for Competitor Analysis?

**先算五事：**

**Calculate the Five Constants:**

- 道：值得。Product launch 需要。✓
- Wisdom: Worth it. Product launch needs it. ✓
- 天：launch 还有 3 周，时候对。✓
- Timing: Launch in 3 weeks, timing is right. ✓
- 地：数据要收集，但有方向。✓
- Environment: Data needs collecting, but direction exists. ✓
- 将：research + synthesis agent 有。✓
- Capability: Research + synthesis agents available. ✓
- 法：流程清楚：收集→分析→呈现。✓
- Process: Workflow clear: collect→analyze→present. ✓

**五事全过。**

**All five constants pass.**

**七计：** 大概能赢 6 个。Task definition 还可以更清晰，但够了。

**Seven metrics:** Probably win 6 of 7. Task definition could be clearer, but sufficient.

**决策：发。**

**Decision: Deploy.**

**怎么发：**

**How to deploy:**

1. 先用现有报告（因间）Use existing reports first (local spies)
2. 再搜缺口（死间）Then search for gaps (doomed spies)
3. 预算 5k tokens Budget 5k tokens
4. 第 3 次迭代检查一次 Check at iteration 3

**结果：赢。**

**Result: Win.**

---

### 场景二：agent 卡住了，一直在问同样的问题

### Scenario 2: Agent Is Stuck, Keeps Asking the Same Question

**这是挂形。**

**This is entangling ground.**

**信号：重复提问 = 你缺上下文。**

**Signal: Repeated questions = You lack context.**

**怎么办：**

**What to do:**

```
停。
Stop.

补上它问的东西。
Provide what it is asking.

然后说：
Then say:

"用上面的信息，2 次迭代内给我结果。
"Use the information above, give me results within 2 iterations.
卡住就做合理假设，标出来。
If stuck, make reasonable assumptions, mark them.
格式：[你说]。"
Format: [you say]."
```

**别让它继续问。**

**Do not let it continue asking.**

问了第二次，你还答？那是你的问题，不是它的问题。

It asks a second time and you still answer? That is your problem, not its problem.

---

### 场景三：要重构生产代码

### Scenario 3: Refactoring Production Code

**这是险形。高风险。**

**This is dangerous ground. High risk.**

**先为不可胜：**

**First make yourself undefeatable:**

- [ ] git branch 建好了 Git branch created
- [ ] 测试能跑 Tests can run
- [ ] roll back 流程写了 Rollback procedure documented
- [ ] agent 不能直接 push Agent cannot push directly
- [ ] 改完要人 review Changes require human review

**这些都好了，再发。**

**When these are done, then deploy.**

**指令：**

**Instructions:**

```
只重构 authentication 模块。
Refactor only the authentication module.

约束：
Constraints:
- 不改 public API 签名 Do not change public API signatures
- 所有测试必须过 All tests must pass
- 最多 3 次迭代，然后我们 review Max 3 iterations, then we review
- 所有改动写文档 Document all changes

不确定的先问，别直接改。
If uncertain, ask first, do not change directly.
```

**这叫先胜后战。**

**This is called: victory before battle.**

---

### 场景四：Before/After

### Scenario 4: Before/After

**❌ 不懂孙子的人：**

**❌ Those who do not understand Sun Tzu:**

```
用户："做竞品分析，写个报告"
User: "Do competitor analysis, write a report"
agent：*开始搜*
agent: *starts searching*
      *找了 50 个来源*
      *finds 50 sources*
      *写了 20 页*
      *writes 20 pages*
      用户："这不是我想要的"
      user: "This is not what I wanted"
      *重来*
      *start over*

token 花了：50k
tokens spent: 50k
结果：垃圾
result: trash
```

**✅ 懂孙子的人：**

**✅ Those who understand Sun Tzu:**

```
用户："做竞品分析，写个报告"
User: "Do competitor analysis, write a report"

agent："等一下。
agent: "Wait.
1. 哪几个竞品？前三？还是全品类？
1. Which competitors? Top 3? Or entire category?
2. 分析什么？定价？功能？营销？
2. Analyze what? Pricing? Features? Marketing?
3. 给谁看？exec team？product team？
3. Who is the audience? exec team? product team?
4. 什么格式？slides？doc？spreadsheet？
4. What format? slides? doc? spreadsheet?
5. 什么时候要？"
5. When is it needed?"

用户："前三，功能 + 定价，给 product team，
User: "Top 3, features + pricing, for product team,
       spreadsheet，明天"
       spreadsheet, tomorrow"

agent："单 agent 能搞定。
agent: "Single agent can handle it.
预算 8k tokens。
Budget 8k tokens.
先用现有数据，再搜缺口。
Use existing data first, then search for gaps.
中间检查一次。"
Check in once in the middle."

用户："开始"
User: "Start"

agent：*Research → Synthesis → Format*
agent: *Research → Synthesis → Format*
      *检查："2/3 找到了，X 没有，用估算？"*
      *Check-in: "Found 2/3, X missing, use estimates?"*
用户："用估算，标成假设"
User: "Use estimates, mark as assumptions"

agent：*交叉验证了定价*
agent: *Cross-verified pricing*
      *交付：8k tokens，方向对*
      *Delivered: 8k tokens, right direction*

token 花了：8k
tokens spent: 8k
结果：对
result: correct
```

**省了 84% 的 token。**

**Saved 84% of tokens.**

**区别在哪里？**

**What is the difference?**

**区别在始计篇。**

**The difference is in Laying Plans.**

一个没算就发。一个算了再发。

One deploys without calculating. One calculates then deploys.

---

## 最后的话

## Final Words

我写这 13 章，不是让你背。

I did not write these 13 chapters for you to memorize.

是让你在做每一个 agent 决策之前，**停一下**。

I wrote them to make you **pause** before every agent decision.

停一下，想一下：

Pause. Think:

- 这任务值得做吗？Is this task worth doing?
- 现在是时候吗？Is now the right time?
- 我赢面大吗？Do I have the advantage?
- 最坏了能 roll back 吗？Can I roll back from the worst case?
- 我读懂信号了吗？Am I reading the signals?
- 三源验证了吗？Have I verified with three sources?

想清楚了再发。

Think clearly, then deploy.

If you cannot answer, do not deploy.

答不上来，别发。

**发出去，就要赢。**

**When you deploy, you win.**

---

## 文件 Files

| 文件 File | 干嘛的 Purpose |
|------|--------|
| `SKILL.md` | 这个文件 This text |
| `references/thirteen-chapters.md` | 13 篇详解 Detailed mappings |
| `scripts/assess-task.py` | 五事七计打分 Five constants scoring |
| `scripts/quick-decision.py` | 快速决策 Quick decision |
| `CARD.md` | 可打印决策卡 Printable reference |

---

## 相关 Related

- [thinking-skills](https://github.com/wanikua/thinking-skills) — 20 个思维框架 20 thinking frameworks
- [awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) — skill 合集 Skill collection
