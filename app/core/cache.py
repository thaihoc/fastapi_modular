from .config import settings
from fastapi_cache import FastAPICache
import logging

logger = logging.getLogger(__name__)

async def init_cache():
    if settings.redis_cache_url is not None:
        from redis import asyncio as aioredis
        from fastapi_cache.backends.redis import RedisBackend
        redis = aioredis.from_url(settings.redis_cache_url)
        FastAPICache.init(RedisBackend(redis), prefix=settings.cache_prefix)
        logger.info("Initialized Redis cache with URL: %s", settings.redis_cache_url)
    else:
        from fastapi_cache.backends.inmemory import InMemoryBackend
        FastAPICache.init(InMemoryBackend(), prefix=settings.cache_prefix)
        logger.info("Initialized in-memory cache")

async def clear_cache():
    await FastAPICache.clear()
    logger.info("Cache cleared")