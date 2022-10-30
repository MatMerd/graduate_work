from aioredis import Redis

from core.exceptions import RedisClientNotExist

_redis_client: Redis


def get_redis_client() -> Redis:
    if not _redis_client:
        raise RedisClientNotExist("Redis client not create when service initialize.")
    return _redis_client
