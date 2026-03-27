# Tech Role Research: Proactive AI Assistant Context

> **Purpose:** What a proactive AI assistant needs to know to help tech professionals without being asked.  
> **Focus:** Daily rhythms, pre/post task needs, time-sensitive triggers, and data sources.  
> **Last updated:** 2026-03-17

---

## Table of Contents

1. [Software Developers / Engineers](#1-software-developers--engineers)
2. [DevOps / SRE Engineers](#2-devops--sre-engineers)
3. [Product Managers](#3-product-managers)
4. [UX/UI Designers](#4-uxui-designers)
5. [Data Scientists / Analysts](#5-data-scientists--analysts)
6. [Cross-Role Patterns](#6-cross-role-patterns)

---

## 1. Software Developers / Engineers

### 1.1 Daily / Weekly Task Rhythm

**Daily:**
- Pull latest code, check for merge conflicts on active branches
- Review assigned GitHub/Jira/Linear tickets for updates or new comments
- Attend standup (usually 09:00-09:30) -- need to report what they did yesterday, what they're doing today, any blockers
- Code, test, debug for the bulk of the day
- Respond to code review requests (PRs waiting on their input)
- Check CI/CD pipelines -- did last night's build pass?
- Slack/Teams: watch for mentions, questions from colleagues, escalations
- Write or update unit/integration tests alongside new code

**Weekly:**
- Sprint planning (beginning of sprint) -- estimate and commit to tickets
- Sprint retrospective / review (end of sprint) -- demo work, reflect
- Architecture or design discussions (ad hoc or scheduled)
- 1:1 with manager
- Code review sessions (formal or informal)
- Dependency/library update checks (especially security patches)

### 1.2 What They Need BEFORE Tasks / Meetings

**Before standup:**
- Summary of what they actually finished yesterday (vs. what they planned)
- Current status of their PR(s) -- any review comments they need to address?
- Any failing tests or build failures overnight
- New tickets assigned to them since last standup

**Before sprint planning:**
- Velocity from last sprint (how many story points completed)
- Outstanding items from the backlog that are up for discussion
- Tech debt items they want to flag
- Any external dependencies that might block upcoming work

**Before code review / PR:**
- Context on what the PR is trying to solve
- Whether the CI is green
- Any related tickets or prior discussions

**Before architecture meetings:**
- Previous ADRs (Architecture Decision Records) relevant to the topic
- Current system diagrams or relevant docs
- Notes from prior discussions on the same topic

### 1.3 Follow-Up AFTER Tasks

- After merging a PR: check deployment status, monitor for errors in staging/prod
- After a bug fix: verify fix in staging, confirm with reporter
- After sprint: update ticket statuses, close resolved issues, write up release notes if applicable
- After an incident: write or contribute to a post-mortem document
- After a code review: action feedback (or reply explaining why not), re-request review
- After deployment: monitor error rates, logs, latency for 15-30 min

### 1.4 Time-Sensitive Triggers

| Trigger | Typical Cadence | Why It Matters |
|---|---|---|
| Sprint deadlines | Every 1-2 weeks | Tickets need to be merged and tested before sprint closes |
| PR review SLA | 24-48h | PRs left open cause merge conflicts and block teammates |
| Dependency security alerts | As they arrive (Dependabot etc.) | Critical CVEs need patching fast |
| On-call rotation start | Weekly/bi-weekly | Developer needs to know they're on-call before it starts |
| Release freeze dates | Scheduled | No merges to main during freeze window |
| Deployment windows | Scheduled or ad hoc | Need to be present for production deployments |
| Build/CI failures | Immediately | Broken main branch blocks the whole team |
| License renewals (dev tools) | Annual | IDE licenses, GitHub plans, cloud credits |

### 1.5 Data Sources They Monitor

- **Version control:** GitHub, GitLab, Bitbucket -- PR status, CI checks, branch status
- **Issue trackers:** Jira, Linear, GitHub Issues, Asana -- assigned tickets, sprint board
- **CI/CD:** GitHub Actions, CircleCI, Jenkins, Buildkite -- build/test/deploy status
- **Error tracking:** Sentry, Datadog, Rollbar -- new errors in their code's area
- **Logs:** CloudWatch, Datadog, Papertrail -- especially after deployments
- **Slack/Teams channels:** #alerts, #deployments, #engineering, #incidents
- **Dependency scanners:** Dependabot, Snyk, Renovate -- security and update PRs
- **Documentation:** Confluence, Notion, internal wikis

### 1.6 "How Did It Know?" Moments

- "Your PR has been waiting for review for 18 hours -- want me to ping the reviewer?"
- "The main branch CI is red since 2am -- looks like John's merge broke the auth tests."
- "Sprint ends in 2 days and you have 3 open tickets still in progress."
- "Dependabot flagged a critical CVE in lodash -- there's a fix available."
- "You're on-call starting Thursday. Here's what was paged last week."
- "Deployment went live 20 min ago -- Sentry is showing 3 new errors in checkout flow."

---

## 2. DevOps / SRE Engineers

### 2.1 Daily / Weekly Task Rhythm

**Daily:**
- Check overnight alerts and on-call logs -- anything that paged?
- Review infrastructure health dashboards (CPU, memory, disk, network)
- Scan for failed jobs, stuck pipelines, or queued deployments
- Respond to developer requests (environment issues, pipeline failures, access)
- Review and merge infra PRs (Terraform, Kubernetes configs, Helm charts)
- Apply patches or updates to infrastructure (especially security patches)
- Monitor costs vs. budget on cloud dashboards

**Weekly:**
- Incident review / post-mortem meetings
- Capacity planning check (are we going to hit limits?)
- Security audit review or vulnerability scan triage
- On-call handover (review week's incidents with incoming on-call)
- Update runbooks based on incidents
- Infrastructure cost review

### 2.2 What They Need BEFORE Tasks / Meetings

**Before an on-call shift:**
- Summary of recent incidents and known flaky alerts
- Current system health status
- Any active deployment or change freeze windows
- Runbook locations for the most common alerts

**Before an incident response:**
- Current system topology / service map
- Recent deployments (what changed in the last 24h?)
- Historical context on similar incidents
- Escalation contacts

**Before deployment:**
- Change advisory board (CAB) approval if required
- Rollback plan documented
- Health checks and monitors ready
- Notify stakeholders of potential downtime window

**Before capacity planning meeting:**
- Growth trend data (past 90 days traffic, storage, compute)
- Projected growth from product roadmap
- Current reserved vs. on-demand cost split
- Upcoming campaigns or launches that will spike load

### 2.3 Follow-Up AFTER Tasks

- After an incident: write post-mortem within 24-48h, assign action items
- After a deployment: verify health checks pass, monitor for 15-30 min
- After adding a new service: update runbooks, alerting, dashboards
- After a security patch: document what was patched, close the CVE ticket
- After on-call rotation: hand over context to next engineer, note anything unresolved
- After capacity changes: update cost projections, notify finance if significant

### 2.4 Time-Sensitive Triggers

| Trigger | Typical Cadence | Why It Matters |
|---|---|---|
| PagerDuty / OpsGenie alert | Real-time | Direct action required -- SLA on response time |
| SSL/TLS certificate expiry | Monitor constantly, 30/14/7 day warnings | Expired cert = site down for everyone |
| On-call rotation changeover | Weekly/bi-weekly | Clean handover prevents gaps |
| Deployment windows | Scheduled | Coordinate with teams, avoid conflicts |
| Cloud cost anomalies | Daily budget checks | Runaway instances can cost thousands overnight |
| Security CVE advisories | As published | High/critical need action within hours |
| Database maintenance windows | Monthly | Downtime for upgrades needs coordination |
| License / subscription renewals | Annual/monthly | Cloud, tooling, monitoring platforms |
| Compliance audit dates | Quarterly/annual | SOC2, ISO27001 evidence collection deadlines |
| DR (disaster recovery) test | Quarterly/annual | Scheduled rehearsal -- needs prep |

### 2.5 Data Sources They Monitor

- **Monitoring:** Datadog, Prometheus/Grafana, New Relic, CloudWatch
- **Alerting:** PagerDuty, OpsGenie, VictorOps
- **Infrastructure as code:** Terraform, Pulumi (GitHub repos)
- **Kubernetes:** kubectl, Lens, ArgoCD, Rancher
- **Cloud consoles:** AWS, GCP, Azure -- cost explorer, service health
- **Security scanning:** Snyk, Trivy, AWS Security Hub, Qualys
- **Log aggregation:** Splunk, Elastic, Datadog Logs, Loki
- **CI/CD:** GitHub Actions, Jenkins, Concourse, Spinnaker
- **Status pages:** Internal + third-party (AWS Status, PagerDuty, Stripe, etc.)
- **Ticket trackers:** Jira, ServiceNow for infra requests

### 2.6 "How Did It Know?" Moments

- "Your SSL cert for api.company.com expires in 12 days."
- "AWS Cost Explorer shows a $800 anomaly in EC2 spend since yesterday -- looks like a GPU instance left running."
- "Post-mortem doc for last night's incident is still empty -- it's been 36h."
- "Kubernetes node pool is at 89% capacity -- might want to scale before the marketing campaign launch Friday."
- "3rd-party service (Stripe) is reporting degraded performance on their status page."
- "Your on-call shift starts in 2 hours. Here's a summary of alerts from this week."

---

## 3. Product Managers

### 3.1 Daily / Weekly Task Rhythm

**Daily:**
- Check email and Slack for stakeholder questions, escalations, or blockers
- Review product metrics dashboard -- any anomalies in key metrics?
- Prioritize and respond to incoming feature requests, bugs, or support escalations
- Update and groom the product backlog
- Sync with engineers on any blockers or ambiguity in requirements
- Review and approve or give feedback on designs, specs, or prototypes
- Write or refine user stories / acceptance criteria

**Weekly:**
- Sprint planning (or equivalent prioritization session)
- Stakeholder updates / roadmap reviews
- Customer calls or user interviews (1-3 per week ideally)
- Metrics review meeting with analytics team
- 1:1 with engineering lead and/or design lead
- Competitive research or market intelligence review
- Write or update PRDs (Product Requirements Documents)

### 3.2 What They Need BEFORE Tasks / Meetings

**Before sprint planning:**
- Ranked backlog with clear acceptance criteria on top items
- Engineering capacity this sprint (any holidays, other commitments?)
- Last sprint velocity
- Any new critical bugs or customer escalations that must be prioritized

**Before stakeholder presentations:**
- Latest metrics on the feature/area being discussed
- Current roadmap status (what's shipped, what's in progress, what's planned)
- Key wins to highlight; known risks to acknowledge
- Customer quotes or data supporting decisions

**Before customer calls:**
- Account history -- who they are, what they've asked for before
- Support tickets or complaints from this customer
- Current product usage data for this customer
- Specific topics they asked to discuss

**Before roadmap reviews:**
- Strategic goals / OKRs for the quarter
- Dependencies on other teams
- What's been deprioritized and why (for when stakeholders ask)

### 3.3 Follow-Up AFTER Tasks

- After sprint review: update roadmap with what actually shipped, communicate to stakeholders
- After customer calls: document insights in a customer feedback tool (Productboard, Notion), share relevant quotes with the team
- After feature launch: monitor key metrics (adoption, errors, support tickets) for 1-2 weeks
- After user interviews: synthesize findings into insights, update personas or jobs-to-be-done framework
- After a bug report escalation: follow up with the reporter with resolution timeline
- After a PRD review: incorporate feedback, get sign-off, hand off to engineering

### 3.4 Time-Sensitive Triggers

| Trigger | Typical Cadence | Why It Matters |
|---|---|---|
| Sprint start/end | Every 1-2 weeks | Planning and review -- the core PM rhythm |
| OKR / goal check-ins | Monthly/quarterly | Must report progress and re-prioritize |
| Quarterly roadmap planning | Quarterly | Major stakeholder alignment event |
| Feature launch date | As committed | External commitments to customers, marketing, sales |
| Customer renewal meetings | Monthly/annual | Sales loops in PM when customers have product concerns |
| Competitor product releases | As they happen | Need to assess impact on roadmap |
| Usage/metric anomalies | Daily/weekly | Drop in adoption or spike in errors needs immediate triage |
| Board presentations | Quarterly | Executive-level metrics and roadmap review |
| Beta program cutoffs | Per launch | Managing beta users, feedback collection deadlines |

### 3.5 Data Sources They Monitor

- **Analytics:** Mixpanel, Amplitude, Heap, PostHog, GA4 -- user behavior, funnel metrics
- **Product management:** Productboard, Jira, Linear, Asana -- backlog, roadmap
- **Customer feedback:** Intercom, Zendesk, UserVoice, Typeform -- support tickets, NPS
- **Business metrics:** Looker, Tableau, internal dashboards -- revenue, retention, churn
- **Research tools:** Dovetail, Notion, Miro -- user research synthesis
- **Competitive intel:** G2, Capterra, Twitter/X, competitor changelogs, Product Hunt
- **Communication:** Slack (multiple channels), email, Confluence for specs
- **Calendar:** Packed with syncs -- awareness of what's coming up is critical

### 3.6 "How Did It Know?" Moments

- "Your sprint ends Friday and 40% of committed tickets are still in progress."
- "Activation rate dropped 8% this week -- correlates with the onboarding change shipped Monday."
- "Competitor X just shipped a feature your customers have been requesting for 6 months."
- "Customer Acme Corp has 3 open support tickets and their renewal is in 30 days."
- "You have a stakeholder roadmap presentation tomorrow -- here's the latest metrics summary."
- "It's been 3 weeks since the feature launched -- no post-launch metrics review has happened yet."
- "Sarah from the sales team just pinged about a customer escalation that has a ticket in Jira -- here's the context."

---

## 4. UX/UI Designers

### 4.1 Daily / Weekly Task Rhythm

**Daily:**
- Check design tool notifications (Figma comments from engineers/PMs)
- Review and respond to feedback on shared designs
- Continue active design work (wireframes, high-fi mockups, prototypes)
- Attend standups (participate in sprint ceremonies alongside engineering)
- Collaborate with engineers on implementation questions ("what did you mean by this component?")
- Review implemented designs in staging vs. Figma specs -- catch discrepancies

**Weekly:**
- Design critique / review session with the design team
- User research sessions (interviews, usability tests)
- Handoff sessions with engineering (walking through specs)
- Sync with PM on upcoming work and priorities
- Update and maintain the design system / component library
- Review competitor apps or design inspiration for ongoing work

### 4.2 What They Need BEFORE Tasks / Meetings

**Before a design critique:**
- Designs loaded and ready to share (links, not just files)
- Summary of the problem being solved and constraints
- Specific questions to get feedback on (don't let critiques become free-for-alls)

**Before user research sessions:**
- Discussion guide / interview script prepared
- Prototype or mockup ready if doing usability testing
- Background on the participant (demographics, experience level)
- Recording consent forms ready

**Before engineering handoff:**
- All assets exported (icons, images at correct sizes/formats)
- Figma specs complete (padding, spacing, colors using design tokens)
- Edge cases and error states designed (not just the happy path)
- Component names aligned with what engineers already call things

**Before a stakeholder design review:**
- Design rationale documented ("we tried X, Y, but went with Z because...")
- Accessibility notes (color contrast, touch target sizes)
- Mobile + desktop views ready if responsive

### 4.3 Follow-Up AFTER Tasks

- After usability tests: synthesize findings into actionable insights, share with PM and engineering
- After engineering handoff: stay available for implementation questions; do QA review when feature is in staging
- After shipping: compare the implemented design vs. Figma; note discrepancies for future sprints
- After design critique: revise designs based on feedback, document decisions
- After a design system update: notify engineering of changed components; update documentation

### 4.4 Time-Sensitive Triggers

| Trigger | Typical Cadence | Why It Matters |
|---|---|---|
| Engineering sprint start | Every 1-2 weeks | Designs must be ready 1 sprint ahead of engineering |
| Usability test sessions | Scheduled | Participants are booked -- prep must be done |
| Design review with leadership | Monthly/quarterly | High-stakes -- needs polish and narrative |
| Feature launch dates | As committed | Final design QA must happen before launch |
| Design system version releases | Planned | Coordinated with engineering -- breaking changes need notice |
| Research recruitment deadlines | Per project | Participant recruitment has lead time (1-2 weeks) |
| Figma / tool license renewals | Annual | Seat-based -- needs admin action |
| Accessibility audit deadlines | Quarterly/annual | Legal/compliance risk if not addressed |

### 4.5 Data Sources They Monitor

- **Design tools:** Figma, Sketch, Adobe XD -- where their work lives; comments are often action items
- **User research:** UserTesting, Maze, Lookback, Hotjar, FullStory -- qualitative and behavioral data
- **Analytics (read access):** Mixpanel, Amplitude -- to understand how designs actually perform
- **Design system:** Storybook, Zeroheight -- component documentation
- **Project management:** Jira, Linear, Asana -- tracking design tickets and sprint work
- **Collaboration:** Miro, FigJam -- workshops and whiteboarding
- **Inspiration / competitive:** Dribbble, Behance, Mobbin, competitor apps
- **Accessibility:** Colour Contrast Analyser, axe DevTools, Wave

### 4.6 "How Did It Know?" Moments

- "You have a Figma comment from the lead engineer that's 2 days old -- might be blocking implementation."
- "Sprint starts Monday and the checkout redesign still has no error states designed."
- "Your usability test is tomorrow at 2pm -- the prototype link is broken (404)."
- "The design system 'Button' component was updated last week -- engineering is still using the old one in 3 files."
- "FullStory shows users rage-clicking on the non-interactive element in the new dashboard."
- "The accessibility audit flagged 4 contrast failures in the new color palette."

---

## 5. Data Scientists / Analysts

### 5.1 Daily / Weekly Task Rhythm

**Daily:**
- Check scheduled pipeline runs -- did overnight ETL jobs succeed?
- Review data quality alerts -- schema changes, null spikes, metric anomalies
- Respond to ad hoc data requests from PMs, marketing, or leadership
- Continue active analysis or model development work
- Monitor model performance (for deployed ML models) -- drift, accuracy degradation
- Update dashboards with correct data if anomalies were found

**Weekly:**
- Attend weekly metrics review meeting -- present key trends
- Stakeholder reporting (weekly business review decks, KPI updates)
- Data pipeline maintenance and optimization
- Experiment analysis (A/B test results -- collect, analyze, report)
- Model retraining (if on schedule)
- Team sync -- share findings, coordinate on shared datasets

### 5.2 What They Need BEFORE Tasks / Meetings

**Before a metrics review meeting:**
- Pre-built dashboards refreshed and correct
- Narrative for notable changes (week-over-week, month-over-month)
- Any anomalies explained or flagged with caveats
- Comparison to targets/OKRs

**Before presenting A/B test results:**
- Statistical significance confirmed (p-value, confidence intervals)
- Sample size and duration (was it run long enough?)
- Segment breakdown (did it help all users equally or just some?)
- Business impact translated to revenue/retention terms

**Before a data model / ML deployment:**
- Offline metrics (accuracy, precision, recall, AUC) documented
- Shadow mode or canary results if available
- Rollback plan if model degrades
- Monitoring dashboards ready

**Before a stakeholder data request:**
- Clarify the actual question behind the request (what decision will this inform?)
- Understand the timeframe and granularity needed
- Know any known data quality issues that might affect the answer

### 5.3 Follow-Up AFTER Tasks

- After delivering analysis: follow up to check if the decision was made / outcome
- After A/B test call: archive experiment results, document learnings, update experiment log
- After a pipeline fix: run backfill if historical data was affected; document root cause
- After a model deployment: monitor for 2-4 weeks for drift or performance degradation
- After a dashboard delivery: check with stakeholders that it answers their questions; iterate
- After a data incident (wrong numbers went out): send correction, document what went wrong and why

### 5.4 Time-Sensitive Triggers

| Trigger | Typical Cadence | Why It Matters |
|---|---|---|
| Scheduled pipeline runs | Daily/hourly | Failure = stale dashboards, bad decisions |
| Weekly business review | Weekly | Leadership needs metrics ready Monday morning |
| Month-end / quarter-end reporting | Monthly/quarterly | Finance and exec dashboards need to close on time |
| A/B test minimum runtime | Per experiment | Calling tests too early causes false positives |
| Model drift alerts | Ongoing | Production model accuracy degrading silently |
| Data schema changes | As deployed | Upstream schema change can silently break pipelines |
| Regulatory/compliance reporting | Quarterly/annual | GDPR data requests, financial reporting |
| ETL SLA breach | Real-time | Dashboards used in morning standups need to be fresh |
| Budget/attribution cycle | Monthly | Marketing attribution models needed for budget decisions |

### 5.5 Data Sources They Monitor

- **Data warehouses:** Snowflake, BigQuery, Redshift, Databricks -- source of truth for analysis
- **Pipeline orchestration:** Airflow, dbt, Prefect, Dagster -- job success/failure
- **Data quality:** Monte Carlo, Great Expectations, dbt tests -- anomaly and freshness alerts
- **BI / dashboards:** Looker, Tableau, Metabase, Mode, Redash -- both authoring and consuming
- **ML platforms:** MLflow, Weights & Biases, SageMaker, Vertex AI -- model tracking
- **Notebooks:** Jupyter, Databricks notebooks, Google Colab -- active analysis
- **Experiment platforms:** Optimizely, LaunchDarkly, in-house -- A/B test status
- **Monitoring:** Grafana, Datadog (for pipeline health), CloudWatch
- **Project trackers:** Jira, Asana, Notion -- data requests queue

### 5.6 "How Did It Know?" Moments

- "Your nightly Airflow DAG failed at 2am -- the revenue dashboard will be stale for the 9am leadership meeting."
- "The A/B test has reached statistical significance (p=0.03) -- you've been running it for 3 weeks now."
- "Week-over-week conversion rate is down 12% -- correlates with the iOS update shipped Tuesday."
- "dbt tests flagged 3% null rate in the user_id column -- this was 0% last week."
- "The churn prediction model's accuracy has dropped from 84% to 71% over the past 30 days."
- "Monthly reporting is due in 3 days -- the finance dashboard hasn't been updated yet this month."
- "Upstream schema change detected: the `events` table dropped the `device_type` column -- 4 of your dashboards depend on it."

---

## 6. Cross-Role Patterns

### 6.1 Universal Time-Sensitive Triggers (All Roles)

| Trigger | Who It Affects |
|---|---|
| On-call / incident alert | DevOps, SRE, sometimes Devs |
| Sprint start / end | Devs, Designers, PMs |
| Quarterly planning | All roles |
| 1:1 with manager | All roles |
| New hire onboarding (when they're the buddy) | All roles |
| Sick day / OOO -- covering someone else | All roles |
| Tool / license renewals | All roles (different tools) |

### 6.2 The "1 Sprint Ahead" Rule

The design -> engineering -> deployment pipeline means:
- **Designers** need to be 1 sprint ahead of engineers (designs ready before sprint starts)
- **PMs** need to be 1 sprint ahead of designers (requirements clear before design starts)
- **DevOps** needs to be ready before launch (infra provisioned before code deploys)

A proactive assistant should warn when this pipeline looks at risk.

### 6.3 Monday Morning vs. Friday Afternoon Patterns

**Monday morning needs:**
- What happened over the weekend? (alerts, pipeline failures, competitor news)
- What's this week's priority? (sprint goals, meetings, deadlines)
- What is blocking the team from starting?

**Friday afternoon needs:**
- What got done this week vs. what was planned?
- What needs to be handed over before the weekend?
- Any alerts or deployments to watch over the weekend?
- Is anything risky going into the weekend? (deployments too close to EOD)

### 6.4 Emotions and State to Watch For

A proactive assistant should read context clues:

- **Deadline pressure:** Cluster of late-night activity, many open tickets, messages getting shorter
- **Post-incident stress:** Recent PagerDuty alerts, rushed deployments, post-mortem docs pending
- **Blocked / frustrated:** PR sitting without review for 48h, pipeline broken for hours
- **Pre-launch anxiety:** Launch is imminent, many open issues, stakeholder pings increasing
- **Context-switching overload:** Many different topics in messages in one day -- might need help prioritizing

### 6.5 What a Proactive AI Should Always Know

For any tech professional, the assistant should always have fresh awareness of:

1. **What's on fire right now** -- active incidents, failing pipelines, blocked PRs
2. **What's coming up in the next 48h** -- meetings, deadlines, sprint events
3. **What's overdue** -- tickets, reviews, follow-ups, documentation
4. **What changed recently** -- deploys, schema changes, model updates, competitor news
5. **What the normal baseline is** -- so anomalies are obvious

### 6.6 The "They Won't Think to Ask" List

Things people know they need but forget to check:

- Certificate expiry dates
- Cost anomalies on cloud bills
- Stale documentation (last updated 18 months ago -- probably wrong)
- Metrics that haven't moved in weeks (often means the tracking is broken, not the product)
- PRs that have been open too long (authors forget, reviewers forget)
- A/B tests that were meant to be temporary but are still running
- Feature flags left on after launch
- Secrets or API keys that are about to expire
- Contractor/vendor access that should have been revoked

---

*End of research document. This file is a living reference -- update as new patterns emerge.*
