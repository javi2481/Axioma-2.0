"""
Rate limiter service for Axioma 2.0 public API.

Uses Valkey as primary counter store with automatic in-memory fallback
when Valkey is unavailable. Tier-based limits: free/pro/enterprise.

Counter key format: rate_limit:{sha256(api_key)}
"""
import hashlib
import time
from typing import Optional

from utils.logging_config import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    Per-API-key rate limiter backed by Redis with in-memory fallback.

    Usage:
        limiter = RateLimiter(valkey_url="redis://localhost:6379/0")
        allowed, remaining, reset_ts = await limiter.check_and_increment(
            api_key="orag_...", tier="free", window=60
        )
    """

    def __init__(self, valkey_url: str):
        self._redis_url = valkey_url
        self._redis = None
        # In-memory fallback: {key_hash: (count, window_start_ts)}
        self._memory_counters: dict = {}
        # Tier cache: {key_hash: (tier, cached_at_ts)}
        self._tier_cache: dict = {}

    # ─────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────

    async def _get_redis(self):
        """Lazy-initialize Redis client."""
        if self._redis is None:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(self._redis_url, decode_responses=True)
        return self._redis

    def _hash_key(self, api_key: str) -> str:
        """SHA-256 hash of the API key — same algorithm as APIKeyService."""
        return hashlib.sha256(api_key.encode()).hexdigest()

    def _check_memory(self, key_hash: str, limit: int, window: int) -> tuple[bool, int, int]:
        """
        In-memory counter fallback (single-process only).

        Resets the counter when the current window expires.
        Returns (allowed, remaining, reset_unix_ts).
        """
        now = time.time()
        entry = self._memory_counters.get(key_hash)

        if entry is None or (now - entry[1]) >= window:
            # New window
            self._memory_counters[key_hash] = (1, now)
            return True, limit - 1, int(now) + window

        count, start = entry
        count += 1
        self._memory_counters[key_hash] = (count, start)
        reset_ts = int(start) + window
        return count <= limit, max(0, limit - count), reset_ts

    # ─────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────

    async def get_tier(self, api_key: str, opensearch_client=None) -> str:
        """
        Resolve the rate-limit tier for an API key.

        Resolution order:
          1. In-memory cache (5-minute TTL)
          2. OpenSearch lookup (if client provided)
          3. Default: "free"
        """
        key_hash = self._hash_key(api_key)
        cached = self._tier_cache.get(key_hash)

        if cached and (time.time() - cached[1]) < 300:  # 5-min TTL
            return cached[0]

        tier = "free"
        if opensearch_client:
            tier = await self._fetch_tier_from_opensearch(key_hash, opensearch_client)

        self._tier_cache[key_hash] = (tier, time.time())
        return tier

    async def check_and_increment(
        self, api_key: str, tier: str, window: int
    ) -> tuple[bool, int, int]:
        """
        Atomically check and increment the request counter.

        Args:
            api_key: Full API key string (orag_...).
            tier: Rate limit tier ("free", "pro", "enterprise").
            window: Time window in seconds.

        Returns:
            (allowed, remaining, reset_unix_ts)
            - allowed: True if request is within the limit.
            - remaining: Requests left in current window (-1 = unlimited).
            - reset_unix_ts: Unix timestamp when the window resets (0 = unlimited).
        """
        from config.settings import RATE_LIMITS

        limit = RATE_LIMITS.get(tier)
        if limit is None:  # enterprise = unlimited
            return True, -1, 0

        key_hash = self._hash_key(api_key)
        redis_key = f"rate_limit:{key_hash}"

        try:
            r = await self._get_redis()
            current = await r.incr(redis_key)
            if current == 1:
                await r.expire(redis_key, window)
            ttl = await r.ttl(redis_key)
            reset_ts = int(time.time()) + max(ttl, 0)
            return current <= limit, max(0, limit - current), reset_ts

        except Exception as exc:
            logger.warning(
                "Valkey unavailable, falling back to in-memory rate limiting",
                error=str(exc),
            )
            return self._check_memory(key_hash, limit, window)

    # ─────────────────────────────────────────────
    # OpenSearch tier lookup
    # ─────────────────────────────────────────────

    async def _fetch_tier_from_opensearch(
        self, key_hash: str, opensearch_client
    ) -> str:
        """Query OpenSearch for the tier of an API key by its hash."""
        from config.settings import API_KEYS_INDEX_NAME
        try:
            result = await opensearch_client.search(
                index=API_KEYS_INDEX_NAME,
                body={
                    "query": {"term": {"key_hash": key_hash}},
                    "_source": ["tier"],
                    "size": 1,
                },
            )
            hits = result.get("hits", {}).get("hits", [])
            if hits:
                return hits[0]["_source"].get("tier", "free")
        except Exception as exc:
            logger.warning(
                "Could not fetch tier from OpenSearch, defaulting to free",
                error=str(exc),
            )
        return "free"
