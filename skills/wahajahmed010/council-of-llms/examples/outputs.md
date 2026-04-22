# Council of LLMs — Example Outputs

## Example 1: Security Review

**Input:**
```python
def authenticate(token):
    user = db.query(f"SELECT * FROM users WHERE token = '{token}'")
    return user
```

**Council Output:**

### Participants
- Security Auditor (openai/gpt-4o)
- Pragmatic Developer (anthropic/claude-3-opus)

### Individual Positions

#### Security Auditor
**Position:** CRITICAL — SQL injection vulnerability
**Key Points:**
1. Direct string interpolation in SQL query
2. Token is user-controlled input
3. Classic injection vector — attacker can extract all data
4. Must use parameterized queries

#### Pragmatic Developer
**Position:** Agrees on severity, notes implementation ease
**Key Points:**
1. Confirms SQL injection risk
2. Fix is simple: use ORM or parameterized queries
3. No valid use case for this pattern
4. Should block CI/CD until fixed

### Agreement Matrix

| Point | Security | Developer |
|-------|----------|-----------|
| SQLi exists | ✅ | ✅ |
| Severity: Critical | ✅ | ✅ |
| Fix difficulty | Low | Low |
| Blocks deployment | ✅ | ✅ |

### Synthesis

**Unanimous consensus:** Critical SQL injection. Must fix before deployment.

**Fix:**
```python
def authenticate(token):
    user = db.query("SELECT * FROM users WHERE token = ?", (token,))
    return user
```

---

## Example 2: Architecture Decision

**Question:** Should we migrate from REST to GraphQL?

**Council Output:**

### Participants
- API Strategist (ollama/kimi-k2.5)
- Performance Engineer (openai/gpt-4o)
- Frontend Lead (anthropic/claude-3-opus)

### Individual Positions

#### API Strategist
**Position:** GraphQL for new services, REST for existing
**Key Points:**
1. GraphQL solves over-fetching
2. Migration cost is high
3. Strangler fig pattern works
4. Don't rewrite working code

#### Performance Engineer
**Position:** REST with optimized endpoints
**Key Points:**
1. GraphQL complexity adds latency
2. Caching is harder
3. REST can be optimized per use case
4. Performance wins are marginal

#### Frontend Lead
**Position:** GraphQL if mobile is priority
**Key Points:**
1. Mobile teams love GraphQL
2. Reduces round trips significantly
3. Type safety is big win
4. But requires team learning curve

### Agreement Matrix

| Point | Strategist | Performance | Frontend |
|-------|------------|-------------|----------|
| GraphQL benefits | ✅ | ⚠️ | ✅ |
| Migration cost | High | Medium | Medium |
| Performance | ⚠️ | ✅ REST | ⚠️ |
| Mobile priority | ⚠️ | ⚠️ | ✅ |

### Key Disagreements

1. **Migration approach**: Strategist says gradual, others say evaluate need first
2. **Performance**: Engineer sees GraphQL complexity; others see query optimization

### Synthesis

**Split consensus:** 
- ✅ GraphQL for new mobile-heavy services
- ✅ REST for existing backend services
- ⚠️ No full migration without clear mobile use case

**Recommendation:** Start with GraphQL for mobile API only. Measure before expanding.

---

## Example 3: Simple Question (Overkill Warning)

**Question:** What time is it in Tokyo?

**Council Output:**

```
⚠️ COUNCIL NOT RECOMMENDED

This is a factual lookup with clear correct answer.
Single model response would be faster and equally accurate.

Use: openclaw ask "What time is it in Tokyo?"
Instead of council for this query.
```

---

## When to Use Council

| Scenario | Single Model | Council |
|----------|--------------|---------|
| Factual lookup | ✅ | ❌ Overkill |
| Security audit | ⚠️ | ✅ Justified |
| Architecture decision | ⚠️ | ✅ Justified |
| Creative writing | ✅ | ❌ Unnecessary |
| Policy analysis | ❌ Biased | ✅ Justified |
