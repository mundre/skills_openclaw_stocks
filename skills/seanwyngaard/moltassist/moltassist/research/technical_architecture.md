# Pulse -- Technical Architecture Spec
**Version:** 0.1 (Research Draft)  
**Date:** 2026-03-17  
**Author:** Architecture Research Agent  

---

## Overview

Pulse is a proactive AI assistant that watches your calendar, email, and data sources, then reaches out to you with contextual help -- without being asked. The core design challenge: always-on intelligence that doesn't drain battery, doesn't burn LLM tokens on noise, respects privacy, and works across iOS, Android, Windows, and Mac.

This document covers:
1. Core daemon architecture
2. Integration layer
3. Recipe schema
4. LLM routing
5. On-the-fly job detection pipeline
6. Multi-platform backend
7. Privacy architecture

---

## 1. Core Daemon Architecture

### Design Philosophy

The daemon must be **event-driven first, polling second**. The enemy is the naive polling loop: checking Gmail every 60 seconds even when nothing changes is wasteful, expensive, and kills battery. The goal is to respond to *changes*, not to continuously ask "anything new?"

### Architecture Layers

```

                  PULSE DAEMON                        
                                                      
      
    Event Bus         Trigger Evaluation Engine   
    (internal)     (rule matching + scoring)   
      
                                                     
     
             Adapter Layer                          
    GCal  Gmail  Outlook  Apple  Webhooks       
     
                                                      
        
    State Store        Cooldown / Dedup Cache     
    (SQLite/local      (prevents spam)            
        

```

### Event-Driven vs. Polling -- Decision Matrix

| Source         | Best Strategy          | Rationale                                       |
|----------------|------------------------|-------------------------------------------------|
| Gmail          | Push (Pub/Sub)         | Google's push API via Cloud Pub/Sub -- zero poll |
| Google Calendar| Push (webhooks)        | Calendar API watch channels                     |
| Outlook/Exchange| Push (Graph webhooks) | MS Graph subscription webhooks                 |
| Apple Calendar | Polling (5-30 min)     | No native push; CalDAV only                     |
| iCloud         | Polling (15 min)       | CalDAV, limited event-driven options            |
| Time-based     | Cron scheduler         | Internal cron for time-triggered recipes        |
| Custom APIs    | Configurable           | User-defined polling interval in recipe         |

**Rule:** Always prefer push. Fall back to polling only when no push mechanism exists. When polling, use exponential backoff during quiet periods and increase frequency when a user-defined "hot window" is active (e.g., before an important meeting).

### Trigger Evaluation Engine

When an event arrives on the bus, it goes through the TEE:

```
Event Arrives
     
     

  1. Event Normalization       -> Canonical format regardless of source

               
               

  2. Recipe Matching           -> Which recipes apply to this event?
     - by source type        
     - by time window        
     - by data patterns      

               
               

  3. Condition Evaluation      -> Does this event satisfy conditions?
     - threshold checks      
     - time comparisons      
     - pattern matching      

               
               

  4. Cooldown Check            -> Has this recipe fired recently?

               
               

  5. Confidence Scoring        -> Score 0.0-1.0. Below threshold -> discard

               
               

  6. Context Gathering         -> Pull additional data if needed

               
               

  7. LLM Dispatch              -> Route to appropriate model

```

### Handling False Positives

False positives are the #1 trust killer. A user who gets 3 irrelevant nudges will uninstall.

**Strategies:**

1. **Confidence threshold** -- each recipe has a minimum confidence score (0.0-1.0). Events that match but score below threshold are logged but not dispatched. Default: `0.75`.

2. **Contextual dampening** -- if the same type of nudge fired in the last N hours, raise the threshold for subsequent fires.

3. **User feedback loop** -- every delivered nudge has a quick " Useful /  Not helpful" action. Negative feedback:
   - Increases cooldown for that recipe
   - Decrements recipe confidence modifier for that user
   - After 3 consecutive negatives, recipe auto-pauses and alerts user

4. **Silent dry-run mode** -- new recipes run in shadow mode for 48h, logging would-have-fired events without delivering. User reviews the log before enabling.

5. **Time-aware suppression** -- suppress non-critical nudges:
   - Between 23:00-07:00 (configurable)
   - During calendar events marked as "busy" or "focus"
   - When the device has been idle for >4h (likely sleeping)

### Battery / Resource Efficiency

- **Daemon runs as a background service** (launchd on Mac, systemd on Linux, Windows Service, iOS BGTaskScheduler, Android WorkManager/JobScheduler)
- **Adaptive polling intervals**: quiet windows (e.g., midnight) -> poll every 30 min. Hot windows (e.g., 30 min before a meeting) -> poll every 2 min
- **Debouncing**: rapid-fire events within a 30s window are batched, not individually evaluated
- **LLM calls only fire post-trigger**: the daemon itself uses zero LLM tokens for routine watch operations

---

## 2. Integration Layer

### V1 Must-Have Integrations

