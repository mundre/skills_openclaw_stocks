# Sulcus REST API Reference

Base URL: `https://api.sulcus.ca`

All endpoints require `Authorization: Bearer YOUR_API_KEY` header.

## Memory Operations

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/agent/nodes` | List all memories (paginated) |
| `GET` | `/api/v1/agent/nodes/:id` | Get single memory by UUID |
| `POST` | `/api/v1/agent/nodes` | Create a new memory |
| `PATCH` | `/api/v1/agent/nodes/:id` | Update memory (content, type, labels) |
| `DELETE` | `/api/v1/agent/nodes/:id` | Delete a memory |
| `POST` | `/api/v1/agent/nodes/bulk-delete` | Delete multiple memories |
| `POST` | `/api/v1/agent/search` | Semantic search (`{"query": "...", "limit": N}`) |

### Create Memory

```bash
curl -X POST https://api.sulcus.ca/api/v1/agent/nodes \
  -H "Authorization: Bearer KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "pointer_summary": "User prefers dark mode",
    "memory_type": "preference",
    "namespace": "default"
  }'
```

### Search Memories

```bash
curl -X POST https://api.sulcus.ca/api/v1/agent/search \
  -H "Authorization: Bearer KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "dark mode preferences", "limit": 5}'
```

### Update Memory

```bash
curl -X PATCH https://api.sulcus.ca/api/v1/agent/nodes/UUID \
  -H "Authorization: Bearer KEY" \
  -H "Content-Type: application/json" \
  -d '{"pointer_summary": "Updated content", "memory_type": "fact"}'
```

## Triggers

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/triggers` | List all triggers |
| `POST` | `/api/v1/triggers` | Create trigger |
| `PATCH` | `/api/v1/triggers/:id` | Update trigger |
| `DELETE` | `/api/v1/triggers/:id` | Delete trigger |
| `GET` | `/api/v1/triggers/:id/history` | Get trigger fire history |

## Thermodynamics

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/settings/thermo` | Get thermo config |
| `PATCH` | `/api/v1/settings/thermo` | Update thermo config |
| `POST` | `/api/v1/feedback` | Send heat feedback (boost/deprecate) |

## Analytics

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/agent/stats` | Memory statistics |
| `GET` | `/api/v1/agent/recall-analytics` | Recall frequency analytics |

## Billing & Account

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/billing/status` | Current plan and usage |
| `POST` | `/api/v1/billing/checkout` | Create Stripe checkout |
| `GET` | `/api/v1/org/members` | List org members |
| `POST` | `/api/v1/org/invite` | Invite member |

## Waitlist

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/waitlist` | Join waitlist (public, no auth) |
| `GET` | `/api/v1/admin/waitlist` | List waitlist entries (admin) |

## Auth

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/auth/me` | Current user info |
| `POST` | `/api/v1/auth/api-keys` | Generate API key |
| `GET` | `/api/v1/auth/api-keys` | List API keys |
| `DELETE` | `/api/v1/auth/api-keys/:id` | Revoke API key |

## Query Parameters (GET /api/v1/agent/nodes)

| Param | Type | Description |
|---|---|---|
| `page` | number | Page number (default: 1) |
| `page_size` | number | Items per page (default: 50) |
| `memory_type` | string | Filter by type |
| `namespace` | string | Filter by namespace |
| `min_heat` | float | Min heat threshold |
| `sort_by` | string | `heat`, `created_at`, `updated_at` |
| `sort_order` | string | `asc` or `desc` |
