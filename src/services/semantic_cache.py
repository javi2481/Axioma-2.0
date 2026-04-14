"""
Semantic cache for LLM responses using Redis vector search (RediSearch).

Uses OpenAI embeddings to find semantically similar previous queries and
return cached responses, avoiding redundant LLM calls for identical or
near-identical prompts.

Falls back silently to passthrough if Redis/RediSearch is unavailable.
"""

import hashlib

from utils.logging_config import get_logger

logger = get_logger(__name__)


class SemanticCache:
    """
    Wrapper around LangChain RedisSemanticCache with graceful fallback.

    If Redis is unavailable or the RediSearch module is missing, all
    operations return None / no-op so the chat flow is never interrupted.
    """

    def __init__(self, redis_url: str, threshold: float = 0.95, ttl: int = 3600):
        self._redis_url = redis_url
        self._threshold = threshold
        self._ttl = ttl
        self._cache = None
        self._init_failed = False

    async def _get_cache(self):
        if self._init_failed:
            return None
        if self._cache is None:
            try:
                from langchain_openai import OpenAIEmbeddings
                from langchain_redis import RedisSemanticCache

                embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
                self._cache = RedisSemanticCache(
                    redis_url=self._redis_url,
                    embeddings=embeddings,
                    score_threshold=self._threshold,
                    ttl=self._ttl,
                )
                logger.info(
                    "SemanticCache initialized",
                    threshold=self._threshold,
                    ttl=self._ttl,
                )
            except Exception as exc:
                logger.warning(
                    "SemanticCache init failed — running in passthrough mode",
                    error=str(exc),
                )
                self._init_failed = True
        return self._cache

    async def get(self, prompt: str) -> str | None:
        """Return a cached response for the prompt, or None if not found."""
        cache = await self._get_cache()
        if cache is None:
            return None
        try:
            result = cache.lookup(prompt, llm_string="axioma-langflow")
            if result:
                prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
                logger.info("SemanticCache hit", prompt_hash=prompt_hash)
                entry = result[0]
                return entry.text if hasattr(entry, "text") else str(entry)
        except Exception as exc:
            logger.warning("SemanticCache lookup failed", error=str(exc))
        return None

    async def set(self, prompt: str, response: str) -> None:
        """Store a prompt→response pair in the cache."""
        cache = await self._get_cache()
        if cache is None:
            return
        try:
            from langchain_core.outputs import Generation

            cache.update(prompt, "axioma-langflow", [Generation(text=response)])
        except Exception as exc:
            logger.warning("SemanticCache set failed", error=str(exc))