| Integration        | Priority | Users Served |
|--------------------|----------|--------------|
| Google Calendar    | P0       | ~70% of users|
| Gmail              | P0       | ~60% of users|
| Outlook/Microsoft 365 | P0    | Enterprise   |
| Apple Calendar     | P1       | iOS/Mac users|
| iCloud Mail        | P2       | Apple-heavy  |

### Integration Strategy: Build Native OAuth (Not Zapier/Make)

**Recommendation: Build native OAuth integrations.**

**Why not Zapier/Make:**
- Introduces a third-party data processor -- a privacy nightmare
- Adds latency (webhooks -> Zapier -> your server -> user)
- Costs money per automation at scale
- You lose control over rate limits and reliability

**Why native OAuth:**
- Direct control over data flow
- Better privacy story ("your data goes direct to Pulse, never to intermediaries")
- Lower latency
- Full access to API primitives (pagination, incremental sync, push channels)

### Google Calendar + Gmail

**Auth:** OAuth 2.0 via Google Identity Platform  
**Scopes needed:**
- `https://www.googleapis.com/auth/calendar.readonly`
- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/gmail.modify` (for marking read, if needed)

**Push mechanism (Gmail):**
```
Gmail API -> Cloud Pub/Sub topic -> Pulse webhook endpoint
```
Setup: `users.watch()` call, creates a Pub/Sub subscription. Google pushes a notification (not the email itself -- just "something changed"). Pulse then fetches only the changed messages via `history.list()`.

Quota limits:
- Gmail: 1 billion quota units/day (reading ~5 units/call -- effectively unlimited)
- Calendar API: 1 million requests/day (free tier)
- Watch subscriptions expire after 7 days -- must be renewed

**Google Calendar Push:**
```
POST https://www.googleapis.com/calendar/v3/calendars/{calendarId}/events/watch
```
Creates a notification channel. Google POSTs to your webhook on any change. Expires after 7 days max.

### Microsoft Outlook/Exchange

**Auth:** OAuth 2.0 via Microsoft Identity Platform (MSAL)  
**Scopes needed:**
- `Calendars.Read`
- `Mail.Read`
- `offline_access`

**Push mechanism:**
```
Microsoft Graph subscriptions -> Pulse webhook endpoint
```
Graph subscriptions: `POST /subscriptions` with a notification URL. MS Graph sends a validation challenge first (must respond within 10s), then pushes change notifications.

Quota limits:
- Subscriptions expire after 4230 minutes (~3 days) for calendar, 4320 minutes for mail
- Must be renewed before expiry
- Rate limit: 10,000 requests/10 min per app per tenant (generous)
- Concurrency: max 1000 active subscriptions per app

### Apple Calendar / iCloud

**Auth:** OAuth 2.0 for iCloud (uses Apple's private OAuth flow -- complex)  
**Alternative:** CalDAV -- username + app-specific password

**The hard truth about Apple:**
- No push API for CalDAV
- Apple doesn't publish a public CalDAV webhook mechanism
- Strategy: poll CalDAV every 5-15 minutes using ETags for change detection

```python
# Efficient CalDAV polling with ETag caching
def poll_caldav(calendar_url, stored_etag):
    response = requests.request('PROPFIND', calendar_url, 
        headers={'If-None-Match': stored_etag})
    if response.status_code == 304:
        return None  # No changes, skip processing
    # Process changes, store new ETag
