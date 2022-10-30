from ast import List
import aiohttp
from aioredis import ConnectionPool, Redis
import pytest
from typing import Dict, Optional

from settings import test_settings
from utils.schemas import HttpResponse, RedisDataSchema


@pytest.fixture(scope="module")
async def session():
    _connector = aiohttp.TCPConnector(limit=30)
    session = aiohttp.ClientSession(
        connector=_connector, base_url=test_settings.service_url
    )
    yield session
    await session.close()


@pytest.fixture(scope="module")
def make_get_request(session: aiohttp.ClientSession):
    async def inner(path: str, query_data: Optional[Dict] = None):
        query_data = query_data or {}
        async with session.get(path, params=query_data) as response:
            return HttpResponse(
                status=response.status,
                body=await response.json(),
                headers=response.headers,
            )

    return inner


@pytest.fixture(scope="module")
def make_post_request(session: aiohttp.ClientSession):
    async def inner(path: str, body_data: Dict):
        body_data = body_data or {}
        async with session.post(path, data=body_data) as response:
            return HttpResponse(
                status=response.status,
                body=await response.json(),
                headers=response.headers,
            )

    return inner


@pytest.fixture(scope="module")
async def redis_client():
    pool = ConnectionPool.from_url(test_settings.redis_url, max_connections=20)
    redis = Redis(connection_pool=pool, decode_responses=True)
    yield redis
    await redis.close()


@pytest.fixture(scope="module")
def clear_redis(redis_client: Redis):
    async def iner():
        return await redis_client.flushall()

    return iner


@pytest.fixture(scope="module")
def redis_write(redis_client: Redis):
    async def iner(redis_list: List[RedisDataSchema]):
        async with redis_client.pipeline() as pipe:
            for redis_data in redis_list:
                await pipe.set(redis_data.key, redis_data.value)
            ok = await pipe.execute()
        assert all(ok), "Redis data not writed"

    return iner


@pytest.fixture(scope="module")
def redis_get(redis_client: Redis):
    async def iner(key: str):
        redis_data = redis_client.get(key)
        if redis_data:
            return redis_data
        return None

    return iner
