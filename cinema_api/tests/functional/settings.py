from pydantic import BaseSettings, RedisDsn


class TestSettings(BaseSettings):
    redis_url: RedisDsn = "redis://user:pass@localhost:6379"
    service_url = "http://cinema_api:8080"

    class Config:
        env_file = ".env"


test_settings = TestSettings()
