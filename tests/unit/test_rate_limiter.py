"""
Unit tests for RateLimiter service.

TDD: these tests were written BEFORE the implementation.
Each test describes the expected behavior of src/services/rate_limiter.py.
Backend: Valkey (BSD-3-Clause, drop-in replacement for Redis).
"""
import hashlib
import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _hash(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def _make_valkey_mock(incr_return: int, ttl_return: int = 55):
    """Return an AsyncMock that behaves like a Valkey client."""
    mock = AsyncMock()
    mock.incr.return_value = incr_return
    mock.expire.return_value = True
    mock.ttl.return_value = ttl_return
    return mock


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def rate_limiter():
    from services.rate_limiter import RateLimiter
    return RateLimiter(valkey_url="redis://localhost:6379/0")


# ─────────────────────────────────────────────────────────────
# Tests: check_and_increment
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_allows_request_within_free_limit(rate_limiter):
    """Request #50 with free tier (limit=100) should be allowed."""
    redis_mock = _make_valkey_mock(incr_return=50)
    rate_limiter._redis = redis_mock

    allowed, remaining, reset_ts = await rate_limiter.check_and_increment(
        api_key="orag_testkey123", tier="free", window=60
    )

    assert allowed is True
    assert remaining == 50  # 100 - 50
    assert reset_ts > 0


@pytest.mark.asyncio
async def test_blocks_request_over_free_limit(rate_limiter):
    """Request #101 with free tier (limit=100) should be blocked."""
    redis_mock = _make_valkey_mock(incr_return=101)
    rate_limiter._redis = redis_mock

    allowed, remaining, _ = await rate_limiter.check_and_increment(
        api_key="orag_testkey123", tier="free", window=60
    )

    assert allowed is False
    assert remaining == 0


@pytest.mark.asyncio
async def test_blocks_request_exactly_at_limit_plus_one(rate_limiter):
    """Request #101 is blocked; request #100 is the last allowed one."""
    redis_mock = _make_valkey_mock(incr_return=100)
    rate_limiter._redis = redis_mock

    allowed, remaining, _ = await rate_limiter.check_and_increment(
        api_key="orag_testkey123", tier="free", window=60
    )

    assert allowed is True
    assert remaining == 0


@pytest.mark.asyncio
async def test_pro_tier_allows_up_to_1000(rate_limiter):
    """Request #999 with pro tier (limit=1000) should be allowed."""
    redis_mock = _make_valkey_mock(incr_return=999)
    rate_limiter._redis = redis_mock

    allowed, remaining, _ = await rate_limiter.check_and_increment(
        api_key="orag_prokey456", tier="pro", window=60
    )

    assert allowed is True
    assert remaining == 1  # 1000 - 999


@pytest.mark.asyncio
async def test_enterprise_tier_is_always_unlimited(rate_limiter):
    """Enterprise tier is never rate limited, regardless of Valkey state."""
    # Valkey should NOT even be called for enterprise
    rate_limiter._redis = AsyncMock()

    allowed, remaining, reset_ts = await rate_limiter.check_and_increment(
        api_key="orag_entkey789", tier="enterprise", window=60
    )

    assert allowed is True
    assert remaining == -1   # sentinel: unlimited
    assert reset_ts == 0
    rate_limiter._redis.incr.assert_not_called()


@pytest.mark.asyncio
async def test_remaining_never_goes_below_zero(rate_limiter):
    """Remaining should be 0, never negative, even when far over limit."""
    redis_mock = _make_valkey_mock(incr_return=500)  # way over free limit of 100
    rate_limiter._redis = redis_mock

    _, remaining, _ = await rate_limiter.check_and_increment(
        api_key="orag_testkey123", tier="free", window=60
    )

    assert remaining == 0


@pytest.mark.asyncio
async def test_counter_key_uses_sha256_hash_not_raw_key(rate_limiter):
    """Valkey key must be rate_limit:{sha256(api_key)}, never the raw key."""
    api_key = "orag_secretkey999"
    redis_mock = _make_valkey_mock(incr_return=1)
    rate_limiter._redis = redis_mock

    await rate_limiter.check_and_increment(api_key=api_key, tier="free", window=60)

    expected_key = f"rate_limit:{_hash(api_key)}"
    redis_mock.incr.assert_called_once_with(expected_key)


@pytest.mark.asyncio
async def test_sets_ttl_on_first_request(rate_limiter):
    """On the first request (incr returns 1), TTL must be set on the Valkey key."""
    redis_mock = _make_valkey_mock(incr_return=1)
    rate_limiter._redis = redis_mock

    await rate_limiter.check_and_increment(
        api_key="orag_newkey", tier="free", window=60
    )

    redis_mock.expire.assert_called_once()
    _, call_args, _ = redis_mock.expire.mock_calls[0]
    assert call_args[1] == 60  # window=60


@pytest.mark.asyncio
async def test_does_not_reset_ttl_on_subsequent_requests(rate_limiter):
    """On request #2+ (incr > 1), expire must NOT be called again on Valkey."""
    redis_mock = _make_valkey_mock(incr_return=5)
    rate_limiter._redis = redis_mock

    await rate_limiter.check_and_increment(
        api_key="orag_existingkey", tier="free", window=60
    )

    redis_mock.expire.assert_not_called()


# ─────────────────────────────────────────────────────────────
# Tests: in-memory fallback when Valkey is unavailable
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_falls_back_to_memory_when_redis_raises(rate_limiter):
    """If Valkey raises an exception, fall back to in-memory counter."""
    redis_mock = AsyncMock()
    redis_mock.incr.side_effect = ConnectionError("Valkey unavailable")
    rate_limiter._redis = redis_mock

    allowed, remaining, reset_ts = await rate_limiter.check_and_increment(
        api_key="orag_testkey", tier="free", window=60
    )

    assert allowed is True   # first request always allowed in fallback
    assert remaining >= 0
    assert reset_ts > 0


@pytest.mark.asyncio
async def test_memory_fallback_tracks_count_across_calls(rate_limiter):
    """In-memory fallback must accumulate requests correctly."""
    redis_mock = AsyncMock()
    redis_mock.incr.side_effect = ConnectionError("Valkey unavailable")
    rate_limiter._redis = redis_mock

    api_key = "orag_fallbackkey"

    # Make 3 requests
    for _ in range(3):
        await rate_limiter.check_and_increment(api_key=api_key, tier="free", window=60)

    # 4th request should show remaining = 100 - 4 = 96
    allowed, remaining, _ = await rate_limiter.check_and_increment(
        api_key=api_key, tier="free", window=60
    )

    assert allowed is True
    assert remaining == 96  # 100 - 4


@pytest.mark.asyncio
async def test_memory_fallback_blocks_when_limit_exceeded(rate_limiter):
    """In-memory fallback must block when free limit (100) is exceeded."""
    redis_mock = AsyncMock()
    redis_mock.incr.side_effect = ConnectionError("Valkey unavailable")
    rate_limiter._redis = redis_mock

    api_key = "orag_heavyuser"
    # Burn through the 100-request free limit
    for _ in range(100):
        await rate_limiter.check_and_increment(api_key=api_key, tier="free", window=60)

    # Request #101 should be blocked
    allowed, remaining, _ = await rate_limiter.check_and_increment(
        api_key=api_key, tier="free", window=60
    )

    assert allowed is False
    assert remaining == 0


# ─────────────────────────────────────────────────────────────
# Tests: get_tier
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_tier_returns_cached_tier(rate_limiter):
    """get_tier() returns from memory cache without hitting OpenSearch."""
    api_key = "orag_cachedkey"
    key_hash = _hash(api_key)

    # Pre-populate cache (not expired)
    rate_limiter._tier_cache[key_hash] = ("pro", time.time())

    tier = await rate_limiter.get_tier(api_key, opensearch_client=None)

    assert tier == "pro"


@pytest.mark.asyncio
async def test_get_tier_defaults_to_free_when_no_opensearch(rate_limiter):
    """If no OpenSearch client and key not in cache, defaults to 'free'."""
    tier = await rate_limiter.get_tier("orag_unknownkey", opensearch_client=None)
    assert tier == "free"


@pytest.mark.asyncio
async def test_get_tier_ignores_expired_cache(rate_limiter):
    """Expired cache entry (>5 min) should be ignored and re-fetched."""
    api_key = "orag_expiredkey"
    key_hash = _hash(api_key)

    # Simulate expired cache entry (6 minutes ago)
    rate_limiter._tier_cache[key_hash] = ("pro", time.time() - 361)

    # No OpenSearch client → falls back to "free"
    tier = await rate_limiter.get_tier(api_key, opensearch_client=None)

    assert tier == "free"
    # Cache should be updated
    assert rate_limiter._tier_cache[key_hash][0] == "free"
