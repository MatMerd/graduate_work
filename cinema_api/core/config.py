from functools import lru_cache

from .settings.base import AppEnvTypes
from .settings.app_settings import AppSettings
from .settings.development_app import DevAppSettings
from .settings.production_app import ProdAppSettings


app_type = {AppEnvTypes.dev: DevAppSettings, AppEnvTypes.prod: ProdAppSettings}


@lru_cache
def get_app_settings(env_type: AppEnvTypes = AppEnvTypes.dev) -> AppSettings:
    config = app_type[env_type]
    return config()
