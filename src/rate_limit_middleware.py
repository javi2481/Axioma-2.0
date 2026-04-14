"""
Rate limiting middleware for Axioma 2.0 public API.

Intercepts all /v1/* requests, checks per-API-key counters in Redis,
and returns 429 when limits are exceeded. Injects X-RateLimit-* headers
into every passing response.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from utils.logging_config import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Starlette middleware that enforces per-API-key rate limits."""

    async def dispatch(self, request, call_next):
        from config.settings import RATE_LIMIT_ENABLED, RATE_LIMIT_WINDOW, RATE_LIMITS

        # Only apply to public v1 endpoints
        if not RATE_LIMIT_ENABLED or not request.url.path.startswith("/v1/"):
            return await call_next(request)

        # Extract API key from X-API-Key header or Authorization: Bearer orag_...
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]  # ["Bearer", "orag_..."][1]
                if token.startswith("orag_"):
                    api_key = token

        # No API key present — let the auth dependency handle the 401
        if not api_key:
            return await call_next(request)

        rate_limiter = request.app.state.rate_limiter

        # Resolve tier (memory cache → OpenSearch fallback)
        opensearch_client = None
        services = getattr(request.app.state, "services", {})
        if services:
            opensearch_client = services.get("clients") and getattr(
                services.get("clients"), "opensearch", None
            )

        tier = await rate_limiter.get_tier(api_key, opensearch_client=opensearch_client)
        allowed, remaining, reset_ts = await rate_limiter.check_and_increment(
            api_key, tier, RATE_LIMIT_WINDOW
        )

        if not allowed:
            logger.info(
                "Rate limit exceeded",
                tier=tier,
                window=RATE_LIMIT_WINDOW,
                path=request.url.path,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Retry after {RATE_LIMIT_WINDOW} seconds.",
                },
                headers={"Retry-After": str(RATE_LIMIT_WINDOW)},
            )

        response = await call_next(request)

        # Inject informational headers
        limit_val = RATE_LIMITS.get(tier)
        response.headers["X-RateLimit-Limit"] = str(limit_val) if limit_val is not None else "unlimited"
        response.headers["X-RateLimit-Remaining"] = str(remaining) if remaining != -1 else "unlimited"
        response.headers["X-RateLimit-Reset"] = str(reset_ts)

        return response
