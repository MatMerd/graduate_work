from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Tuple
import orjson

import loguru
from pydantic import RedisDsn, SecretStr

import core.log as log
from core.exceptions import SettingsNotFoundError
from .base import BaseAppSettings


def json_config_settings_source(settings: BaseAppSettings) -> dict[str, Any]:
    folder_path = Path(__file__).parent
    settings_filename = settings.__config__.settings_filename  # type: ignore
    setting_path = folder_path / settings_filename
    setting_path = setting_path.absolute()
    if not setting_path.exists():
        log.logger.warning("Warning: settings.json file not exist in project")
        raise SettingsNotFoundError("Create settings.json from settings_template.json")

    api_settings = orjson.loads(setting_path.read_text())

    return api_settings


class AppSettings(BaseAppSettings):
    debug: bool = False
    docs_url: str = "/api/openapi"
    openapi_prefix: str = ""
    openapi_url: str = "/api/openapi.json"
    redoc_url: str = "/api/redoc"
    title: str = "Cinema API service"
    version: str = "0.1.0"

    redis_url: RedisDsn
    celery_broker_url: RedisDsn
    celery_result_backend: RedisDsn

    secret_key: SecretStr = SecretStr("secret")

    api_prefix: str = "/api/v1"

    jwt_token_prefix: str = "Bearer"
    auth_service_url: str = "http://127.0.0.1:8080"

    middleware: dict[str, Any]
    logger: dict[str, Any]

    log_level: int = logging.INFO
    loggers_type: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    class Config:
        env_file_encoding = "utf-8"
        settings_filename: str = "settings.json"

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                json_config_settings_source,
                env_settings,
                file_secret_settings,
            )

    @property
    def app_settings(self) -> dict[str, Any]:
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }

    def setup_logger(
        self, bind_name, *, filter: Callable | None = None
    ) -> loguru.Logger:
        logging.getLogger().handlers = [log.InterceptHandler()]
        for logger_name in self.loggers_type:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [log.InterceptHandler(level=self.log_level)]
        log.logger.remove()
        log.logger.add(**self.logger, filter=log.filter_by_name(bind_name), rotation="10 MB", retention="10 days")  # type: ignore
        return log.logger.bind(name=bind_name)
