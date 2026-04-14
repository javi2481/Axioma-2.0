# Rate Limiting Implementation Guide

> Technical guide to implement rate limiting for Axioma 2.0
> Based on Starlette/FastAPI with Redis backend
> Last updated: 2026-04-13

---

## Why Rate Limiting?

Rate limiting is the **final step** to protect your infrastructure and LLM costs before opening the API to customers.

**Benefits:**
- Cost control: Prevent runaway API bills
- Infrastructure protection: Avoid OpenSearch overload
- Per-client limits: Different tiers (Free/Pro/Enterprise)

---

## Architecture Overview

```
Request → Rate Limit Middleware → Redis (check counter)
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
              Within Limit                     Exceeds Limit
                    │                               │
                    ▼                               ▼
              Proceed to API                   429 Response
```

---

## Step 1: Add Redis to Docker Compose

Edit `docker-compose.yml`:

```yaml
redis:
  image: redis:alpine
  container_name: axioma_redis
  ports:
    - "6379:6379"
  restart: always
```

Also add to `.env`:
```bash
REDIS_URL=redis://redis:6379/0
```

---

## Step 2: Create Rate Limit Middleware

Create `src/rate_limit_middleware.py`:

```python
import redis.asyncio as redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import Request
import os

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
RATE_LIMIT_REQUESTS = 50  # Requests limit
RATE_LIMIT_WINDOW = 60    # Window in seconds

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.redis = redis.from_url(REDIS_URL, decode_responses=True)

    async def dispatch(self, request: Request, call_next):
        # 1. Check if endpoint requires rate limiting
        if not request.url.path.startswith("/v1/"):
            return await call_next(request)

        # 2. Extract API Key from header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return await call_next(request)
            
        api_key = auth_header.split(" ")[1]
        
        # 3. Rate limiting logic in Redis
        redis_key = f"rate_limit:{api_key}"
        
        # Increment counter
        current_requests = await self.redis.incr(redis_key)
        
        # Set TTL on first request
        if current_requests == 1:
            await self.redis.expire(redis_key, RATE_LIMIT_WINDOW)
            
        # 4. Block if exceeds limit
        if current_requests > RATE_LIMIT_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded", 
                    "message": f"Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds"
                },
                headers={"Retry-After": str(RATE_LIMIT_WINDOW)}
            )
            
        # Continue if OK
        response = await call_next(request)
        
        # Inject informative headers
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(max(0, RATE_LIMIT_REQUESTS - current_requests))
        
        return response
```

---

## Step 3: Connect to Main Application

Edit `src/main.py`:

```python
from rate_limit_middleware import RateLimitMiddleware

async def create_app():
    app = FastAPI(...)
    
    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)
    
    # ... rest of configuration ...
    
    return app
```

---

## Implementation According to SDD Design

This implementation follows the design in `docs/specs/api-rate-limiting-design.md`:

| Design Decision | Implementation |
|-----------------|----------------|
| Dependency vs Middleware | ✅ Middleware (as per design) |
| Redis + fallback | ✅ Redis primary |
| Tier support | TODO: Add tier logic (free: 100, pro: 1000, enterprise: ∞) |
| Headers | ✅ X-RateLimit-Limit, X-RateLimit-Remaining |

---

## Tier Configuration (Advanced)

For tiered rate limiting:

```python
TIER_LIMITS = {
    "free": 100,      # 100 requests/minute
    "pro": 1000,      # 1000 requests/minute
    "enterprise": None  # unlimited
}

async def get_tier_limit(api_key: str) -> int:
    tier = await get_tier_from_api_key(api_key)
    return TIER_LIMITS.get(tier, TIER_LIMITS["free"])
```

---

## Why This Design is Ideal

| Benefit | How It's Achieved |
|---------|-------------------|
| **Exact Cost Protection** | `rate_limit:{api_key}` = per-client, not per-IP |
| **Zero Latency** | Redis `incr()` is atomic, sub-millisecond |
| **Scalability** | Centralized Redis works across multiple backend containers |
| **Production Ready** | Standard industry approach |

---

## Files to Modify/Create

| File | Action |
|------|--------|
| `docker-compose.yml` | Add Redis service |
| `.env` | Add REDIS_URL |
| `src/rate_limit_middleware.py` | **CREATE** |
| `src/main.py` | Add middleware |

---

## Status

- [ ] Add Redis to docker-compose.yml
- [ ] Add REDIS_URL to .env
- [ ] Create src/rate_limit_middleware.py
- [ ] Connect middleware in src/main.py
- [ ] Add tier support (optional, for Free/Pro/Enterprise)
- [ ] Test locally
- [ ] Deploy

---

*Guide based on Starlette/FastAPI architecture*
*Part of Axioma 2.0 SDD implementation*
