# Memory Triggers

Triggers are programmable rules that fire when memory events occur. They automate memory lifecycle management without agent intervention.

## Trigger Events

| Event | Fires when |
|---|---|
| `on_create` | A new memory is stored |
| `on_recall` | A memory is accessed/searched |
| `on_decay` | A memory's heat drops below threshold |
| `on_boost` | A memory's heat is boosted above threshold |

## Trigger Actions

| Action | What it does |
|---|---|
| `notify` | Send notification (via configured channel) |
| `boost` | Increase memory heat |
| `tag` | Add a tag/label to the memory |
| `deprecate` | Mark memory for accelerated decay |

## Filters

Triggers can filter on:
- `filter_memory_type`: Only fire for specific types (e.g., `"fact"`, `"preference"`)
- `filter_namespace`: Only fire in specific namespace
- `filter_label_pattern`: Regex match on memory labels
- `filter_heat_below`: Only fire when heat is below threshold
- `filter_heat_above`: Only fire when heat is above threshold

## Creating Triggers

### Via REST API

```bash
curl -X POST https://api.sulcus.ca/api/v1/triggers \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cold Memory Alert",
    "event": "on_decay",
    "action": "notify",
    "filter_memory_type": "fact",
    "filter_heat_below": 0.1,
    "cooldown_seconds": 3600
  }'
```

### Via Python SDK

```python
from sulcus import Sulcus

client = Sulcus(api_key="sk-...")
trigger = client.create_trigger(
    name="Recall Boost",
    event="on_recall",
    action="boost",
    action_config={"amount": 0.15},
    filter_memory_type="procedural",
    cooldown_seconds=300
)
```

### Via Node.js SDK

```typescript
import { Sulcus } from "sulcus";

const client = new Sulcus({ apiKey: "sk-..." });
const trigger = await client.createTrigger({
  name: "Hot Memory Tagger",
  event: "on_boost",
  action: "tag",
  actionConfig: { tag: "high-value" },
  filterHeatAbove: 0.9,
  cooldownSeconds: 600,
});
```

## Managing Triggers

```bash
# List all triggers
curl https://api.sulcus.ca/api/v1/triggers -H "Authorization: Bearer KEY"

# Get trigger history
curl https://api.sulcus.ca/api/v1/triggers/TRIGGER_ID/history -H "Authorization: Bearer KEY"

# Delete a trigger
curl -X DELETE https://api.sulcus.ca/api/v1/triggers/TRIGGER_ID -H "Authorization: Bearer KEY"

# Toggle enabled/disabled
curl -X PATCH https://api.sulcus.ca/api/v1/triggers/TRIGGER_ID \
  -H "Authorization: Bearer KEY" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

## Common Trigger Patterns

### 1. Cold Memory Alert
Notify when important facts are about to be forgotten:
```json
{"event": "on_decay", "action": "notify", "filter_memory_type": "fact", "filter_heat_below": 0.1}
```

### 2. Procedural Recall Boost
Auto-reinforce procedures each time they're used:
```json
{"event": "on_recall", "action": "boost", "action_config": {"amount": 0.15}, "filter_memory_type": "procedural"}
```

### 3. Preference Notification
Get notified when a new preference is learned:
```json
{"event": "on_create", "action": "notify", "filter_memory_type": "preference"}
```

### 4. High-Value Tagger
Auto-tag memories that get boosted above 0.9 heat:
```json
{"event": "on_boost", "action": "tag", "action_config": {"tag": "high-value"}, "filter_heat_above": 0.9}
```

## Limits

- `max_fires`: Optional cap on total times a trigger fires (null = unlimited)
- `cooldown_seconds`: Minimum interval between firings (prevents spam)