```

**Alternative for Mac users:** Use EventKit via a native Mac helper app that subscribes to local calendar change notifications -- zero network polling, instant.

### Auth Token Management

All OAuth tokens stored encrypted (AES-256-GCM) in:
- **Mac/iOS:** Keychain
- **Android:** Android Keystore
- **Windows:** Windows Credential Manager

Refresh tokens are long-lived. Access tokens refresh automatically before expiry via background task.

---

## 3. The Recipe Schema

### Design Principles

A recipe is a declarative description of: "when X happens in context Y, gather Z, ask the LLM P, and deliver via channel C -- but not more than once every D minutes."

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://pulse.app/schemas/recipe/v1",
  "title": "PulseRecipe",
  "type": "object",
  "required": ["id", "name", "version", "triggers", "context", "prompt", "delivery", "cooldown"],
  "properties": {

    "id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique recipe identifier"
    },

    "name": {
      "type": "string",
      "maxLength": 100,
      "examples": ["Pre-meeting Brief", "Overdue Invoice Alert"]
    },

    "description": {
      "type": "string",
      "maxLength": 500
    },

    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "examples": ["1.0.0"]
    },

    "author": {
      "type": "object",
      "properties": {
        "type": { "type": "string", "enum": ["system", "user", "community"] },
        "id": { "type": "string" },
        "job_role": { "type": "string", "examples": ["Executive Assistant", "Sales Manager"] }
      }
    },

    "enabled": {
      "type": "boolean",
      "default": true
    },

    "shadow_mode": {
      "type": "boolean",
      "default": false,
      "description": "If true, recipe evaluates but does not deliver. Logs would-have-fired events."
    },

    "confidence_threshold": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.75,
      "description": "Minimum confidence score before a trigger is acted on"
    },

    "triggers": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["type"],
        "properties": {

          "type": {
            "type": "string",
            "enum": ["time_before_event", "time_after_event", "cron", "email_received", "email_keyword", "calendar_event_created", "calendar_event_changed", "data_threshold", "webhook", "manual"]
          },

          "source": {
            "type": "string",
            "enum": ["google_calendar", "gmail", "outlook_calendar", "outlook_mail", "apple_calendar", "icloud_mail", "custom_webhook", "internal"],
            "description": "Data source this trigger watches"
          },

          "conditions": {
            "type": "array",
            "description": "All conditions must be true (AND logic). Use nested 'or' for OR logic.",
            "items": {
              "type": "object",
              "required": ["field", "operator", "value"],
              "properties": {
                "field": {
                  "type": "string",
                  "examples": ["event.title", "email.subject", "email.from", "event.attendees.count", "event.location"]
                },
                "operator": {
                  "type": "string",
                  "enum": ["equals", "not_equals", "contains", "not_contains", "matches_regex", "gt", "gte", "lt", "lte", "in_list", "not_in_list", "exists", "not_exists"]
                },
                "value": {
                  "description": "Comparison value -- string, number, boolean, or array"
                },
                "or": {
                  "type": "array",
                  "description": "Nested OR conditions",
                  "items": { "$ref": "#/properties/triggers/items/properties/conditions/items" }
                }
              }
            }
          },

          "time_offset_minutes": {
            "type": "integer",
            "description": "For time_before_event / time_after_event: minutes offset from event start/end. Negative = before.",
            "examples": [-30, -60, 10]
          },

          "cron_expression": {
            "type": "string",
            "description": "Standard cron expression for cron-type triggers",
            "examples": ["0 9 * * 1-5", "*/15 9-17 * * *"]
          },

          "hot_window": {
            "type": "object",
            "description": "Increase polling frequency during this time window",
            "properties": {
              "start_offset_minutes": { "type": "integer", "examples": [-120] },
              "end_offset_minutes": { "type": "integer", "examples": [30] },
              "poll_interval_seconds": { "type": "integer", "examples": [120] }
            }
          }

        }
      }
    },

    "context": {
      "type": "object",
      "description": "What to gather when a trigger fires",
      "properties": {

        "gather": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["type"],
            "properties": {
              "type": {
                "type": "string",
                "enum": ["calendar_event_details", "recent_emails_from_attendee", "email_thread", "attendee_profiles", "weather", "news_search", "web_search", "user_notes", "previous_meeting_summary", "custom_api"]
              },
              "params": {
                "type": "object",
                "description": "Type-specific parameters",
                "examples": [
                  { "lookback_hours": 72, "max_emails": 10 },
                  { "query_template": "{{event.attendees[0].name}} {{event.attendees[0].company}}" }
                ]
              },
              "required": {
                "type": "boolean",
                "default": false,
                "description": "If true and context fetch fails, abort the trigger"
              },
              "max_tokens_budget": {
                "type": "integer",
                "description": "Max tokens this context item may consume in the prompt",
                "examples": [500, 1000, 2000]
              }
            }
          }
        },

        "total_context_budget_tokens": {
          "type": "integer",
          "default": 4000,
          "description": "Hard cap on total context tokens sent to LLM"
        }

      }
    },

    "prompt": {
      "type": "object",
      "required": ["template"],
      "properties": {

        "system": {
          "type": "string",
          "description": "System prompt override. Defaults to Pulse system prompt if omitted.",
          "examples": ["You are a proactive executive assistant. Be concise and specific."]
        },

        "template": {
          "type": "string",
          "description": "Handlebars-style template. Variables from trigger event + context are injected.",
          "examples": [
            "You have a meeting with {{event.attendees | join(', ')}} in {{time_until_event}} minutes.\n\nRecent email context:\n{{context.recent_emails}}\n\nProvide a 3-bullet brief covering: key topics likely to come up, any open items from email, and one smart question to ask."
          ]
        },

        "output_format": {
          "type": "string",
          "enum": ["markdown", "plain_text", "json", "bullet_list"],
          "default": "markdown"
        },

        "max_output_tokens": {
          "type": "integer",
          "default": 500,
          "examples": [150, 300, 800]
        },

        "tone": {
          "type": "string",
          "enum": ["brief", "conversational", "formal", "urgent"],
          "default": "conversational"
        }

      }
    },

    "routing": {
      "type": "object",
      "description": "LLM routing hints. If omitted, auto-routing applies.",
      "properties": {
        "preferred_model": {
          "type": "string",
          "enum": ["auto", "claude-haiku", "claude-sonnet", "claude-opus", "gpt-4o-mini", "gpt-4o", "gemini-flash", "gemini-pro"],
          "default": "auto"
        },
        "complexity_override": {
          "type": "string",
          "enum": ["low", "medium", "high"],
          "description": "Override auto-complexity detection"
        },
        "fallback_model": {
          "type": "string",
          "description": "Use this if primary model is unavailable or rate-limited"
        }
      }
    },

    "delivery": {
      "type": "object",
      "required": ["channels"],
      "properties": {

        "channels": {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "object",
            "required": ["type"],
            "properties": {
              "type": {
                "type": "string",
                "enum": ["push_notification", "sms", "email", "telegram", "slack", "in_app", "webhook"]
              },
              "config": {
                "type": "object",
                "description": "Channel-specific config",
                "examples": [
                  { "telegram_chat_id": "YOUR_CHAT_ID", "topic_id": 16 },
                  { "email_to": "{{user.email}}", "subject_template": "Heads up: {{event.title}}" },
                  { "sms_to": "{{user.phone}}" }
                ]
              },
              "priority": {
                "type": "string",
                "enum": ["normal", "high", "critical"],
                "default": "normal"
              },
              "truncate_to_chars": {
                "type": "integer",
                "description": "For push/SMS -- truncate output to N chars",
                "examples": [160, 300]
              }
            }
          }
        },

        "suppress_during": {
          "type": "array",
          "description": "Suppress delivery during these calendar event types",
          "items": {
            "type": "string",
            "enum": ["busy", "focus_time", "out_of_office", "tentative"]
          }
        },

        "quiet_hours": {
          "type": "object",
          "properties": {
            "start": { "type": "string", "pattern": "^([01]\\d|2[0-3]):[0-5]\\d$", "examples": ["23:00"] },
            "end": { "type": "string", "pattern": "^([01]\\d|2[0-3]):[0-5]\\d$", "examples": ["07:00"] },
            "timezone": { "type": "string", "examples": ["Africa/Johannesburg"] },
            "override_if_critical": { "type": "boolean", "default": false }
          }
        }

      }
    },

    "cooldown": {
      "type": "object",
      "required": ["period_minutes"],
      "properties": {
        "period_minutes": {
          "type": "integer",
          "minimum": 0,
          "description": "Minimum minutes between fires of this recipe for the same event/entity",
          "examples": [60, 1440, 10080]
        },
        "scope": {
          "type": "string",
          "enum": ["per_event", "per_recipe", "per_user_per_recipe"],
          "default": "per_event",
          "description": "per_event = cooldown per unique event. per_recipe = global recipe cooldown."
        },
        "reset_on_significant_change": {
          "type": "boolean",
          "default": true,
          "description": "Reset cooldown if the triggering event changes significantly (e.g., meeting time changes)"
        }
      }
    },

    "feedback": {
      "type": "object",
      "description": "Feedback and learning configuration",
      "properties": {
        "collect_feedback": { "type": "boolean", "default": true },
        "auto_pause_after_negatives": { "type": "integer", "default": 3 },
        "auto_adjust_confidence": { "type": "boolean", "default": true }
      }
    },

    "metadata": {
      "type": "object",
      "properties": {
        "tags": { "type": "array", "items": { "type": "string" } },
        "job_roles": { "type": "array", "items": { "type": "string" }, "examples": [["Executive Assistant", "Chief of Staff"]] },
        "community_rating": { "type": "number", "minimum": 0, "maximum": 5 },
        "install_count": { "type": "integer" },
        "created_at": { "type": "string", "format": "date-time" },
        "updated_at": { "type": "string", "format": "date-time" }
      }
    }

  }
}
```

