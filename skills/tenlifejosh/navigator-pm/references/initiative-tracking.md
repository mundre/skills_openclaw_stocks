# Initiative Tracking — Reference Guide

Tracking multiple workstreams without losing any, status reporting formats,
and dashboard design for a founder-led company.

---

## 1. THE INITIATIVE REGISTRY

### What Gets Tracked
```
ACTIVE INITIATIVES: Currently in execution (maximum 3)
IN-PROGRESS: Started but waiting on something
PAUSED: Deliberately paused with resume condition
BACKLOG: Scored and waiting for bandwidth
COMPLETE: Done and measured
KILLED: Deliberately stopped (archive, don't delete — learn from it)
```

### Initiative Registry Format
```json
{
  "initiatives": [
    {
      "id": "TLC-001",
      "name": "GND Cold Outreach Campaign",
      "status": "active",
      "owner": "Hutch + Joshua",
      "goal": "5 new GND clients by Q2 end",
      "metric": "Clients added: 0/5",
      "started": "2024-01-15",
      "target": "2024-03-31",
      "last_update": "2024-01-22",
      "blockers": [],
      "notes": "Week 1: 10 emails sent, 1 response"
    }
  ]
}
```

---

## 2. STATUS TRACKING

### Status Definitions
```
🟢 ACTIVE: In execution, on track
🟡 AT RISK: In execution, behind pace — needs attention
🔴 BLOCKED: Cannot proceed due to specific blocker
⏸️ PAUSED: Deliberately paused — resume condition documented
✅ COMPLETE: Done and measured
❌ KILLED: Stopped — reason documented
📋 BACKLOG: Scored, waiting for bandwidth
```

---

## 3. THE INITIATIVE DASHBOARD

### Weekly Dashboard Format
```
## TLC Initiative Dashboard — Week of [Date]

ACTIVE WORKSTREAMS (Maximum 3):

1. GND Client Acquisition | 🟢 ON TRACK
   Goal: 5 clients by March 31
   Current: 2 clients ($198 MRR)
   This week: Send 10 more cold emails, follow up with 3 open conversations
   Owner: Joshua + Hutch

2. Gumroad Catalog Optimization | 🟡 AT RISK
   Goal: All 9 products with optimized listings
   Current: 4/9 complete
   Blocker: Need Scribe to refresh 5 remaining descriptions
   Owner: Scribe Agent → Hutch review

3. Budget Binder Etsy Launch | 🟢 ON TRACK
   Goal: Live on Etsy by Friday
   Current: Listing drafted, 80% complete
   This week: Complete listing, upload file, test purchase
   Owner: Publisher Agent

PAUSED:
  - Prayful beta | ⏸️ Resume: When GND hits 5 clients
  
BACKLOG (next up):
  - First Job Playbook Etsy listing | 📋 Priority: HIGH
  - Legacy Letters description refresh | 📋 Priority: MEDIUM
```

---

## 4. TRACKING WITHOUT DROWNING

### The Minimum Viable Tracking System
```
What to track: Only what you need to make decisions about
What not to track: Everything that "might be useful someday"

MANDATORY TRACKING:
  - Active initiative status (weekly)
  - Revenue (weekly)
  - Quarterly OKR progress (weekly)
  
OPTIONAL TRACKING (add when problems arise):
  - Email open/reply rates (if GND outreach isn't converting)
  - Gumroad conversion rates (if products aren't selling)
  - Time spent per initiative (if bandwidth is a concern)

RULE: If you're spending more time tracking than doing — the tracking system is too heavy.
```
