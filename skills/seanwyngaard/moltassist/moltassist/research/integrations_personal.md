# Pulse -- Personal & Consumer Integrations Research
**"Start with the customer experience and work backwards to the technology."** -- Steve Jobs

This document maps each integration to the specific human moments it unlocks for Pulse. Not features -- moments. The gym session someone's about to skip. The bill due tomorrow. The car that's been overdue for a service for 3,000 km.

---

## Table of Contents
1. [Health & Fitness](#1-health--fitness)
2. [Finance & Banking](#2-finance--banking)
3. [Home & Lifestyle](#3-home--lifestyle)
4. [Travel & Transport](#4-travel--transport)
5. [Entertainment & Media](#5-entertainment--media)
6. [Privacy, Sensitivity & Trust](#6-privacy-sensitivity--trust)

---

## 1. Health & Fitness

### 1.1 Apple HealthKit / Health API

**What it exposes:**
- Steps, distance, active calories, resting calories, VO2 max
- Heart rate (resting, walking, workout)
- Sleep: time in bed, sleep stages (core, deep, REM), sleep duration
- Blood oxygen, HRV (heart rate variability)
- Menstrual cycle data
- Body weight, BMI, body fat %
- Nutrition logs (if user logs food)
- Medications (if logged)
- Workout sessions (type, duration, distance, HR)
- Blood pressure, blood glucose (from connected devices)

**API access model:** HealthKit is iOS-only, on-device. No cloud API -- requires a native iOS app with HealthKit entitlement that the user explicitly authorises. Data can be read in real-time or as historical queries. Requires Apple developer account + HealthKit entitlement approval.

**MCP server:** No official MCP server. Community project `mcp-apple-health` exists but reads from exported XML -- not live. Pulse would need a native iOS companion app or a Health Records integration.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Sleep debt warning** | It's Monday morning. User slept 5h last night, average 5.8h this week. Calendar shows a big presentation at 2pm. | *"Heads up -- you're running on 5 hours. You've got your product review at 2pm. Might be worth a coffee and a 20-min walk before it, not a heavy lunch."* |
| **Rest day nudge** | User hit the gym 5 days in a row. HRV dropped 18% below baseline. They have a workout blocked for today. | *"Your HRV's dipped pretty hard this week. Your body's flagging recovery mode. Could be worth making today a walk instead of a session."* |
| **Skipped workout pattern** | User has skipped their Tuesday gym session 3 weeks running. It's Monday night. | *"Tomorrow's your Tuesday session. You've skipped the last three -- not judging, just flagging. Want me to move it or hold it?"* |
| **Heart rate anomaly** | Resting HR is 12 bpm above the user's 30-day average with no obvious workout context. | *"Your resting HR is running high today -- 78 vs your usual 66. Could be stress, dehydration, or something worth watching. How are you feeling?"* |
| **Activity milestone** | User is 847 steps from their all-time monthly step record with 2 hours left in the day. | *"You're 847 steps from your all-time step record for March. A 7-minute walk gets you there."* |

---

### 1.2 Strava API

**What it exposes:**
- All athlete activities (runs, rides, swims, hikes, etc.) with GPS route, pace, distance, elevation, HR, cadence, power
- Segment performances (KOMs, PRs)
- Personal records (fastest 5K, longest ride, etc.)
- Athlete stats (year-to-date totals)
- Gear (shoes, bikes with mileage tracking)
- Followers/following, kudos, clubs
- Training load estimates (suffer score)

**API access model:** OAuth2, REST. Free tier limited (1,000 req/day, 100 req/15min). Activity data available within ~30 seconds of upload via webhook. Webhooks available for new activity events. No bulk historical export without manual auth.

**MCP server:** Yes -- `mcp-strava` exists (community). Exposes athlete profile, recent activities, and gear data as tools.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Shoe retirement alert** | User's primary running shoes have logged 685km. Recommended retirement is 500-800km. | *"Your Asics Nimbus are at 685km -- getting close to retirement territory. You've been logging some knee pain too. Could be connected."* |
| **PR window** | Weather is perfect, user's recent training is strong, and they're 8 seconds off their 5K PR. | *"Conditions are ideal this morning -- 14C, low wind. Your recent sessions suggest you're in shape to crack your 5K PR. Just saying."* |
| **Training gap** | User hasn't logged an activity in 11 days. They usually run 4x/week. | *"It's been 11 days since your last run. Everything okay? No pressure -- just checking in."* |
| **Race prep** | User registered for a half marathon (via Strava or calendar). It's 6 weeks out and their long run has stalled at 12km. | *"Your half marathon is 6 weeks away. You've been capped at 12km long runs -- you'll want to push 16-18km in the next 3 weeks to feel comfortable on the day."* |

---

### 1.3 Fitbit API / Google Fit

**What it exposes (Fitbit):**
- Steps, floors, distance, active minutes
- Sleep stages, sleep score
- Resting HR, intraday HR (1-min resolution -- premium tier only)
- Active Zone Minutes
- Weight, body fat, BMI (if scale connected)
- Food log, water intake
- Female health tracking
- SpO2 (select devices)
- Skin temperature variation

**What it exposes (Google Fit):**
- Activity sessions (type, duration, distance)
- Steps, calories, heart points
- Sleep data
- Weight, blood pressure, blood glucose
- Less granular than HealthKit or Fitbit

**API access model (Fitbit):** OAuth2, REST. Webhooks (subscriptions) for near-real-time data. Intraday data requires personal app approval (email Fitbit). Google Fit REST API deprecated for new apps in 2024 -- Health Connect (Android) is the replacement.

**MCP server:** No official MCP. Community `mcp-fitbit` exists for basic activity/sleep reads.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Low activity day** | It's 6pm, user has only 1,200 steps. They usually hit 8,000+. | *"You've barely moved today -- 1,200 steps. Even a 15-minute walk would make a difference. Want me to block 15 mins on your calendar?"* |
| **Sleep score crash** | Fitbit sleep score dropped to 62 ("Fair"). User has an important call at 9am. | *"Sleep score was 62 last night -- your body didn't get much deep sleep. Hydrate before your 9am and keep it light this morning."* |
| **Weight trend** | Weight has crept up 2.1kg over the past 45 days despite regular activity. | *"Your weight's up about 2kg over the last 6 weeks, even with consistent workouts. Could be worth looking at what's changed in the food department."* |

---

### 1.4 Whoop API

**What it exposes:**
- Recovery score (0-100) -- composite of HRV, resting HR, sleep performance
- Strain score -- cardiovascular load for the day
- Sleep stages, sleep need, sleep debt
- Respiratory rate
- Blood oxygen during sleep
- Cycle data (24h windows)

**API access model:** Not officially public. WHOOP has an undocumented API that third-party apps access via OAuth. As of 2024, WHOOP launched a developer platform in beta -- limited access, invite-based. No webhooks confirmed publicly.

**MCP server:** Community `mcp-whoop` exists. Limited -- reads daily recovery, strain, and sleep data.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Red recovery, heavy day planned** | Recovery is 23% (Red). User has a gym session + evening social event. | *"Recovery is 23% today -- your body's asking for a rest. Up to you, but a light session would serve you better than pushing it."* |
| **Green recovery, rest day scheduled** | Recovery is 91% (Green). User has a rest day planned. | *"You're in the green -- 91% recovery, highest this week. If you were thinking about a session today, your body's ready for it."* |
| **Sleep debt accumulating** | Sleep debt has built to 4.5 hours over the week. It's Thursday. | *"You're carrying 4.5 hours of sleep debt this week. Friday night might be a good reset -- early night, no alarm."* |

---

### 1.5 Garmin Connect API

**What it exposes:**
- All activity types (running, cycling, swimming, strength, yoga, etc.)
- Body Battery (energy/fatigue score)
- Stress score (throughout the day from HR variability)
- Training Status (peaking, productive, unproductive, detraining)
- Training Load
- VO2 max, fitness age
- Race predictor times
- Sleep stages, sleep score
- Steps, intensity minutes
- Golf rounds (if applicable)
- Daily health snapshot

**API access model:** Garmin Health API (enterprise/B2B) requires partnership agreement with Garmin. The Connect API is consumer-facing via OAuth2 with limited public access. Webhook support for new activities. Rate limited. Best accessed via partnership programme.

**MCP server:** No official MCP. Limited community implementations.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Body Battery empty** | It's 3pm. Body Battery is at 8. User has a dinner party tonight. | *"Body Battery is nearly empty -- 8 out of 100. If you can grab 20 minutes of quiet before 6pm, it'll help. Skipping afternoon caffeine might too."* |
| **Training status: unproductive** | Garmin flags Training Status as "Unproductive" -- load without adaptation. | *"Garmin's flagging your training as unproductive -- you're putting in the work but not recovering enough to adapt. Classic overtraining signal."* |
| **Race predictor milestone** | VO2 max improved, race predictor now shows sub-4h marathon for first time. | *"Your predicted marathon time just dropped below 4 hours for the first time -- 3:58. That's a real fitness milestone."* |

---

### 1.6 MyFitnessPal API

**What it exposes:**
- Daily food diary (meals, calories, macros, micros)
- Exercise log
- Weight log
- Goals (calorie target, macro splits)
- Net calories (food minus exercise)
- Streak data

**API access model:** MFP had a public API that was deprecated in 2020. Current access is via unofficial/reverse-engineered API (`python-myfitnesspal` library) or through approved partnerships. No official public API as of 2024. This limits Pulse's access unless using a partnership route or user data export.

**MCP server:** No official MCP. The deprecation makes this tricky.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Under calorie target (intentional cut)** | It's 8pm. User logged lunch but nothing for dinner. They're 600 calories under target. | *"You're 600 calories under today -- if you're intentionally cutting, great. If not, your body could use some fuel before bed."* |
| **Macro miss** | User is hitting calorie goals but getting only 60g protein against a 150g target. | *"You're hitting calories this week but protein is consistently low -- around 60g vs your 150g goal. That'll slow muscle recovery."* |
| **Logging streak broken** | User missed logging for 3 days. | *"You haven't logged in 3 days. No judgement -- want to pick it back up today or take a break from tracking for a bit?"* |

---

### 1.7 Oura Ring API

**What it exposes:**
- Readiness score (0-100) -- composite recovery metric
- Sleep score: total sleep, efficiency, latency, timing, deep, REM, light
- Resting HR, HRV (RMSSD)
- Respiratory rate
- Body temperature deviation from baseline
- Activity score, daily movement
- Cardiovascular Age (select plans)
- Period prediction (female health)

**API access model:** Official public REST API via OAuth2. Well-documented. Personal access tokens available for self-use. Webhooks available for real-time data push (daily summaries, activity sessions). One of the most developer-friendly health APIs.

**MCP server:** `mcp-oura` exists (community, maintained). Reads readiness, sleep, and activity data. Solid option for Pulse.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Low readiness + big day** | Readiness is 58. User has a job interview at 10am. | *"Readiness is 58 today -- not your best. Your interview is at 10am. Get outside for 10 minutes beforehand, it'll help more than another coffee."* |
| **Temperature spike** | Body temp deviation is +0.6C above baseline for second consecutive night. | *"Your body temp has been elevated two nights running. That's often the earliest sign you're fighting something. Rest and fluids today -- don't push it."* |
| **Optimal window alert** | Readiness 90+. Weekend. No commitments on calendar. | *"Readiness is 94 -- one of your best scores this month. Perfect day for a long run or a big effort if you want it."* |
| **Period prediction** | Oura predicts period in 2 days. | *"Heads up -- Oura predicts your period starting in about 2 days. Might be worth having supplies ready."* |

---

## 2. Finance & Banking

### 2.1 Plaid

**What it exposes:**
- Bank account balances (checking, savings, investment)
- Transaction history (merchant, amount, category, date)
- Recurring transactions (subscriptions, bills, salary)
- Income detection
- Liabilities (credit cards, student loans, mortgages)
- Identity (name, address on account)
- Auth (account/routing numbers for ACH)
- Investment holdings, transactions (Investments product)

**API access model:** REST + OAuth. Requires Plaid developer account. Production requires business approval. US, Canada, UK, EU coverage. Webhooks for real-time transaction updates (fire within seconds to minutes of transaction). Strong MX competitor in US; Truelayer for UK/EU.

**MCP server:** `mcp-plaid` -- community implementation exists. Exposes balance and transactions as tools. Not widely maintained.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Bill due tomorrow** | Electricity direct debit detected as recurring. Due date inferred from past patterns. Account balance is sufficient but only just. | *"Your electricity bill comes out tomorrow -- usually around R850. Your current balance is R1,240. You'll be fine, just keeping you posted."* |
| **Subscription creep** | Analysis shows 14 active subscriptions totalling $287/month. Several haven't been used in 60+ days. | *"You've got 14 active subscriptions -- $287/month. Three of them (Calm, Duolingo Plus, MLB.TV) haven't been touched in 2+ months. Want me to flag which ones to cancel?"* |
| **Unusual large transaction** | $340 charge from an unfamiliar merchant appears. | *"There's a $340 charge from 'AMZN Mktp US' that just posted. Is that yours? If not, worth flagging to your bank now."* |
| **Balance running low** | End of month. Main account drops below user-set threshold of $500. | *"Balance is $480 -- just below your $500 buffer. Payday is 3 days away. You're fine, but heads up."* |
| **Savings goal milestone** | Emergency fund savings account hits $5,000 (a pre-set goal). | *"Your emergency fund just hit $5,000. That's 3 months of living expenses -- a real milestone. You did that."* |

---

### 2.2 Yodlee (Envestnet Yodlee)

**What it exposes:**
- Similar to Plaid: account balances, transactions, investments, liabilities
- Stronger coverage for investment accounts (401k, IRAs, brokerage)
- Bill payment data
- More global coverage than Plaid (170+ countries)
- Net worth aggregation

**API access model:** REST. Enterprise-focused -- requires commercial agreement. More institutionally oriented than Plaid. FastLink (widget) for easy account linking. Generally more expensive but broader financial institution coverage.

**MCP server:** No known MCP server.

**Customer Moments:** Similar to Plaid. Key differentiation is investment account depth:

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Retirement contribution gap** | It's March. User has contributed $3,200 to IRA. Annual limit is $7,000. 9 months left in the year. | *"You're $3,800 short of your IRA max for the year. At your current pace you'll under-contribute by about $1,400. Worth bumping your monthly transfer?"* |
| **Portfolio drift** | Investment allocation has drifted significantly from target (60/40 is now 72/28 after market run). | *"Your portfolio has drifted to 72% equities -- your target was 60%. Might be worth a rebalance conversation with your advisor."* |

---

### 2.3 Open Banking APIs (UK/EU)

**What it exposes:**
- Account information (balances, transactions) -- same as Plaid but regulated under PSD2/Open Banking
- UK: 9 major banks mandated (HSBC, Barclays, Lloyds, NatWest, Santander, etc.)
- EU: Varies by country under PSD2
- Strong Customer Authentication (SCA) required
- Payment initiation (PISP) -- can initiate payments with user consent

**API access model:** OAuth2 (FAPI-compliant). Requires FCA authorisation (UK) or national competent authority (EU). Third-party providers (TPPs) need regulatory approval. Access via aggregators: TrueLayer (UK/EU), Nordigen/GoCardless, Salt Edge, Yapily.

**MCP server:** TrueLayer has an MCP server in development (announced 2025). Nordigen has community MCP tools.

**Customer Moments:** Same as Plaid for UK/EU users. Additional moment:

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Standing order missed** | User's bank shows a failed direct debit for gym membership (insufficient funds). | *"Your gym direct debit bounced today -- not enough in the account. They'll usually retry in 3 days. Worth topping up before then to avoid late fees."* |

---

### 2.4 Crypto: Coinbase API, Binance API, Luno API

**What they expose:**

**Coinbase:**
- Portfolio balances (all assets)
- Trade history
- Live prices (via websocket feed)
- Price alerts
- Staking rewards
- NFT holdings (limited)

**Binance:**
- Spot, margin, futures balances
- Trade history
- Live order book + price feeds
- P&L data
- Staking, savings, earn products

**Luno:**
- BTC, ETH, XRP, USDC balances
- Transaction history (buy/sell/send/receive)
- Live price feed
- Pending orders
- Market depth

**API access model:** All three have public REST + WebSocket APIs. Key management (API key + secret). Coinbase has Advanced Trade API (replaces Pro). Binance rate limits are generous. Luno is simpler but solid for SA/African markets.

**MCP server:** 
- `mcp-coinbase` -- official SDK with MCP-compatible tools (Coinbase AgentKit)
- `mcp-binance` -- community implementation
- No Luno MCP known; straightforward REST, easy to wrap

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Price alert (user-defined)** | BTC drops to user's target buy price. | *"Bitcoin just hit R920,000 -- the level you mentioned last week. You've got R15,000 in your Luno wallet."* |
| **Significant portfolio move** | Portfolio down 18% in 48 hours during market crash. | *"Your crypto portfolio is down 18% in the last 2 days -- R43,000 off your peak. Market's moving fast. No action needed, just keeping you in the loop."* |
| **Tax event reminder** | Approaching end of tax year. User has made multiple trades. | *"Tax year ends in 6 weeks. You've made 23 trades this year -- might be worth pulling your transaction history now for your accountant."* |
| **Staking reward** | Coinbase staking reward deposited. | *"Your ETH staking reward just came in -- 0.0042 ETH (~$14). Small, but it compounds."* |

---

### 2.5 Invoicing: Xero API, QuickBooks API, FreshBooks

**What they expose:**

**Xero:**
- Invoices (status: draft, sent, due, overdue, paid)
- Bills (accounts payable)
- Bank reconciliation status
- Profit & loss, balance sheet
- Cash flow
- Contacts (customers/suppliers)
- Expense claims
- Payroll (if using Xero Payroll)

**QuickBooks:**
- Similar to Xero; stronger in US market
- Invoice aging reports
- Employee timesheets (QB Time integration)
- Inventory
- Tax summaries

**FreshBooks:**
- Invoices, estimates, retainers
- Time tracking
- Expense tracking
- Client portal status (has the client viewed the invoice?)

**API access model:** All three: OAuth2, REST. Well-documented. Webhooks for invoice status changes, payment events. Rate limits apply (Xero: 60 calls/min per app per tenant).

**MCP server:** 
- `mcp-xero` -- community, maintained. Invoice and contact tools.
- `mcp-quickbooks` -- community implementation exists.
- No FreshBooks MCP known.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Invoice overdue** | Invoice #1047 for $3,200 is 14 days overdue. Client hasn't responded to the auto-reminder. | *"Invoice #1047 ($3,200 -- Acme Corp) is 14 days overdue. Want me to draft a follow-up email? Sometimes a personal touch works better than the automated one."* |
| **Cash flow warning** | Outgoings next 30 days projected at $18,000. Current receivables: $9,000 outstanding. Bank balance: $7,500. | *"Cash flow is tight next month -- $18K going out, $9K receivable, $7.5K in the bank. If those invoices don't clear you'll have a gap. Worth a quick call to your biggest debtor?"* |
| **Payment received** | Large invoice paid. | *"$4,500 just landed from DataTech -- Invoice #1039 cleared. "* |
| **Invoice viewed** | FreshBooks shows client opened invoice for first time. | *"Acme just opened your invoice -- first time they've looked at it. Good moment to follow up if you haven't heard from them."* |

---

### 2.6 Credit Card Spend Tracking

**What it exposes (via Plaid/Open Banking):**
- Transaction-level spend by category
- Monthly spend vs previous month
- Merchant-level patterns
- Rewards/cashback tracking (limited -- usually requires bank partnership)
- Payment due dates
- Statement balances vs available credit

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Spend pace warning** | It's the 18th. User has already spent $2,800 on dining this month vs $1,200 average. | *"Dining spend is $2,800 this month -- more than double your usual. Still 13 days to go. Just flagging."* |
| **Payment due** | Credit card payment due in 3 days. Balance: $1,840. | *"Your Amex payment is due in 3 days -- $1,840 outstanding. You've got enough in your checking account to cover it."* |
| **Rewards milestone** | User is 2,300 points from a free flight redemption. | *"You're 2,300 points from a free domestic flight on your Amex. A $230 spend in the next 30 days gets you there."* |

---

## 3. Home & Lifestyle

### 3.1 Smart Home: Google Home API, Apple HomeKit, SmartThings, Philips Hue

**What they expose:**

**Google Home (Matter + Google Home APIs):**
- Device state (lights, locks, thermostats, sensors, cameras)
- Presence detection (home/away)
- Automations/routines status
- Energy usage (Nest Thermostat)
- Camera events (Nest -- motion, person, package)

**Apple HomeKit:**
- Same device categories but iOS/macOS ecosystem
- Home/Away based on iPhone location
- Accessory status
- Automation triggers
- No cloud API -- requires HomeKit hub (HomePod/AppleTV)

**SmartThings:**
- Wide device compatibility
- Scene and automation management
- Presence
- Energy monitoring (SmartThings Energy)
- Device health status

**Philips Hue:**
- Light state (on/off, brightness, colour, colour temperature)
- Groups and rooms
- Scenes
- Sensor data (Hue motion sensors, daylight sensors)
- Entertainment zones
- Energy usage (Hue Gradient)

**API access model:**
- Google Home: Developer Preview API (limited, requires enrolment)
- HomeKit: Local only (HomeKit Accessory Protocol) + iCloud remote access; no public cloud API
- SmartThings: REST API, OAuth2, webhook support -- solid and public
- Hue: Local REST API (direct to bridge, no cloud needed) + Hue Remote API (cloud)

**MCP servers:**
- `mcp-homeassistant` -- the de facto standard for smart home MCP; integrates all of the above via Home Assistant
- `mcp-philips-hue` -- community, local bridge access
- No official Google Home or Apple HomeKit MCP

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Left home, left lights on** | User's phone leaves the geofence. Three lights still on. | *"Looks like you left -- bedroom and living room lights are still on. Want me to turn them off?"* |
| **Front door unlocked** | It's midnight. Front door lock reports unlocked state. | *"Front door is showing unlocked -- it's past midnight. Is that intentional?"* |
| **Thermostat anomaly** | Heating has been running for 6 hours straight. Outdoor temp is 22C. | *"Your heating's been on for 6 hours -- it's 22 degrees outside. Might be worth checking the thermostat."* |
| **Motion detected, no one home** | Motion sensor triggers in main room when presence is 'Away'. | *"Motion detected in the living room -- your home shows everyone away. Could be a pet, could be worth checking."* |
| **Morning light routine** | User's alarm goes off. Hue lights in bedroom gradually warm up. Coffee maker triggered. | *(Silent -- this is an automation, not a notification. Pulse confirms:) "Morning. Lights and coffee are going."* |

---

### 3.2 Amazon Alexa Skills API

**What it exposes:**
- Smart home control (via Alexa Smart Home Skill)
- Shopping list (Alexa shopping list API)
- To-do list
- Reminders and alarms
- Calendar events (linked calendar)
- Media playback status
- Routines
- Flash briefing
- Guard (away mode -- listens for smoke/CO2/glass break)

**API access model:** Alexa Skills Kit (ASK) -- REST, OAuth2. Skill development via Alexa Developer Console. Smart home skills require separate certification. Voice model training required. Proactive API (send notifications to user without being asked) available for approved skills.

**MCP server:** No official MCP. Alexa's model is voice-in/response-out -- doesn't naturally fit MCP pattern.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Shopping list item running low** | User's Alexa shopping list has "milk" added 3 times in the past month. Thursday morning. | *"Milk's been added to your Alexa list three times in the last month -- usually mid-week. Might be one to add to the weekly Woolies order."* |
| **Alexa Guard alert** | Alexa Guard detects possible glass break while user is away. | *"Alexa Guard picked up what might be a glass break at home while you're out. Could be nothing -- worth a quick check."* |

---

### 3.3 Grocery/Shopping: AnyList, OurGroceries, Instacart

**What they expose:**

**AnyList:**
- Shopping lists (items, quantities, categories)
- Recipe library
- Meal plan

**OurGroceries:**
- Shared shopping lists (household)
- Item history

**Instacart:**
- Order history
- Delivery ETA
- Cart contents
- Store availability

**API access model:**
- AnyList: No public API. Reverse-engineered or export only.
- OurGroceries: No public API.
- Instacart: No public consumer API. Instacart Connect (B2B) requires partnership. Limited.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Reorder reminder** | Instacart order history shows user orders oat milk, coffee pods, and eggs every ~3 weeks. It's been 21 days. | *"It's been 3 weeks since your last Instacart order. Running low on the usual suspects -- coffee pods, oat milk, eggs?"* |
| **Delivery arriving** | Instacart delivery ETA: 12 minutes. | *"Your Instacart order is 12 minutes away."* |

---

### 3.4 Vehicle: Tesla API, OBD2/Car Maintenance

**What they expose:**

**Tesla API:**
- Battery level, range estimate
- Charge state (charging/not, time to full)
- Climate (cabin temp, preconditioning)
- Location
- Lock/unlock state
- Odometer
- Tyre pressure
- Scheduled departure
- Sentry mode events

**OBD2 (via adapters: Automatic, Bouncie, Zubie, or self-hosted):**
- Vehicle speed, RPM, fuel level
- DTC codes (engine warning codes)
- Trip data (distance, duration, fuel used)
- Odometer
- Battery voltage (12V)
- Some: hard braking, rapid acceleration events

**API access model:**
- Tesla: Fleet API (official, OAuth2) for third-party apps. Well-documented but Tesla occasionally changes it.
- OBD2 cloud: Automatic (defunct), Bouncie (REST + webhooks), Zubie (API available). Self-hosted: OBD2 adapter + Home Assistant or custom scripts.

**MCP server:** 
- `mcp-tesla` -- community implementation exists. Controls and reads vehicle data.
- No standard OBD2 MCP, but Home Assistant MCP covers it if car is integrated there.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Low charge, long drive tomorrow** | Tesla is at 22% battery. Calendar shows a 280km drive tomorrow. | *"Your Tesla is at 22% -- tomorrow's drive to Stellenbosch is 280km round trip. You'll want to charge tonight unless you're planning a stop."* |
| **Car left unlocked** | Tesla shows unlocked status at 11pm. | *"Your Tesla is showing unlocked. Want me to lock it?"* |
| **Service overdue** | Odometer-based: car is 3,400km past recommended oil service interval. | *"Your car is 3,400km overdue for a service. Want me to find available slots at your usual place?"* |
| **Engine warning code** | OBD2 detects DTC P0420 (catalytic converter efficiency). | *"Your car's thrown an engine code -- P0420 (catalytic converter). It won't stop you driving but it needs attention. Want me to book it in?"* |
| **Tyre pressure low** | TPMS reports front-left is 26 PSI vs 33 PSI recommended. | *"Front-left tyre is running a bit low -- 26 PSI vs the recommended 33. Worth topping up before a motorway run."* |

---

### 3.5 Property: Zillow API, Property Listing APIs

**What they expose:**

**Zillow:**
- Zestimate (estimated property value)
- Price history
- Property details
- Nearby listings
- Mortgage rates
- Rent Zestimate

**Rightmove / Zoopla (UK):**
- Property listings
- Sold price history
- Valuation estimates
- Agent contact

**South Africa -- Lightstone / Property24:**
- Property valuations
- Sales history
- Area market data

**API access model:**
- Zillow: Public API deprecated (2021). Only Bridge Interactive API for licensed agents. Limited consumer access.
- Rightmove/Zoopla: No public API.
- Property24: No public API.
- Lightstone: Enterprise/licensed access only.

Realistically, Pulse would need to scrape or partner. Web scraping of sold prices is legal and common.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Property value milestone** | Zestimate (or equivalent) shows user's home has appreciated $50,000 since purchase. | *"Your home's estimated value just crossed $600K -- up about $50K since you bought it. Your equity position is looking solid."* |
| **Similar property sold nearby** | Comparable property 3 streets away sold for $720K. | *"A 3-bed in your street just sold for $720K -- similar size to yours. Useful data point if you're ever thinking about selling."* |

---

## 4. Travel & Transport

### 4.1 TripIt API

**What it exposes:**
- Complete trip itineraries (flights, hotels, cars, activities)
- Confirmation numbers
- Flight departure/arrival details
- Hotel check-in/check-out
- Real-time flight updates (TripIt Pro)
- Points/miles tracking (Pro)

**API access model:** OAuth2, REST. Webhook/push support for itinerary updates. Well-maintained. Free tier for basic itinerary parsing; Pro for real-time flight data.

**MCP server:** Community `mcp-tripit` in development. No mature implementation yet.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Check-in reminder** | Online check-in opens 24h before flight. | *"Online check-in just opened for your Cape Town -> Joburg flight tomorrow morning. Want me to remind you to grab a window seat?"* |
| **Flight gate change** | Gate changed from B12 to A4. User is in the lounge. | *"Gate change -- your flight is now departing from A4, not B12. That's a 6-minute walk, you've got time."* |
| **Hotel check-in approaching** | Arriving in Joburg at 14:00. Hotel check-in is 15:00. | *"Your hotel check-in is 15:00 and you land at 14:00. There's about a 35-minute drive from the airport -- should be fine."* |
| **Passport expiry alert** | User's passport expires in 4 months. TripIt shows international travel booked. | *"Your passport expires in 4 months -- your London trip is in 3. Some countries require 6 months validity on arrival. Worth checking and renewing now."* |

---

### 4.2 Google Maps / Waze

**What they expose:**

**Google Maps Platform:**
- Directions + real-time traffic
- ETA computation
- Places (restaurants, businesses, reviews)
- Distance Matrix
- Geocoding/reverse geocoding
- Street View imagery

**Waze (via Waze Ads/Beacons API -- very limited public access):**
- Mostly B2B. Not a consumer API. Traffic data available via HERE, TomTom, or MapBox as alternatives.

**API access model:** Google Maps: REST, key-based. Pay-per-use. No real-time traffic streaming for free -- each query costs. Waze: No consumer API. For real-time traffic, use Google Directions API or TomTom.

**MCP server:** `mcp-google-maps` -- official and community versions exist. Places search, directions, geocoding.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Leave now alert** | Calendar event at 9am, 25km away. Current traffic suggests 45 min. It's 8:05am. | *"Leave in the next 5 minutes for your 9am -- traffic's heavy on the N1, it's a 45-minute drive right now."* |
| **Faster route exists** | User is en route. An incident has slowed their current route. | *"There's an accident ahead on your route -- adding 20 minutes. Via De Waal Drive saves you 15."* |

---

### 4.3 Uber/Lyft APIs

**What they expose:**
- Ride estimates (price, time to pickup)
- Ride status (requested, arriving, in progress, complete)
- Ride history
- Receipts

**API access model:** Both have severely restricted consumer APIs. Uber's public API is deprecated for ride ordering (only available to enterprise partners). Lyft's API is also restricted. Ride history available only in-app or via data export. Pulse would need screen scraping or email receipt parsing for practical integration.

**Practical workaround:** Parse Uber/Lyft email receipts (via Gmail integration) for ride history and spend tracking.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Surge pricing warning** | User typically rides home at 5:30pm on Fridays. It's Friday 5:20pm, surge is 2.1x. | *"Uber surge is 2.1x right now -- if you wait 20 minutes it usually drops. Just flagging."* |
| **Monthly ride spend** | Email receipt parsing shows $340 in Uber this month vs $180 average. | *"Uber spend this month is $340 -- nearly double your usual. Worth knowing."* |

---

### 4.4 Airbnb / Booking.com

**What they expose:**
- **Airbnb:** No public consumer API (deprecated 2016). Hosts have limited API access. Email parsing is the main route.
- **Booking.com:** Affiliate API (not useful for personal use). No consumer API.

**Practical approach:** Email receipt/confirmation parsing. Combine with TripIt (which parses Airbnb/Booking confirmation emails automatically).

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Check-in instructions** | Booking.com reservation for tomorrow. Host sent key code via email. | *"You check in to your Airbnb tomorrow at 3pm. Key code from the host: #4821. Address saved."* |
| **Review reminder** | 24 hours after Airbnb checkout. | *"You checked out of your Airbnb yesterday -- worth leaving a review while it's fresh. Hosts really do appreciate it."* |

---

### 4.5 Flight Tracking: FlightAware, Flightradar24 APIs

**What they expose:**

**FlightAware AeroAPI:**
- Real-time flight position, altitude, speed
- Departure/arrival status (on-time, delayed, diverted, cancelled)
- Gate information
- Historical flight data
- Aircraft type
- Estimated times (ATIS, block)

**Flightradar24 (Radar API):**
- Live aircraft position data
- Flight details
- Airport stats
- Limited public API -- premium tiers required for commercial use

**API access model:**
- FlightAware AeroAPI: REST, key-based. Pay-per-query (or flat rate plans). Very reliable. The standard for real-time flight data.
- Flightradar24: Business API requires contract. FR24 is better for radar visualisation than data extraction.

**MCP server:** Community `mcp-flightaware` wrapping AeroAPI exists. Flight status by IATA flight number.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Flight delayed** | User is going to pick someone up from the airport. Flight shows 55-minute delay. | *"Flight SA471 from Johannesburg is running 55 minutes late -- now arriving at 16:35. No need to leave yet."* |
| **Connecting flight at risk** | User is on a delayed inbound flight. Connecting flight gap is now 35 minutes. | *"Your connection to Amsterdam is tight -- your inbound is 40 minutes late and the gate closes in 75. You'll need to move fast."* |
| **Flight cancelled** | Flight cancelled the night before travel. | *"Your 06:30 SAA flight tomorrow has been cancelled. I'm checking alternatives -- there's a 09:15 on FlySafair and a 10:00 on Kulula."* |

---

### 4.6 Public Transit GTFS Feeds

**What they expose:**
- Static GTFS: routes, stops, schedules, fares
- GTFS-RT (Realtime): vehicle positions, trip updates (delays), service alerts
- Feeds available for most major transit agencies globally (many free/open)
- Agencies: TfL (London), NYC MTA, BART, Cape Town MyCiTi, etc.

**API access model:** GTFS static = downloadable ZIP. GTFS-RT = protocol buffer feed (HTTP endpoint). Most feeds are free and open. Google Maps, Apple Maps, and Transit App all consume these feeds.

**MCP server:** No mainstream MCP. Could be built directly -- GTFS parsing is well-supported in Python/Node.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Service disruption** | User normally takes the 8:17 train. There's a signal failure causing major delays. | *"The 8:17 to Waterloo is delayed -- signal failure at Clapham Junction. Next reliable service is 8:52. Leave a bit later or allow extra time."* |
| **Last train warning** | User is out at 23:30. Last tube is at 00:01, 15-minute walk away. | *"Last tube from Angel is at 00:01 -- 15-minute walk. You need to leave now."* |

---

## 5. Entertainment & Media

### 5.1 Spotify API

**What it exposes:**
- Currently playing track (real-time)
- Playback state (playing/paused, device, volume)
- Listening history (recently played -- last 50 tracks)
- Saved tracks, albums, playlists
- Followed artists
- Top artists and tracks (short, medium, long-term)
- Audio features (tempo, energy, valence/mood, danceability)
- New releases from followed artists
- Recommendations
- Podcast subscriptions + episode progress

**API access model:** OAuth2, REST. Real-time playback via WebSocket (Spotify Connect). Webhooks not available -- requires polling or WebSocket connection. Rate limits: 180 requests/rolling 30 seconds. Well-documented, widely used.

**MCP server:** `mcp-spotify` -- multiple community implementations. Playback control, search, queue management. Actively maintained.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Favourite artist tour** | User's top artist announced UK tour dates. | *"The National just announced dates for a UK tour -- Manchester on March 14, London on March 17. Tickets go on sale Friday."* |
| **New release alert** | Followed artist drops new album. | *"Bon Iver dropped a new album at midnight -- 'SABLE, fABLE'. Your Friday playlist just sorted itself out."* |
| **Workout playlist nudge** | User is at the gym (location or activity context). No workout playlist active. | *"You're at the gym with no music going. Want your Power Hour playlist?"* |
| **Mood read** | User has been playing slow, melancholic music for 3 hours (low valence tracks). | *(Optional and sensitive -- this is a moment where tone matters.) "You've been in a quiet mood today -- anything you want to talk about, or just need space?"* |
| **Podcast catch-up** | Favourite podcast released a new episode. User has 45 minutes in the car. | *"New Lex Fridman episode dropped -- 2h 40 mins. Save it for a long drive."* |

---

### 5.2 YouTube Data API

**What it exposes:**
- Subscribed channels
- New videos from subscriptions
- Watch history (requires OAuth, not always available via API)
- Liked videos
- Playlists
- Video details (duration, view count, description)
- Channel stats
- Live stream status

**API access model:** OAuth2 + API key. REST. Well-documented. Rate limits are strict (10,000 units/day free -- each API call costs units). Watch history not reliably accessible via API -- tied to Google account data. YouTube Data API v3.

**MCP server:** `mcp-youtube` -- community implementations. Can fetch channel info, video metadata, search. Limited due to API unit costs.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **New video from favourite channel** | User watches a specific tech channel regularly. New video posted. | *"Linus dropped a new video -- 'We Built the Ultimate Home Server.' 22 minutes. Worth a lunch break watch."* |
| **Live stream starting** | Subscribed creator going live in 10 minutes. | *"MKBHD is going live in 10 minutes -- looks like a new phone review."* |

---

### 5.3 Goodreads / Book Tracking

**What it exposes (Goodreads):**
- Books read, reading, want-to-read
- Star ratings and reviews
- Reading challenges (annual goal)
- Friends' reads/reviews

**API access model:** Goodreads deprecated their public API in 2020. No reliable official access. 

**Alternatives:**
- **Open Library API** (Internet Archive) -- book metadata, open access
- **Google Books API** -- book metadata, user shelves
- **Literal.club API** -- modern alternative, has API
- **Hardcover.app** -- open-source Goodreads alternative with GraphQL API
- **StoryGraph** -- no public API yet

**MCP server:** `mcp-openlibrary` -- community. Book lookup, metadata. No user shelf data.

**Customer Moments:**

| Moment | Scene | Pulse message |
|--------|-------|---------------|
| **Reading goal off-pace** | User set a 24-book reading goal. It's September. They've read 8. | *"You're at 8 books for the year -- your 24-book goal needs roughly 2 per month. At current pace you'll land around 14. Still doable if you want to push."* |
| **Author new release** | Favourite author releases new book. | *"Cormac McCarthy's next book just went on pre-order. Given your reading history, figured you'd want to know."* |
| **Book recommendation based on mood** | User just finished a thriller (detected via Goodreads or manual input). | *"If you liked 'The Girl with the Dragon Tattoo', your next read based on your history might be 'The Snowman' by Jo Nesb."* |

---

## 6. Privacy, Sensitivity & Trust

### 6.1 Sensitivity Tiers

Not all data is equal. Pulse needs to classify integrations by sensitivity and handle them differently:

| Tier | Data type | Examples | Handling |
|------|-----------|----------|----------|
| ** Tier 1 -- Intimate** | Health, menstrual, sleep, mental health signals, body data | HealthKit, Oura, Whoop | Stored encrypted on-device only. Never sent to third parties. AI processing done locally or with explicit consent. Explicit opt-in per data type. |
| ** Tier 2 -- Sensitive** | Banking, financial transactions, crypto, income | Plaid, Xero, Coinbase | Encrypted in transit and at rest. Zero third-party data sharing. User controls data retention. Read-only access. |
| ** Tier 3 -- Personal** | Location, home data, vehicle, travel | HomeKit, Tesla, TripIt | User sets comfort level. Location data minimised. Home state data kept local where possible. |
| ** Tier 4 -- Lifestyle** | Entertainment, media, grocery | Spotify, YouTube, Goodreads | Lower sensitivity but still deserves care. No selling to advertisers. |

---

### 6.2 How Trust Gets Established

**The problem:** Pulse is asking people to hand over the keys to their entire life. Bank accounts. Health data. Their front door. This is an extraordinary ask. Trust has to be earned deliberately.

**Trust-building principles:**

1. **Radical transparency about what's accessed**
   - Show a live log: "Here's what Pulse read today." No black box.
   - Every integration shows exactly what data fields are accessed.
   - "Pulse read your Oura sleep score and readiness. It did not access your detailed sleep stage data."

2. **Granular permissions -- not all-or-nothing**
   - Don't force users to grant all or nothing.
   - "Connect Plaid -- choose which accounts Pulse can see" (e.g., exclude joint account)
   - "Connect HealthKit -- allow: sleep, steps. Not allowed: weight, menstrual data."

3. **Value before asking**
   - Don't ask for bank data on day 1.
   - Let users experience value from low-sensitivity integrations first (Spotify, Strava).
   - Earn permission for sensitive integrations over time.

4. **Local-first architecture for Tier 1 data**
   - Health and financial data should be processed on-device where possible.
   - "Your health data never leaves your phone."
   - This is a genuine architectural and competitive differentiator.

5. **Explicit opt-in for each proactive message type**
   - "Would you like Pulse to remind you about low battery on your car?"
   - "Can Pulse check on your sleep score after late nights?"
   - Each type of insight requires user consent -- not a blanket "allow notifications."

6. **No dark patterns**
   - No pre-ticked boxes.
   - No "improved experience" that means selling data.
   - No "we may share with trusted partners" (we don't).

7. **Easy off-ramp**
   - Revoking access is one tap.
   - Deleting all data is one tap + confirmation.
   - No "are you sure?" gauntlet.

8. **Show the impact clearly**
   - "Since connecting HealthKit, Pulse has sent you 14 insights. Here they are."
   - Users should always be able to see what Pulse is doing with their data and feel good about it.

---

### 6.3 The Notification Problem

Even with the right integrations, being proactive is a tightrope. Too many notifications = deleted. Too few = forgotten.

**Rules for Pulse notifications:**

- **One insight per topic per day maximum** -- if the car needs a service AND the tyre is low, combine them.
- **Time-sensitivity matters** -- a gate change is time-critical. A book recommendation is not.
- **User controls the dial** -- proactive level: "quiet / regular / everything"
- **Never notify during known focus/sleep hours** -- respect Do Not Disturb
- **Learn from silence** -- if a user consistently ignores a type of notification, stop sending them
- **Feeling, not data** -- notifications should feel like a smart friend, not a surveillance report

**The test:** Would a smart, perceptive friend who had access to all this information send this message right now? If yes, send it. If it sounds like a status report, don't.

---

### 6.4 MCP Server Summary

| Integration | MCP Server | Status |
|-------------|-----------|--------|
| Apple HealthKit | None official | Community (XML export only) |
| Strava | `mcp-strava` | Community, functional |
| Fitbit | `mcp-fitbit` | Community, basic |
| Whoop | `mcp-whoop` | Community, limited |
| Garmin Connect | None | Not available |
| Oura Ring | `mcp-oura` | Community, maintained |
| Plaid | `mcp-plaid` | Community |
| TrueLayer (Open Banking) | In development | Announced 2025 |
| Coinbase | `mcp-coinbase` | Official SDK |
| Binance | `mcp-binance` | Community |
| Xero | `mcp-xero` | Community |
| QuickBooks | `mcp-quickbooks` | Community |
| Home Assistant (covers HomeKit, Hue, SmartThings) | `mcp-homeassistant` | Community, well-maintained |
| Philips Hue | `mcp-philips-hue` | Community (local) |
| Tesla | `mcp-tesla` | Community |
| TripIt | `mcp-tripit` | Community, in development |
| Google Maps | `mcp-google-maps` | Official + community |
| FlightAware | `mcp-flightaware` | Community |
| Spotify | `mcp-spotify` | Community, maintained |
| YouTube | `mcp-youtube` | Community |
| Open Library | `mcp-openlibrary` | Community |

---

### 6.5 Integration Priority Matrix

For Pulse MVP, prioritise integrations that:
1. Have reliable API access
2. Generate high-value, time-sensitive moments
3. Are low enough sensitivity to onboard quickly

| Priority | Integration | Why |
|----------|-------------|-----|
|  P1 | **Oura Ring** | Best API, time-sensitive health moments, affluent early adopter overlap |
|  P1 | **Strava** | Active user base, clear moments, easy OAuth |
|  P1 | **Spotify** | Universal appeal, low sensitivity, MCP available |
|  P1 | **Plaid** | Highest-value financial moments, strong API |
|  P1 | **Google Calendar** (implicit) | The backbone of time-aware proactive notifications |
|  P2 | **HealthKit** | Requires iOS app, but enormous data richness |
|  P2 | **Tesla** | Affluent segment, high-value moments |
|  P2 | **FlightAware + TripIt** | Travel moments are extremely high value |
|  P2 | **Xero/QuickBooks** | High value for freelancers/small business |
|  P3 | **SmartThings / Hue** | Requires home setup, lower universality |
|  P3 | **Coinbase/Luno** | Volatile access, niche segment |
|  P3 | **GTFS transit** | High value for non-car users, complex to maintain |

---

*Research compiled: March 2026*  
*For Pulse product team*