### Example Recipe Instance -- "Pre-Meeting Brief"

```json
{
  "id": "a3f4c891-2b1e-4d77-9f0a-123456789abc",
  "name": "Pre-Meeting Brief",
  "description": "30 minutes before any external meeting, pull recent email context and generate a talking points brief",
  "version": "1.0.0",
  "author": { "type": "system", "job_role": "Executive Assistant" },
  "enabled": true,
  "shadow_mode": false,
  "confidence_threshold": 0.80,

  "triggers": [{
    "type": "time_before_event",
    "source": "google_calendar",
    "time_offset_minutes": -30,
    "conditions": [
      { "field": "event.attendees.count", "operator": "gte", "value": 2 },
      { "field": "event.status", "operator": "not_equals", "value": "cancelled" },
      { "field": "event.transparency", "operator": "not_equals", "value": "transparent" }
    ],
    "hot_window": {
      "start_offset_minutes": -90,
      "end_offset_minutes": 0,
      "poll_interval_seconds": 120
    }
  }],

  "context": {
    "gather": [
      {
        "type": "calendar_event_details",
        "required": true,
        "max_tokens_budget": 500
      },
      {
        "type": "recent_emails_from_attendee",
        "params": { "lookback_hours": 168, "max_emails": 5, "exclude_self": true },
        "required": false,
        "max_tokens_budget": 2000
      },
      {
        "type": "previous_meeting_summary",
        "params": { "max_meetings": 2 },
        "required": false,
        "max_tokens_budget": 800
      }
    ],
    "total_context_budget_tokens": 3500
  },

  "prompt": {
    "system": "You are a sharp executive assistant. Be concise, specific, and actionable. No fluff.",
    "template": "Meeting in {{time_until_event_minutes}} minutes: **{{event.title}}**\nWith: {{event.attendees | join(', ')}}\nDuration: {{event.duration_minutes}} min\n\nRecent email context:\n{{context.recent_emails_from_attendee}}\n\nPrevious meetings:\n{{context.previous_meeting_summary}}\n\nProvide:\n1. **3 key topics** likely to come up\n2. **Any open items** from email thread\n3. **One smart question** to ask\n4. **Watch out for** (any friction points from recent context)",
    "output_format": "markdown",
    "max_output_tokens": 400,
    "tone": "brief"
  },

  "routing": {
    "preferred_model": "auto",
    "complexity_override": "medium"
  },

  "delivery": {
    "channels": [{
      "type": "push_notification",
      "priority": "high",
      "truncate_to_chars": 300
    }],
    "suppress_during": ["busy", "focus_time"],
    "quiet_hours": {
      "start": "22:00",
      "end": "07:00",
      "timezone": "Africa/Johannesburg",
      "override_if_critical": false
    }
  },

  "cooldown": {
    "period_minutes": 20,
    "scope": "per_event",
    "reset_on_significant_change": true
  },

  "feedback": {
    "collect_feedback": true,
    "auto_pause_after_negatives": 3,
    "auto_adjust_confidence": true
  },

  "metadata": {
    "tags": ["meetings", "email", "briefing"],
    "job_roles": ["Executive Assistant", "Sales Manager", "Chief of Staff", "Consultant"],
    "created_at": "2026-03-17T00:00:00Z"
  }
}
```

