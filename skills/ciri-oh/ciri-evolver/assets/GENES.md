# Genes Library

> Reusable strategy templates for skill self-evolution.
> Format: ## [GENE-YYYYMMDD-XXX] signal_pattern

## [GENE-20260416-001] TimeoutError

**Category**: repair
**Signals**: TimeoutError, GatewayTimeout

### Strategy
Handle timeout errors gracefully:

1. **Detect**: Catch timeout exceptions (ETIMEDOUT, ESOCKETTIMEDOUT)
2. **Retry**: Implement exponential backoff with jitter
   - Initial delay: 1000ms
   - Max delay: 30000ms
   - Max retries: 3
3. **Pool**: Use connection pooling with configurable limits
4. **Fallback**: If all retries fail, return cached response or graceful error

### Validation
- node test/timeout.test.js

---

## [GENE-20260416-002] RateLimitError

**Category**: repair
**Signals**: RateLimitError

### Strategy
Handle rate limiting:

1. **Detect**: Identify 429 responses with Retry-After header
2. **Queue**: Implement request queue with priority
3. **Cooldown**: Honor Retry-After delay
4. **Burst**: Use token bucket algorithm for controlled bursting

### Validation
- node test/ratelimit.test.js

---

## [GENE-20260416-003] ContextOverflow

**Category**: optimize
**Signals**: ContextOverflow

### Strategy
Reduce context memory pressure:

1. **Prune**: Enable stricter cache TTL (1h recommended)
2. **Archive**: Daily session archival to memory/
3. **Floor**: Set reserveTokensFloor to 100k
4. **Heartbeat**: Use lightContext mode for heartbeat

### Validation
- Check context usage stays below 80% of limit

---

## [GENE-20260416-005] AuthError

**Category**: repair
**Signals**: AuthError

### Strategy
Handle authentication errors:

1. **Verify**: Check API key validity and refresh tokens
2. **Refresh**: Implement automatic token refresh logic
3. **Cache**: Add token caching with TTL
4. **Retry**: Re-authenticate and retry failed requests

### Validation
- Verify API key is correctly configured
- Check token refresh logic works

---

## [GENE-20260416-004] ModelFallback

**Category**: repair
**Signals**: ModelFallback

### Strategy
Fix model routing issues:

1. **Verify**: Check API key validity and model availability
2. **Route**: Implement proper model selection logic
3. **Fallback**: Document expected fallback chain
4. **Monitor**: Log model selection decisions

### Validation
- Verify model list loads correctly
- Check fallback chain works as expected
