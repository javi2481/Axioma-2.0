# Design: Rate Limiting for API

> **Nota de migración (2026-04-15):** El backend fue migrado de Redis (SSPL) a **Valkey 9.x** (BSD-3-Clause, Linux Foundation). El diseño y las decisiones arquitectónicas documentadas aquí permanecen válidos — Valkey es protocolo-compatible con Redis. Ver `docker-compose.yml` y `src/services/rate_limiter.py` para el estado actual.

## Technical Approach

Implement rate limiting as a FastAPI dependency that runs BEFORE the `get_api_key_user_async` dependency. This ensures rate limits are checked before authentication. The approach uses a middleware pattern with Redis as primary storage and in-memory fallback.

## Architecture Decisions

### Decision: Dependency vs Middleware

**Choice**: FastAPI dependency (before hook)  
**Alternatives considered**: 
- ASGI middleware (runs after, harder to get API key)
- Flask-style before_request decorator (not FastAPI native)

**Rationale**: Dependencies run in order and can access request object. We can extract API key from header and check limits before authentication runs. Simpler to test and debug than global middleware.

### Decision: Redis vs In-Memory

**Choice**: Redis primary, in-memory fallback  
**Alternatives considered**:
- In-memory only (not production-ready)
- OpenSearch as storage (too slow)
- Local file (race conditions)

**Rationale**: Redis is already available in the infrastructure, fast atomic operations. Fallback ensures local dev works without Redis. Production needs distributed rate limiting.

### Decision: Key Format for Redis

**Choice**: `ratelimit:{key_hash}:{window}`  
**Alternatives considered**:
- `ratelimit:{key_id}:{window}` (exposes key_id)
- `ratelimit:{user_id}:{window}` (doesn't work for anonymous API keys)

**Rationale**: Uses hashed API key to avoid storing raw keys. Window is minute granularity (1min sliding window).

### Decision: Limit Storage Location

**Choice**: Store in API key document in OpenSearch  
**Alternatives considered**:
- Redis only (lose tier on restart)
- Separate index (extra complexity)

**Rationale**: Tier is metadata that should persist. Redis counters are ephemeral. On startup, load tier from OpenSearch.

## Data Flow

```
Request arrives
     │
     ▼
Extract API key from header
     │
     ▼
Hash key → look up tier in Redis (cache) or OpenSearch
     │
     ▼
Get current count from Redis counter
     │
     ▼
count < limit? ──NO──→ 429 Too Many Requests
│                     
YES
     │
     ▼
Increment counter
     │
     ▼
Proceed to get_api_key_user_async
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/services/rate_limiter.py` | Create | RateLimiter service class |
| `src/dependencies.py` | Modify | Add `get_rate_limiter` dependency |
| `src/api/v1/search.py` | Modify | Add `Depends(get_rate_limiter)` |
| `src/api/v1/chat.py` | Modify | Add `Depends(get_rate_limiter)` |
| `src/api/v1/documents.py` | Modify | Add `Depends(get_rate_limiter)` |
| `src/api/v1/models.py` | Modify | Add `Depends(get_rate_limiter)` |
| `config/settings.py` | Modify | Add rate limit config |

## Interfaces / Contracts

```python
# src/services/rate_limiter.py

class RateLimiter:
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.fallback_counts = {}  # in-memory fallback
    
    async def check_limit(self, api_key: str, tier: str) -> tuple[bool, dict]:
        """
        Returns (allowed, rate_limit_info)
        rate_limit_info: {
            "limit": int,
            "remaining": int,
            "reset": int
        }
        """
        pass
    
    async def increment(self, api_key: str, tier: str) -> None:
        pass
    
    async def get_tier(self, api_key_hash: str) -> str:
        """Get tier from cache or OpenSearch"""
        pass
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | RateLimiter.check_limit() logic | Mock Redis, test edge cases |
| Unit | Tier calculation | Test free/pro/enterprise limits |
| Integration | Full flow with valid key | pytest with test Redis |
| Integration | 429 response when exceeded | pytest, exceed limit |
| Integration | Redis fallback | Mock Redis unavailable |

## Migration / Rollback

No migration required. This is a new capability.

Rollback:
1. Remove `Depends(get_rate_limiter)` from all v1 endpoints
2. Restart service
3. Existing API keys work without limits

## Open Questions

- [ ] Should we add rate limit to non-v1 endpoints (e.g., /auth)?
- [ ] How to handle burst traffic? Consider burst allowance
- [ ] Need to verify Redis is already in docker-compose

## Configuration

```python
# config/settings.py additions
RATE_LIMITS = {
    "free": 100,      # requests per minute
    "pro": 1000,
    "enterprise": None  # unlimited
}
REDIS_RATE_LIMIT_KEY = "ratelimit"
RATE_LIMIT_WINDOW = 60  # seconds
```
