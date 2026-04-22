from .config import settings
from fastapi_cache import FastAPICache
import logging

logger = logging.getLogger(__name__)

_redis_client = None  # sync redis.Redis, set by init_cache when redis_cache_url is configured


async def init_cache():
    global _redis_client
    if settings.redis_cache_url is not None:
        import redis as sync_redis
        from redis import asyncio as aioredis
        from fastapi_cache.backends.redis import RedisBackend
        async_redis = aioredis.from_url(settings.redis_cache_url)
        FastAPICache.init(RedisBackend(async_redis), prefix=settings.cache_prefix)
        _redis_client = sync_redis.from_url(settings.redis_cache_url)
        logger.info("Initialized Redis cache with URL: %s", settings.redis_cache_url)
    else:
        from fastapi_cache.backends.inmemory import InMemoryBackend
        FastAPICache.init(InMemoryBackend(), prefix=settings.cache_prefix)
        logger.info("Initialized in-memory cache")


def get_redis_client():
    """Return sync Redis client if configured, else None."""
    return _redis_client


async def clear_cache():
    await FastAPICache.clear()
    logger.info("Cache cleared")