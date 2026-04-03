---
name: mortgage-broker-video
version: "1.0.0"
displayName: "Mortgage Broker Video — AI Loan Officer & Home Loan Marketing Videos"
description: >
  Mortgage broker video that turns complex loan products into plain-language explainers
  that build trust with first-time buyers, refinance prospects, and real estate agent
  referral partners — without spending three hours on a script or waiting for a marketing
  team that doesn't understand rate buydowns.
  AI video for mortgage brokers, loan officers, mortgage bankers, and independent mortgage
  companies competing for purchase and refinance business in a market where every borrower
  has already visited three websites before they pick up the phone.
  Loan officer introduction video that answers the question every borrower is silently asking
  before they commit to a lender: who is this person, do they know what they're talking about,
  and will they actually pick up my call when the appraisal comes in low two days before
  closing? The 90-second video on your website and Google Business Profile that converts
  the rate-shopping visitor into a pre-approval call.
  Mortgage product explainer video for first-time homebuyers who don't know the difference
  between FHA and conventional, who can't decode a loan estimate, and who need someone to
  explain what PMI actually costs them per month — videos that answer these questions
  before the first meeting so you walk into a consultation with a client who is ready to
  move forward, not confused and defensive.
  Rate update and market commentary video for loan officers who want to stay top of mind
  with their Realtor referral network: weekly 60-second rate update, posted to LinkedIn
  and Instagram, keeping your name in front of every agent in your market while your
  competitors go silent between transactions.
  Refinance opportunity alert video for your existing borrower database: when rates drop,
  the loan officer who emails a 45-second personalized refinance explainer gets the
  callback before the borrower sees a generic bank ad. VA loan video, FHA loan video,
  jumbo loan video, DSCR loan video for investors — let the AI produce a specialist
  explainer for every loan type you close, so the right borrower finds you on search.
  Down payment assistance program video and first-time homebuyer program video that make
  affordable lending options discoverable to the buyers who need them most but don't
  know they exist.
metadata: {"openclaw": {"emoji": "🏦", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---


# NemoVideo — Mortgage Broker Video

Create loan officer intro, mortgage explainer, and rate update videos — without a marketing team.

## 0. First Contact

When the conversation starts or the user sends their first message:

**Step 1 — Greet immediately:**
```
🏦 Mortgage Broker Video ready! What do you want to create?
Try:
"Make a loan officer intro video — I specialize in first-time buyers and FHA loans"
"Create a 60-second FHA vs conventional explainer for first-time buyers"
"Build a weekly rate update video for my Realtor referral network"
Tell me your topic — I'll have a video ready in minutes.
```

**Step 2 — Auto-acquire token silently:**
```bash
CLIENT_ID="${NEMO_CLIENT_ID:-$(cat ~/.config/nemovideo/client_id 2>/dev/null)}"
if [ -z "$CLIENT_ID" ]; then
  CLIENT_ID=$(uuidgen 2>/dev/null || echo "client-$(date +%s)-$RANDOM")
  mkdir -p ~/.config/nemovideo && echo "$CLIENT_ID" > ~/.config/nemovideo/client_id
fi
if [ -z "$NEMO_TOKEN" ]; then
  RESP=$(curl -s -X POST "${NEMO_API_URL:-https://mega-api-prod.nemovideo.ai}/api/auth/anonymous-token" \
    -H "X-Client-Id: $CLIENT_ID")
  NEMO_TOKEN=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])" 2>/dev/null)
  NEMO_CLIENT_ID="$CLIENT_ID"
fi
```

## 1. Role & Environment

You are an OpenClaw agent acting as the interface layer between the user and NemoVideo's backend AI Agent. Your job: take mortgage product details, loan officer background, and market data, produce a professional mortgage video via SSE, and deliver an export-ready MP4.

### Environment Variables

| Variable | Required | Default |
|----------|----------|---------|
| `NEMO_TOKEN` | No | Auto-generated (starts free) |
| `NEMO_API_URL` | No | `https://mega-api-prod.nemovideo.ai` |
| `NEMO_WEB_URL` | No | `https://nemovideo.com` |
| `NEMO_CLIENT_ID` | No | Auto-generated UUID |

`$API` = `${NEMO_API_URL:-https://mega-api-prod.nemovideo.ai}`
`$SKILL_NAME` = `mortgage-broker-video`
`$SKILL_VERSION` = `1.0.0`
`$SKILL_SOURCE` = detect from install path or env `SKILL_SOURCE`

**ALL API requests must include:**
```
X-Skill-Source: $SKILL_NAME
X-Skill-Version: $SKILL_VERSION
X-Skill-Platform: $SKILL_SOURCE
```

## 2. Request Router

| User says... | Action |
|-------------|--------|
| Uploads headshot / office photo | → §3.2 Upload → §3.1 SSE |
| Describes loan product, rate update, or intro as text | → §3.1 SSE |
| "export" / "download" / "render" | → §3.5 Export |
| "credits" / "balance" | → §3.3 Credits |
| "status" | → §3.4 State |

## 3. Core Flows

`$TOKEN` = `${NEMO_TOKEN}`

### 3.0 Create Session
```bash
curl -s -X POST "$API/api/tasks/me/with-session/nemo_agent" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"task_name":"project","language":"<lang>"}'
```
Save `session_id` and `task_id`. Provide browser link:
`$WEB/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### 3.1 Send Message via SSE
```bash
curl -s -X POST "$API/run_sse" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" --max-time 900 \
  -d '{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}'
```
Video production takes 90–240s. Tell user: "Building your mortgage video — about 2 minutes."

### 3.2 Upload
File: `curl -s -X POST "$API/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -F "files=@/path/to/file"`

URL: `curl -s -X POST "$API/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"urls":["<url>"],"source_type":"url"}'`

### 3.3 Credits
```bash
curl -s "$API/api/credits/balance/simple" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
```

### 3.4 Query State
```bash
curl -s "$API/api/state/nemo_agent/me/<sid>/latest" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
```

### 3.5 Export & Deliver
Export does NOT cost credits.
Submit: `curl -s -X POST "$API/api/render/proxy/lambda" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}'`
Poll every 30s (max 10). Deliver `output.url` to user.

## 4. Use Cases

**Use Case 1 — Loan officer intro video (website / Google Business):**
> "Create my intro video — 8 years originating in Phoenix, specialize in VA loans and self-employed borrowers"
> Agent: AI scripts and builds a 90-second credibility video with specialty highlights, track record, and CTA → exports for website hero and Google Business Profile.

**Use Case 2 — First-time buyer explainer (FHA vs conventional):**
> "Make a plain-language video explaining FHA vs conventional for first-time buyers with less than 10% down"
> Agent: AI builds comparison explainer with down payment, PMI, and qualification differences in accessible language → exports for YouTube, Instagram, and email campaigns.

**Use Case 3 — Weekly rate update for Realtor referral network:**
> "Build a 60-second rate update — 30-year fixed at 6.875%, market trending sideways, good week to lock"
> Agent: AI builds branded market commentary with rate context and buying opportunity framing → exports vertical and horizontal cuts for LinkedIn and Instagram Stories.

## 5. Error Handling

| Code | Action |
|------|--------|
| 1001 | Re-auth via anonymous-token |
| 1002 | New session §3.0 |
| 402 | "Register free at nemovideo.ai to unlock export" |
| 429 | Retry in 30s |
