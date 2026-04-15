# Tasks: Rate Limiting for API

> **Nota de migración (2026-04-15):** Implementación completada con **Valkey 9.x** (BSD-3-Clause) en lugar de Redis (SSPL). Las tasks están cerradas. El historial refleja las decisiones originales de diseño.

## Phase 1: Foundation / Configuration

- [ ] 1.1 Add RATE_LIMITS config to `config/settings.py` (free: 100, pro: 1000, enterprise: None)
- [ ] 1.2 Add REDIS_RATE_LIMIT_KEY and RATE_LIMIT_WINDOW to settings
- [ ] 1.3 Add Redis client initialization in `src/main.py` for rate limiting

## Phase 2: Core Implementation

- [ ] 2.1 Create `src/services/rate_limiter.py` with RateLimiter class
- [ ] 2.2 Implement `check_limit()` method with Redis + fallback
- [ ] 2.3 Implement `increment()` method for counter
- [ ] 2.4 Implement `get_tier()` to load tier from OpenSearch or cache

## Phase 3: Integration

- [ ] 3.1 Add `get_rate_limiter` dependency in `src/dependencies.py`
- [ ] 3.2 Add rate limiting to `/api/v1/search` endpoint
- [ ] 3.3 Add rate limiting to `/api/v1/chat` endpoint
- [ ] 3.4 Add rate limiting to `/api/v1/documents` endpoint
- [ ] 3.5 Add rate limiting to `/api/v1/models` endpoint
- [ ] 3.6 Add rate limiting to `/api/v1/knowledge_filters` endpoint

## Phase 4: Testing

- [ ] 4.1 Write unit test: RateLimiter.check_limit() returns correct limits for each tier
- [ ] 4.2 Write unit test: RateLimiter falls back to in-memory when Redis unavailable
- [ ] 4.3 Write integration test: 429 returned when limit exceeded
- [ ] 4.4 Write integration test: X-RateLimit-* headers present in response
- [ ] 4.5 Verify all spec scenarios pass

## Phase 5: Cleanup

- [ ] 5.1 Add docstrings to RateLimiter class and methods
- [ ] 5.2 Verify no debug logs in production code
- [ ] 5.3 Update swagger docs with rate limit info
