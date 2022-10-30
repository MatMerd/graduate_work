import logging
from .app_settings import AppSettings


class DevAppSettings(AppSettings):
    debug: bool = True

    title: str = "Cinema API service"

    logging_level: int = logging.DEBUG

    class Config(AppSettings.Config):
        env_file = ".dev-env"
