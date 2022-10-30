from enum import Enum

from pydantic import BaseSettings


class AppEnvTypes(Enum):
    prod = "prod"
    dev = "dev"


class BaseAppSettings(BaseSettings):
    app_env: AppEnvTypes = AppEnvTypes.dev

    class Config:
        env_file = ".env"
