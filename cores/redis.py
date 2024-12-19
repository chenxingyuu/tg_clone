from ghkit.database import redis_client

from cores.config import settings

REDIS = redis_client.RedisClient(
    host=settings.redis.host,
    port=settings.redis.port,
    password=settings.redis.password,
    db=settings.redis.default_db,
)

ASYNC_REDIS = redis_client.AsyncRedisClient(
    host=settings.redis.host,
    port=settings.redis.port,
    password=settings.redis.password,
    db=settings.redis.default_db,
)
