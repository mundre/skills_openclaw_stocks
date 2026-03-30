# Thermodynamic Configuration

Sulcus uses a thermodynamic model for memory lifecycle. All parameters are configurable per-tenant.

## Default Half-Lives

| Memory Type | Default Half-Life | Meaning |
|---|---|---|
| `episodic` | 24 hours | Drops to 50% heat in 24h without recall |
| `semantic` | 30 days | General knowledge decays slowly |
| `preference` | 90 days | User preferences are long-lived |
| `procedural` | 180 days | Procedures are very durable |
| `fact` | 30 days | Facts decay like semantic memory |
| `moment` | 12 hours | Fleeting context fades fast |

## Decay Formula

```
decay_factor = 2^(-tick_interval / half_life)
new_heat = current_heat × decay_factor
```

With stability from spaced repetition:
```
effective_half_life = base_half_life × stability
```

Each recall multiplies stability (default: ×1.5), stretching the effective half-life.

## Decay Classes

Override the base half-life per-node:

| Class | Multiplier | Use case |
|---|---|---|
| `volatile` | 0.5× | Temporary context, session-scoped info |
| `normal` | 1.0× | Default behavior |
| `persistent` | 2.0× | Important long-term knowledge |
| `permanent` | ∞ | Never decays (equivalent to pinning) |

## Tick Modes

Controls when decay calculations run:

| Mode | Behavior |
|---|---|
| `activity` | Tick every N operations (default: 10), max 1h idle gap |
| `fixed` | Tick at fixed intervals regardless of activity |
| `hybrid` | Activity-driven with fixed background ticks |

## Resonance

When a memory is recalled, heat spreads to related memories:

| Parameter | Default | Description |
|---|---|---|
| `spread_factor` | 0.3 | Fraction of heat that spreads to neighbors |
| `depth` | 2 | How many hops heat spreads |
| `damping` | 0.5 | Heat reduction per hop |
| `thermal_gate` | 0.1 | Min heat for a node to propagate further |

## Per-Node Overrides

Individual memories can have:
- `min_heat`: Floor value (memory never cools below this)
- `ttl_hours`: Hard expiry (memory deleted after this time)
- `valid_from` / `valid_until`: Temporal bounds (memory only active in time window)

## Configuring via API

```bash
# Get current thermo config
curl https://api.sulcus.ca/api/v1/settings/thermo \
  -H "Authorization: Bearer KEY"

# Update thermo config
curl -X PATCH https://api.sulcus.ca/api/v1/settings/thermo \
  -H "Authorization: Bearer KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "half_lives": {
      "episodic": 43200,
      "semantic": 2592000,
      "preference": 7776000
    },
    "resonance": {
      "spread_factor": 0.4,
      "depth": 3
    }
  }'
```

## Configuring via SDK

```python
from sulcus import Sulcus

client = Sulcus(api_key="sk-...")
config = client.get_thermo_config()
client.set_thermo_config({
    "half_lives": {"episodic": 43200},
    "resonance": {"spread_factor": 0.4}
})
```

```typescript
import { Sulcus } from "sulcus";

const client = new Sulcus({ apiKey: "sk-..." });
const config = await client.getThemoConfig();
await client.setThermoConfig({
  halfLives: { episodic: 43200 },
  resonance: { spreadFactor: 0.4 },
});
```

## Feedback Loop

Send explicit heat adjustments:

```bash
# Boost a memory
curl -X POST https://api.sulcus.ca/api/v1/feedback \
  -H "Authorization: Bearer KEY" \
  -H "Content-Type: application/json" \
  -d '{"node_id": "UUID", "signal": "boost", "amount": 0.2}'

# Deprecate a memory (accelerate decay)
curl -X POST https://api.sulcus.ca/api/v1/feedback \
  -H "Authorization: Bearer KEY" \
  -H "Content-Type: application/json" \
  -d '{"node_id": "UUID", "signal": "deprecate", "amount": 0.3}'
```
