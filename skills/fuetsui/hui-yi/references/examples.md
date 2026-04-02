# Cold Memory Examples

Read this file when you need a concrete reference for creating notes, index entries, or tags.json entries.

## Example 1 — Experience note (full triple)

### The note (`memory/cold/postgres-migration.md`)

```markdown
# Migrating Postgres with zero downtime

## TL;DR
- Use logical replication, not pg_dump, for zero-downtime migration.
- Cutover window is ~2 minutes if sequences are pre-synced.

## Memory type
- experience

## Semantic context
If someone is planning a production database migration and needs to minimize downtime,
this note explains why logical replication beats pg_dump and covers the key steps for a
smooth cutover.

## Triggers
- postgres migration
- zero downtime database move
- logical replication cutover

## Use this when
- Planning a production database migration
- Evaluating pg_dump vs logical replication tradeoffs

## Decisions / lessons
- DO: pre-sync sequences 1 hour before cutover
- DO: run a dry-run cutover on staging first
- AVOID: relying on pg_dump for databases > 50GB in production

## Confidence
- high

## Last verified
- 2025-03-15

## Related tags
- postgres
- migration
- devops
```

### The index entry (`memory/cold/index.md`)

```markdown
- `postgres-migration.md` — Zero-downtime Postgres migration via logical replication
  - type: experience
  - tags: postgres, migration, devops
  - triggers: postgres migration, zero downtime database move, logical replication cutover
  - read when: planning production DB migration; evaluating pg_dump vs logical replication
  - confidence: high
  - updated: 2025-03-15
```

### The tags.json entry

```json
{
  "title": "Migrating Postgres with zero downtime",
  "path": "memory/cold/postgres-migration.md",
  "type": "experience",
  "summary": "Use logical replication for zero-downtime Postgres migration; pre-sync sequences before cutover.",
  "semantic_context": "If someone is planning a production database migration and needs to minimize downtime, this note explains why logical replication beats pg_dump and covers the key steps for a smooth cutover.",
  "tags": ["postgres", "migration", "devops"],
  "triggers": ["postgres migration", "zero downtime database move", "logical replication cutover"],
  "scenarios": ["planning production DB migration", "evaluating pg_dump vs logical replication"],
  "confidence": "high",
  "last_verified": "2025-03-15",
  "updated": "2025-03-15"
}
```

## Example 2 — Fact note (full triple)

### The note (`memory/cold/api-rate-limits.md`)

```markdown
# Internal API rate limits

## TL;DR
- Standing rate limits for payment and user service APIs.
- Check this before designing batch jobs or load tests.

## Memory type
- fact

## Semantic context
If someone is designing a batch job, load test, or integration that hits internal APIs,
this note has the standing rate limits to prevent 429 errors.

## Triggers
- rate limit
- API throttle
- 429 error

## Use this when
- Designing a batch job that calls internal APIs
- Debugging 429 errors in production

## Key facts
- Payment API: 500 req/s per client, burst to 800
- User service: 2000 req/s, no burst allowance
- Auth service: 100 req/s, strict

## Confidence
- medium

## Last verified
- 2025-02-20

## Related tags
- api
- rate-limit
- infrastructure
```

### The index entry

```markdown
- `api-rate-limits.md` — Standing rate limit values for internal APIs
  - type: fact
  - tags: api, rate-limit, infrastructure
  - triggers: rate limit, API throttle, 429 error
  - read when: designing batch jobs against internal APIs; debugging 429 errors
  - confidence: medium
  - updated: 2025-02-20
```

### The tags.json entry

```json
{
  "title": "Internal API rate limits",
  "path": "memory/cold/api-rate-limits.md",
  "type": "fact",
  "summary": "Standing rate limits for payment and user service APIs.",
  "semantic_context": "If someone is designing a batch job, load test, or integration that hits internal APIs, this note has the standing rate limits to prevent 429 errors.",
  "tags": ["api", "rate-limit", "infrastructure"],
  "triggers": ["rate limit", "API throttle", "429 error"],
  "scenarios": ["designing batch jobs against internal APIs", "debugging 429 errors"],
  "confidence": "medium",
  "last_verified": "2025-02-20",
  "updated": "2025-02-20"
}
```

## Example 3 — Background note (skeleton)

```markdown
# Project Atlas — architecture history

## TL;DR
- Atlas started as a monolith (2022), split into 4 services (2023), consolidated auth into a shared gateway (2024).
- Current pain point: service-to-service latency after the split.

## Memory type
- background

## Semantic context
If someone is making architecture decisions for Project Atlas, onboarding a new team
member, or evaluating whether to merge services, this note provides the full history
of how the system evolved and the rationale behind each major decision.

## Triggers
- atlas architecture
- project atlas history
- service split decision

## Use this when
- Making new architecture decisions for Atlas
- Onboarding someone to Atlas context
- Evaluating whether to merge services back

## Key facts
- 4 services: user, billing, content, auth-gateway
- Auth gateway handles all cross-service tokens since 2024-Q2
- Latency budget: 200ms p99 end-to-end

## Decisions / lessons
- DO: check latency dashboard before proposing new service boundaries
- AVOID: adding a 5th service without first reducing current inter-service calls

## Confidence
- high

## Last verified
- 2025-04-01

## Related tags
- atlas
- architecture
- microservices

## Details
[Extended project history, migration timeline, and stakeholder context would go here.]
```

## Key differences by type

| Aspect | fact | experience | background |
|---|---|---|---|
| Typical length | 10–20 lines | 20–35 lines | 30–60+ lines |
| Key facts section | primary content | optional | usually present |
| Decisions / lessons | rarely needed | primary content | often present |
| Details section | omit | optional | expected |
| Update frequency | low (stable data) | low (lessons don't change) | medium (context evolves) |