---

## 4. LLM Routing

### Routing Philosophy

Not every nudge needs Sonnet. A "your standup is in 10 minutes" reminder is a Haiku job. A "here's your board presentation brief with synthesis across 20 documents" is Opus territory. Smart routing cuts costs dramatically while keeping quality high where it matters.

### Routing Decision Tree

```
Trigger fires -> Recipe has preferred_model?
    
     YES (not "auto") -> Use that model
    
     NO ("auto") -> Score complexity
              
              
        
                  COMPLEXITY SCORER               
                                                  
          Score = 0                               
          + context_tokens / 500          (0-8)   
          + reasoning_required ? 3 : 0    (0-3)   
          + synthesis_required ? 2 : 0    (0-2)   
          + external_data_sources.count   (0-3)   
          + output_length_class           (0-2)   
          - user_in_hurry ? 2 : 0         (0-2)   
        
                              
              
            0-4              5-10            11+
                                            
                                            
          HAIKU           SONNET            OPUS
        (simple         (analysis,        (deep
         nudges,         synthesis,       research,
         reminders,      briefs,          complex
         alerts)         summaries)       reasoning)
```

### Complexity Scoring -- Detailed Factors

```python
class ComplexityScorer:
    
    def score(self, recipe: Recipe, context: GatheredContext) -> tuple[float, str]:
        score = 0.0
        
        # Context volume
        context_token_score = min(context.total_tokens / 500, 8)
        score += context_token_score
        
        # Reasoning indicators (in prompt template)
        reasoning_keywords = ['analyze', 'synthesize', 'compare', 'evaluate', 
                               'assess', 'recommend', 'strategy', 'implications']
        if any(kw in recipe.prompt.template.lower() for kw in reasoning_keywords):
            score += 3
        
        # Multi-source synthesis
        if len(context.sources) > 2:
            score += 2
        
        # External data count
        score += min(len(context.external_fetches), 3)
        
        # Output length
        if recipe.prompt.max_output_tokens > 600:
            score += 2
        elif recipe.prompt.max_output_tokens > 300:
            score += 1
        
        # Time pressure reduces score (prefer speed)
        if context.trigger_event.urgency == 'high':
            score -= 2
        
        # Model selection
        if score <= 4:
            return score, 'claude-haiku-3-5'
        elif score <= 10:
            return score, 'claude-sonnet-4-5'
        else:
            return score, 'claude-opus-4'
```

### Model Routing Table

| Use Case | Model | Rationale |
|----------|-------|-----------|
| Simple time reminder ("standup in 10 min") | claude-haiku-3-5 | No synthesis needed |
| Pre-meeting brief (5-10 emails) | claude-sonnet-4-5 | Synthesis, moderate context |
| Daily digest (30+ emails) | claude-sonnet-4-5 | High volume, moderate reasoning |
| Board prep brief (docs + emails + news) | claude-opus-4 | Deep synthesis |
| Invoice overdue alert | claude-haiku-3-5 | Simple threshold check |
| Contract renewal brief | claude-sonnet-4-5 | Needs context + analysis |
| New job recipe generation | claude-sonnet-4-5 | Creative + structured output |

### Cost Guards

