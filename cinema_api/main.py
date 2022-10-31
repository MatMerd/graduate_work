from typing import Any
import uvicorn

import aioredis
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware

from api.v1 import cinema_room, cinema_room_ws
from core.exceptions import CinemaRoomNotFoundError
from db import redis
import core.log as log
from core import config
from core.settings.base import AppEnvTypes


app = FastAPI(
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


def setup_app(env_type: AppEnvTypes | None = None):
    if env_type:
        api_settings = config.get_app_settings(env_type)
    else:
        api_settings = config.get_app_settings()

    config.settings = api_settings

    log.main_logger = api_settings.setup_logger("main_logger")
    setup_app_middleware(api_settings.middleware)
    setup_routers(api_prefix=api_settings.api_prefix)

    @app.on_event("startup")
    async def startup():
        redis._redis_client = await aioredis.from_url(
            api_settings.redis_url,
            max_connections=100,
            encoding="utf-8",
            decode_responses=True,
        )
        log.main_logger.info("Redis has been initialize")

    @app.on_event("shutdown")
    async def shutdown():
        await redis._redis_client.close()

    @app.exception_handler(CinemaRoomNotFoundError)
    async def cinema_not_found_exception_handler(
        request: Request, exc: CinemaRoomNotFoundError
    ):
        return ORJSONResponse(status_code=exc.status_code, content=exc.json_error())


def setup_app_middleware(middleware_settings: dict[str, Any]):
    log.main_logger.info("Setup middlewares")
    app.add_middleware(CORSMiddleware, **middleware_settings)


def setup_routers(api_prefix: str):
    app.include_router(router=cinema_room.router, prefix=f"{api_prefix}/cinema-room")
    app.include_router(
        router=cinema_room_ws.router, prefix=f"{api_prefix}/cinema-room/ws"
    )


if __name__ == "__main__":
    setup_app()
    uvicorn.run(
        "main:app",
        reload=True,
    )
else:
    setup_app()
