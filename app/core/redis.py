from app.core.config import settings

class NoopAsyncRedis:
    async def get(self, key):
        return None

    async def setex(self, key, time, value):
        return True

    async def delete(self, *keys):
        return 0

    async def scan_iter(self, match=None):
        if False:
            yield None

    async def ping(self):
        return True

try:
    import redis.asyncio as aioredis
    from redis.exceptions import RedisError

    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
except ModuleNotFoundError:
    redis_client = NoopAsyncRedis()
    RedisError = Exception

async def get_redis():
    """Dependency provider for FastAPI endpoint controllers."""
    yield redis_client