- **Token budget enforcement**: each recipe defines `max_output_tokens`. Context is trimmed to `total_context_budget_tokens` before dispatch.
- **Monthly user cap**: configurable soft limit on LLM spend per user (warn at 80%, pause at 100%)
- **Model fallback**: if Sonnet is rate-limited, fall back to the recipe's `fallback_model` -- don't just fail silently
- **Batching**: if multiple recipes trigger within 60 seconds, evaluate whether context overlaps and batch into a single LLM call

---

## 5. On-the-Fly Job Detection Pipeline

When a user enters a job title with no matching recipes in the library, Pulse spins up this pipeline:

```
User enters job title: "Revenue Operations Analyst"
              
              

  1. Library Lookup            -> Fuzzy match against known roles
     (vector similarity)          "Ops Analyst" -> partial match?
     If similarity > 0.85 -> use closest match
                No good match
               

  2. Web Research              -> Brave/Serper API
     "Revenue Operations          + LinkedIn role descriptions
      Analyst responsibilities    + job boards (Indeed, Glassdoor)
      day in the life tasks" 

               
               

  3. Research Synthesis        -> Haiku/Sonnet extracts:
                                  - Core responsibilities (10-15 items)
                                  - Key data sources used
                                  - Common pain points / time sinks
                                  - Important recurring events
                                  - Stakeholders they interact with

               
               

  4. Recipe Generation         -> Sonnet generates 5-10 starter recipes
                                  using the recipe JSON schema
                                  Each recipe gets:
                                  - Appropriate trigger
                                  - Context gather config
                                  - Prompt template for this role

               
               

  5. Validation                -> Schema validation (JSON Schema)
                                  Prompt template sanity check
                                  Duplicate detection vs existing library

               
               

  6. Shadow Mode Deploy        -> All new recipes start in shadow_mode: true
                                  48h observation period
                                  User reviews "would have fired" log

               
               

  7. User Activation           -> User sees generated recipes
     + Community Submission       Reviews, edits, approves each
                                  Optional: "Submit to community library"
                                  Community submissions are reviewed before publishing

```

### Implementation Detail

```python
class JobRecipeGenerator:
    
    async def generate(self, job_title: str, user_id: str) -> list[Recipe]:
        # Step 1: Library fuzzy match
        similar = await self.recipe_library.fuzzy_match(job_title, threshold=0.85)
        if similar:
            return similar  # Return closest existing recipes
        
        # Step 2: Web research (parallel fetches)
        search_queries = [
            f"{job_title} responsibilities day in the life",
            f"{job_title} tools software used",
            f"{job_title} common challenges pain points",
            f"{job_title} key meetings deliverables"
        ]
        research_results = await asyncio.gather(*[
            self.web_searcher.search(q, max_results=5) for q in search_queries
        ])
        
        # Step 3: Synthesize research
        synthesis_prompt = f"""
        Based on this research about "{job_title}", extract:
        1. Core daily/weekly responsibilities (bullet list)
        2. Key data sources and tools used
        3. Common time-sensitive tasks (meetings, deadlines, reports)
        4. Important stakeholders and communication patterns
        5. Top 3 pain points where proactive help would matter most
        
        Research: {research_results}
        """
        role_profile = await self.llm.complete(synthesis_prompt, model='claude-sonnet-4-5')
        
        # Step 4: Generate recipes
        recipe_gen_prompt = f"""
        Create 5-8 Pulse recipes for a {job_title}.
        
        Role profile:
        {role_profile}
        
        Each recipe must follow this JSON schema exactly:
        {RECIPE_SCHEMA_SUMMARY}
        
        Focus on:
        - The 2-3 highest-value proactive nudges for this role
        - Mix of time-based, event-based, and email-based triggers
        - Prompts that give genuinely useful, specific output for this role
        
        Return a JSON array of recipe objects.
        """
        raw_recipes = await self.llm.complete(recipe_gen_prompt, model='claude-sonnet-4-5', 
                                               output_format='json')
        
        # Step 5: Validate + persist
        validated = [self.validate_recipe(r) for r in raw_recipes]
        await self.user_profile.save_recipes(user_id, validated, shadow_mode=True)
        
        return validated
```

### Community Library Submission Flow

```
User approves recipe -> "Submit to library?" prompt
    
     Yes -> Strip PII from prompt templates
             Add metadata (job_role, tags, rating=0)
             POST to community API (needs Pulse account)
             Enters moderation queue (auto + human review)
             Published if passes review
    
     No  -> Stays in user's private library only
```

---

## 6. Multi-Platform Backend Architecture

### Stack Recommendation

