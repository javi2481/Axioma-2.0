import pytest
from unittest.mock import MagicMock, patch

from services.semantic_cache import SemanticCache


@pytest.fixture
def cache():
    return SemanticCache("redis://localhost:6379/0", threshold=0.95, ttl=3600)


# --- cache hit ---
@pytest.mark.asyncio
async def test_get_returns_cached_response(cache):
    mock_entry = MagicMock()
    mock_entry.text = "respuesta cacheada"
    mock_redis_cache = MagicMock()
    mock_redis_cache.lookup.return_value = [mock_entry]
    cache._cache = mock_redis_cache

    result = await cache.get("¿cómo configuro el embedding?")

    assert result == "respuesta cacheada"
    mock_redis_cache.lookup.assert_called_once_with(
        "¿cómo configuro el embedding?", llm_string="axioma-langflow"
    )


# --- cache miss ---
@pytest.mark.asyncio
async def test_get_returns_none_on_miss(cache):
    mock_redis_cache = MagicMock()
    mock_redis_cache.lookup.return_value = []
    cache._cache = mock_redis_cache

    result = await cache.get("pregunta sin cache")

    assert result is None


# --- fallback: Redis no disponible en init ---
@pytest.mark.asyncio
async def test_get_returns_none_when_init_fails(cache):
    cache._init_failed = True
    result = await cache.get("cualquier pregunta")
    assert result is None


# --- fallback: lookup lanza excepción ---
@pytest.mark.asyncio
async def test_get_returns_none_on_lookup_exception(cache):
    mock_redis_cache = MagicMock()
    mock_redis_cache.lookup.side_effect = Exception("Redis connection error")
    cache._cache = mock_redis_cache

    result = await cache.get("pregunta")

    assert result is None  # no debe propagar la excepción


# --- set guarda correctamente ---
@pytest.mark.asyncio
async def test_set_calls_update(cache):
    mock_redis_cache = MagicMock()
    cache._cache = mock_redis_cache

    await cache.set("¿qué es RAG?", "RAG es Retrieval-Augmented Generation")

    mock_redis_cache.update.assert_called_once()
    call_args = mock_redis_cache.update.call_args
    assert call_args[0][0] == "¿qué es RAG?"
    assert call_args[0][1] == "axioma-langflow"


# --- set silencioso si cache no inicializado ---
@pytest.mark.asyncio
async def test_set_is_noop_when_init_failed(cache):
    cache._init_failed = True
    # No debe lanzar excepción
    await cache.set("pregunta", "respuesta")


# --- lazy init llama a RedisSemanticCache ---
@pytest.mark.asyncio
async def test_init_creates_redis_cache(cache):
    # Los imports son lazy (dentro del método) → parchear el paquete real
    with patch("langchain_redis.RedisSemanticCache") as mock_cls, \
         patch("langchain_openai.OpenAIEmbeddings"):
        mock_cls.return_value = MagicMock()
        await cache._get_cache()
        mock_cls.assert_called_once()


# --- segunda llamada no reinicializa ---
@pytest.mark.asyncio
async def test_get_cache_reuses_instance(cache):
    mock_instance = MagicMock()
    cache._cache = mock_instance

    result1 = await cache._get_cache()
    result2 = await cache._get_cache()

    assert result1 is result2 is mock_instance


# --- set silencioso si update lanza excepción ---
@pytest.mark.asyncio
async def test_set_handles_update_exception(cache):
    mock_redis_cache = MagicMock()
    mock_redis_cache.update.side_effect = Exception("write error")
    cache._cache = mock_redis_cache

    # No debe propagar la excepción
    await cache.set("pregunta", "respuesta")


# --- init failure marca _init_failed y no reintenta ---
@pytest.mark.asyncio
async def test_init_failure_sets_flag_and_does_not_retry(cache):
    with patch("langchain_redis.RedisSemanticCache") as mock_cls, \
         patch("langchain_openai.OpenAIEmbeddings"):
        mock_cls.side_effect = Exception("no redis")
        await cache._get_cache()  # falla, marca _init_failed = True
        assert cache._init_failed is True

        # Segunda llamada no debe tocar RedisSemanticCache
        mock_cls.reset_mock()
        await cache._get_cache()
        mock_cls.assert_not_called()