```

                    CLIENT APPS                               
   iOS (Swift/SwiftUI)    Android (Kotlin)    Mac (Swift)  
   Windows (.NET MAUI or Electron)                            

                          HTTPS / WebSocket
                         

                  API GATEWAY (Cloudflare)                    
              Rate limiting, Auth, DDoS protection            

                         
              
                                   
   
   FastAPI Backend           Supabase (Postgres + Auth)  
   (Python 3.12+)          User profiles, recipes,       
                           feedback, community library   
   - REST API              Row-Level Security enforced   
   - WebSocket hub      
   - Webhook receiver
   - Trigger eval       
   - LLM dispatch            Redis (Upstash)             
                           Cooldown cache, dedup,        
      rate limiting, session state  
                          
                         

                NOTIFICATION SERVICES                         
                                                              
   APNs (iOS/Mac)    FCM (Android)    Telegram Bot API     
   Twilio (SMS)      SendGrid (email)  Slack API            



                BACKGROUND WORKERS (Celery)                   
                                                              
   - Webhook subscription renewal (Google/MS 7-day expiry)   
   - CalDAV polling for Apple Calendar                        
   - Recipe shadow mode log aggregation                       
   - Community library moderation queue                       
   - OAuth token refresh                                      

```

### Why FastAPI (not Node)?

| Criteria | FastAPI (Python) | Node/Express |
|----------|------------------|--------------|
| LLM SDK ecosystem |  Best-in-class (Anthropic, OpenAI, Google all primary in Python) |  Good but secondary |
| Async performance |  async/await native |  Native async |
| Type safety |  Pydantic v2 |  TypeScript needed |
| Data/ML libraries |  pandas, sklearn for analytics |  Limited |
| Team familiarity | Context-dependent | Context-dependent |

**Verdict:** FastAPI + Pydantic v2 is the right choice. Pydantic models for recipe validation are first-class citizens.

### Why Supabase (not Firebase/PlanetScale)?

- **Postgres** = complex queries for recipe matching, filtering, search
- **Row-Level Security** = privacy by default at DB layer
- **Auth** = handles OAuth flows, JWT, MFA out of the box
- **Realtime** = WebSocket subscriptions for live recipe status updates to client
- **Self-hostable** = enterprise customers can run their own Supabase instance
- **Open source** = no vendor lock-in

### Push Notifications

```python
class NotificationDispatcher:
    
    async def dispatch(self, user_id: str, content: str, priority: str):
        user = await self.db.get_user(user_id)
        
        tasks = []
        for channel in user.active_channels:
            if channel.type == 'apns':
                tasks.append(self.send_apns(channel.token, content, priority))
            elif channel.type == 'fcm':
                tasks.append(self.send_fcm(channel.token, content, priority))
            elif channel.type == 'telegram':
                tasks.append(self.send_telegram(channel.chat_id, content, channel.topic_id))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # Log failures, retry with exponential backoff
```

**APNs setup:**
- Use APNs HTTP/2 API with JWT auth (no cert renewal headaches)
- `apns2` Python library
- Notification service extension for rich notifications (action buttons for feedback)

**FCM setup:**
- Firebase Admin SDK
- FCM v1 API (legacy API deprecated 2024)
- High-priority messages for critical nudges

### Deployment

```
Development:   Docker Compose (FastAPI + Supabase local + Redis)
Staging:       Fly.io (FastAPI), Supabase cloud, Upstash Redis
Production:    Fly.io multi-region OR Railway
               Cloudflare for edge/CDN/WAF
               Backups: Supabase daily backups + S3
```

Fly.io is preferred over AWS for v1 -- far less operational overhead, global anycast, built-in health checks.

---

## 7. Privacy Architecture

### Core Principle: Minimum Viable Data Transmission

> "Don't send data to the cloud unless you have to. When you do, send the minimum. When you store it, encrypt it."

### Architecture Tiers

```
TIER 1 -- ON-DEVICE ONLY (never leaves device)

- Raw email content
- Raw calendar event details  
- OAuth access tokens
- User's private notes
- Unprocessed data from integrations

TIER 2 -- EPHEMERAL TRANSIT (sent to backend, not stored)

- Assembled context for LLM calls (sent, result returned, discarded)
- Trigger evaluation data (evaluated server-side, raw data not persisted)

TIER 3 -- STORED IN BACKEND (encrypted, minimal)

- User profile (email, preferences, timezone)
- Recipe configurations
- Delivery channel tokens (APNs/FCM tokens, Telegram chat ID)
- Anonymized feedback signals (/ per recipe, no content)
- Usage stats (trigger fired: yes/no, model used, latency)

NEVER STORED

- Email content
- Calendar event titles/descriptions
- LLM prompts or responses
- Names of attendees
```

### On-Device Processing Option (Privacy Mode)

For maximum privacy, offer a **"Local Mode"** where:
- The Pulse daemon runs entirely on-device
- LLM calls go directly to a local model (Ollama + Llama 3.2, Phi-4, Mistral)
- Or go directly to the LLM API (user provides their own API key -- Anthropic/OpenAI)
- The Pulse backend is used only for recipe sync and push notification routing

```
Standard Mode:
  Device -> Pulse Backend -> LLM API -> Pulse Backend -> Push Notification -> Device

Local Mode (Privacy):
  Device -> Local LLM (Ollama) -> Push Notification (local) -> Device
  Device -> LLM API (user's own key) -> Push Notification -> Device
```

### Encryption Architecture

```
ENCRYPTION AT REST

- OAuth tokens: AES-256-GCM, key = device-derived secret (Keychain/Keystore)
- On-device cache: SQLCipher (encrypted SQLite)
- Supabase: Postgres column encryption for user secrets using pgcrypto

ENCRYPTION IN TRANSIT

- All API calls: TLS 1.3 minimum, HSTS enforced
- Certificate pinning: enforced on iOS/Android clients
- Webhook endpoints: HMAC signature verification (Google, MS Graph both support this)

END-TO-END FOR SENSITIVE CONTEXT

- If cloud LLM is used: context assembled on-device, encrypted with user's
  ephemeral key before transit, decrypted only for LLM call, immediately discarded
- Pulse backend never sees plaintext context
```

### Granular Permission Controls

```
INTEGRATION PERMISSIONS (user controls each)

 Google Calendar -- read events
 Google Calendar -- read attendee details
 Gmail -- scan for trigger keywords
 Gmail -- read full email content
 Gmail -- access attachments

RECIPE PERMISSIONS (per recipe)

- "This recipe needs access to: email content, calendar events, attendee names"
- User approves each data type per recipe (not blanket approval)
- Permission can be revoked per recipe without disabling the recipe entirely
  (recipe degrades gracefully with less context)

DATA RETENTION

- LLM call context: ephemeral (never stored)
- Processed nudge content: stored 30 days (configurable: 7/30/90/never)
- Feedback signals: stored anonymized indefinitely (for recipe improvement)
- Integration tokens: stored until user revokes or account deleted
```

### GDPR / Data Residency

- EU users: data in EU Supabase region (Frankfurt)
- Data export: one-click export of all stored data (recipes, profile, feedback history)
- Right to deletion: account delete wipes all backend data within 24h, sends confirmation
- Data processing agreement: required for enterprise customers

### Threat Model

| Threat | Mitigation |
|--------|-----------|
| Backend breach exposes user data | Minimal data stored; no email/calendar content |
| OAuth token theft | Tokens in OS secure storage; short-lived access tokens |
| Man-in-the-middle | TLS 1.3 + cert pinning on mobile |
| LLM provider sees sensitive data | Local mode option; context minimization |
| Insider threat (Pulse employee) | No employee access to user email/calendar content |
| Recipe abuse (malicious community recipes) | Moderation queue; sandbox evaluation; HMAC signing |

---

## Appendix A: Technology Stack Summary

| Layer | Technology | Reasoning |
|-------|-----------|-----------|
| Backend API | FastAPI (Python 3.12) | Best LLM ecosystem, async, Pydantic |
| Database | Supabase (Postgres) | RLS, Auth, Realtime, self-hostable |
| Cache / Cooldown | Upstash Redis | Serverless Redis, generous free tier |
| Background jobs | Celery + Redis | Proven, flexible, integrates with FastAPI |
| iOS app | Swift / SwiftUI | Native performance, EventKit, Keychain |
| Android app | Kotlin + Jetpack Compose | Modern Android, WorkManager for daemon |
| Mac app | Swift / SwiftUI (macOS) | Native, launchd daemon, EventKit |
| Windows app | .NET MAUI or Electron | MAUI preferred; Electron as fallback |
| Push (iOS/Mac) | APNs (HTTP/2, JWT) | Native Apple push |
| Push (Android) | FCM v1 | Google standard |
| Push (cross-platform) | Telegram Bot API | Already in stack; zero infra |
| SMS | Twilio | Reliable, global |
| Email delivery | SendGrid | Deliverability, templates |
| Edge/CDN/WAF | Cloudflare | DDoS, rate limiting, global |
| Deployment | Fly.io | Low-ops, multi-region, great DX |
| Local LLM (privacy mode) | Ollama | Open source, cross-platform, easy |
| LLM primary | Anthropic Claude API | Best-in-class for synthesis |
| Web search (job pipeline) | Brave Search API | Privacy-friendly, good quality |
| Schema validation | JSON Schema (Draft 7) + Pydantic | Dual validation |
| Encryption | AES-256-GCM, TLS 1.3, SQLCipher | Industry standard |

---

## Appendix B: V1 Scope Recommendation

**Build in V1:**
- Google Calendar + Gmail integration (covers ~70% of users)
- Daemon with time-based + email-based triggers
- 10-15 curated system recipes for top 5 job roles
- Push notification delivery (APNs + FCM + Telegram)
- Recipe schema + shadow mode
- Basic LLM routing (Haiku vs Sonnet)
- FastAPI backend + Supabase
- iOS + Android apps

**Defer to V2:**
- Outlook/Exchange integration
- Apple Calendar / iCloud
- On-the-fly job detection pipeline
- Community library
- Local mode (Ollama)
- Windows/Mac desktop apps
- SMS delivery
- Custom recipe builder UI

**Rationale:** Ship fast, validate the core loop (watcher -> trigger -> nudge -> feedback) before building the broader integration surface. The Gmail + Google Calendar integration alone covers the majority of the target market and is the hardest to get right.

---

*End of technical architecture spec. This document is a living spec -- update as decisions are made and tradeoffs are resolved.*
